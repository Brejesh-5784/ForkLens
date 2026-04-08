/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'forklens-dark': '#1a1a14',      // Dark Olive-Black
        'forklens-card': '#2a2a1e',      // Slightly lighter olive-black
        'forklens-border': '#3a3a2a',    // Border color
        'forklens-amber': '#C8A84B',     // Amber Gold
        'forklens-muted': '#8a8a7a',     // Secondary text
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'serif'],
        sans: ['Inter', 'sans-serif'],
      },
      letterSpacing: {
        tightest: '-.05em',
      }
    },
  },
  plugins: [],
}
