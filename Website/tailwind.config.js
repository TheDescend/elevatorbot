module.exports = {
    content: [
        "./pages/**/*.{js,ts,jsx,tsx}",
        "./components/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "descend": "#71b093",
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
