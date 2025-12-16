/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // For glass/dark backgrounds
        backdrop: {
          DEFAULT: 'rgba(24,27,38,0.8)', // glass dark
          strong: 'rgba(17, 20, 29, 0.95)',
          soft: 'rgba(40,48,60,0.7)'
        },
        glass: {
          DEFAULT: 'rgba(40,48,64,0.52)', // semi-dark glass
          light: 'rgba(76,82,104,0.38)',
          hicolor: 'rgba(52,106,150,0.26)'
        },
        ...theme => ({
          primary: theme.primary,
        }),
        dark: {
          900: '#13171f', // main true dark
          800: '#161c24',
          700: '#222736',
          600: '#2d3548',
          500: '#3d415b'
        },
        accent: {
          vibrant: '#4bc9f6', // cyan
          pink: '#f472b6',
          purple: '#a78bfa',
          blue: '#60a5fa',
          glass: '#6dd5fa',
        },
      },
      boxShadow: {
        glass: '0 8px 32px 0 rgba(10,20,40,0.28)',
        glassxl: '0 12px 48px 0 rgba(10,20,40,0.35)',
      },
      backdropBlur: {
        glass: '10px',
        glassxl: '18px',
      },
    }
  },
  plugins: []
};

