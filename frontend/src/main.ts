import { createSSRApp } from 'vue'
import pinia from './stores'
import './style/github-markdown.scss'
import './style/normalize.scss'
import './style/highlight.scss'

import './style/tailwind.css'
import './style/variables.scss'
import App from './App.vue'
export function createApp() {
  const app = createSSRApp(App)
  app.use(pinia)
  return {
    app
  }
}
