import { useEffect, useRef, useState } from 'react'
import { Eye, ShieldAlert, Scan, FileSearch, Layers } from 'lucide-react'

export default function ImagePreviewWithRegions({ file, regions = [] }) {
  const [url, setUrl] = useState(null)
  const [naturalSize, setNaturalSize] = useState({ w: 1, h: 1 })
  const [activeRegion, setActiveRegion] = useState(null)
  const imgRef = useRef(null)

  useEffect(() => {
    if (!file) return
    const objectUrl = URL.createObjectURL(file)
    setUrl(objectUrl)
    return () => URL.revokeObjectURL(objectUrl)
  }, [file])

  if (!file || file.type === 'application/pdf') {
    return (
      <div className="rounded-xl border border-ink-700/70 bg-ink-900/60 p-8 text-center">
        <div className="mx-auto w-10 h-10 rounded-lg bg-ink-800 flex items-center justify-center text-slate-400 mb-2">
          <Scan size={20} />
        </div>
        <p className="text-sm font-medium text-slate-300">
          {file ? 'PDF Document Processing Active' : 'No document preview available'}
        </p>
        <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
          {file
            ? 'PDF pages are rendered and analyzed in backend isolation. Extracted OCR fields and anomaly findings are detailed below.'
            : 'Upload a document to view forensic region highlighting.'}
        </p>
      </div>
    )
  }

  const severityColor = (sev) => {
    if (sev === 'HIGH') {
      return {
        border: 'border-rose-500',
        bg: 'bg-rose-500/20',
        text: 'text-rose-300',
        badgeBg: 'bg-rose-500 text-slate-950',
        hex: '#f43f5e',
      }
    }
    if (sev === 'MEDIUM') {
      return {
        border: 'border-amber-500',
        bg: 'bg-amber-500/20',
        text: 'text-amber-300',
        badgeBg: 'bg-amber-500 text-slate-950',
        hex: '#f59e0b',
      }
    }
    return {
      border: 'border-sky-400',
      bg: 'bg-sky-500/20',
      text: 'text-sky-300',
      badgeBg: 'bg-sky-400 text-slate-950',
      hex: '#38bdf8',
    }
  }

  return (
    <div className="space-y-4">
      {/* Forensic Viewer Frame */}
      <div className="relative rounded-xl border border-ink-700/80 bg-ink-950 overflow-hidden shadow-panel">
        {/* Top Viewer Bar */}
        <div className="px-4 py-2 bg-ink-900/90 border-b border-ink-700/70 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2 font-mono text-[11px]">
            <Scan size={14} className="text-accent-400" />
            <span className="text-slate-300 font-semibold">FORENSIC INSPECTION OVERLAY</span>
          </div>
          <div className="flex items-center gap-3 text-[11px]">
            <span className="flex items-center gap-1.5 text-slate-400">
              <Layers size={13} className="text-slate-400" />
              {regions.length} {regions.length === 1 ? 'region' : 'regions'} flagged
            </span>
          </div>
        </div>

        {/* Image Display with Bounding Boxes */}
        <div className="relative flex justify-center items-center bg-black/40 p-4 min-h-[220px]">
          <div className="relative inline-block max-w-full">
            {url && (
              <img
                ref={imgRef}
                src={url}
                alt="Document preview"
                className="block max-w-full max-h-[420px] h-auto rounded-md shadow-lg object-contain border border-ink-800"
                onLoad={(e) => setNaturalSize({ w: e.target.naturalWidth || 1, h: e.target.naturalHeight || 1 })}
              />
            )}

            {/* Render Suspicious Bounding Boxes */}
            {regions.map((r, idx) => {
              const leftPct = (r.x / naturalSize.w) * 100
              const topPct = (r.y / naturalSize.h) * 100
              const widthPct = (r.width / naturalSize.w) * 100
              const heightPct = (r.height / naturalSize.h) * 100
              const colors = severityColor(r.severity)
              const isSelected = activeRegion === idx

              return (
                <div
                  key={idx}
                  onMouseEnter={() => setActiveRegion(idx)}
                  onMouseLeave={() => setActiveRegion(null)}
                  className={`absolute border-2 rounded-sm transition-all duration-150 cursor-pointer ${colors.border} ${colors.bg} ${
                    isSelected ? 'ring-2 ring-white/80 scale-[1.02] z-20' : 'z-10'
                  }`}
                  style={{
                    left: `${leftPct}%`,
                    top: `${topPct}%`,
                    width: `${widthPct}%`,
                    height: `${heightPct}%`,
                    boxShadow: `0 0 16px ${colors.hex}60`,
                  }}
                >
                  {/* Severity Badge */}
                  <span
                    className={`absolute -top-5 left-0 text-[9px] font-bold px-1.5 py-0.5 rounded shadow whitespace-nowrap tracking-wider ${colors.badgeBg}`}
                  >
                    {r.severity}
                  </span>

                  {/* Corner Crosshair Accents */}
                  <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-white" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 border-t-2 border-r-2 border-white" />
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b-2 border-l-2 border-white" />
                  <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-white" />
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Region Inspection Cards */}
      {regions.length > 0 && (
        <div className="space-y-2.5">
          <div className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
            <ShieldAlert size={16} className="text-amber-400" />
            Detected Anomaly Coordinates & Reasoning
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {regions.map((r, idx) => {
              const colors = severityColor(r.severity)
              const isSelected = activeRegion === idx
              return (
                <div
                  key={idx}
                  onMouseEnter={() => setActiveRegion(idx)}
                  onMouseLeave={() => setActiveRegion(null)}
                  className={`p-3.5 rounded-xl border transition-all duration-150 ${
                    isSelected
                      ? 'bg-ink-800 border-accent-400 shadow-md'
                      : 'bg-ink-900/80 border-ink-700/70 hover:border-ink-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-mono text-xs text-slate-300 font-semibold">
                      Region #{idx + 1} ({r.x}, {r.y}) [{r.width}×{r.height}]
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold tracking-wider ${colors.badgeBg}`}>
                      {r.severity}
                    </span>
                  </div>
                  <p className="text-sm text-slate-200 leading-snug">{r.reason}</p>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
