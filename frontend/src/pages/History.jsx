import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowRight,
  History as HistoryIcon,
  Search,
  Filter,
  ShieldAlert,
  ShieldCheck,
  ShieldX,
  FileSearch,
  Clock,
  Sparkles,
  Layers,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import RiskBadge from '../components/RiskBadge'
import { listScreenings } from '../services/api'

export default function History() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [riskFilter, setRiskFilter] = useState('ALL')

  useEffect(() => {
    listScreenings(100)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const filteredItems = useMemo(() => {
    if (!data?.items) return []
    return data.items.filter((item) => {
      // Risk filter
      if (riskFilter !== 'ALL' && item.risk_level !== riskFilter) {
        return false
      }
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const idMatch = item.screening_id.toLowerCase().includes(q)
        const typeMatch = item.document_types?.some((t) => t.toLowerCase().includes(q))
        return idMatch || typeMatch
      }
      return true
    })
  }, [data, riskFilter, searchQuery])

  return (
    <div className="pb-16">
      <PageHeader
        title="Screening Audit Log"
        subtitle="Complete record of all identity verification requests and forensic verdicts"
        badge="Audit Trail"
        action={
          <Link
            to="/screen"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold text-white bg-accent-600 hover:bg-accent-500 shadow-sm transition-all"
          >
            <FileSearch size={15} />
            <span>New Screening</span>
          </Link>
        }
      />

      <div className="p-6 lg:p-8 space-y-7 max-w-7xl mx-auto">
        {error && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 text-sm px-4 py-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <ShieldAlert size={18} className="text-rose-400 shrink-0" />
              <span>Could not load history log: {error}</span>
            </div>
            <span className="text-xs font-mono text-rose-400/80 font-bold">HTTP Error</span>
          </div>
        )}

        {/* Top Summary Metrics Chips */}
        {data && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-ink-700/80 bg-ink-900/90 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Total Logged
                </span>
                <span className="text-2xl sm:text-3xl font-black text-white mono-num mt-1 block">
                  {data.total || 0}
                </span>
              </div>
              <div className="w-9 h-9 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-300">
                <Layers size={18} />
              </div>
            </div>

            <div className="p-4 rounded-xl border border-ink-700/80 bg-ink-900/90 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Low Risk
                </span>
                <span className="text-2xl sm:text-3xl font-black text-emerald-400 mono-num mt-1 block">
                  {data.low_risk_count || 0}
                </span>
              </div>
              <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <ShieldCheck size={18} />
              </div>
            </div>

            <div className="p-4 rounded-xl border border-ink-700/80 bg-ink-900/90 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  Medium Risk
                </span>
                <span className="text-2xl sm:text-3xl font-black text-amber-400 mono-num mt-1 block">
                  {data.medium_risk_count || 0}
                </span>
              </div>
              <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <ShieldAlert size={18} />
              </div>
            </div>

            <div className="p-4 rounded-xl border border-ink-700/80 bg-ink-900/90 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                  High Risk
                </span>
                <span className="text-2xl sm:text-3xl font-black text-rose-400 mono-num mt-1 block">
                  {data.high_risk_count || 0}
                </span>
              </div>
              <div className="w-9 h-9 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                <ShieldX size={18} />
              </div>
            </div>
          </div>
        )}

        {/* Filters and Search Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-ink-900/80 p-4 rounded-xl border border-ink-700/80">
          {/* Search box */}
          <div className="relative flex-1 max-w-md">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by ID or document type…"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-ink-800 border border-ink-700 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-accent-400"
            />
          </div>

          {/* Risk filter buttons */}
          <div className="flex items-center gap-2 overflow-x-auto">
            <span className="text-xs uppercase font-bold text-slate-400 mr-1 flex items-center gap-1.5">
              <Filter size={13} /> Filter:
            </span>
            {['ALL', 'LOW RISK', 'MEDIUM RISK', 'HIGH RISK'].map((lvl) => (
              <button
                key={lvl}
                type="button"
                onClick={() => setRiskFilter(lvl)}
                className={`px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-bold transition-all whitespace-nowrap ${
                  riskFilter === lvl
                    ? 'bg-accent-600 text-white shadow-sm'
                    : 'bg-ink-800 text-slate-300 hover:text-white border border-ink-700/60'
                }`}
              >
                {lvl === 'ALL' ? 'All Records' : lvl}
              </button>
            ))}
          </div>
        </div>

        {/* Screenings Table */}
        <div className="rounded-2xl border border-ink-700/80 bg-ink-900/90 shadow-panel overflow-hidden">
          {loading ? (
            <div className="p-16 text-center text-sm text-slate-400 flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-2 border-accent-400 border-t-transparent rounded-full animate-spin" />
              <span>Loading screening history records…</span>
            </div>
          ) : !filteredItems.length ? (
            <div className="p-16 text-center">
              <HistoryIcon className="mx-auto mb-3.5 text-slate-600 opacity-60" size={40} />
              <p className="text-base font-bold text-slate-200">No matching screenings found</p>
              <p className="text-sm text-slate-400 mt-1.5">
                {searchQuery || riskFilter !== 'ALL'
                  ? 'Try clearing the search query or adjusting the risk filter.'
                  : 'Start by screening your first document or running a demo scenario.'}
              </p>
              {(searchQuery || riskFilter !== 'ALL') && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery('')
                    setRiskFilter('ALL')
                  }}
                  className="mt-3.5 text-sm font-bold text-accent-400 hover:text-accent-300"
                >
                  Reset filters
                </button>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-slate-400 uppercase tracking-wider border-b border-ink-700/70 bg-ink-950/50">
                    <th className="px-5 py-4 font-bold">Screening ID</th>
                    <th className="px-5 py-4 font-bold">Document Type(s)</th>
                    <th className="px-5 py-4 font-bold">Timestamp</th>
                    <th className="px-5 py-4 font-bold">Status</th>
                    <th className="px-5 py-4 font-bold">Risk Score</th>
                    <th className="px-5 py-4 font-bold">Security Level</th>
                    <th className="px-5 py-4 font-bold text-right">Audit Record</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-800/60">
                  {filteredItems.map((item) => (
                    <tr
                      key={item.screening_id}
                      className="hover:bg-ink-800/40 transition-colors group"
                    >
                      <td className="px-5 py-4 font-mono text-xs font-semibold text-slate-300">
                        <span className="px-2.5 py-1 rounded-md bg-ink-800 border border-ink-700/60">
                          {item.screening_id.slice(0, 8)}…
                        </span>
                      </td>
                      <td className="px-5 py-4 font-bold text-slate-100 capitalize">
                        {item.document_types.map((t) => t.replace('_', ' ')).join(', ') || '—'}
                      </td>
                      <td className="px-5 py-4 text-slate-400 font-mono text-xs font-medium">
                        {new Date(item.created_at).toLocaleString(undefined, {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-md bg-ink-800 text-slate-300 border border-ink-700 capitalize">
                          {item.status}
                        </span>
                      </td>
                      <td className="px-5 py-4 mono-num font-bold text-slate-100">
                        {item.risk_score != null ? `${item.risk_score.toFixed(1)} / 100` : '—'}
                      </td>
                      <td className="px-5 py-4">
                        {item.risk_level ? (
                          <RiskBadge level={item.risk_level} size="sm" />
                        ) : (
                          <span className="text-xs text-slate-400">—</span>
                        )}
                      </td>
                      <td className="px-5 py-4 text-right">
                        {item.status === 'completed' && (
                          <Link
                            to={`/results/${item.screening_id}`}
                            className="inline-flex items-center gap-1.5 text-sm font-bold text-accent-400 hover:text-accent-300 group-hover:translate-x-0.5 transition-all"
                          >
                            <span>Inspect</span>
                            <ArrowRight size={14} />
                          </Link>
                        )}
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
