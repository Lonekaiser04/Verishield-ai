import clsx from 'clsx'
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react'

const CONFIG = {
  'LOW RISK': {
    label: 'LOW RISK',
    icon: ShieldCheck,
    text: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    dot: 'bg-emerald-400',
    dotPulse: 'bg-emerald-400/40',
  },
  'MEDIUM RISK': {
    label: 'MEDIUM RISK',
    icon: ShieldAlert,
    text: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    dot: 'bg-amber-400',
    dotPulse: 'bg-amber-400/40',
  },
  'HIGH RISK': {
    label: 'HIGH RISK',
    icon: ShieldX,
    text: 'text-rose-400',
    bg: 'bg-rose-500/10',
    border: 'border-rose-500/30',
    dot: 'bg-rose-400',
    dotPulse: 'bg-rose-400/40',
  },
}

export default function RiskBadge({ level, size = 'md', showIcon = true, showDot = true }) {
  const cfg = CONFIG[level] || CONFIG['MEDIUM RISK']
  const Icon = cfg.icon

  const sizeClasses = {
    sm: 'text-xs px-3 py-1 gap-1.5 font-semibold',
    md: 'text-sm px-3.5 py-1.5 gap-2 font-bold tracking-wide',
    lg: 'text-base px-5 py-2.5 gap-2.5 font-extrabold tracking-wider',
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border shadow-sm transition-all',
        cfg.text,
        cfg.bg,
        cfg.border,
        sizeClasses[size]
      )}
    >
      {showDot && (
        <span className="relative flex h-2.5 w-2.5">
          <span className={clsx('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', cfg.dotPulse)} />
          <span className={clsx('relative inline-flex rounded-full h-2.5 w-2.5', cfg.dot)} />
        </span>
      )}
      {showIcon && <Icon size={size === 'lg' ? 19 : size === 'sm' ? 14 : 16} className="shrink-0" />}
      <span>{cfg.label}</span>
    </span>
  )
}

export function riskColor(level) {
  return (CONFIG[level] || CONFIG['MEDIUM RISK']).text
}
