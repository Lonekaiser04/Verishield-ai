import { useEffect, useState } from 'react'
import { useParams, useLocation, Link } from 'react-router-dom'
import {
  ArrowLeft,
  FileText,
  ScanText,
  ShieldAlert,
  ShieldCheck,
  UserCheck,
  GitCompareArrows,
  Info,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Printer,
  Sparkles,
  Calendar,
  User,
  Hash,
  MapPin,
  Clock,
  Layers,
  Activity,
  SearchCode,
  Shield,
  ExternalLink,
  ChevronRight,
  FileSearch,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import RiskBadge from '../components/RiskBadge'
import RiskGauge from '../components/RiskGauge'
import ImagePreviewWithRegions from '../components/ImagePreviewWithRegions'
import { getScreening } from '../services/api'

function StatusIcon({ status }) {
  if (status === 'PASS') return <CheckCircle2 size={18} className="text-emerald-400" />
  if (status === 'WARN') return <AlertTriangle size={18} className="text-amber-400" />
  return <XCircle size={18} className="text-rose-400" />
}

function FieldItem({ label, value, icon: Icon }) {
  return (
    <div className="flex items-start justify-between py-2.5 border-b border-ink-800/70 last:border-0 gap-3">
      <span className="text-sm text-slate-300 flex items-center gap-2 shrink-0 font-medium">
        {Icon && <Icon size={14} className="text-slate-400" />}
        <span>{label}</span>
      </span>
      <span className="text-sm font-bold text-slate-100 text-right mono-num truncate max-w-[65%]">
        {value || <span className="text-slate-400 font-normal italic">Not detected</span>}
      </span>
    </div>
  )
}

function SectionCard({ icon: Icon, title, badge, action, children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-ink-700/80 bg-gradient-to-b from-ink-900/90 to-ink-950/90 p-6 shadow-panel ${className}`}>
      <div className="flex items-center justify-between border-b border-ink-800/80 pb-4 mb-5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-ink-800/90 border border-ink-700/60 flex items-center justify-center text-accent-400">
            <Icon size={18} />
          </div>
          <h3 className="text-base font-bold text-white font-heading">{title}</h3>
        </div>
        <div className="flex items-center gap-2.5">
          {badge}
          {action}
        </div>
      </div>
      {children}
    </div>
  )
}

export default function Results() {
  const { screeningId } = useParams()
  const location = useLocation()
  const [data, setData] = useState(location.state?.result || null)
  const uploadedFiles = location.state?.files || []
  const [loading, setLoading] = useState(!location.state?.result)
  const [error, setError] = useState(null)
  const [activeDocTab, setActiveDocTab] = useState(0)

  useEffect(() => {
    if (data) return
    const cached = sessionStorage.getItem('lastResult')
    if (cached) {
      try {
        const parsed = JSON.parse(cached)
        if (parsed.screening_id === screeningId) {
          setData(parsed)
          setLoading(false)
          return
        }
      } catch (e) {
        // ignore parse error
      }
    }
    getScreening(screeningId)
      .then(setData)
      .catch((err) => setError(err?.response?.data?.detail || err.message))
      .finally(() => setLoading(false))
  }, [screeningId, data])

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-8 text-center space-y-4">
        <div className="relative flex items-center justify-center w-16 h-16 rounded-2xl bg-accent-500/10 border border-accent-500/30">
          <div className="w-8 h-8 border-2 border-accent-400 border-t-transparent rounded-full animate-spin" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-slate-100 font-heading">Retrieving Screening Audit Record</h2>
          <p className="text-sm text-slate-400 mt-1 font-mono">{screeningId}</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="p-8 max-w-2xl mx-auto space-y-4">
        <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-sm p-4 flex items-start gap-3">
          <ShieldAlert size={20} className="text-rose-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-bold text-base">Screening Record Not Found</p>
            <p className="mt-1 text-slate-300 leading-relaxed">{error || 'Could not locate the requested screening session.'}</p>
          </div>
        </div>
        <Link
          to="/screen"
          className="inline-flex items-center gap-2 text-sm font-semibold text-accent-400 hover:text-accent-300 transition-colors"
        >
          <ArrowLeft size={16} />
          <span>Return to New Screening</span>
        </Link>
      </div>
    )
  }

  const {
    risk_assessment,
    documents = [],
    face_verification,
    cross_document,
    demo_mode,
    demo_scenario,
    created_at,
  } = data

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="pb-20">
      <PageHeader
        title="Screening Analysis Verdict"
        subtitle={`Session ID: ${data.screening_id}`}
        badge="Defense Intelligence"
        action={
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handlePrint}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-bold text-slate-300 bg-ink-850 hover:bg-ink-800 border border-ink-700/80 transition-all hover:border-slate-600 print:hidden"
            >
              <Printer size={15} />
              <span>Print Report</span>
            </button>
            <Link
              to="/screen"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold text-white bg-accent-600 hover:bg-accent-500 shadow-sm transition-all print:hidden"
            >
              <FileSearch size={15} />
              <span>New Screening</span>
            </Link>
          </div>
        }
      />

      <div className="p-6 lg:p-8 space-y-7 max-w-7xl mx-auto">
        {/* Synthetic Demo Notification */}
        {demo_mode && (
          <div className="rounded-xl border border-sky-500/30 bg-gradient-to-r from-sky-950/40 via-ink-900 to-ink-900 px-4 py-3.5 text-sm flex items-center justify-between gap-4">
            <div className="flex items-center gap-2.5 text-sky-300">
              <Sparkles size={17} className="text-sky-400 shrink-0" />
              <span>
                <strong className="font-bold text-white">Hackathon Synthetic Sandbox Result</strong>
                {demo_scenario ? ` · Scenario: ${demo_scenario}` : ''}
              </span>
            </div>
            <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-sky-500/15 text-sky-300 border border-sky-500/30 shrink-0">
              Test Pipeline
            </span>
          </div>
        )}

        {/* 1. Executive Verdict Hero Banner */}
        <div className="rounded-2xl border border-ink-700/80 bg-gradient-to-br from-ink-900 via-ink-900 to-ink-950 p-6 lg:p-8 shadow-panel relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-accent-500/5 rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col lg:flex-row items-center lg:items-start gap-8 relative z-10">
            {/* Left Gauge & Badge */}
            <div className="flex flex-col items-center gap-4 shrink-0">
              <RiskGauge score={risk_assessment.risk_score} level={risk_assessment.risk_level} size={180} />
              <RiskBadge level={risk_assessment.risk_level} size="lg" />
            </div>

            {/* Middle: AI Security Findings & Explanations */}
            <div className="flex-1 min-w-0 space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <Activity size={17} className="text-accent-400" />
                  <h2 className="text-xs sm:text-sm font-bold text-slate-400 uppercase tracking-wider">
                    Executive Screening Summary
                  </h2>
                </div>
                <h3 className="text-xl sm:text-2xl font-black text-white font-heading">
                  Automated Multi-Layer Risk Assessment
                </h3>
              </div>

              {/* Explanations list with severity badges */}
              <div className="space-y-2.5">
                {risk_assessment.explanations?.map((exp, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3.5 rounded-xl bg-ink-850/70 border border-ink-700/60 text-sm text-slate-100"
                  >
                    <span className="flex items-center justify-center w-6 h-6 rounded-md bg-accent-500/15 text-accent-400 text-xs font-mono font-bold shrink-0 mt-0.5">
                      {idx + 1}
                    </span>
                    <span className="leading-relaxed font-medium">{exp}</span>
                  </div>
                ))}
              </div>

              {/* Human-in-the-loop statutory disclaimer */}
              <div className="flex items-start gap-2.5 text-xs sm:text-[13px] text-slate-300 bg-ink-950/60 rounded-xl p-3.5 border border-ink-800/80">
                <Info size={16} className="text-accent-400 shrink-0 mt-0.5" />
                <span className="leading-relaxed">
                  VeriShield operates as an AI-assisted heuristic screening system. Scores and flags are decision-support indicators for human officers and do not query government databases or make final legal determinations.
                </span>
              </div>
            </div>
          </div>

          {/* Quick Telemetry Strip */}
          <div className="mt-8 pt-6 border-t border-ink-800/80 grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-3.5 rounded-xl bg-ink-850/50 border border-ink-700/50">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Documents Screened
              </span>
              <span className="text-lg sm:text-xl font-black text-white mono-num mt-1 block">
                {documents.length} {documents.length === 1 ? 'Credential' : 'Credentials'}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-ink-850/50 border border-ink-700/50">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Tampering Score
              </span>
              <span className="text-lg sm:text-xl font-black text-white mono-num mt-1 block">
                {Math.max(...documents.map((d) => d.tampering?.tampering_score || 0)).toFixed(0)} / 100
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-ink-850/50 border border-ink-700/50">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Face Biometrics
              </span>
              <span className="text-lg sm:text-xl font-black text-white mono-num mt-1 block truncate">
                {face_verification
                  ? `${face_verification.face_similarity.toFixed(0)}% (${face_verification.match_status})`
                  : 'Not Provided'}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-ink-850/50 border border-ink-700/50">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Cross-Doc Consistency
              </span>
              <span className="text-lg sm:text-xl font-black text-white mono-num mt-1 block">
                {cross_document?.consistency_level || 'Single Doc'}
              </span>
            </div>
          </div>
        </div>

        {/* 2. Risk Score Breakdown Bars */}
        <SectionCard
          icon={ShieldAlert}
          title="Weighted Risk Score Breakdown"
          badge={
            <span className="text-xs sm:text-sm font-mono text-slate-400 font-semibold">
              Weights Total: 100%
            </span>
          }
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {risk_assessment.breakdown.map((item) => {
              const pct = (item.points_awarded / (item.max_points || 1)) * 100
              return (
                <div
                  key={item.category}
                  className="p-4 rounded-xl bg-ink-850/60 border border-ink-700/60 space-y-2.5"
                >
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-bold text-slate-100">{item.category}</span>
                    <span className="mono-num font-bold text-slate-200">
                      {item.points_awarded.toFixed(1)} <span className="text-slate-400 font-normal">/ {item.max_points.toFixed(0)} pts</span>
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="h-2.5 rounded-full bg-ink-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        pct > 60
                          ? 'bg-gradient-to-r from-amber-500 to-rose-500'
                          : pct > 20
                          ? 'bg-gradient-to-r from-sky-400 to-amber-400'
                          : 'bg-emerald-400'
                      }`}
                      style={{ width: `${Math.min(100, Math.max(4, pct))}%` }}
                    />
                  </div>

                  {item.reason && (
                    <p className="text-xs sm:text-[13px] text-slate-300 leading-snug">
                      {item.reason}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        </SectionCard>

        {/* 3. Document Tabs (if multiple documents) */}
        {documents.length > 1 && (
          <div className="flex items-center gap-2.5 overflow-x-auto pb-1">
            <span className="text-xs sm:text-sm font-bold text-slate-300 uppercase tracking-wider mr-1">
              Inspecting Document:
            </span>
            {documents.map((doc, idx) => (
              <button
                key={doc.document_id}
                type="button"
                onClick={() => setActiveDocTab(idx)}
                className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                  activeDocTab === idx
                    ? 'bg-accent-600 text-white shadow-md'
                    : 'bg-ink-900 border border-ink-700/80 text-slate-400 hover:text-slate-200'
                }`}
              >
                Doc #{idx + 1}: {doc.document_type.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>
        )}

        {/* 4. Per-Document Forensic Examination */}
        {documents.map((doc, idx) => {
          // If multiple documents, only render active tab unless all tabs mode is preferred
          if (documents.length > 1 && activeDocTab !== idx) return null

          return (
            <SectionCard
              key={doc.document_id}
              icon={FileText}
              title={`Credential Analysis: ${doc.document_type.replace('_', ' ').toUpperCase()}${
                doc.original_filename ? ` — ${doc.original_filename}` : ''
              }`}
              badge={
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-sky-500/15 text-sky-300 border border-sky-500/30">
                    Confidence: {(doc.classification_confidence * 100).toFixed(0)}%
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                    OCR Quality: {doc.ocr_confidence.toFixed(0)}%
                  </span>
                </div>
              }
            >
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Column 1: Extracted Credential Fields */}
                <div className="p-4 rounded-xl bg-ink-850/70 border border-ink-700/70 space-y-3.5">
                  <div className="flex items-center justify-between pb-1 border-b border-ink-800/80">
                    <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <ScanText size={16} className="text-accent-400" />
                      Extracted OCR Fields
                    </h4>
                    <span className="text-xs text-slate-400 font-mono font-medium">
                      Raw Text Parsed
                    </span>
                  </div>

                  <div className="divide-y divide-ink-800/80">
                    <FieldItem label="Full Name" value={doc.extracted_fields.name} icon={User} />
                    <FieldItem label="Date of Birth" value={doc.extracted_fields.date_of_birth} icon={Calendar} />
                    <FieldItem label="Gender" value={doc.extracted_fields.gender} />
                    <FieldItem
                      label="Document Number"
                      value={doc.extracted_fields.document_number}
                      icon={Hash}
                    />
                    {doc.extracted_fields.parent_name && (
                      <FieldItem label="Father/Spouse" value={doc.extracted_fields.parent_name} />
                    )}
                    {doc.extracted_fields.address && (
                      <FieldItem label="Address" value={doc.extracted_fields.address} icon={MapPin} />
                    )}
                    {doc.extracted_fields.nationality && (
                      <FieldItem label="Nationality" value={doc.extracted_fields.nationality} />
                    )}
                    {doc.extracted_fields.expiry_date && (
                      <FieldItem label="Expiry Date" value={doc.extracted_fields.expiry_date} icon={Calendar} />
                    )}
                    {doc.extracted_fields.issue_date && (
                      <FieldItem label="Issue Date" value={doc.extracted_fields.issue_date} icon={Calendar} />
                    )}
                  </div>
                </div>

                {/* Column 2: Format & Algorithmic Validation */}
                <div className="p-4 rounded-xl bg-ink-850/70 border border-ink-700/70 space-y-3.5">
                  <div className="flex items-center justify-between pb-1 border-b border-ink-800/80">
                    <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <StatusIcon status={doc.validation.validation_status} />
                      Format Validation
                    </h4>
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                        doc.validation.validation_status === 'PASS'
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                          : doc.validation.validation_status === 'WARN'
                          ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                          : 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                      }`}
                    >
                      {doc.validation.validation_status}
                    </span>
                  </div>

                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between text-sm py-2 border-b border-ink-800/70">
                      <span className="text-slate-400 font-medium">Expiry Verification</span>
                      <span className="text-slate-100 font-semibold mono-num">
                        {doc.validation.expiry_status}
                      </span>
                    </div>

                    {doc.validation.issues?.length > 0 ? (
                      <div className="space-y-2 pt-1">
                        <span className="text-xs sm:text-[13px] font-bold text-rose-400 block">
                          Identified Syntax/Format Anomalies:
                        </span>
                        <ul className="space-y-1.5 text-sm text-slate-200">
                          {doc.validation.issues.map((issue, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-rose-400 font-bold">•</span>
                              <span>{issue}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ) : (
                      <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-300 flex items-center gap-2.5">
                        <CheckCircle2 size={17} className="text-emerald-400 shrink-0" />
                        <span>All document syntax and structure patterns validated cleanly.</span>
                      </div>
                    )}

                    <p className="text-xs text-slate-400 pt-2.5 border-t border-ink-800/70 leading-relaxed">
                      {doc.validation.disclaimer}
                    </p>
                  </div>
                </div>

                {/* Column 3: Heuristic Tampering Analysis */}
                <div className="p-4 rounded-xl bg-ink-850/70 border border-ink-700/70 space-y-3.5">
                  <div className="flex items-center justify-between pb-1 border-b border-ink-800/80">
                    <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                      <SearchCode size={16} className="text-accent-400" />
                      Tampering Heuristics
                    </h4>
                    <span
                      className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                        doc.tampering.tampering_level === 'LOW'
                          ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                          : doc.tampering.tampering_level === 'MEDIUM'
                          ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                          : 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                      }`}
                    >
                      {doc.tampering.tampering_level} RISK
                    </span>
                  </div>

                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between text-sm py-2 border-b border-ink-800/70">
                      <span className="text-slate-400 font-medium">Anomaly Score</span>
                      <span className="text-slate-100 font-bold mono-num">
                        {doc.tampering.tampering_score.toFixed(0)} / 100
                      </span>
                    </div>

                    {doc.tampering.detected_indicators?.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <span className="text-xs sm:text-[13px] font-bold text-amber-400 block">
                          Detection Indicators:
                        </span>
                        <ul className="space-y-1.5 text-sm text-slate-200">
                          {doc.tampering.detected_indicators.map((ind, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-amber-400 font-bold">•</span>
                              <span>{ind}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {doc.tampering.suspicious_regions?.length > 0 && (
                      <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-sm text-amber-300">
                        {doc.tampering.suspicious_regions.length} suspicious bounding region(s) flagged for human review.
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Document Image Overlay (if uploaded) */}
              {uploadedFiles[idx] && (
                <div className="mt-6 pt-6 border-t border-ink-800/80">
                  <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider mb-3.5 flex items-center gap-2">
                    <ShieldAlert size={16} className="text-accent-400" />
                    Forensic Document Image & Bounding Box Inspection
                  </h4>
                  <ImagePreviewWithRegions
                    file={uploadedFiles[idx]}
                    regions={doc.tampering?.suspicious_regions || []}
                  />
                </div>
              )}
            </SectionCard>
          )
        })}

        {/* 5. Biometric Face Verification Section */}
        {face_verification && (
          <SectionCard
            icon={UserCheck}
            title="Biometric Face Verification (1:1 Matching)"
            badge={
              <span
                className={`text-xs font-bold px-3 py-1 rounded-full border ${
                  face_verification.match_status === 'LIKELY MATCH'
                    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    : face_verification.match_status === 'MANUAL REVIEW REQUIRED'
                    ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                    : 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                }`}
              >
                {face_verification.match_status}
              </span>
            }
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
              <div className="p-6 rounded-xl bg-ink-850/70 border border-ink-700/60 text-center space-y-1.5">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Embedding Similarity
                </span>
                <span className="text-5xl font-black mono-num text-white block">
                  {face_verification.face_similarity.toFixed(1)}%
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Confidence: {(face_verification.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <div className="md:col-span-2 space-y-3.5">
                <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                  Biometric Analysis Notes
                </h4>
                {face_verification.notes?.length > 0 ? (
                  <ul className="space-y-2 text-sm text-slate-200">
                    {face_verification.notes.map((n, i) => (
                      <li key={i} className="flex items-start gap-2.5 p-3 rounded-xl bg-ink-850/60 border border-ink-750">
                        <ChevronRight size={16} className="text-accent-400 shrink-0 mt-0.5" />
                        <span className="leading-relaxed">{n}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-300">
                    Facial features from the document photo align with the portrait image with high structural correlation.
                  </p>
                )}
              </div>
            </div>
          </SectionCard>
        )}

        {/* 6. Cross-Document Consistency Matrix */}
        {cross_document && cross_document.consistency_level !== 'N/A' && (
          <SectionCard
            icon={GitCompareArrows}
            title="Cross-Document Identity Consistency Matrix"
            badge={
              <span
                className={`text-xs font-bold px-3 py-1 rounded-full border ${
                  cross_document.consistency_level === 'HIGH'
                    ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    : cross_document.consistency_level === 'MEDIUM'
                    ? 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                    : 'bg-rose-500/15 text-rose-400 border-rose-500/30'
                }`}
              >
                {cross_document.consistency_level} CONSISTENCY
              </span>
            }
          >
            <div className="space-y-4">
              {cross_document.comparisons?.length > 0 && (
                <div className="overflow-x-auto rounded-xl border border-ink-700/70">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs text-slate-400 uppercase tracking-wider border-b border-ink-700/70 bg-ink-850">
                        <th className="px-5 py-3 font-bold">Identity Field</th>
                        <th className="px-5 py-3 font-bold">Values Found Across Documents</th>
                        <th className="px-5 py-3 font-bold text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-ink-800/60 bg-ink-900/60">
                      {cross_document.comparisons.map((c, i) => (
                        <tr key={i} className="hover:bg-ink-800/40 transition-colors">
                          <td className="px-5 py-3.5 font-bold text-slate-100 capitalize">
                            {c.field_name.replace('_', ' ')}
                          </td>
                          <td className="px-5 py-3.5 font-mono text-slate-200">
                            {Object.entries(c.values || {})
                              .map(([k, v]) => `${k.toUpperCase()}: "${v || '—'}"`)
                              .join('  ·  ')}
                          </td>
                          <td className="px-5 py-3.5 text-center">
                            {c.consistent ? (
                              <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/30">
                                <CheckCircle2 size={13} />
                                Match
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 text-xs font-bold text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-full border border-rose-500/30">
                                <XCircle size={13} />
                                Conflict
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {cross_document.findings?.length > 0 && (
                <div className="space-y-2 pt-2">
                  <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
                    Consistency Analysis Findings:
                  </h4>
                  <ul className="space-y-1.5 text-sm text-slate-200">
                    {cross_document.findings.map((f, i) => (
                      <li key={i} className="flex items-start gap-2.5">
                        <span className="text-accent-400 font-bold">•</span>
                        <span className="leading-relaxed">{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </SectionCard>
        )}
      </div>
    </div>
  )
}
