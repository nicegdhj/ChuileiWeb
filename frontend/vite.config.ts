import { defineConfig, loadEnv } from 'vite'
import path from 'path'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig(({ mode }) => {
  const viteEnv = loadEnv(mode, process.cwd())
  return {
    base: mode === 'production' ? '/chuilei/chat/' : '/',
    resolve: {
      alias: {
        '@': `${path.resolve(__dirname, 'src')}`
      }
    },
    build: {
      sourcemap: process.env.NODE_ENV === 'development'
    },
    plugins: [uni()],
    server: {
      host: true,
      port: 8080,
      hmr: true,
      open: false,
      cors: true,
      proxy: {
        '/api': {
          target: viteEnv.VITE_BACKEND_URL || 'http://localhost:8000',
          changeOrigin: true
        },
        '/files': {
          target: viteEnv.VITE_BACKEND_URL || 'http://localhost:8000',
          changeOrigin: true
        }
      }
    },
    css: {
      postcss: {
        plugins: [require('tailwindcss'), require('autoprefixer')]
      }
    }
  }
})
