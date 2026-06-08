import logging
import json
import asyncio
import httpx
from typing import AsyncIterator, List, Dict, Any

logger = logging.getLogger(__name__)

# --- Mock 模拟数据，用于连不上外部信令服务时的容灾降级演示 ---
MOCK_PCAP_MSG = """### 📊 信令分析报告

**业务信息概要**：
* **用户信息**：
  * 用户 IMSI：`4600846`
* **终端信息**：
  * 5GNSA能力: 不支持
  * 5GSA能力：不支持
* **网络信息**：
  * 业务发起TAC区：`6737`
  * 业务发起小区：`262824577`

**关键流程信息**：
1. UE 向 MME 发起 Attach 流程
2. UE 向 MME 发起 PDN Connectivity 流程

**异常根因推理**：
* **第1个流程：Attach 拒绝**
  * **问题分析**：2024-06-02 14:09:02.201 RAN（10.106.177.131）向 APP-HDNJIHzjAMFm005BHW-07AHW011 发起 Attach 流程，2024-06-02 14:09:02.687 DFMHSS05FE01AZX 向 APP-HDNJIHhdnDRASTP1AHWA-07AHW012 发送 Update-Location Answer 消息，并携带原因值 `5421:DIAMETER_ERROR_RAT_NOT_ALLOWED`，最后 MME 向 RAN 发送 Attach reject，并携带原因值 `No suitable cells in tracking area`，从而导致流程失败。
  * **可能原因**：用户接入类型受限或漫游权限受限。
  * **排障建议**：建议核查 HSS 侧 RAT-Type AVP 确认接入限制以及 PLMN 漫游权限相关配置。
"""

MOCK_SWIMLANE_DATA = json.dumps([
    {
        "identifyCallName": "主叫",
        "srcDevice": "UE",
        "dstDevice": "RAN",
        "appl": "RRC",
        "3": "2026-06-08 17:00:00.000",
        "5": "RRC Setup Request"
    },
    {
        "identifyCallName": "主叫",
        "srcDevice": "RAN",
        "dstDevice": "UE",
        "appl": "RRC",
        "3": "2026-06-08 17:00:00.045",
        "5": "RRC Setup"
    },
    {
        "identifyCallName": "主叫",
        "srcDevice": "UE",
        "dstDevice": "RAN",
        "appl": "RRC",
        "3": "2026-06-08 17:00:00.090",
        "5": "RRC Setup Complete (Attach Request)"
    },
    {
        "identifyCallName": "主叫",
        "srcDevice": "RAN",
        "dstDevice": "MME",
        "appl": "S1AP",
        "3": "2026-06-08 17:00:00.120",
        "5": "Initial UE Message (Attach Request)"
    },
    {
        "identifyCallName": "主叫",
        "srcDevice": "MME",
        "dstDevice": "HSS",
        "appl": "Diameter",
        "3": "2026-06-08 17:00:00.310",
        "5": "Update Location Request"
    },
    {
        "identifyCallName": "主叫",
        "srcDevice": "HSS",
        "dstDevice": "MME",
        "appl": "Diameter",
        "3": "2026-06-08 17:00:00.580",
        "5": "Update Location Answer (DIAMETER_ERROR_RAT_NOT_ALLOWED)"
    },
    {
        "identifyCallName": "主叫",
        "srcDevice": "MME",
        "dstDevice": "RAN",
        "appl": "S1AP",
        "3": "2026-06-08 17:00:00.720",
        "5": "Downlink NAS Transport (Attach Reject: No suitable cells in tracking area)"
    },
    {
        "identifyCallName": "主叫",
        "srcDevice": "RAN",
        "dstDevice": "UE",
        "appl": "RRC",
        "3": "2026-06-08 17:00:00.750",
        "5": "RRC Connection Release"
    }
], ensure_ascii=False)


async def upload_pcap_file(api_base_url: str, file_name: str, file_path: str) -> str:
    """上传本地 PCAP 文件至第三方信令系统，并返回分配的 fileId (即 ai_ref_id)。

    如果服务无法连接或失败，则自动降级返回 Mock ID 以保证演示顺畅。
    """
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
    except Exception as e:
        logger.exception("Failed to read local pcap file: %s", file_path)
        raise RuntimeError(f"本地信令文件读取失败: {str(e)}")

    upload_url = f"{api_base_url.rstrip('/')}/importSinglePcap"
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info("Uploading pcap file to %s, filename=%s", upload_url, file_name)
            files = {
                "pcapfilename": (file_name, file_content, "application/vnd.tcpdump.pcap")
            }
            resp = await client.post(upload_url, files=files)
            if resp.status_code != 200:
                logger.error(
                    "Failed to upload pcap, status_code=%s, response=%s",
                    resp.status_code,
                    resp.text,
                )
                raise RuntimeError(f"上传信令文件至分析服务失败 (HTTP {resp.status_code})")

            data = resp.json()
            if not data.get("success"):
                logger.error("Failed to upload pcap, api_response=%s", data)
                raise RuntimeError(f"信令服务上传失败: {data.get('message', '未知接口错误')}")

            file_id = data["data"]["fileId"]
            logger.info("Pcap uploaded successfully. ai_ref_id: %s", file_id)
            return file_id
    except Exception as e:
        logger.warning("Failed to connect/upload to signalling service, falling back to Mock. Error: %s", str(e))
        return "mock_ai_ref_id"


async def fetch_pcap_msg(
    api_base_url: str,
    ai_ref_id: str,
    module_type: str,
) -> AsyncIterator[str]:
    """流式获取特定模块下的 AI 推理分析建议文本。

    如果为 Mock ID 或拉取失败，则流式推送 Mock 报告内容。
    """
    if ai_ref_id == "mock_ai_ref_id":
        chunk_size = 15
        for i in range(0, len(MOCK_PCAP_MSG), chunk_size):
            yield MOCK_PCAP_MSG[i : i + chunk_size]
            await asyncio.sleep(0.02)
        return

    msg_url = f"{api_base_url.rstrip('/')}/getPcapMsg"
    params = {
        "aiRefId": ai_ref_id,
        "type": module_type,
        "sub_type": "undefined",
    }

    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            logger.info("Fetching pcap analysis from %s, params=%s", msg_url, params)
            async with client.stream("GET", msg_url, params=params) as response:
                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code}")

                async for line in response.iter_lines():
                    if not line:
                        continue
                    if not line.startswith("data:"):
                        continue
                    msg = line[len("data:") :].strip()
                    if msg == "[DONE]":
                        break

                    try:
                        json_msg = json.loads(msg)
                        if isinstance(json_msg, dict):
                            if json_msg.get("event") == "text_chunk":
                                text = json_msg.get("data", {}).get("text", "")
                                if text:
                                    yield text
                            elif "answer" in json_msg:
                                yield json_msg["answer"]
                    except json.JSONDecodeError:
                        yield msg
    except Exception as e:
        logger.warning("Failed to fetch pcap msg from upstream, falling back to Mock. Error: %s", str(e))
        # 发生错误，降级推送 Mock 报告
        chunk_size = 15
        for i in range(0, len(MOCK_PCAP_MSG), chunk_size):
            yield MOCK_PCAP_MSG[i : i + chunk_size]
            await asyncio.sleep(0.02)


async def get_pcap_modules(api_base_url: str, ai_ref_id: str) -> List[Dict[str, Any]]:
    """获取该 PCAP 分析后可用的一组诊断诊断/推理模块。"""
    if ai_ref_id == "mock_ai_ref_id":
        return [{"value": "attach_reject", "display": "Attach拒绝根因推理"}]

    modules_url = f"{api_base_url.rstrip('/')}/getPcapModuleType"
    params = {"aiRefId": ai_ref_id}
    try:
        async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
            resp = await client.get(modules_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status"):
                    return data.get("result", [])
    except Exception as e:
        logger.warning("Failed to fetch module types from upstream, falling back to Mock. Error: %s", str(e))
    # 发生异常默认降级返回 Mock 模块
    return [{"value": "attach_reject", "display": "Attach拒绝根因推理"}]


async def run_xinling_swimlane_bridge(
    api_base_url: str,
    ai_ref_id: str,
) -> AsyncIterator[str]:
    """获取 PCAP 报文信令交互泳道图数据，并以一帧完整的 JSON 字符串形式流式产出。"""
    if ai_ref_id == "mock_ai_ref_id":
        yield MOCK_SWIMLANE_DATA
        return

    url = f"{api_base_url.rstrip('/')}/importPcapByAiRefId"
    params = {"aiRefId": ai_ref_id}

    try:
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            logger.info("Fetching swimlane data from %s, params=%s", url, params)
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status"):
                    reports = data.get("result", {}).get("reports", [])
                    logger.info("Swimlane data fetched successfully, %d reports.", len(reports))
                    yield json.dumps(reports, ensure_ascii=False)
                    return
            raise RuntimeError("status is false or status_code is not 200")
    except Exception as e:
        logger.warning("Failed to fetch swimlane from upstream, falling back to Mock. Error: %s", str(e))
        yield MOCK_SWIMLANE_DATA
