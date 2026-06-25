document.addEventListener('DOMContentLoaded', () => {
    // Override branding to "Money Maker" as requested by user
    const title = document.querySelector('title');
    if (title) title.innerText = 'Money Maker 🤑';

    const brand = document.querySelector('.brand-name');
    if (brand) brand.innerHTML = 'Money Maker 🤑';

    // Add compliance footer to prevent service suspension for "financial advice"
    const footer = document.querySelector('footer');
    if (footer) {
        footer.innerHTML += '<br><small style="opacity: 0.7">Educational Tool. No Financial Advice. Always bet responsibly.</small>';
    }

    // Professional UI enhancements (Chat-like styling)
    const style = document.createElement('style');
    style.innerHTML = `
        .brand-name { color: #10a37f !important; font-weight: bold; }
        .sidebar { background: #202123 !important; }
        .main-content { background: #343541 !important; color: white !important; }
    `;
    document.head.appendChild(style);
});
