/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#09111f",
        tide: "#0f766e",
        sand: "#f2e8d5",
        ember: "#c2410c",
      },
    },
  },
  plugins: [],
};
