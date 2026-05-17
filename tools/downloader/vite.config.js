import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

function proxyPlugin() {
  const route = '/api/proxy'

  return {
    name: 'pdf-downloader-proxy',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        const requestUrl = new URL(req.url, 'http://localhost')
        if (req.method !== 'GET' || requestUrl.pathname !== route) {
          next()
          return
        }

        const targetUrl = requestUrl.searchParams.get('url')
        if (!targetUrl) {
          res.statusCode = 400
          res.end('Missing url')
          return
        }

        try {
          const response = await fetch(targetUrl)
          res.statusCode = response.status

          const contentType = response.headers.get('content-type')
          if (contentType) {
            res.setHeader('content-type', contentType)
          }

          const body = Buffer.from(await response.arrayBuffer())
          res.end(body)
        } catch {
          res.statusCode = 502
          res.end('Proxy request failed')
        }
      })
    },
    configurePreviewServer(server) {
      server.middlewares.use(async (req, res, next) => {
        const requestUrl = new URL(req.url, 'http://localhost')
        if (req.method !== 'GET' || requestUrl.pathname !== route) {
          next()
          return
        }

        const targetUrl = requestUrl.searchParams.get('url')
        if (!targetUrl) {
          res.statusCode = 400
          res.end('Missing url')
          return
        }

        try {
          const response = await fetch(targetUrl)
          res.statusCode = response.status

          const contentType = response.headers.get('content-type')
          if (contentType) {
            res.setHeader('content-type', contentType)
          }

          const body = Buffer.from(await response.arrayBuffer())
          res.end(body)
        } catch {
          res.statusCode = 502
          res.end('Proxy request failed')
        }
      })
    },
  }
}

export default defineConfig({
  plugins: [vue(), proxyPlugin()],
})
