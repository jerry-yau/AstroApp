// Check dark mode status each load
if (localStorage.getItem('dark')) {
    document.documentElement.setAttribute('data-bs-theme', 'dark')
}

// Light-Dark Mode Switch
document.getElementById("colorSwitch").addEventListener('click', () => {
    if (document.documentElement.getAttribute('data-bs-theme') == 'dark') {
        document.documentElement.setAttribute('data-bs-theme', 'light')
        localStorage.removeItem('dark')
    }
    else {
        document.documentElement.setAttribute('data-bs-theme', 'dark')
        localStorage.setItem('dark', true)
    }
})