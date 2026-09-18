export default function PageHeader({ title, subtitle, badge, action }) {
  return (
    <header className="border-b border-ink-700/60 bg-ink-950/85 backdrop-blur-md px-6 lg:px-8 py-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 sticky top-0 z-20 shadow-sm">
      <div className="min-w-0">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl sm:text-3xl lg:text-[32px] font-extrabold tracking-tight text-white font-heading">
            {title}
          </h1>
          {badge && (
            <span className="inline-flex items-center px-3 py-0.5 rounded-full text-xs sm:text-sm font-semibold bg-accent-500/10 text-accent-400 border border-accent-500/30">
              {badge}
            </span>
          )}
        </div>
        {subtitle && <p className="text-sm sm:text-base text-slate-300 mt-1 max-w-3xl leading-relaxed">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0 flex items-center gap-2.5">{action}</div>}
    </header>
  )
}
