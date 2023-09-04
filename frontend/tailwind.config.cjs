/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'iy-orange': {
          50: '#FFCE6D',
          100: '#FFA049',
          200: '#FF7A00'
        },
        'iy-green': {
          50: '#B1DA41',
          100: '#93C123'
        },
        'iy-black': {
          50: '#292929'
        },
        'iy-blue': {
          100: '#459be3'
        }
      },
      fontFamily: {
        oswald: ['Oswald'],
        osans: ['"Open Sans"']
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))'
      },
      screens: {
        xs: '480px',
        xxs: '320px'
      },
      scale: {
        85: '0.85',
        80: '0.80',
        70: '0.70'
      }
    }
  },
  plugins: []
};
