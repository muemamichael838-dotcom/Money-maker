document.addEventListener('DOMContentLoaded', () => {
    const title = document.querySelector('title');
    if (title) title.innerText = 'MarketInsights-AI';

    const brand = document.querySelector('.brand-name');
    if (brand) brand.innerHTML = 'MarketInsights-AI';

    const footer = document.querySelector('footer');
    if (footer) {
        footer.innerHTML += '<br><small>For Educational Research Purposes Only. No Financial Advice Provided.</small>';
    }
});
