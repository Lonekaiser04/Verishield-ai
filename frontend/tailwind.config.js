/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#070b14', // deepest navy canvas
          900: '#0b1324', // card background
          850: '#0f1a30', // elevated surface
          800: '#152442', // active/hover surface
          750: '#1a2c4e', // secondary border
          700: '#223862', // standard border
          600: '#314f85', // muted border / label
          500: '#476fa8', // secondary text
          400: '#6c94cc',
        },
        accent: {
          300: '#7dd3fc',
          400: '#38bdf8', // electric cyan accent
          500: '#0284c7', // primary blue
          600: '#0369a1',
          700: '#075985',
        },
        risk: {
          low: '#10b981',
          lowBg: 'rgba(16, 185, 129, 0.12)',
          lowBorder: 'rgba(16, 185, 129, 0.3)',
          medium: '#f59e0b',
          mediumBg: 'rgba(245, 158, 11, 0.12)',
          mediumBorder: 'rgba(245, 158, 11, 0.3)',
          high: '#f43f5e',
          highBg: 'rgba(244, 63, 94, 0.12)',
          highBorder: 'rgba(244, 63, 94, 0.3)',
        },
      },
      fontFamily: {
        heading: ['"Plus Jakarta Sans"', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        sans: ['Inter', '"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'ui-monospace', 'monospace'],
      },
      boxShadow: {
        panel: '0 4px 20px -2px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(34, 56, 98, 0.45)',
        'panel-hover': '0 8px 30px -4px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(56, 189, 248, 0.35)',
        glow: '0 0 25px -5px rgba(56, 189, 248, 0.25)',
      },
    },
  },
  plugins: [],
}
