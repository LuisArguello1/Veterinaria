tailwind.config = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2d9574", // Verde Veterinario
          50: "#f0f9f6",
          100: "#dcf0e8",
          200: "#b8e1d1",
          300: "#85ccb3",
          400: "#4db08e",
          500: "#2d9574",
          600: "#257a5f",
          700: "#206350",
          800: "#1e5143",
          900: "#1c4439",
        },
        secondary: {
          DEFAULT: "#1e8fff", // Azul Médico
          50: "#eff9ff",
          100: "#daf2ff",
          200: "#bde8ff",
          300: "#91daff",
          400: "#56c4ff",
          500: "#2ba9ff",
          600: "#1e8fff",
          700: "#1a75eb",
          800: "#1c5fbe",
          900: "#1e5295",
        },
        accent: {
          DEFAULT: "#ff7b1c", // Naranja Cálido
          50: "#fff8f0",
          100: "#ffefd9",
          200: "#ffdbb3",
          300: "#ffc182",
          400: "#ff9d4f",
          500: "#ff7b1c",
          600: "#f05d00",
          700: "#c74800",
          800: "#a03800",
          900: "#822e00",
        },
        success: {
          DEFAULT: "#22c55e", // Verde Salud
          50: "#f0fdf0",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e",
          600: "#16a34a",
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
        },
        warning: {
          DEFAULT: "#f59e0b", // Amarillo Atención
          50: "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
          800: "#92400e",
          900: "#78350f",
        },
        danger: {
          DEFAULT: "#f43f5e", // Rojo Médico
          50: "#fef2f2",
          100: "#fee2e2",
          200: "#fecdd3",
          300: "#fda4af",
          400: "#fb7185",
          500: "#f43f5e",
          600: "#e11d48",
          700: "#be123c",
          800: "#9f1239",
          900: "#881337",
        },
        neutral: {
          DEFAULT: "#737373", // Grises Profesionales
          50: "#fafafa",
          100: "#f5f5f5",
          200: "#e5e5e5",
          300: "#d4d4d4",
          400: "#a3a3a3",
          500: "#737373",
          600: "#525252",
          700: "#404040",
          800: "#262626",
          900: "#171717",
        },
        dark: {
          DEFAULT: "#0f172a", // Azul Marino Profundo
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
        }
      },
      // Gradientes predefinidos para sistema veterinario
      backgroundImage: {
        'gradient-medical': 'linear-gradient(135deg, #2d9574 0%, #1e8fff 50%, #22c55e 100%)',
        'gradient-care': 'linear-gradient(135deg, #ff7b1c 0%, #f43f5e 50%, #2ba9ff 100%)',
        'gradient-health': 'linear-gradient(135deg, #22c55e 0%, #2d9574 50%, #1e8fff 100%)',
        'gradient-professional': 'linear-gradient(135deg, #0f172a 0%, #1e293b 30%, #475569 100%)',
        'gradient-warm': 'linear-gradient(135deg, #ff7b1c 0%, #fbbf24 50%, #f43f5e 100%)',
        'gradient-trust': 'linear-gradient(135deg, #1e8fff 0%, #2d9574 50%, #22c55e 100%)',
      }
    },
  },
};