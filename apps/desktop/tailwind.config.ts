import type { Config } from 'tailwindcss';

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: '#080B10',
        panel: '#0D121B',
        panel2: '#111827',
        line: '#1F2937',
        muted: '#8B96A8',
        text: '#E5E7EB',
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
        critical: '#FB7185',
        info: '#38BDF8'
      },
      borderRadius: {
        ui: '8px'
      }
    }
  },
  plugins: []
} satisfies Config;
