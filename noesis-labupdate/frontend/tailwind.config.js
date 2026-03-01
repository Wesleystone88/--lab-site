/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Cormorant Garamond"', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        body: ['"DM Sans"', 'sans-serif'],
      },
      colors: {
        void: '#080810',
        surface: '#0e0e1a',
        panel: '#13131f',
        border: '#1e1e30',
        accent: '#7c6af7',
        'accent-dim': '#4a3fa0',
        'accent-glow': '#a89df9',
        gold: '#c9a84c',
        'text-primary': '#e8e6f0',
        'text-secondary': '#8b8aaa',
        'text-dim': '#4a4960',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 3s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
        'fade-in': 'fadeIn 0.8s ease forwards',
        'slide-up': 'slideUp 0.6s ease forwards',
      },
      keyframes: {
        glow: {
          '0%': { textShadow: '0 0 20px rgba(124, 106, 247, 0.3)' },
          '100%': { textShadow: '0 0 60px rgba(124, 106, 247, 0.8), 0 0 120px rgba(124, 106, 247, 0.3)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(24px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
