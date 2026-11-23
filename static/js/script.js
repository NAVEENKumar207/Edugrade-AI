/**
 * EduGrade AI - Main Frontend JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // 3. Chart filter interactions (Dashboard)
    const chartFilter = document.querySelector('.card-header select');
    if (chartFilter) {
        chartFilter.addEventListener('change', (e) => {
            const val = e.target.value;
            const barWrappers = document.querySelectorAll('.bars .bar-wrapper');
            
            if (val === 'Last 3 Semesters') {
                barWrappers.forEach((wrapper, index) => {
                    if (index < 2) {
                        wrapper.style.display = 'none';
                    } else {
                        wrapper.style.display = 'flex';
                    }
                });
            } else {
                barWrappers.forEach((wrapper) => {
                    wrapper.style.display = 'flex';
                });
            }
        });
    }

    // 4. Smooth Scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // 5. Sidebar Navigation Active State
    const sidebarLinks = document.querySelectorAll('.sidebar nav a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            sidebarLinks.forEach(item => item.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // 6. Action button triggers
    const aiAdvisorBtn = document.querySelector('.ai-card .outline-button');
    if (aiAdvisorBtn) {
        aiAdvisorBtn.addEventListener('click', () => {
            alert('AI Advisor: Connecting to EduGrade AI Intelligence Service...\n\nRecommendation: Operating Systems memory management focus will improve semester GPA by ~0.4.');
        });
    }

    const cgpaPlannerBtn = document.querySelector('.bottom-grid .outline-button');
    if (cgpaPlannerBtn) {
        cgpaPlannerBtn.addEventListener('click', () => {
            const newTarget = prompt('Enter your Target CGPA (e.g. 9.2):', '9.0');
            if (newTarget && !isNaN(newTarget)) {
                const targetValElem = document.querySelector('.target-value');
                if (targetValElem) targetValElem.textContent = parseFloat(newTarget).toFixed(1);
                
                const progressFill = document.querySelector('.progress-fill');
                if (progressFill) {
                    const pct = Math.min(100, Math.max(10, (8.42 / parseFloat(newTarget)) * 100));
                    progressFill.style.width = pct + '%';
                }
            }
        });
    }

    // 7. Global Theme Toggle Initialization
    const initTheme = () => {
        const savedTheme = localStorage.getItem('edugrade_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (savedTheme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        if (document.body) {
            document.body.setAttribute('data-theme', savedTheme);
            if (savedTheme === 'dark') {
                document.body.classList.add('dark');
            } else {
                document.body.classList.remove('dark');
            }
        }
        updateThemeToggleIcons(savedTheme);
    };

    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || (document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        if (newTheme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        if (document.body) {
            document.body.setAttribute('data-theme', newTheme);
            if (newTheme === 'dark') {
                document.body.classList.add('dark');
            } else {
                document.body.classList.remove('dark');
            }
        }
        try {
            localStorage.setItem('edugrade_theme', newTheme);
        } catch (e) {}
        updateThemeToggleIcons(newTheme);
    };

    const updateThemeToggleIcons = (theme) => {
        const toggleBtns = document.querySelectorAll('.theme-toggle-btn, .legacy-theme-toggle');
        toggleBtns.forEach(btn => {
            if (theme === 'dark') {
                btn.classList.add('is-dark');
                btn.classList.remove('is-light');
                btn.setAttribute('title', 'Switch to Light Mode');
                btn.setAttribute('aria-label', 'Switch to Light Mode');
                const text = btn.querySelector('.theme-text');
                if (text) text.textContent = 'Light Mode';
                const icon = btn.querySelector('.theme-icon');
                if (icon) icon.textContent = '☀️';
            } else {
                btn.classList.add('is-light');
                btn.classList.remove('is-dark');
                btn.setAttribute('title', 'Switch to Dark Mode');
                btn.setAttribute('aria-label', 'Switch to Dark Mode');
                const text = btn.querySelector('.theme-text');
                if (text) text.textContent = 'Dark Mode';
                const icon = btn.querySelector('.theme-icon');
                if (icon) icon.textContent = '🌙';
            }
        });
    };

    // Use event delegation so dynamic buttons also trigger toggle
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.theme-toggle-btn, .legacy-theme-toggle');
        if (btn) {
            toggleTheme();
        }
    });

    initTheme();
});

