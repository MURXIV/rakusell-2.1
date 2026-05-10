/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        brand: {
          teal:      '#0ABFB8',
          'teal-d':  '#08A89F',
          orange:    '#F5A623',
          'orange-d':'#E09410',
        },
      },
    },
  },
  plugins: [],
}
