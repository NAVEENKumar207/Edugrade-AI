/**
 * EduGrade AI - Main Frontend JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Role Toggle Handler (Login & Signup Pages)
    const roleTabs = document.querySelectorAll('.role-tab');
    const roleInput = document.getElementById('selected-role');
    const authForm = document.querySelector('.auth-card form');
    const authTitle = document.getElementById('auth-role-title');
    const authSubtitle = document.getElementById('auth-role-subtitle');
    const studentFields = document.querySelectorAll('.student-only');
    const adminFields = document.querySelectorAll('.admin-only');
    const identifierInput = document.getElementById('identifier-input');
    const passwordInput = document.querySelector('.auth-card input[type="password"]');

    const isStaticFileMode = window.location.protocol === 'file:' || window.location.pathname.endsWith('.html');

    function selectRole(selectedRole) {
        roleTabs.forEach(t => {
            if (t.getAttribute('data-role') === selectedRole) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        if (roleInput) {
            roleInput.value = selectedRole;
        }

        // Update Login UI
        if (window.location.pathname.includes('login') || (authForm && authForm.getAttribute('data-form-type') === 'login')) {
            if (selectedRole === 'admin') {
                if (authTitle) authTitle.textContent = 'Admin / Faculty Sign in';
                if (authSubtitle) authSubtitle.textContent = 'Enter administrative credentials to manage college records.';
                if (identifierInput) identifierInput.placeholder = 'admin@college.edu or Faculty ID';
                if (isStaticFileMode && authForm) {
                    authForm.setAttribute('action', 'admin_dashboard.html');
                }
            } else {
                if (authTitle) authTitle.textContent = 'Student Sign in';
                if (authSubtitle) authSubtitle.textContent = 'Enter your student details to access your dashboard.';
                if (identifierInput) identifierInput.placeholder = 'student@example.com or Roll No';
                if (isStaticFileMode && authForm) {
                    authForm.setAttribute('action', 'dashboard.html');
                }
            }
        }

        // Update Signup UI
        if (window.location.pathname.includes('signup') || (authForm && authForm.getAttribute('data-form-type') === 'signup')) {
            if (selectedRole === 'admin') {
                if (authTitle) authTitle.textContent = 'Create Faculty / Admin Account';
                if (authSubtitle) authSubtitle.textContent = 'Set up your administrator profile with authorization key.';
                studentFields.forEach(el => el.style.display = 'none');
                adminFields.forEach(el => el.style.display = 'block');
                if (isStaticFileMode && authForm) {
                    authForm.setAttribute('action', 'admin_dashboard.html');
                }
            } else {
                if (authTitle) authTitle.textContent = 'Create Student Account';
                if (authSubtitle) authSubtitle.textContent = 'Set up your student profile to track your academic progress.';
                studentFields.forEach(el => el.style.display = 'block');
                adminFields.forEach(el => el.style.display = 'none');
                if (isStaticFileMode && authForm) {
                    authForm.setAttribute('action', 'dashboard.html');
                }
            }
        }
    }

    if (roleTabs.length > 0) {
        roleTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const selectedRole = this.getAttribute('data-role');
                selectRole(selectedRole);
            });
        });
    }

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
        const savedTheme = localStorage.getItem('edugrade_theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        if (document.body) {
            document.body.setAttribute('data-theme', savedTheme);
        }
        updateThemeToggleIcons(savedTheme);
    };

    const toggleTheme = () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        if (document.body) {
            document.body.setAttribute('data-theme', newTheme);
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

