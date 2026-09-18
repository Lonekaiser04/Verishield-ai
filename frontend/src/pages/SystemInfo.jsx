import { useEffect, useState } from 'react'
import {
  Info,
  ShieldCheck,
  AlertTriangle,
  Layers,
  Lock,
  Cpu,
  ScanText,
  SearchCode,
  UserCheck,
  GitCompareArrows,
  ArrowRight,
  CheckCircle2,
  FileText,
  ShieldAlert,
  Server,
  Database,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import { getSystemInfo } from '../services/api'

export default function SystemInfo() {
  const [info, setInfo] = useState(null)

  useEffect(() => {
    getSystemInfo().then(setInfo).catch(() => {})
  }, [])

  const pipelineStages = [
    { step: '01', title: 'Ingestion & Preprocessing', icon: FileText, desc: 'Image normalization, EXIF sanitization & PDF rasterization' },
    { step: '02', title: 'Document Classifier', icon: Layers, desc: 'Heuristic & visual pattern identification for Indian ID types' },
    { step: '03', title: 'OCR & Field Extraction', icon: ScanText, desc: 'Multi-lingual text extraction with confidence scoring per field' },
    { step: '04', title: 'Format & MRZ Validator', icon: ShieldCheck, desc: 'Algorithmic pattern checking, expiry verification & checksums' },
    { step: '05', title: 'Tampering Engine', icon: SearchCode, desc: 'Error Level Analysis (ELA), edge discontinuity & font checks' },
    { step: '06', title: 'Face Biometrics', icon: UserCheck, desc: '1:1 facial embedding distance & similarity comparison' },
    { step: '07', title: 'Cross-Document Matrix', icon: GitCompareArrows, desc: 'Multi-document consistency check across conflicting fields' },
    { step: '08', title: 'Risk Scoring Engine', icon: Cpu, desc: 'Weighted multi-factor aggregation & transparent explanations' },
  ]

  return (
    <div className="pb-20">
      <PageHeader
        title="System Architecture & Governance"
        subtitle="Technical overview of the multi-modal AI pipeline, heuristic boundaries, and compliance framework"
        badge="Defense Architecture"
      />

      <div className="p-6 lg:p-8 max-w-6xl mx-auto space-y-8">
        {/* Architecture Pipeline Flowchart */}
        <div className="rounded-2xl border border-ink-700/80 bg-gradient-to-b from-ink-900/90 to-ink-950/90 p-6 sm:p-8 shadow-panel space-y-6">
          <div className="flex items-center justify-between border-b border-ink-800/80 pb-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-sky-500/15 border border-sky-500/30 text-sky-400 flex items-center justify-center">
                <Cpu size={20} />
              </div>
              <div>
                <h3 className="text-lg font-extrabold text-white font-heading">
                  VeriShield 8-Stage Inspection Pipeline
                </h3>
                <p className="text-sm text-slate-300 mt-0.5">
                  Sequential processing flow executed on submitted identity documents
                </p>
              </div>
            </div>
            <span className="text-xs font-mono font-bold px-3 py-1.5 rounded-lg bg-ink-800 text-sky-300 border border-ink-700">
              Modular AI Architecture
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {pipelineStages.map((st, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-ink-850/60 border border-ink-700/60 hover:border-accent-500/50 transition-all duration-150 relative group"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-mono font-bold text-accent-400 bg-accent-500/10 px-2 py-0.5 rounded border border-accent-500/20">
                    STAGE {st.step}
                  </span>
                  <st.icon size={17} className="text-slate-400 group-hover:text-accent-400 transition-colors" />
                </div>
                <h4 className="text-sm font-bold text-slate-100 group-hover:text-white transition-colors">
                  {st.title}
                </h4>
                <p className="text-xs sm:text-[13px] text-slate-300 mt-1.5 leading-snug">
                  {st.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Capabilities vs Boundaries Split */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* What this system is */}
          <div className="rounded-2xl border border-emerald-500/30 bg-gradient-to-b from-emerald-950/20 to-ink-950 p-6 sm:p-7 shadow-sm space-y-4">
            <div className="flex items-center gap-3 text-emerald-400">
              <CheckCircle2 size={20} />
              <h3 className="text-base font-bold text-white font-heading">Platform Capabilities & Purpose</h3>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed">
              {info?.app_name || 'VeriShield'} is an advanced <strong className="text-white font-bold">preliminary screening and decision-support tool</strong> engineered for high-throughput identity document verification.
            </p>
            <ul className="space-y-2.5 text-sm text-slate-200 pt-3 border-t border-emerald-500/20">
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Automatic classification of major Indian government credential formats.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>High-precision OCR parsing with confidence metrics for human auditing.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Multi-document cross-referencing to catch conflicting identity records.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-emerald-400 font-bold">•</span>
                <span>Explainable AI output with line-by-line evidence justification.</span>
              </li>
            </ul>
          </div>

          {/* What this system is NOT */}
          <div className="rounded-2xl border border-rose-500/30 bg-gradient-to-b from-rose-950/20 to-ink-950 p-6 sm:p-7 shadow-sm space-y-4">
            <div className="flex items-center gap-3 text-rose-400">
              <AlertTriangle size={20} />
              <h3 className="text-base font-bold text-white font-heading">Operational Boundaries & Safeguards</h3>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed">
              VeriShield is designed with strict human-in-the-loop safeguards to protect constitutional due process and prevent automated bias.
            </p>
            <ul className="space-y-2.5 text-sm text-slate-200 pt-3 border-t border-rose-500/20">
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span><strong className="text-white">Does NOT query live government databases</strong> (e.g. UIDAI, NSDL, Parivahan, or ECI).</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>Outputs are probabilistic risk indicators, not definitive legal rulings of fraud.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>Never replaces designated verification officers in statutory processes.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-400 font-bold">•</span>
                <span>All medium and high risk findings mandate manual inspection.</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Supported Document Types */}
        <div className="rounded-2xl border border-ink-700/80 bg-ink-900/90 p-6 sm:p-7 shadow-panel space-y-5">
          <div className="flex items-center gap-3 border-b border-ink-800/80 pb-4">
            <Layers size={20} className="text-accent-400" />
            <h3 className="text-base font-bold text-white font-heading">Supported Government Credentials</h3>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
            {[
              { type: 'Aadhaar Card', code: 'aadhaar', fields: '12-digit UID, Name, DOB, Gender, Address' },
              { type: 'PAN Card', code: 'pan', fields: '10-char alphanumeric, Name, Father, DOB' },
              { type: 'Passport', code: 'passport', fields: 'MRZ Type-3, Passport No, Expiry, Nationality' },
              { type: 'Driving Licence', code: 'driving_licence', fields: 'State DL No, Valid Till, DOB, Name' },
              { type: 'Voter ID (EPIC)', code: 'voter_id', fields: 'EPIC alphanumeric, Name, Relative, Age' },
            ].map((doc) => (
              <div
                key={doc.code}
                className="p-4 rounded-xl bg-ink-850/60 border border-ink-700/60 flex flex-col justify-between"
              >
                <div>
                  <span className="text-sm font-bold text-white block">{doc.type}</span>
                  <span className="text-xs font-mono font-semibold text-accent-400 mt-0.5 block">{doc.code}</span>
                </div>
                <p className="text-xs sm:text-[13px] text-slate-300 mt-2.5 leading-relaxed">{doc.fields}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Scoring Bands & Escalation Rules */}
        <div className="rounded-2xl border border-ink-700/80 bg-ink-900/90 p-6 sm:p-7 shadow-panel space-y-5">
          <div className="flex items-center gap-3 border-b border-ink-800/80 pb-4">
            <ShieldCheck size={20} className="text-accent-400" />
            <h3 className="text-base font-bold text-white font-heading">Risk Scoring Bands & Escalation Matrix</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
            <div className="rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-5">
              <span className="text-xs sm:text-sm font-mono font-semibold text-slate-300">Score Range: 0 – 30</span>
              <div className="text-lg sm:text-xl font-black text-emerald-400 mt-1">LOW RISK</div>
              <p className="text-xs sm:text-sm text-slate-200 mt-2 leading-relaxed">
                Document exhibits standard typography, valid checksum patterns, and no tampering indicators.
              </p>
            </div>
            <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 p-5">
              <span className="text-xs sm:text-sm font-mono font-semibold text-slate-300">Score Range: 31 – 60</span>
              <div className="text-lg sm:text-xl font-black text-amber-400 mt-1">MEDIUM RISK</div>
              <p className="text-xs sm:text-sm text-slate-200 mt-2 leading-relaxed">
                Minor syntax ambiguities, low OCR confidence, or moderate compression anomalies detected.
              </p>
            </div>
            <div className="rounded-xl bg-rose-500/10 border border-rose-500/30 p-5">
              <span className="text-xs sm:text-sm font-mono font-semibold text-slate-300">Score Range: 61 – 100</span>
              <div className="text-lg sm:text-xl font-black text-rose-400 mt-1">HIGH RISK</div>
              <p className="text-xs sm:text-sm text-slate-200 mt-2 leading-relaxed">
                Significant tampering detected, verified facial mismatch, or direct cross-document identity conflicts.
              </p>
            </div>
          </div>
          <div className="p-4 rounded-xl bg-ink-850/60 border border-ink-700/60 text-sm text-slate-200 leading-relaxed">
            <strong className="text-accent-300 font-bold">Automatic Escalation Rule:</strong> Severe individual security findings (such as confirmed biometric face mismatch or irreconcilable DOB discrepancy between companion documents) automatically escalate the case to <span className="text-rose-400 font-bold">HIGH RISK</span> regardless of individual category weights.
          </div>
        </div>

        {/* Privacy & Compliance Section */}
        <div className="rounded-2xl border border-ink-700/80 bg-ink-900/90 p-6 sm:p-7 shadow-panel space-y-5">
          <div className="flex items-center gap-3 border-b border-ink-800/80 pb-4">
            <Lock size={20} className="text-accent-400" />
            <h3 className="text-base font-bold text-white font-heading">Privacy Architecture & Data Handling</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm text-slate-300">
            <div className="p-4 rounded-xl bg-ink-850/50 border border-ink-750 space-y-2">
              <div className="font-bold text-white text-base">Synthetic Sandbox</div>
              <p className="text-slate-300 leading-relaxed text-xs sm:text-sm">
                Demonstrations and hackathon evaluations utilize synthetic benchmark documents without personal data exposure.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-ink-850/50 border border-ink-750 space-y-2">
              <div className="font-bold text-white text-base">Ephemeral Processing</div>
              <p className="text-slate-300 leading-relaxed text-xs sm:text-sm">
                Uploaded document binaries are purged automatically upon screening completion when AUTO_DELETE_UPLOADS is active.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-ink-850/50 border border-ink-750 space-y-2">
              <div className="font-bold text-white text-base">Derived Audit Logs</div>
              <p className="text-slate-300 leading-relaxed text-xs sm:text-sm">
                Only derived forensic risk scores, parsed fields, and explanatory evidence are retained in the audit database.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
