# syntax=docker/dockerfile:1
ARG NPM_REGISTRY=https://registry.npmmirror.com

FROM node:18-alpine AS builder
WORKDIR /app
ARG NPM_REGISTRY
RUN npm config set registry "$NPM_REGISTRY" && npm install -g pnpm
COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --no-frozen-lockfile
COPY . .
RUN pnpm run build

FROM nginx:1.25-alpine
COPY --from=builder /app/dist/build/h5 /usr/share/nginx/html/chuilei/chatbox
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
