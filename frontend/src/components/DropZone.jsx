import { useCallback, useRef, useState } from 'react'
import { UploadCloud, X, FileText, Image as ImageIcon, CheckCircle2, ShieldAlert } from 'lucide-react'
import clsx from 'clsx'

const ACCEPTED = ['.jpg', '.jpeg', '.png', '.pdf']

export default function DropZone({ files, onFilesChange, multiple = true, label, hint, showSupportedBadges = true }) {
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  const handleFiles = useCallback(
    (fileList) => {
      const arr = Array.from(fileList).filter((f) =>
        ACCEPTED.some((ext) => f.name.toLowerCase().endsWith(ext))
      )
      if (!arr.length) return
      if (multiple) {
        onFilesChange([...files, ...arr])
      } else {
        onFilesChange([arr[0]])
      }
    },
    [files, multiple, onFilesChange]
  )

  const removeFile = (idx) => {
    onFilesChange(files.filter((_, i) => i !== idx))
  }

  return (
    <div className="space-y-3">
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          handleFiles(e.dataTransfer.files)
        }}
        className={clsx(
          'group cursor-pointer rounded-xl border-2 border-dashed p-7 text-center transition-all duration-200 relative overflow-hidden',
          dragOver
            ? 'border-accent-400 bg-accent-500/10 shadow-[0_0_25px_rgba(56,189,248,0.2)] scale-[1.01]'
            : 'border-ink-700 bg-gradient-to-b from-ink-900/90 to-ink-950/80 hover:border-accent-500/60 hover:bg-ink-850/60'
        )}
      >
        <input
          ref={inputRef}
          type="file"
          multiple={multiple}
          accept={ACCEPTED.join(',')}
          className="hidden"
          onChange={(e) => {
            handleFiles(e.target.files)
            e.target.value = ''
          }}
        />

        {/* Center upload icon */}
        <div className="mx-auto mb-3.5 flex items-center justify-center w-12 h-12 rounded-xl bg-accent-500/10 text-accent-400 border border-accent-500/30 group-hover:scale-110 group-hover:border-accent-400 transition-transform duration-200">
          <UploadCloud size={24} />
        </div>

        <p className="text-base font-bold text-slate-100 group-hover:text-accent-300 transition-colors">
          {label || 'Drag & drop document images or PDFs, or click to browse'}
        </p>
        <p className="text-sm text-slate-300 mt-1">
          {hint || 'Accepts PNG, JPG, JPEG, or PDF · Max 10MB per file'}
        </p>

        {showSupportedBadges && (
          <div className="mt-4 pt-3 border-t border-ink-800/80 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-300">
            <span className="text-xs uppercase font-bold text-slate-400 mr-1">Supported:</span>
            {['Aadhaar Card', 'PAN Card', 'Passport', 'Driving Licence', 'Voter ID'].map((badge) => (
              <span
                key={badge}
                className="px-2.5 py-1 rounded-md bg-ink-800 text-slate-200 border border-ink-700 text-xs font-semibold"
              >
                {badge}
              </span>
            ))}
          </div>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2.5">
          <div className="flex items-center justify-between text-sm text-slate-300 font-semibold px-1">
            <span>Uploaded Files ({files.length})</span>
            <span className="text-accent-400">Ready for screening</span>
          </div>
          {files.map((file, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between rounded-xl border border-ink-700/80 bg-ink-900/90 px-4 py-3 shadow-sm transition-all hover:border-ink-600"
            >
              <div className="flex items-center gap-3.5 min-w-0">
                <div className="w-9 h-9 rounded-lg bg-accent-500/10 border border-accent-500/20 flex items-center justify-center shrink-0">
                  {file.type === 'application/pdf' ? (
                    <FileText size={18} className="text-accent-400" />
                  ) : (
                    <ImageIcon size={18} className="text-accent-400" />
                  )}
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-bold text-slate-100 truncate">{file.name}</div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    {(file.size / 1024).toFixed(1)} KB · {file.type || 'Document File'}
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  removeFile(idx)
                }}
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-md transition-colors shrink-0 ml-2"
                title="Remove file"
              >
                <X size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
