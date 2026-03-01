// νόησις Lab - Website Interactions

// Back to Top Button
document.addEventListener('DOMContentLoaded', function() {
    // Create back to top button
    const backToTop = document.createElement('a');
    backToTop.href = '#';
    backToTop.className = 'back-to-top';
    backToTop.innerHTML = '↑';
    backToTop.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTop);

    // Show/hide on scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });

    // Smooth scroll to top
    backToTop.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

// Animate cards on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all deck cards
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.deck-card, .feature, .download-option');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(card);
    });
});

// Copy code snippets on click
document.addEventListener('DOMContentLoaded', function() {
    const codeBlocks = document.querySelectorAll('code');
    codeBlocks.forEach(block => {
        block.style.cursor = 'pointer';
        block.title = 'Click to copy';
        
        block.addEventListener('click', function() {
            const text = this.textContent;
            navigator.clipboard.writeText(text).then(() => {
                const originalText = this.textContent;
                this.textContent = '✓ Copied!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 1500);
            });
        });
    });
});

// Highlight active nav section
document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('nav a[href^="#"]');

    function highlightNav() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.style.backgroundColor = '';
            link.style.color = '';
            if (link.getAttribute('href') === `#${current}`) {
                link.style.backgroundColor = 'var(--color-secondary)';
                link.style.color = 'white';
            }
        });
    }

    window.addEventListener('scroll', highlightNav);
});

// Add loading animation for external links
document.addEventListener('DOMContentLoaded', function() {
    const externalLinks = document.querySelectorAll('a[target="_blank"]');
    externalLinks.forEach(link => {
        link.addEventListener('click', function() {
            this.style.opacity = '0.6';
            setTimeout(() => {
                this.style.opacity = '1';
            }, 300);
        });
    });
});

// Console easter egg
console.log('%c νόησις™ Card System', 'font-size: 20px; font-weight: bold; color: #3498db;');
console.log('%c Structure precedes automation. Thinking is treated as engineering.', 'font-style: italic; color: #7f8c8d;');
console.log('%c Copyright © 2026 Timothy Wesley Stone', 'color: #2c3e50;');
console.log('%c GitHub: https://github.com/Wesleystone88/--lab-site', 'color: #27ae60;');
