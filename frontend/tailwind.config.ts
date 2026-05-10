import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101318",
        panel: "#151922",
        line: "#29303d",
        accent: "#28c76f",
        signal: "#38bdf8"
      },
      boxShadow: {
        soft: "0 18px 50px rgba(0, 0, 0, 0.25)"
      }
    }
  },
  plugins: []
} satisfies Config;

