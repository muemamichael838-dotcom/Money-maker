// This script will be loaded by env-builder.html or a similar mechanism to customize the UI
document.addEventListener('DOMContentLoaded', () => {
    const title = document.querySelector('title');
    if (title) title.innerText = 'Money Maker🤑 - AI Agent';

    const brand = document.querySelector('.brand-name');
    if (brand) brand.innerHTML = 'Money Maker🤑';

    // Add custom links to the sidebar if possible
    const sidebar = document.querySelector('.sidebar-nav');
    if (sidebar) {
        const oddsLink = document.createElement('a');
        oddsLink.href = '#/odds';
        oddsLink.innerText = 'Market Odds';
        sidebar.appendChild(oddsLink);
    }
});
