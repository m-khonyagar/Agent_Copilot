import { lazy, Suspense, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

const DocumentEditor = lazy(() =>
  import('../../components/DocumentEditor/DocumentEditor').then((m) => ({
    default: m.DocumentEditor,
  }))
)

// ── Types ────────────────────────────────────────────────────────────────────

interface OfficeDocument {
  id: string
  title: string
  file_type: string
  status: string
  version: number
  owner_id: string
  created_at: string
  updated_at: string | null
}

interface EditorConfigResponse {
  config: Record<string, unknown>
  onlyoffice_url: string
}

// ── API helpers ──────────────────────────────────────────────────────────────

function authHeader() {
  const token = localStorage.getItem('amline_access_token') ?? ''
  return { Authorization: `Bearer ${token}` }
}

const BASE = import.meta.env.VITE_API_URL ?? ''

async function fetchDocuments(): Promise<OfficeDocument[]> {
  const res = await axios.get(`${BASE}/onlyoffice-docs`, { headers: authHeader() })
  return res.data
}

async function createDocument(payload: {
  title: string
  file_type: string
}): Promise<OfficeDocument> {
  const res = await axios.post(`${BASE}/onlyoffice-docs`, payload, {
    headers: authHeader(),
  })
  return res.data
}

async function deleteDocument(id: string): Promise<void> {
  await axios.delete(`${BASE}/onlyoffice-docs/${id}`, { headers: authHeader() })
}

async function fetchEditorConfig(id: string, mode = 'edit'): Promise<EditorConfigResponse> {
  const res = await axios.get(`${BASE}/onlyoffice-docs/${id}/editor-config?mode=${mode}`, {
    headers: authHeader(),
  })
  return res.data
}

// ── File-type icons ───────────────────────────────────────────────────────────

const FILE_TYPE_ICON: Record<string, string> = {
  docx: '📝',
  xlsx: '📊',
  pptx: '📽️',
  pdf: '📄',
  odt: '📝',
  ods: '📊',
  odp: '📽️',
}

function fileIcon(type: string): string {
  return FILE_TYPE_ICON[type.toLowerCase()] ?? '📄'
}

const FILE_TYPES = [
  { value: 'docx', label: 'Word (docx)' },
  { value: 'xlsx', label: 'Excel (xlsx)' },
  { value: 'pptx', label: 'PowerPoint (pptx)' },
]

// ── Create-document modal ─────────────────────────────────────────────────────

interface CreateModalProps {
  onClose: () => void
  onCreate: (title: string, fileType: string) => void
  busy: boolean
}

function CreateModal({ onClose, onCreate, busy }: CreateModalProps) {
  const [title, setTitle] = useState('')
  const [fileType, setFileType] = useState('docx')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    onCreate(title.trim(), fileType)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" dir="rtl">
      <div className="w-full max-w-md rounded-2xl border border-[var(--amline-border)] bg-[var(--amline-surface)] p-6 shadow-amline dark:border-slate-700 dark:bg-slate-900">
        <h2 className="mb-4 text-lg font-bold text-[var(--amline-fg)]">سند جدید</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-[var(--amline-fg-muted)]">
              عنوان سند
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="مثال: قرارداد اجاره واحد ۱۲"
              className="w-full rounded-amline-md border border-[var(--amline-border)] bg-[var(--amline-bg)] px-3 py-2 text-sm text-[var(--amline-fg)] outline-none focus:border-[var(--amline-primary)] focus:ring-1 focus:ring-[var(--amline-primary)] dark:border-slate-600 dark:bg-slate-800"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-[var(--amline-fg-muted)]">
              نوع فایل
            </label>
            <select
              value={fileType}
              onChange={(e) => setFileType(e.target.value)}
              className="w-full rounded-amline-md border border-[var(--amline-border)] bg-[var(--amline-bg)] px-3 py-2 text-sm text-[var(--amline-fg)] outline-none focus:border-[var(--amline-primary)] dark:border-slate-600 dark:bg-slate-800"
            >
              {FILE_TYPES.map((ft) => (
                <option key={ft.value} value={ft.value}>
                  {ft.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-amline-md border border-[var(--amline-border)] px-4 py-2 text-sm text-[var(--amline-fg-muted)] transition-colors hover:bg-[var(--amline-surface-muted)] dark:border-slate-600"
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={busy || !title.trim()}
              className="rounded-amline-md bg-[var(--amline-primary)] px-4 py-2 text-sm font-semibold text-white transition-colors hover:opacity-90 disabled:opacity-50"
            >
              {busy ? 'در حال ایجاد…' : 'ایجاد سند'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function OfficePage() {
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [activeDocId, setActiveDocId] = useState<string | null>(null)
  const [editorMode, setEditorMode] = useState<'edit' | 'view'>('edit')

  const { data: docs = [], isLoading, isError } = useQuery({
    queryKey: ['office-docs'],
    queryFn: fetchDocuments,
  })

  const { data: editorData } = useQuery({
    queryKey: ['office-editor-config', activeDocId, editorMode],
    queryFn: () => fetchEditorConfig(activeDocId!, editorMode),
    enabled: !!activeDocId,
  })

  const createMutation = useMutation({
    mutationFn: createDocument,
    onSuccess: (doc) => {
      queryClient.invalidateQueries({ queryKey: ['office-docs'] })
      setShowCreate(false)
      setActiveDocId(doc.id)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteDocument,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['office-docs'] })
      if (activeDocId === id) setActiveDocId(null)
    },
  })

  function handleDelete(id: string) {
    if (confirm('آیا از حذف این سند اطمینان دارید؟')) {
      deleteMutation.mutate(id)
    }
  }

  // ── Editor full-screen view ─────────────────────────────────────────────

  if (activeDocId && editorData) {
    const activeDoc = docs.find((d) => d.id === activeDocId)
    return (
      <div className="flex h-[calc(100vh-4rem)] flex-col" dir="rtl">
        {/* Editor toolbar */}
        <div className="flex shrink-0 items-center justify-between border-b border-[var(--amline-border)] bg-[var(--amline-surface)] px-4 py-3 dark:border-slate-700 dark:bg-slate-900">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setActiveDocId(null)}
              className="flex items-center gap-1.5 rounded-amline-md border border-[var(--amline-border)] px-3 py-1.5 text-sm text-[var(--amline-fg-muted)] transition-colors hover:bg-[var(--amline-surface-muted)] dark:border-slate-600"
              aria-label="بازگشت به فهرست اسناد"
            >
              ← بازگشت
            </button>
            <span className="text-sm font-semibold text-[var(--amline-fg)]">
              {fileIcon(activeDoc?.file_type ?? 'docx')} {activeDoc?.title}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--amline-fg-muted)]">
              نسخه {activeDoc?.version ?? 1}
            </span>
            <button
              type="button"
              onClick={() => setEditorMode(editorMode === 'edit' ? 'view' : 'edit')}
              className="rounded-amline-md border border-[var(--amline-border)] px-3 py-1.5 text-xs transition-colors hover:bg-[var(--amline-surface-muted)] dark:border-slate-600"
            >
              {editorMode === 'edit' ? '👁 فقط نمایش' : '✏️ ویرایش'}
            </button>
          </div>
        </div>

        {/* Editor */}
        <div className="flex-1 overflow-hidden">
          <Suspense
            fallback={
              <div className="flex h-full items-center justify-center">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--amline-primary)] border-t-transparent" />
              </div>
            }
          >
            <DocumentEditor
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              config={editorData.config as any}
              onlyofficeUrl={editorData.onlyoffice_url}
              height="100%"
              width="100%"
            />
          </Suspense>
        </div>
      </div>
    )
  }

  // ── Document list view ──────────────────────────────────────────────────

  return (
    <div dir="rtl" className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--amline-fg)]">اسناد آفیس</h1>
          <p className="mt-1 text-sm text-[var(--amline-fg-muted)]">
            ایجاد و ویرایش اسناد Word، Excel و PowerPoint با ONLYOFFICE
          </p>
        </div>
        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 rounded-amline-md bg-[var(--amline-primary)] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:opacity-90"
        >
          <span aria-hidden="true">+</span>
          سند جدید
        </button>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex justify-center py-16">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--amline-primary)] border-t-transparent" />
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center dark:border-red-800 dark:bg-red-950/30">
          <p className="text-sm text-red-700 dark:text-red-300">خطا در بارگذاری اسناد</p>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !isError && docs.length === 0 && (
        <div className="flex flex-col items-center gap-4 rounded-2xl border border-dashed border-[var(--amline-border)] py-16 text-center dark:border-slate-700">
          <span className="text-5xl">📂</span>
          <p className="text-[var(--amline-fg-muted)]">هنوز سندی ایجاد نشده</p>
          <button
            type="button"
            onClick={() => setShowCreate(true)}
            className="rounded-amline-md bg-[var(--amline-primary)] px-5 py-2 text-sm font-semibold text-white hover:opacity-90"
          >
            اولین سند را بسازید
          </button>
        </div>
      )}

      {/* Document grid */}
      {docs.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {docs.map((doc) => (
            <div
              key={doc.id}
              className="group relative flex flex-col gap-3 rounded-2xl border border-[var(--amline-border)] bg-[var(--amline-surface)] p-5 shadow-[var(--amline-shadow-sm)] transition-shadow hover:shadow-amline dark:border-slate-700 dark:bg-slate-900"
            >
              {/* Icon + type badge */}
              <div className="flex items-start justify-between">
                <span className="text-4xl" aria-hidden="true">
                  {fileIcon(doc.file_type)}
                </span>
                <span className="rounded-full bg-[var(--amline-primary-muted)] px-2.5 py-0.5 text-xs font-medium text-[var(--amline-primary)] dark:bg-blue-950/40 dark:text-blue-300">
                  {doc.file_type.toUpperCase()}
                </span>
              </div>

              {/* Title */}
              <div className="min-w-0 flex-1">
                <p className="truncate font-semibold text-[var(--amline-fg)]">{doc.title}</p>
                <p className="mt-0.5 text-xs text-[var(--amline-fg-muted)]">
                  نسخه {doc.version} ·{' '}
                  {new Date(doc.created_at).toLocaleDateString('fa-IR', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                </p>
              </div>

              {/* Status badge */}
              <span
                className={`self-start rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  doc.status === 'saved'
                    ? 'bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-300'
                    : doc.status === 'error'
                      ? 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-300'
                      : doc.status === 'saving'
                        ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300'
                        : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
                }`}
              >
                {doc.status === 'saved'
                  ? '✓ ذخیره شد'
                  : doc.status === 'error'
                    ? '✗ خطا'
                    : doc.status === 'saving'
                      ? '⟳ در حال ذخیره'
                      : '● فعال'}
              </span>

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setEditorMode('edit')
                    setActiveDocId(doc.id)
                  }}
                  className="flex-1 rounded-amline-md bg-[var(--amline-primary)] px-3 py-2 text-xs font-semibold text-white transition-all hover:opacity-90"
                >
                  ✏️ ویرایش
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setEditorMode('view')
                    setActiveDocId(doc.id)
                  }}
                  className="rounded-amline-md border border-[var(--amline-border)] px-3 py-2 text-xs transition-colors hover:bg-[var(--amline-surface-muted)] dark:border-slate-600"
                  aria-label="مشاهده"
                >
                  👁
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(doc.id)}
                  className="rounded-amline-md border border-red-200 px-3 py-2 text-xs text-red-600 transition-colors hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950/30"
                  aria-label="حذف"
                >
                  🗑
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create modal */}
      {showCreate && (
        <CreateModal
          onClose={() => setShowCreate(false)}
          onCreate={(title, fileType) => createMutation.mutate({ title, file_type: fileType })}
          busy={createMutation.isPending}
        />
      )}
    </div>
  )
}
