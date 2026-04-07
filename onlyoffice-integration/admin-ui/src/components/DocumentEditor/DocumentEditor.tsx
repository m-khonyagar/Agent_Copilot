import { useEffect, useRef, useState } from 'react'

interface EditorConfig {
  document: {
    fileType: string
    key: string
    title: string
    url: string
    permissions: Record<string, boolean>
  }
  documentType: string
  editorConfig: {
    callbackUrl: string
    lang: string
    mode: string
    user: { id: string; name: string }
    customization: Record<string, unknown>
  }
  token: string
}

interface DocumentEditorProps {
  /** Full ONLYOFFICE editor config object (returned from /onlyoffice-docs/:id/editor-config) */
  config: EditorConfig
  /** Base URL of the ONLYOFFICE Document Server, e.g. http://onlyoffice:8180 */
  onlyofficeUrl: string
  /** Callback fired when the editor is fully ready */
  onReady?: () => void
  /** Callback fired when ONLYOFFICE fires an error event */
  onError?: (event: unknown) => void
  /** Height of the editor iframe (default: 100%) */
  height?: string
  /** Width of the editor iframe (default: 100%) */
  width?: string
}

declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    DocsAPI?: any
  }
}

let _scriptLoaded = false
let _scriptLoading = false
const _callbacks: Array<() => void> = []

function loadOnlyOfficeScript(baseUrl: string, onLoad: () => void) {
  if (_scriptLoaded) {
    onLoad()
    return
  }
  _callbacks.push(onLoad)
  if (_scriptLoading) return

  _scriptLoading = true
  const script = document.createElement('script')
  script.src = `${baseUrl.replace(/\/$/, '')}/web-apps/apps/api/documents/api.js`
  script.async = true
  script.onload = () => {
    _scriptLoaded = true
    _scriptLoading = false
    _callbacks.forEach((cb) => cb())
    _callbacks.length = 0
  }
  document.head.appendChild(script)
}

let _instanceCounter = 0

/**
 * DocumentEditor
 *
 * Renders an ONLYOFFICE Document Editor inside an iframe via the DocsAPI.
 * The ONLYOFFICE JS SDK is loaded lazily from the configured Document Server.
 *
 * Usage:
 * ```tsx
 * <DocumentEditor
 *   config={editorConfigFromApi}
 *   onlyofficeUrl="https://office.amline.ir"
 * />
 * ```
 */
export function DocumentEditor({
  config,
  onlyofficeUrl,
  onReady,
  onError,
  height = '100%',
  width = '100%',
}: DocumentEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const editorRef = useRef<any>(null)
  const instanceIdRef = useRef(`onlyoffice-editor-${++_instanceCounter}`)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    loadOnlyOfficeScript(onlyofficeUrl, () => {
      if (!window.DocsAPI) {
        setError('ONLYOFFICE DocsAPI is not available. Check the Document Server URL.')
        setLoading(false)
        return
      }

      // Destroy any previous instance attached to this container
      if (editorRef.current) {
        try {
          editorRef.current.destroyEditor()
        } catch (err) {
          console.warn('[DocumentEditor] destroyEditor failed before re-init:', err)
        }
      }

      editorRef.current = new window.DocsAPI.DocEditor(instanceIdRef.current, {
        ...config,
        events: {
          onReady: () => {
            setLoading(false)
            onReady?.()
          },
          onError: (evt: unknown) => {
            setError('خطا در بارگذاری ویرایشگر')
            setLoading(false)
            onError?.(evt)
          },
          onDocumentStateChange: () => {
            // Document modified — can be used to show a "unsaved" indicator
          },
        },
        width,
        height,
      })
    })

    return () => {
      if (editorRef.current) {
        try {
          editorRef.current.destroyEditor()
        } catch (err) {
          console.warn('[DocumentEditor] destroyEditor failed on unmount:', err)
        }
        editorRef.current = null
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config.document.key, onlyofficeUrl])

  return (
    <div className="relative h-full w-full" style={{ height, width }}>
      {loading && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 bg-[var(--amline-bg)]">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--amline-primary)] border-t-transparent" />
          <p className="text-sm text-[var(--amline-fg-muted)]">در حال بارگذاری ویرایشگر…</p>
        </div>
      )}
      {error && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 bg-[var(--amline-bg)] p-6">
          <span className="text-4xl">⚠️</span>
          <p className="text-center text-sm text-red-600 dark:text-red-400">{error}</p>
          <p className="text-center text-xs text-[var(--amline-fg-muted)]">
            مطمئن شوید که سرویس ONLYOFFICE در آدرس{' '}
            <code className="rounded bg-slate-100 px-1 dark:bg-slate-800">{onlyofficeUrl}</code>{' '}
            در دسترس است.
          </p>
        </div>
      )}
      <div
        id={instanceIdRef.current}
        ref={containerRef}
        className="h-full w-full"
        aria-label="ویرایشگر سند"
      />
    </div>
  )
}
