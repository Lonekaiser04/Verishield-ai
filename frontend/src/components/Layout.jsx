import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ScanLine, History, Info, Shield, Cpu, ExternalLink } from 'lucide-react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/screen', label: 'New Screening', icon: ScanLine },
  { to: '/history', label: 'Screening History', icon: History },
  { to: '/system', label: 'System Architecture', icon: Info },
]

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex bg-ink-950 text-slate-100 font-sans selection:bg-accent-500/30 selection:text-white">
      {/* Sidebar */}
      <aside className="w-72 shrink-0 border-r border-ink-700/80 bg-gradient-to-b from-ink-900 via-ink-900 to-ink-950 flex flex-col z-30 shadow-panel">
        {/* Brand Header */}
        <div className="h-20 flex items-center gap-3.5 px-6 border-b border-ink-700/70">
          <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br from-accent-500/20 to-accent-600/10 border border-accent-400/30 shadow-[0_0_15px_rgba(56,189,248,0.15)]">
            <Shield className="text-accent-400" size={24} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xl font-black tracking-tight text-white font-heading">
                VeriShield
              </span>
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30 tracking-wider">
                SIH
              </span>
            </div>
            <div className="text-xs sm:text-[13px] font-bold text-slate-400 tracking-wider uppercase mt-0.5 truncate">
              Identity Integrity AI
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-6 space-y-2.5">
          <div className="px-3 pb-2 text-xs font-extrabold tracking-wider text-slate-400 uppercase">
            Platform Modules
          </div>
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                clsx(
                  'group flex items-center gap-3.5 px-4 py-3.5 rounded-xl text-[15px] font-bold tracking-wide transition-all duration-150 relative',
                  isActive
                    ? 'bg-gradient-to-r from-accent-500/15 to-transparent text-accent-300 border-l-3 border-accent-400 shadow-sm'
                    : 'text-slate-300 hover:text-white hover:bg-ink-850/80 border-l-3 border-transparent'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    size={20}
                    className={clsx(
                      'shrink-0 transition-colors',
                      isActive ? 'text-accent-400' : 'text-slate-400 group-hover:text-slate-200'
                    )}
                  />
                  <span>{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* System Status Pill */}
        <div className="px-5 py-4 border-t border-ink-700/60 bg-ink-950/40">
          <div className="flex items-center justify-between text-sm font-bold text-slate-300 mb-2">
            <span className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400" />
              </span>
              Engine Active
            </span>
            <span className="text-xs font-mono font-semibold text-slate-400">v1.0.0-SIH</span>
          </div>
          <div className="flex items-center gap-2.5 p-2.5 rounded-lg bg-ink-850/80 border border-ink-700/60 text-xs sm:text-[13px] text-slate-300">
            <Cpu size={16} className="text-sky-400 shrink-0" />
            <span className="truncate font-semibold">Multi-Modal Defense Pipeline</span>
          </div>
        </div>

        {/* Disclaimer / Human Review Notice */}
        <div className="p-5 border-t border-ink-700/60 bg-ink-950/60">
          <div className="rounded-xl bg-ink-900/80 border border-ink-700/70 p-3.5">
            <p className="text-xs sm:text-[13px] leading-relaxed text-slate-300">
              <span className="text-white font-bold">AI Decision Support</span>: Intended for preliminary screening & anomaly detection. Final judgment remains with human verification officers.
            </p>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-security-grid">
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  )
}
