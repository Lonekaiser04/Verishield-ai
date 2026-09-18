import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Loader2,
  ScanLine,
  Sparkles,
  User,
  FileWarning,
  ShieldAlert,
  FileCheck,
  Cpu,
  Layers,
  CheckCircle2,
  ArrowRight,
  Fingerprint,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import DropZone from '../components/DropZone'
import RiskBadge from '../components/RiskBadge'
import { screenDocuments, listDemoScenarios, runDemoScenario } from '../services/api'

const DOC_TYPE_OPTIONS = [
  { value: '', label: 'Auto-detect Document Type' },
  { value: 'aadhaar', label: 'Aadhaar Card' },
  { value: 'pan', label: 'PAN Card' },
  { value: 'passport', label: 'Passport' },
  { value: 'driving_licence', label: 'Driving Licence' },
  { value: 'voter_id', label: 'Voter ID' },
]

export default function NewScreening() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [mode, setMode] = useState(searchParams.get('demo') ? 'demo' : 'upload')

  const [documents, setDocuments] = useState([])
  const [personPhoto, setPersonPhoto] = useState([])
  const [manualType, setManualType] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [scenarios, setScenarios] = useState([])
  const [demoLoading, setDemoLoading] = useState(null)

  useEffect(() => {
    if (mode === 'demo') {
      listDemoScenarios().then((d) => setScenarios(d.scenarios || [])).catch(() => {})
    }
  }, [mode])

  const handleAnalyze = async () => {
    if (!documents.length) {
      setError('Please upload at least one document to screen.')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const result = await screenDocuments({
        documents,
        documentTypes: manualType ? [manualType] : [],
        personPhoto: personPhoto[0] || null,
      })
      sessionStorage.setItem('lastResult', JSON.stringify(result))
      navigate(`/results/${result.screening_id}`, { state: { result, files: documents } })
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Screening pipeline execution failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleDemoRun = async (scenarioId) => {
    setDemoLoading(scenarioId)
    setError(null)
    try {
      const result = await runDemoScenario(scenarioId)
      sessionStorage.setItem('lastResult', JSON.stringify(result))
      navigate(`/results/${result.screening_id}`, { state: { result } })
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Demo scenario execution failed.')
    } finally {
      setDemoLoading(null)
    }
  }

  return (
    <div className="pb-16">
      <PageHeader
        title="Document Screening"
        subtitle="Submit credentials for automated fraud inspection, OCR parsing, and cross-verification"
        badge="Multi-Modal Engine"
      />

      <div className="p-6 lg:p-8 max-w-4xl mx-auto space-y-6">
        {/* Mode Selector Segmented Pill */}
        <div className="flex p-1 rounded-2xl bg-ink-900 border border-ink-700/80 shadow-sm w-full sm:w-fit">
          <button
            type="button"
            onClick={() => setMode('upload')}
            className={`flex-1 sm:flex-none flex items-center justify-center gap-2.5 px-6 py-3 rounded-xl text-sm font-bold transition-all duration-150 ${
              mode === 'upload'
                ? 'bg-gradient-to-r from-accent-600 to-accent-500 text-white shadow-md'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <ScanLine size={16} />
            <span>Upload Documents</span>
          </button>
          <button
            type="button"
            onClick={() => setMode('demo')}
            className={`flex-1 sm:flex-none flex items-center justify-center gap-2.5 px-6 py-3 rounded-xl text-sm font-bold transition-all duration-150 ${
              mode === 'demo'
                ? 'bg-gradient-to-r from-accent-600 to-accent-500 text-white shadow-md'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            <Sparkles size={16} className={mode === 'demo' ? 'text-white' : 'text-accent-400'} />
            <span>Hackathon Demo Sandbox</span>
          </button>
        </div>

        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-sm px-4.5 py-4 flex items-start gap-3 shadow-sm">
            <FileWarning size={18} className="text-rose-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold text-base">Screening Submission Error</p>
              <p className="text-sm text-rose-300/95 leading-relaxed">{error}</p>
            </div>
          </div>
        )}

        {mode === 'upload' ? (
          <div className="space-y-6">
            {/* Step 1: Document Upload */}
            <div className="rounded-2xl border border-ink-700/80 bg-ink-900/90 p-6 sm:p-7 shadow-panel space-y-4.5">
              <div className="flex items-center justify-between border-b border-ink-800/80 pb-3.5">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-sky-500/15 border border-sky-500/30 text-sky-400 flex items-center justify-center text-sm font-black">
                    1
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white font-heading">
                      Identity Document(s)
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-300 mt-0.5">
                      Upload one document, or multiple documents for cross-document identity verification.
                    </p>
                  </div>
                </div>
                <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-md bg-ink-800 text-slate-300 border border-ink-700">
                  Required
                </span>
              </div>

              <DropZone
                files={documents}
                onFilesChange={setDocuments}
                multiple
                label="Drop identity documents here, or browse files"
                hint="Supports PNG, JPG, JPEG, and PDF documents"
                showSupportedBadges
              />

              {/* Single document manual override option */}
              {documents.length === 1 && (
                <div className="pt-3.5 border-t border-ink-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-ink-850/50 p-4 rounded-xl border border-ink-700/50">
                  <div>
                    <div className="text-sm font-bold text-slate-100">Document Type Classification</div>
                    <div className="text-xs text-slate-300 mt-0.5">Default: Automated multi-modal classifier</div>
                  </div>
                  <select
                    value={manualType}
                    onChange={(e) => setManualType(e.target.value)}
                    className="bg-ink-800 border border-ink-700 rounded-xl px-4 py-2.5 text-sm font-semibold text-slate-200 focus:outline-none focus:border-accent-400 focus:ring-1 focus:ring-accent-400/50"
                  >
                    {DOC_TYPE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Step 2: Biometric Verification Photo (Optional) */}
            <div className="rounded-2xl border border-ink-700/80 bg-ink-900/90 p-6 sm:p-7 shadow-panel space-y-4.5">
              <div className="flex items-center justify-between border-b border-ink-800/80 pb-3.5">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-sky-500/15 border border-sky-500/30 text-sky-400 flex items-center justify-center text-sm font-black">
                    2
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
                      <span>Biometric Face Verification</span>
                      <span className="text-xs font-normal text-slate-400">(Optional)</span>
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-300 mt-0.5">
                      Upload a portrait photograph to match against the facial image extracted from the ID card.
                    </p>
                  </div>
                </div>
                <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-md bg-ink-850 text-slate-300 border border-ink-750">
                  Optional
                </span>
              </div>

              <DropZone
                files={personPhoto}
                onFilesChange={setPersonPhoto}
                multiple={false}
                label="Drop subject portrait photo here, or browse"
                hint="Clear front-facing image (JPG, PNG) for 1:1 facial embedding matching"
                showSupportedBadges={false}
              />
            </div>

            {/* Action Bar */}
            <div className="pt-2">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={loading || !documents.length}
                className="w-full inline-flex items-center justify-center gap-3 bg-gradient-to-r from-accent-600 via-accent-500 to-sky-400 hover:from-accent-500 hover:to-sky-300 disabled:from-ink-800 disabled:to-ink-800 disabled:text-slate-400 text-white font-black py-4 px-6 rounded-xl shadow-[0_0_25px_rgba(56,189,248,0.25)] hover:shadow-[0_0_35px_rgba(56,189,248,0.4)] disabled:shadow-none transition-all duration-200 active:scale-[0.99] text-base tracking-wide"
              >
                {loading ? (
                  <>
                    <Loader2 size={20} className="animate-spin text-white" />
                    <span>Running Multi-Modal Screening Pipeline…</span>
                  </>
                ) : (
                  <>
                    <ScanLine size={20} />
                    <span>Run VeriShield Security Screening</span>
                  </>
                )}
              </button>

              <p className="text-center text-xs sm:text-[13px] text-slate-300 mt-3.5 flex items-center justify-center gap-2">
                <Cpu size={16} className="text-sky-400" />
                <span>Pipeline conducts OCR, format validation, tampering analysis, and risk scoring in safe isolation.</span>
              </p>
            </div>
          </div>
        ) : (
          /* Demo Scenarios View */
          <div className="space-y-4">
            <div className="rounded-xl border border-sky-500/30 bg-gradient-to-r from-sky-950/40 via-ink-900 to-ink-900 p-6 shadow-panel">
              <div className="flex items-center gap-2.5 mb-2">
                <Sparkles size={18} className="text-accent-400" />
                <h3 className="text-base font-bold text-white font-heading">
                  Smart India Hackathon Pre-loaded Test Cases
                </h3>
              </div>
              <p className="text-sm text-slate-200 leading-relaxed">
                These scenarios execute bundled synthetic test identities through the identical production pipeline (OCR, heuristic tampering, biometrics, and cross-doc logic).
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {scenarios.map((s) => (
                <div
                  key={s.id}
                  className="rounded-xl border border-ink-700/80 bg-gradient-to-b from-ink-900/90 to-ink-950/90 p-5 sm:p-6 shadow-sm hover:border-ink-600 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-5"
                >
                  <div className="space-y-2 max-w-xl">
                    <div className="flex items-center gap-2.5">
                      <h4 className="text-base font-bold text-white font-heading">{s.title}</h4>
                      <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded-md bg-ink-800 text-slate-200 border border-ink-700/80">
                        {s.documents?.length || 1} doc{s.documents?.length > 1 ? 's' : ''}
                      </span>
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed">{s.description}</p>
                    <div className="flex items-center gap-2 pt-1">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Expected Verdict:
                      </span>
                      <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                        s.expected_risk.includes('LOW')
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : s.expected_risk.includes('MEDIUM')
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                      }`}>
                        {s.expected_risk}
                      </span>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleDemoRun(s.id)}
                    disabled={demoLoading !== null}
                    className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white bg-accent-600 hover:bg-accent-500 disabled:opacity-50 transition-all shadow-sm shrink-0 self-start sm:self-center"
                  >
                    {demoLoading === s.id ? (
                      <>
                        <Loader2 size={16} className="animate-spin" />
                        <span>Simulating…</span>
                      </>
                    ) : (
                      <>
                        <ScanLine size={16} />
                        <span>Run Scenario</span>
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
