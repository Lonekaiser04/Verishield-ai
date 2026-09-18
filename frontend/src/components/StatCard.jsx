import clsx from 'clsx'

export default function StatCard({ label, value, icon: Icon, accent = 'default', hint }) {
  const config = {
    default: {
      text: 'text-slate-100',
      iconBg: 'bg-slate-800/80 text-slate-400 border-slate-700/60',
      borderTop: 'border-t-slate-500/40',
    },
    low: {
      text: 'text-emerald-400',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      borderTop: 'border-t-emerald-500/60',
    },
    medium: {
      text: 'text-amber-400',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      borderTop: 'border-t-amber-500/60',
    },
    high: {
      text: 'text-rose-400',
      iconBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      borderTop: 'border-t-rose-500/60',
    },
    accent: {
      text: 'text-sky-400',
      iconBg: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
      borderTop: 'border-t-sky-500/60',
    },
  }

  const theme = config[accent] || config.default

  return (
    <div className={clsx(
      'rounded-xl border border-ink-700/70 bg-gradient-to-b from-ink-900/90 to-ink-950/90 p-5 backdrop-blur-sm transition-all duration-200 hover:border-ink-600 hover:shadow-lg hover:-translate-y-0.5 relative overflow-hidden',
      'border-t-2',
      theme.borderTop
    )}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs sm:text-[13px] font-bold text-slate-300 uppercase tracking-wider">
          {label}
        </span>
        {Icon && (
          <div className={clsx('w-9 h-9 rounded-xl flex items-center justify-center border', theme.iconBg)}>
            <Icon size={17} />
          </div>
        )}
      </div>
      <div className={clsx('text-3xl sm:text-4xl font-black mono-num tracking-tight', theme.text)}>
        {value}
      </div>
      {hint && <div className="text-xs sm:text-sm text-slate-300 mt-2.5 font-medium">{hint}</div>}
    </div>
  )
}
