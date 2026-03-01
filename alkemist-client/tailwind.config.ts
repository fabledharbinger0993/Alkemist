import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark IDE theme palette
        surface: {
          950: "#0a0a0f",
          900: "#111118",
          800: "#1a1a24",
          700: "#22222f",
          600: "#2e2e3e",
        },
        accent: {
          500: "#7c3aed",
          400: "#8b5cf6",
          300: "#a78bfa",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Cascadia Code", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
