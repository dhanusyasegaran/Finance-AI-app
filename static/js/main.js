document.addEventListener('DOMContentLoaded', function () {
    // 1. Scroll Reveal Animation Logic
    const observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px' // Start reveal slightly before element enters
    };

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                // Optional: stop observing once revealed
                // revealObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Apply reveal to all cards and elements with .reveal class
    document.querySelectorAll('.card, .reveal, .table-dark tr').forEach(el => {
        el.classList.add('reveal'); // Ensure class is present
        revealObserver.observe(el);
    });

    // 2. Interactive Button Feedback
    const interactiveButtons = document.querySelectorAll('.btn-primary, .btn-success, .btn-info, .btn-outline-primary');
    
    interactiveButtons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05) translateY(-3px)';
        });

        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) translateY(0)';
        });

        btn.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.95)';
        });

        btn.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1.05) translateY(-3px)';
        });
        
        // Form specific loading state
        if (btn.type === 'submit') {
            const form = btn.closest('form');
            if (form) {
                form.addEventListener('submit', function() {
                    btn.classList.add('is-loading');
                    const originalText = btn.innerHTML;
                    btn.innerHTML = `<span class="loading-spinner"></span> ${originalText}`;
                });
            }
        }
    });

    // 3. Smooth Anchor Scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // 4. Data Refresh Interactivity (Optional visual flair)
    // Add a glowing flash effect to values when they might have "changed"
    document.querySelectorAll('h3, .fs-4').forEach(val => {
        val.addEventListener('mouseover', function() {
            this.classList.add('text-glow-active');
            setTimeout(() => this.classList.remove('text-glow-active'), 1000);
        });
    });
});
