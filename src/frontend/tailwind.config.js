/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', 
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        "spin-slow": "spin 20s linear infinite",
        "spin-reverse": "spin-reverse 15s linear infinite",
        matrix: "matrix 20s linear infinite",
        blob: "blob 7s infinite",
      },
      keyframes: {
        "spin-reverse": {
          from: { transform: "rotate(360deg)" },
          to: { transform: "rotate(0deg)" },
        },
        matrix: {
          "0%": { transform: "translateY(-100%)", opacity: "1" },
          "100%": { transform: "translateY(1000%)", opacity: "0" },
        },
        blob: {
          "0%, 100%": { transform: "translate(0, 0) scale(1)" },
          "25%": { transform: "translate(20px, -20px) scale(1.1)" },
          "50%": { transform: "translate(-20px, 20px) scale(0.9)" },
          "75%": { transform: "translate(20px, 20px) scale(1.1)" },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
};
