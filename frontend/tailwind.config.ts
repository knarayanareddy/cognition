import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // CL Score Band colours (from F-05)
        "cl-optimal": "#22c55e",    // Green
        "cl-moderate": "#eab308",   // Yellow
        "cl-high": "#f97316",       // Orange
        "cl-critical": "#ef4444",   // Red
        "cl-burnout": "#991b1b",    // Dark Red
        // Badge colours
        "badge-live": "#22c55e",
        "badge-mock": "#eab308",
        "badge-dryrun": "#eab308",
      },
    },
  },
  plugins: [],
};

export default config;
