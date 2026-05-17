<script setup>
import { computed, ref } from 'vue'

const pageUrl = ref('')
const loading = ref(false)
const bulkLoading = ref(false)
const error = ref('')
const success = ref('')
const pdfLinks = ref([])
const proxyRoute = '/api/proxy'

const hasResults = computed(() => pdfLinks.value.length > 0)

function buildProxyUrl(targetUrl) {
  return `${proxyRoute}?url=${encodeURIComponent(targetUrl)}`
}

function decodeText(value) {
  try {
    return decodeURI(value)
  } catch {
    return value
  }
}

function normalizeDownloadName(name) {
  return name.replace(/\+/g, '_')
}

function triggerBrowserDownload(blob, name) {
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  const downloadName = normalizeDownloadName(name)
  link.download = downloadName.endsWith('.pdf') ? downloadName : `${downloadName}.pdf`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(objectUrl)
}

function guessFileName(targetUrl) {
  try {
    const parsed = new URL(targetUrl)
    const lastSegment = parsed.pathname.split('/').filter(Boolean).pop()
    return lastSegment ? normalizeDownloadName(decodeURIComponent(lastSegment)) : 'downloaded.pdf'
  } catch {
    return 'downloaded.pdf'
  }
}

function isPdfUrl(targetUrl) {
  try {
    const parsed = new URL(targetUrl)
    return /\.pdf($|[?#])/i.test(parsed.pathname + parsed.search + parsed.hash)
  } catch {
    return false
  }
}

function normalizeCandidate(value, baseUrl) {
  try {
    const resolved = new URL(value, baseUrl)
    return resolved.toString()
  } catch {
    return null
  }
}

function collectPdfLinks(doc, baseUrl) {
  const candidates = new Set()
  const selectors = ['a[href]', 'link[href]', 'iframe[src]', 'embed[src]', 'object[data]']

  for (const selector of selectors) {
    for (const element of doc.querySelectorAll(selector)) {
      const raw =
        element.getAttribute('href') ??
        element.getAttribute('src') ??
        element.getAttribute('data') ??
        ''
      const normalized = normalizeCandidate(raw, baseUrl)
      if (normalized && isPdfUrl(normalized)) {
        candidates.add(normalized)
      }
    }
  }

  return [...candidates].map((targetUrl) => ({
    url: targetUrl,
    name: guessFileName(targetUrl),
  }))
}

async function fetchPageHtml(targetUrl) {
  const response = await fetch(buildProxyUrl(targetUrl))
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/pdf')) {
    return { contentType, html: '', isPdf: true }
  }

  const htmlBlob = await response.blob()
  const html = await htmlBlob.text()
  return { contentType, html, isPdf: false }
}

async function downloadPdfBlob(targetUrl) {
  const response = await fetch(buildProxyUrl(targetUrl))
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return response.blob()
}

async function fetchPdfLinks() {
  error.value = ''
  success.value = ''
  pdfLinks.value = []

  const targetUrl = pageUrl.value.trim()
  if (!targetUrl) {
    error.value = 'กรุณาใส่ URL ของหน้าเว็บ'
    return
  }

  let parsed
  try {
    parsed = new URL(targetUrl)
  } catch {
    error.value = 'URL ไม่ถูกต้อง'
    return
  }

  loading.value = true

  try {
    const { html, isPdf } = await fetchPageHtml(parsed.toString())
    if (isPdf || isPdfUrl(parsed.toString())) {
      pdfLinks.value = [{ url: parsed.toString(), name: guessFileName(parsed.toString()) }]
      success.value = 'พบไฟล์ PDF 1 รายการ'
      return
    }

    const document = new DOMParser().parseFromString(html, 'text/html')
    pdfLinks.value = collectPdfLinks(document, parsed.toString())

    if (!pdfLinks.value.length) {
      error.value = 'ไม่พบลิงก์ PDF ในหน้านี้'
      return
    }

    success.value = `พบไฟล์ PDF ${pdfLinks.value.length} รายการ`
  } catch {
    error.value = 'ค้นหาลิงก์ไม่สำเร็จ'
  } finally {
    loading.value = false
  }
}

async function downloadPdf(targetUrl, name) {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const blob = await downloadPdfBlob(targetUrl)
    triggerBrowserDownload(blob, name)

    success.value = 'ดาวน์โหลดไฟล์แล้ว'
  } catch {
    error.value = 'ดาวน์โหลดไม่สำเร็จ'
  } finally {
    loading.value = false
  }
}

async function downloadAllPdfs() {
  error.value = ''
  success.value = ''

  if (!pdfLinks.value.length) {
    error.value = 'ยังไม่มีรายการ PDF ให้ดาวน์โหลด'
    return
  }

  bulkLoading.value = true

  try {
    for (const item of pdfLinks.value) {
      const blob = await downloadPdfBlob(item.url)
      triggerBrowserDownload(blob, item.name)
    }

    success.value = `ดาวน์โหลดไฟล์ทั้งหมด ${pdfLinks.value.length} รายการแล้ว`
  } catch {
    error.value = 'ดาวน์โหลดทั้งหมดไม่สำเร็จ'
  } finally {
    bulkLoading.value = false
  }
}
</script>

<template>
  <main class="shell">
    <section class="card">
      <p class="eyebrow">PDF Downloader</p>
      <h1>ค้นหาและดาวน์โหลด PDF</h1>
      <p class="description">ดึง HTML ของหน้าเว็บมาก่อน แล้วค้นหาลิงก์ PDF เพื่อดาวน์โหลด</p>

      <form class="form" @submit.prevent="fetchPdfLinks">
        <label class="field">
          <span>Page URL</span>
          <input
            v-model="pageUrl"
            type="url"
            placeholder="https://example.com/page"
            autocomplete="off"
          />
        </label>

        <button type="submit" :disabled="loading || bulkLoading">
          {{ loading ? 'กำลังค้นหา...' : 'ค้นหา PDF' }}
        </button>
      </form>

      <div v-if="hasResults" class="results">
        <div class="results-header">
          <p class="results-title">PDF links</p>
          <button type="button" class="secondary" :disabled="loading || bulkLoading" @click="downloadAllPdfs">
            {{ bulkLoading ? 'กำลังดาวน์โหลดทั้งหมด...' : 'Download all' }}
          </button>
        </div>
        <div class="result-list">
          <div v-for="item in pdfLinks" :key="item.url" class="result-item">
            <div>
              <p class="result-name">{{ item.name }}</p>
              <p class="result-url">{{ decodeText(item.url) }}</p>
            </div>
            <button type="button" :disabled="loading || bulkLoading" @click="downloadPdf(item.url, item.name)">
              Download
            </button>
          </div>
        </div>
      </div>

      <p v-if="error" class="message error">{{ error }}</p>
      <p v-else-if="success" class="message success">{{ success }}</p>
    </section>
  </main>
</template>
