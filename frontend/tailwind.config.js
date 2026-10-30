/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        surface: "#111827",
        surfaceBorder: "#1f2937",
        accent: "#3b82f6",
        human: "#10b981",
        ai: "#ef4444",
        uncertain: "#f59e0b",
        insufficient: "#6b7280"
      }
    },
  },
  plugins: [],
}

