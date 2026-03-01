// νόησις Terminal Interface — Minimal Interactions

document.addEventListener('DOMContentLoaded', function() {
    
    // SMOOTH SCROLL FOR ANCHOR LINKS
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // SUBTLE EXTERNAL LINK INDICATOR
    // (Optional: adds slight opacity fade on hover for external links)
    document.querySelectorAll('a[target="_blank"]').forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.opacity = '0.7';
        });
        link.addEventListener('mouseleave', function() {
            this.style.opacity = '1';
        });
    });

    // CONSOLE IDENTITY LOG
    // Terminal aesthetic: announce system presence
    console.log(
        '%cνόησις%c — Deterministic Cognitive Substrate',
        'font-family: monospace; font-size: 20px; font-weight: bold; color: #2dd4bf;',
        'font-family: monospace; font-size: 14px; color: #9ca3af;'
    );
    console.log('%cStructure precedes automation. Thinking is treated as engineering.', 'font-family: monospace; color: #10b981;');
    console.log('%cRepository: https://github.com/Wesleystone88/--lab-site', 'font-family: monospace; color: #2dd4bf;');
});
