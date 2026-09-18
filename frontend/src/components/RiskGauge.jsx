export default function RiskGauge({ score, level, size = 180 }) {
  const radius = size / 2
  const stroke = 13
  const normalizedRadius = radius - stroke
  const circumference = normalizedRadius * 2 * Math.PI
  const clampedScore = Math.max(0, Math.min(100, score || 0))
  const pct = clampedScore / 100
  const strokeDashoffset = circumference - pct * circumference

  // Refined enterprise colors
  const colorMap = {
    'LOW RISK': {
      stroke: '#10b981',
      glow: 'rgba(16, 185, 129, 0.25)',
      gradientStart: '#34d399',
      gradientEnd: '#059669',
      label: 'Low Risk',
      textColor: 'text-emerald-400',
    },
    'MEDIUM RISK': {
      stroke: '#f59e0b',
      glow: 'rgba(245, 158, 11, 0.25)',
      gradientStart: '#fbbf24',
      gradientEnd: '#d97706',
      label: 'Moderate Risk',
      textColor: 'text-amber-400',
    },
    'HIGH RISK': {
      stroke: '#f43f5e',
      glow: 'rgba(244, 63, 94, 0.25)',
      gradientStart: '#fb7185',
      gradientEnd: '#e11d48',
      label: 'Critical Risk',
      textColor: 'text-rose-400',
    },
  }

  const currentTheme = colorMap[level] || colorMap['MEDIUM RISK']
  const gradientId = `gauge-grad-${level ? level.replace(/\s+/g, '-') : 'default'}`

  return (
    <div className="relative inline-flex flex-col items-center justify-center select-none">
      <div className="relative inline-flex items-center justify-center p-2.5 rounded-full bg-ink-900/60 border border-ink-700/50 shadow-inner">
        <svg height={size} width={size} className="-rotate-90">
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={currentTheme.gradientStart} />
              <stop offset="100%" stopColor={currentTheme.gradientEnd} />
            </linearGradient>
            <filter id="gauge-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor={currentTheme.stroke} floodOpacity="0.35" />
            </filter>
          </defs>

          {/* Background Track */}
          <circle
            stroke="#152442"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />

          {/* Animated Value Arc */}
          <circle
            stroke={`url(#${gradientId})`}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={`${circumference} ${circumference}`}
            style={{
              strokeDashoffset,
              transition: 'stroke-dashoffset 1s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
            strokeLinecap="round"
            filter="url(#gauge-glow)"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
        </svg>

        {/* Center Readout */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="text-xs font-bold tracking-wider uppercase text-slate-400">
            Risk Score
          </span>
          <span className={`text-4xl sm:text-5xl font-black mono-num leading-tight ${currentTheme.textColor}`}>
            {Math.round(clampedScore)}
          </span>
          <span className="text-xs text-slate-400 font-mono tracking-tight font-medium">
            out of 100
          </span>
        </div>
      </div>
    </div>
  )
}
