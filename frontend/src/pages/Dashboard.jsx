import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  FileSearch,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  ArrowRight,
  Sparkles,
  ScanText,
  SearchCode,
  UserCheck,
  GitCompareArrows,
  Clock,
  ChevronRight,
  Shield,
  Activity,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import RiskBadge from '../components/RiskBadge'
import { listScreenings } from '../services/api'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    listScreenings(10)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="pb-12">
      <PageHeader
        title="Command Dashboard"
        subtitle="Identity document fraud intelligence and multi-modal risk screening"
        badge="Defense Suite"
        action={
          <div className="flex items-center gap-3">
            <Link
              to="/screen?demo=1"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold text-slate-300 bg-ink-850 hover:bg-ink-800 border border-ink-700/80 transition-all hover:border-slate-600"
            >
              <Sparkles size={15} className="text-accent-400" />
              <span>Demo Scenarios</span>
            </Link>
            <Link
              to="/screen"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-accent-600 to-accent-500 hover:from-accent-500 hover:to-accent-400 text-white text-xs sm:text-sm font-bold px-4 py-2 rounded-xl shadow-[0_0_20px_rgba(56,189,248,0.25)] transition-all hover:shadow-[0_0_25px_rgba(56,189,248,0.4)] active:scale-95"
            >
              <FileSearch size={16} />
              <span>New Screening</span>
            </Link>
          </div>
        }
      />

      <div className="p-6 lg:p-8 space-y-8 max-w-7xl mx-auto">
        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-xs px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldAlert size={16} className="text-rose-400 shrink-0" />
              <span>Could not load screening history: {error}. Check if backend is active.</span>
            </div>
            <span className="text-[11px] font-mono text-rose-400/80">HTTP 8000</span>
          </div>
        )}

        {/* 4 Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Total Screenings"
            value={loading ? '—' : data?.total ?? 0}
            icon={FileSearch}
            accent="accent"
            hint="Documents submitted for analysis"
          />
          <StatCard
            label="Low Risk Cases"
            value={loading ? '—' : data?.low_risk_count ?? 0}
            icon={ShieldCheck}
            accent="low"
            hint="Format & security checks passed"
          />
          <StatCard
            label="Medium Risk Cases"
            value={loading ? '—' : data?.medium_risk_count ?? 0}
            icon={ShieldAlert}
            accent="medium"
            hint="Recommended for secondary review"
          />
          <StatCard
            label="High Risk Cases"
            value={loading ? '—' : data?.high_risk_count ?? 0}
            icon={ShieldX}
            accent="high"
            hint="Tampering or conflicts flagged"
          />
        </div>

        {/* Hackathon Demo Quick Launcher Banner */}
        <div className="rounded-2xl border border-sky-500/30 bg-gradient-to-r from-sky-950/40 via-ink-900/90 to-ink-900/90 p-6 shadow-panel relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-accent-500/5 rounded-full blur-3xl pointer-events-none" />
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
            <div className="flex items-start sm:items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-accent-500/15 border border-accent-400/30 flex items-center justify-center shrink-0 shadow-[0_0_15px_rgba(56,189,248,0.2)]">
                <Sparkles size={22} className="text-accent-400" />
              </div>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-lg font-extrabold text-white font-heading">
                    Smart India Hackathon Demo Sandbox
                  </h3>
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    Synthetic Datasets Ready
                  </span>
                </div>
                <p className="text-sm text-slate-200 mt-1 max-w-3xl leading-relaxed font-normal">
                  Evaluate VeriShield without uploading real identity documents. Instant pre-loaded scenarios test genuine credentials, forged DOB fields, biometric face mismatches, and cross-document inconsistencies.
                </p>
              </div>
            </div>
            <Link
              to="/screen?demo=1"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-slate-950 bg-accent-400 hover:bg-accent-300 transition-all shadow-[0_0_20px_rgba(56,189,248,0.35)] shrink-0 self-start md:self-center"
            >
              <span>Explore Demo Scenarios</span>
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>

        {/* 4 Pipeline Capabilities Overview */}
        <div className="space-y-3.5">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Activity size={16} className="text-accent-400" />
              VeriShield Multi-Stage Defense Pipeline
            </h2>
            <Link to="/system" className="text-sm font-semibold text-accent-400 hover:text-accent-300">
              System Architecture →
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              {
                icon: ScanText,
                title: 'OCR & Auto-Classification',
                desc: 'Aadhaar, PAN, Passport, DL & Voter ID document recognition with confidence metrics.',
              },
              {
                icon: SearchCode,
                title: 'Heuristic Tampering Detection',
                desc: 'Error Level Analysis (ELA), edge discontinuity inspection, and suspicious font checks.',
              },
              {
                icon: UserCheck,
                title: 'Biometric Face Verification',
                desc: '1:1 facial embedding similarity check between ID card photo and person portrait.',
              },
              {
                icon: GitCompareArrows,
                title: 'Cross-Document Consistency',
                desc: 'Multi-document matrix matching name, DOB, and relationship integrity across cards.',
              },
            ].map((p, idx) => (
              <div
                key={idx}
                className="p-4.5 rounded-xl border border-ink-700/70 bg-gradient-to-b from-ink-900/80 to-ink-950/80 transition-all duration-150 hover:border-ink-600 shadow-sm"
              >
                <div className="w-9 h-9 rounded-lg bg-ink-800 border border-ink-700/60 flex items-center justify-center text-accent-400 mb-3">
                  <p.icon size={18} />
                </div>
                <div className="text-sm font-bold text-slate-100">{p.title}</div>
                <div className="text-xs sm:text-[13px] text-slate-300 mt-1.5 leading-relaxed">{p.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Screenings Table */}
        <div className="rounded-xl border border-ink-700/80 bg-ink-900/90 shadow-panel overflow-hidden">
          <div className="px-6 py-4.5 border-b border-ink-700/70 flex items-center justify-between bg-ink-900">
            <div className="flex items-center gap-2.5">
              <Clock size={17} className="text-accent-400" />
              <h2 className="text-base font-bold text-slate-100 font-heading">Recent Screening Activity</h2>
            </div>
            <Link
              to="/history"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-accent-400 hover:text-accent-300 transition-colors"
            >
              <span>View full audit log</span>
              <ChevronRight size={15} />
            </Link>
          </div>

          {loading ? (
            <div className="p-12 text-center text-sm text-slate-400 flex flex-col items-center gap-2">
              <div className="w-6 h-6 border-2 border-accent-400 border-t-transparent rounded-full animate-spin" />
              <span>Loading screening records…</span>
            </div>
          ) : !data?.items?.length ? (
            <div className="p-12 text-center">
              <Shield size={36} className="mx-auto text-slate-600 mb-2.5 opacity-60" />
              <p className="text-base font-bold text-slate-200">No screenings recorded yet</p>
              <p className="text-sm text-slate-400 mt-1">Run an analysis with uploaded documents or a demo case.</p>
              <div className="mt-4 flex items-center justify-center gap-3">
                <Link
                  to="/screen?demo=1"
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-bold text-accent-400 bg-accent-500/10 border border-accent-500/30 rounded-xl hover:bg-accent-500/20"
                >
                  <Sparkles size={15} />
                  Run Demo Case
                </Link>
                <Link
                  to="/screen"
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-accent-600 rounded-xl hover:bg-accent-500"
                >
                  <FileSearch size={15} />
                  New Upload
                </Link>
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-slate-300 uppercase tracking-wider border-b border-ink-700/70 bg-ink-950/50">
                    <th className="px-6 py-3.5 font-bold">Screening ID</th>
                    <th className="px-6 py-3.5 font-bold">Document Type(s)</th>
                    <th className="px-6 py-3.5 font-bold">Date & Time</th>
                    <th className="px-6 py-3.5 font-bold">Risk Score</th>
                    <th className="px-6 py-3.5 font-bold">Security Verdict</th>
                    <th className="px-6 py-3.5 font-bold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-800/60">
                  {data.items.map((item) => (
                    <tr
                      key={item.screening_id}
                      className="hover:bg-ink-800/40 transition-colors group"
                    >
                      <td className="px-6 py-4 font-mono text-xs text-slate-300">
                        <span className="px-2.5 py-1 rounded-md bg-ink-800 border border-ink-700/60 font-semibold">
                          {item.screening_id.slice(0, 8)}…
                        </span>
                      </td>
                      <td className="px-6 py-4 font-semibold text-slate-100 capitalize">
                        {item.document_types.map((t) => t.replace('_', ' ')).join(', ') || '—'}
                      </td>
                      <td className="px-6 py-4 text-slate-300 font-mono text-xs">
                        {new Date(item.created_at).toLocaleString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="px-6 py-4 mono-num font-extrabold text-slate-100">
                        {item.risk_score != null ? `${item.risk_score.toFixed(1)} / 100` : '—'}
                      </td>
                      <td className="px-6 py-4">
                        {item.risk_level ? (
                          <RiskBadge level={item.risk_level} size="sm" />
                        ) : (
                          <span className="text-xs text-slate-400 capitalize">{item.status}</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link
                          to={`/results/${item.screening_id}`}
                          className="inline-flex items-center gap-1.5 text-sm font-bold text-accent-400 hover:text-accent-300 group-hover:translate-x-0.5 transition-all"
                        >
                          <span>Review</span>
                          <ArrowRight size={14} />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
