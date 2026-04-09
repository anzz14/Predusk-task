import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Minimalist black & white palette
        background: "#ffffff",
        "background-dark": "#0a0a0a",
        foreground: "#000000",
        "foreground-muted": "#6b7280",
        "foreground-light": "#f5f5f5",
        
        border: "#e5e5e5",
        "border-medium": "#d4d4d8",
        
        input: "#ffffff",
        ring: "#000000",
        
        primary: {
          DEFAULT: "#000000",
          foreground: "#ffffff",
        },
        secondary: {
          DEFAULT: "#ffffff",
          foreground: "#000000",
        },
        destructive: {
          DEFAULT: "#ef4444",
          foreground: "#ffffff",
        },
        muted: {
          DEFAULT: "#f5f5f5",
          foreground: "#6b7280",
        },
        accent: {
          DEFAULT: "#000000",
          foreground: "#ffffff",
        },
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          '"Segoe UI"',
          "Roboto",
          '"Helvetica Neue"',
          "Arial",
          "sans-serif",
        ],
      },
      boxShadow: {
        xs: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        sm: "0 1px 2px 0 rgba(0, 0, 0, 0.08)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;