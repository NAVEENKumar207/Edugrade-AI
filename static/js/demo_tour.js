/**
 * EduGrade AI - Auto-Play Guided Demo Tour Engine
 * Industrial Academic Precision Presentation Controller
 * Plain JavaScript, zero external dependencies.
 * Controls fake SVG cursor, native event dispatching for ReactPy WebSockets,
 * Swiss-Brutalist captions, floating presenter dock, and non-destructive cleanup.
 */

(function () {
    'use strict';

    // -------------------------------------------------------------
    // Configuration & State
    // -------------------------------------------------------------
    const urlParams = new URLSearchParams(window.location.search);
    const speedParam = parseFloat(urlParams.get('speed') || '1.0');
    const autoAudio = urlParams.get('audio') === '1';

    const CONFIG = {
        speedMultiplier: isNaN(speedParam) || speedParam <= 0 ? 1.0 : speedParam,
        typingSpeedMs: 40,
        cursorEaseMs: 700,
        actionWaitTimeoutMs: 10000,
        stepMinDurationMs: 12000,
        enableAudioNarration: autoAudio,
    };

    const state = {
        isRunning: false,
        isPaused: false,
        isAborted: false,
        currentStepIndex: 0,
        stepTimer: null,
        cursorX: window.innerWidth / 2,
        cursorY: window.innerHeight / 2,
    };

    // -------------------------------------------------------------
    // Utilities & Native Event Dispatcher
    // -------------------------------------------------------------
    function sleep(ms) {
        return new Promise((resolve) => setTimeout(resolve, Math.max(10, ms / CONFIG.speedMultiplier)));
    }

    async function waitWhilePaused() {
        while (state.isPaused && !state.isAborted) {
            await sleep(150);
        }
    }

    function setNativeValue(element, value) {
        if (!element) return;
        const tag = element.tagName.toUpperCase();
        let descriptor = null;

        if (tag === 'INPUT') {
            descriptor = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
        } else if (tag === 'TEXTAREA') {
            descriptor = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
        } else if (tag === 'SELECT') {
            descriptor = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
        }

        if (descriptor && descriptor.set) {
            descriptor.set.call(element, value);
        } else {
            element.value = value;
        }

        element.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
        element.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
    }

    async function waitForElement(selector, timeoutMs = CONFIG.actionWaitTimeoutMs) {
        const start = Date.now();
        while (Date.now() - start < timeoutMs) {
            if (state.isAborted) return null;
            await waitWhilePaused();
            const el = document.querySelector(selector);
            if (el && el.offsetParent !== null) {
                return el;
            }
            if (el && selector.includes('tab')) {
                return el;
            }
            await sleep(100);
        }
        return document.querySelector(selector);
    }

    // -------------------------------------------------------------
    // Audio Narration via Web Speech API
    // -------------------------------------------------------------
    function speakNarration(text) {
        if (!CONFIG.enableAudioNarration || !window.speechSynthesis) return;
        try {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.warn('[EduGrade Demo] Speech narration error:', e);
        }
    }

    function stopNarration() {
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
    }

    // -------------------------------------------------------------
    // UI Elements Creation (Cursor, Caption, Controls, Overlays)
    // -------------------------------------------------------------
    function injectStyles() {
        if (document.getElementById('edugrade-demo-styles')) return;
        const style = document.createElement('style');
        style.id = 'edugrade-demo-styles';
        style.textContent = `
            #edugrade-fake-cursor {
                position: fixed;
                top: 0;
                left: 0;
                width: 28px;
                height: 28px;
                pointer-events: none;
                z-index: 2147483647;
                transition: transform ${CONFIG.cursorEaseMs}ms cubic-bezier(0.22, 1, 0.36, 1);
                will-change: transform;
                filter: drop-shadow(0 4px 10px rgba(0,0,0,0.45));
                display: none;
            }
            .edugrade-cursor-ripple {
                position: fixed;
                width: 32px;
                height: 32px;
                margin-top: -16px;
                margin-left: -16px;
                border-radius: 50%;
                border: 3px solid #ff3316;
                background: rgba(255, 51, 22, 0.3);
                pointer-events: none;
                z-index: 2147483646;
                animation: edugrade-ripple-anim 500ms ease-out forwards;
            }
            @keyframes edugrade-ripple-anim {
                0% { transform: scale(0.4); opacity: 1; }
                100% { transform: scale(2.2); opacity: 0; }
            }
            #edugrade-tour-caption-bar {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                z-index: 2147483640;
                background: #111111;
                color: #ffffff;
                border-top: 4px solid #ff3316;
                box-shadow: 0 -10px 30px rgba(0,0,0,0.5);
                font-family: 'Space Grotesk', system-ui, sans-serif;
                padding: 16px 24px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                transition: transform 300ms ease;
            }
            #edugrade-tour-controls {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 2147483645;
                background: #111111;
                border: 2px solid #ff3316;
                color: #ffffff;
                padding: 8px 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.4);
                font-family: 'IBM Plex Mono', monospace;
                font-size: 12px;
            }
            .edugrade-control-btn {
                background: #222222;
                color: #ffffff;
                border: 1px solid #444444;
                padding: 6px 12px;
                cursor: pointer;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                display: inline-flex;
                align-items: center;
                gap: 4px;
                transition: all 150ms;
            }
            .edugrade-control-btn:hover {
                background: #ff3316;
                color: #ffffff;
                border-color: #ff3316;
            }
            .edugrade-control-btn.active {
                background: #ff3316;
                color: #ffffff;
            }
            #edugrade-intro-overlay, #edugrade-outro-overlay {
                position: fixed;
                inset: 0;
                background: rgba(17, 17, 17, 0.94);
                z-index: 2147483644;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 24px;
                color: #ffffff;
                font-family: 'Space Grotesk', sans-serif;
            }
            .edugrade-progress-dots {
                display: flex;
                gap: 4px;
                align-items: center;
                width: 100%;
            }
            .edugrade-progress-seg {
                flex: 1;
                height: 4px;
                background: #333333;
                transition: background 300ms ease;
            }
            .edugrade-progress-seg.done {
                background: #ff3316;
            }
            .edugrade-progress-seg.active {
                background: #ffffff;
            }
        `;
        document.head.appendChild(style);
    }

    function createCursor() {
        let cursor = document.getElementById('edugrade-fake-cursor');
        if (!cursor) {
            cursor = document.createElement('div');
            cursor.id = 'edugrade-fake-cursor';
            cursor.innerHTML = `
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 3L10.07 20.97L13.58 13.58L20.97 10.07L3 3Z" fill="#ff3316" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>
                </svg>
            `;
            document.body.appendChild(cursor);
        }
        return cursor;
    }

    function createCaptionBar() {
        let bar = document.getElementById('edugrade-tour-caption-bar');
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'edugrade-tour-caption-bar';
            bar.innerHTML = `
                <div class="edugrade-progress-dots" id="edugrade-progress-container"></div>
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span id="edugrade-caption-step" style="font-family:'IBM Plex Mono', monospace; font-size:12px; font-weight:bold; background:#ff3316; color:#ffffff; padding:2px 8px; text-transform:uppercase;">STEP 01 / 14</span>
                        <h2 id="edugrade-caption-title" style="margin:0; font-size:18px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Tour Starting...</h2>
                    </div>
                    <span style="font-family:'IBM Plex Mono', monospace; font-size:11px; color:#aaaaaa;">EDUGRADE AI AUTONOMOUS DEMO • ESC TO EXIT</span>
                </div>
                <p id="edugrade-caption-desc" style="margin:0; font-family:'Inter', sans-serif; font-size:14px; line-height:1.5; color:#cccccc; max-width:1200px;">
                    Preparing the academic twin environment...
                </p>
            `;
            document.body.appendChild(bar);
        }
        return bar;
    }

    function createControls() {
        let controls = document.getElementById('edugrade-tour-controls');
        if (!controls) {
            controls = document.createElement('div');
            controls.id = 'edugrade-tour-controls';
            controls.innerHTML = `
                <button class="edugrade-control-btn" id="edugrade-btn-pause" title="Pause / Resume Tour (Space)">
                    <span id="edugrade-pause-label">⏸ Pause</span>
                </button>
                <button class="edugrade-control-btn" id="edugrade-btn-skip" title="Skip to Next Step">
                    ⏭ Skip
                </button>
                <button class="edugrade-control-btn ${CONFIG.enableAudioNarration ? 'active' : ''}" id="edugrade-btn-audio" title="Toggle English Voice Narration">
                    🔊 Voice
                </button>
                <button class="edugrade-control-btn" id="edugrade-btn-exit" style="background:#8b0000; border-color:#8b0000;" title="Exit Demo (Esc)">
                    ✕ Exit
                </button>
            `;
            document.body.appendChild(controls);

            // Bind handlers
            document.getElementById('edugrade-btn-pause').addEventListener('click', togglePause);
            document.getElementById('edugrade-btn-skip').addEventListener('click', skipStep);
            document.getElementById('edugrade-btn-audio').addEventListener('click', toggleAudio);
            document.getElementById('edugrade-btn-exit').addEventListener('click', exitTour);
        }
        return controls;
    }

    // -------------------------------------------------------------
    // Cursor Movement & Interactions
    // -------------------------------------------------------------
    async function moveCursor(x, y) {
        state.cursorX = x;
        state.cursorY = y;
        const cursor = createCursor();
        cursor.style.display = 'block';
        cursor.style.transform = `translate(${x}px, ${y}px)`;
        await sleep(CONFIG.cursorEaseMs);
    }

    async function moveCursorToTarget(selectorOrElem) {
        if (state.isAborted) return null;
        await waitWhilePaused();

        let elem = typeof selectorOrElem === 'string' ? await waitForElement(selectorOrElem) : selectorOrElem;
        if (!elem) {
            console.warn('[EduGrade Demo] Target not found for move:', selectorOrElem);
            return null;
        }

        // Scroll element smoothly into visible viewport if needed
        elem.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });
        await sleep(350);

        const rect = elem.getBoundingClientRect();
        const targetX = rect.left + rect.width / 2;
        const targetY = rect.top + rect.height / 2;

        await moveCursor(targetX, targetY);
        return elem;
    }

    async function clickTarget(selectorOrElem) {
        if (state.isAborted) return;
        await waitWhilePaused();

        const elem = await moveCursorToTarget(selectorOrElem);
        if (!elem) return;

        // Visual click ripple
        const ripple = document.createElement('div');
        ripple.className = 'edugrade-cursor-ripple';
        ripple.style.left = `${state.cursorX}px`;
        ripple.style.top = `${state.cursorY}px`;
        document.body.appendChild(ripple);
        setTimeout(() => ripple.remove(), 550);

        await sleep(150);
        try {
            elem.focus();
            elem.click();
        } catch (err) {
            console.warn('[EduGrade Demo] Click error:', err);
        }
        await sleep(400);
    }

    async function typeIntoTarget(selectorOrElem, text, speedMs = CONFIG.typingSpeedMs) {
        if (state.isAborted) return;
        await waitWhilePaused();

        const elem = await moveCursorToTarget(selectorOrElem);
        if (!elem) return;

        elem.focus();
        setNativeValue(elem, '');
        await sleep(100);

        for (let i = 0; i < text.length; i++) {
            if (state.isAborted) return;
            await waitWhilePaused();
            setNativeValue(elem, text.substring(0, i + 1));
            await sleep(speedMs);
        }
        await sleep(250);
    }

    async function setSliderValue(selectorOrElem, value) {
        if (state.isAborted) return;
        await waitWhilePaused();

        const elem = await moveCursorToTarget(selectorOrElem);
        if (!elem) return;

        setNativeValue(elem, value);
        await sleep(400);
    }

    // -------------------------------------------------------------
    // Tour Navigation Helper
    // -------------------------------------------------------------
    async function navigateTo(navId) {
        if (state.isAborted) return;
        const targetSelector = `[data-demo="nav-${navId}"]`;
        const link = await waitForElement(targetSelector, 3000);
        if (link) {
            await clickTarget(link);
            await sleep(700);
        } else {
            console.log(`[EduGrade Demo] Direct nav link ${navId} not in DOM; checking current page.`);
        }
    }

    // -------------------------------------------------------------
    // Caption & Step Updates
    // -------------------------------------------------------------
    function updateCaption(stepIndex, totalSteps, title, description) {
        const stepSpan = document.getElementById('edugrade-caption-step');
        const titleH2 = document.getElementById('edugrade-caption-title');
        const descP = document.getElementById('edugrade-caption-desc');
        const progressCont = document.getElementById('edugrade-progress-container');

        const stepNum = String(stepIndex + 1).padStart(2, '0');
        const totalNum = String(totalSteps).padStart(2, '0');

        if (stepSpan) stepSpan.textContent = `STEP ${stepNum} / ${totalNum}`;
        if (titleH2) titleH2.textContent = title;
        if (descP) descP.textContent = description;

        // Render progress segments
        if (progressCont) {
            progressCont.innerHTML = '';
            for (let i = 0; i < totalSteps; i++) {
                const seg = document.createElement('div');
                seg.className = 'edugrade-progress-seg ' + (i < stepIndex ? 'done' : i === stepIndex ? 'active' : '');
                progressCont.appendChild(seg);
            }
        }

        speakNarration(`${title}. ${description}`);
    }

    // -------------------------------------------------------------
    // 14-Step Tour Declarative Script (>= 12s per step)
    // -------------------------------------------------------------
    const TOUR_STEPS = [
        // STEP 1: Landing Page
        {
            title: "Welcome to EduGrade AI",
            description: "An Academic Digital Twin & Career Readiness Platform powered by Django 6, ReactPy WebSockets, and deterministic 10-point CBCS telemetry.",
            actions: async () => {
                await moveCursor(window.innerWidth / 2, window.innerHeight / 2);
                await sleep(1500);

                const scaleCard = document.querySelector('[data-demo="hero-stat-scale"]');
                if (scaleCard) await moveCursorToTarget(scaleCard);
                await sleep(1200);

                const latencyCard = document.querySelector('[data-demo="hero-stat-latency"]');
                if (latencyCard) await moveCursorToTarget(latencyCard);
                await sleep(1200);

                const twinTab = document.querySelector('[data-demo="feat-tab-twin"]');
                if (twinTab) await clickTarget(twinTab);
                await sleep(1200);

                const movesTab = document.querySelector('[data-demo="feat-tab-moves"]');
                if (movesTab) await clickTarget(movesTab);
                await sleep(1200);

                // Move to Portal Login
                const loginBtn = document.querySelector('[data-demo="landing-login-btn"]');
                if (loginBtn) {
                    await clickTarget(loginBtn);
                }
                await sleep(2000);
            }
        },

        // STEP 2: Authentication
        {
            title: "Student Authentication & Self-Reported Ledger",
            description: "Logging in as demo student. EduGrade AI operates as an institutional student portal with instant session authentication.",
            actions: async () => {
                await waitForElement('[data-demo="login-username"]', 4000);
                await typeIntoTarget('[data-demo="login-username"]', 'demo_student', 50);
                await sleep(800);

                await typeIntoTarget('[data-demo="login-password"]', 'student123', 50);
                await sleep(800);

                await clickTarget('[data-demo="login-submit-btn"]');
                await sleep(2500);
                await waitForElement('[data-demo="card-cgpa"]', 6000);
            }
        },

        // STEP 3: Student Dashboard Overview
        {
            title: "Executive Academic Dashboard",
            description: "Live calculation of 8.64 CGPA, 136 completed credits, and zero standing arrears with historical semester SGPA progression.",
            actions: async () => {
                await moveCursorToTarget('[data-demo="card-cgpa"]');
                await sleep(2000);

                await moveCursorToTarget('[data-demo="card-sgpa"]');
                await sleep(1800);

                await moveCursorToTarget('[data-demo="card-credits"]');
                await sleep(1800);

                await moveCursorToTarget('[data-demo="card-arrears"]');
                await sleep(1800);

                // Hover SGPA chart bars
                const bar1 = document.querySelector('[data-demo="chart-bar-1"]');
                if (bar1) await moveCursorToTarget(bar1);
                await sleep(1000);

                const bar6 = document.querySelector('[data-demo="chart-bar-6"]');
                if (bar6) await moveCursorToTarget(bar6);
                await sleep(2000);
            }
        },

        // STEP 4: Next Best Move & Early Warning Alerting
        {
            title: "Early Warning & Next Best Move",
            description: "Continuous telemetry checks for SGPA drops (>0.5) and arrears, computing proactive guidance before academic risks occur.",
            actions: async () => {
                const nbmBanner = document.querySelector('[data-demo="next-best-move-banner"]');
                if (nbmBanner) {
                    await moveCursorToTarget(nbmBanner);
                    await sleep(3500);
                }

                const trendCard = document.querySelector('[data-demo="trend-alert-card"]');
                if (trendCard) {
                    await moveCursorToTarget(trendCard);
                    await sleep(3500);
                }
                await sleep(3000);
            }
        },

        // STEP 5: Future Lab - Academic Digital Twin Simulation
        {
            title: "Future Lab: Academic Digital Twin",
            description: "Monte Carlo simulation modeling 100 stochastic academic futures to project graduation CGPA across varying student effort levels.",
            actions: async () => {
                await navigateTo('future_lab');
                await waitForElement('[data-demo="twin-cgpa-slider"]', 5000);

                await setSliderValue('[data-demo="twin-cgpa-slider"]', '9.00');
                await sleep(1500);

                const effortHigher = document.querySelector('[data-demo="twin-effort-higher"]');
                if (effortHigher) await clickTarget(effortHigher);
                await sleep(1500);

                const runSimBtn = document.querySelector('[data-demo="twin-run-sim-btn"]');
                if (runSimBtn) await clickTarget(runSimBtn);
                await sleep(2500);

                const resCard = document.querySelector('[data-demo="twin-results-card"]');
                if (resCard) await moveCursorToTarget(resCard);
                await sleep(3500);
            }
        },

        // STEP 6: Future Lab - Next Best Move & Marks Target Calculator
        {
            title: "Future Lab: Marks Target Engine",
            description: "Deterministic university exam target calculator computing exact external exam scores needed based on internal assessments.",
            actions: async () => {
                const gradeBtnA = document.querySelector('[data-demo="nbm-grade-A"]');
                if (gradeBtnA) {
                    await clickTarget(gradeBtnA);
                    await sleep(1500);
                }

                const internalInput = document.querySelector('[data-demo="marks-internal-input"]');
                if (internalInput) {
                    await typeIntoTarget(internalInput, '44', 60);
                    await sleep(1000);
                }

                const gradeSelect = document.querySelector('[data-demo="marks-grade-select"]');
                if (gradeSelect) {
                    await moveCursorToTarget(gradeSelect);
                    setNativeValue(gradeSelect, 'O');
                    await sleep(1000);
                }

                const calcBtn = document.querySelector('[data-demo="marks-calc-btn"]');
                if (calcBtn) await clickTarget(calcBtn);
                await sleep(2000);

                const resCard = document.querySelector('[data-demo="marks-result-card"]');
                if (resCard) await moveCursorToTarget(resCard);
                await sleep(3500);
            }
        },

        // STEP 7: My Journey & Career Milestones
        {
            title: "My Journey: Gamified Milestones & Badges",
            description: "Seven deterministic achievement badges tracking Distinction (≥8.5 CGPA), Zero Arrears, Comeback, and chronological semester growth.",
            actions: async () => {
                await navigateTo('journey');
                await waitForElement('[data-demo="journey-badges-shelf"]', 5000);

                const shelf = document.querySelector('[data-demo="journey-badges-shelf"]');
                if (shelf) await moveCursorToTarget(shelf);
                await sleep(2500);

                const badge0 = document.querySelector('[data-demo="journey-badge-0"]');
                if (badge0) await moveCursorToTarget(badge0);
                await sleep(1500);

                const badge4 = document.querySelector('[data-demo="journey-badge-4"]');
                if (badge4) await moveCursorToTarget(badge4);
                await sleep(1500);

                const timeline = document.querySelector('[data-demo="journey-timeline"]');
                if (timeline) await moveCursorToTarget(timeline);
                await sleep(4000);
            }
        },

        // STEP 8: Transcripts & Results Ledger
        {
            title: "Transcripts & Results: Institutional Ledger",
            description: "Self-reported student ledger with granular course filtering, live credit accumulation, and O-grade tallies.",
            actions: async () => {
                await navigateTo('results');
                await waitForElement('[data-demo="results-tab-all"]', 5000);

                const tabSem1 = document.querySelector('[data-demo="results-tab-1"]');
                if (tabSem1) {
                    await clickTarget(tabSem1);
                    await sleep(2000);
                }

                const tabAll = document.querySelector('[data-demo="results-tab-all"]');
                if (tabAll) {
                    await clickTarget(tabAll);
                    await sleep(2000);
                }

                const searchInput = document.querySelector('[data-demo="results-search-input"]');
                if (searchInput) {
                    await typeIntoTarget(searchInput, 'Python', 60);
                    await sleep(2000);
                    await typeIntoTarget(searchInput, '', 30);
                    await sleep(1500);
                }
                await sleep(2000);
            }
        },

        // STEP 9: Add Result Modal & Non-Destructive Cleanup
        {
            title: "Course Result CRUD & Real-Time Recalculation",
            description: "Adding course result recalculates SGPA, CGPA, and placement eligibility instantly without page reloads.",
            actions: async () => {
                const addBtn = document.querySelector('[data-demo="results-add-btn"]');
                if (addBtn) {
                    await clickTarget(addBtn);
                    await sleep(1500);
                }

                const codeInput = document.querySelector('[data-demo="modal-course-code"]');
                if (codeInput) {
                    await typeIntoTarget(codeInput, 'DEMO101', 50);
                    await sleep(600);
                }

                const nameInput = document.querySelector('[data-demo="modal-course-name"]');
                if (nameInput) {
                    await typeIntoTarget(nameInput, 'Advanced Cloud Computing', 40);
                    await sleep(600);
                }

                const credInput = document.querySelector('[data-demo="modal-credits"]');
                if (credInput) {
                    await typeIntoTarget(credInput, '3', 50);
                    await sleep(600);
                }

                const gradeSelect = document.querySelector('[data-demo="modal-grade"]');
                if (gradeSelect) {
                    setNativeValue(gradeSelect, 'O');
                    await sleep(600);
                }

                const saveBtn = document.querySelector('[data-demo="modal-save-btn"]');
                if (saveBtn) {
                    await clickTarget(saveBtn);
                    await sleep(2500);
                }

                // Close or cancel form
                const cancelBtn = document.querySelector('[data-demo="modal-cancel-btn"]');
                if (cancelBtn) {
                    await clickTarget(cancelBtn);
                    await sleep(1000);
                }
                await sleep(2000);
            }
        },

        // STEP 10: Bulk CSV Import & Transcript PDF Export
        {
            title: "CSV Bulk Ingestion & Official Transcript Export",
            description: "Supports standardized institutional CSV grade files and generates tamper-evident ReportLab PDF transcripts with dynamic QR codes.",
            actions: async () => {
                const csvBtn = document.querySelector('[data-demo="results-csv-btn"]');
                if (csvBtn) {
                    await clickTarget(csvBtn);
                    await sleep(2500);
                }

                const csvArea = document.querySelector('[data-demo="csv-textarea"]');
                if (csvArea) {
                    await moveCursorToTarget(csvArea);
                    await sleep(2000);
                }

                const closeCsv = document.querySelector('[data-demo="csv-close-btn"]');
                if (closeCsv) {
                    await clickTarget(closeCsv);
                    await sleep(1200);
                }

                const pdfBtn = document.querySelector('[data-demo="results-export-pdf"]');
                if (pdfBtn) {
                    await moveCursorToTarget(pdfBtn);
                    await sleep(2500);
                }
                await sleep(2000);
            }
        },

        // STEP 11: CGPA Planner & Simulator
        {
            title: "Predictive CGPA Planner & Feasibility Engine",
            description: "Calculates the exact average SGPA required across remaining semesters to achieve target honors, modeling what-if graduation scenarios.",
            actions: async () => {
                await navigateTo('planner');
                await waitForElement('[data-demo="planner-target-slider"]', 5000);

                await setSliderValue('[data-demo="planner-target-slider"]', '9.00');
                await sleep(2000);

                const preset85 = document.querySelector('[data-demo="planner-preset-85"]');
                if (preset85) {
                    await clickTarget(preset85);
                    await sleep(1500);
                }

                const verdictCard = document.querySelector('[data-demo="planner-verdict-card"]');
                if (verdictCard) {
                    await moveCursorToTarget(verdictCard);
                    await sleep(3000);
                }

                const scenarios = document.querySelector('[data-demo="planner-scenarios-table"]');
                if (scenarios) {
                    await moveCursorToTarget(scenarios);
                    await sleep(3500);
                }
            }
        },

        // STEP 12: Placement Eligibility Matrix & Skill Map
        {
            title: "Placement Eligibility Matrix & Academic Skill Map",
            description: "Direct mapping of company CTC, minimum CGPA, and max arrears cutoffs with credit-weighted academic mastery scores.",
            actions: async () => {
                await navigateTo('placements');
                await waitForElement('[data-demo="skill-map-container"]', 5000);

                const skillMap = document.querySelector('[data-demo="skill-map-container"]');
                if (skillMap) {
                    await moveCursorToTarget(skillMap);
                    await sleep(3000);
                }

                const tabEligible = document.querySelector('[data-demo="placement-tab-eligible"]');
                if (tabEligible) {
                    await clickTarget(tabEligible);
                    await sleep(2000);
                }

                const tabAction = document.querySelector('[data-demo="placement-tab-action"]');
                if (tabAction) {
                    await clickTarget(tabAction);
                    await sleep(2000);
                }

                const card0 = document.querySelector('[data-demo="placement-company-card-0"]');
                if (card0) {
                    await moveCursorToTarget(card0);
                    await sleep(3000);
                }
                await sleep(1500);
            }
        },

        // STEP 13: Grounded AI Academic Advisor
        {
            title: "Grounded AI Academic Advisor",
            description: "Transcript-grounded LLM advice synthesized through Groq Cloud Llama 3.3 with deterministic academic intelligence fallback and voice accessibility.",
            actions: async () => {
                await navigateTo('advisor');
                await waitForElement('[data-demo="advisor-chat-input"]', 5000);

                const chip0 = document.querySelector('[data-demo="advisor-chip-0"]');
                if (chip0) {
                    await clickTarget(chip0);
                    await sleep(4000);
                }

                const speakerBtn = document.querySelector('[data-demo="advisor-speaker-btn"]');
                if (speakerBtn) {
                    await moveCursorToTarget(speakerBtn);
                    await sleep(2500);
                }

                const inputEl = document.querySelector('[data-demo="advisor-chat-input"]');
                if (inputEl) {
                    await moveCursorToTarget(inputEl);
                    await sleep(3000);
                }
                await sleep(2000);
            }
        },

        // STEP 14: Academic Regulations & Presentation Summary
        {
            title: "Curriculum Regulations & Presentation Conclusion",
            description: "Authoritative UGC 10-point scale regulations, self-reported ledger verification, and holistic academic digital twin summary.",
            actions: async () => {
                await navigateTo('regulations');
                await waitForElement('[data-demo="regulations-grade-table"]', 5000);

                const gradeTable = document.querySelector('[data-demo="regulations-grade-table"]');
                if (gradeTable) {
                    await moveCursorToTarget(gradeTable);
                    await sleep(2500);
                }

                const sem2Tab = document.querySelector('[data-demo="curriculum-tab-2"]');
                if (sem2Tab) {
                    await clickTarget(sem2Tab);
                    await sleep(2000);
                }

                await navigateTo('profile');
                await waitForElement('[data-demo="profile-edit-btn"]', 5000);
                await sleep(2000);

                // Show Outro Overlay
                showOutroOverlay();
                await sleep(4000);
            }
        }
    ];

    // -------------------------------------------------------------
    // Tour Flow Control
    // -------------------------------------------------------------
    async function startTour() {
        if (state.isRunning) return;

        console.log('[EduGrade Demo] Initializing environment...');
        injectStyles();
        createCursor();
        createCaptionBar();
        createControls();

        // Seed demo environment via backend endpoint
        try {
            await fetch('/api/demo/prepare/', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        } catch (e) {
            console.warn('[EduGrade Demo] Prepare call warning:', e);
        }

        state.isRunning = true;
        state.isPaused = false;
        state.isAborted = false;
        state.currentStepIndex = 0;

        showIntroOverlay();
        await sleep(3000);
        hideIntroOverlay();

        for (let i = 0; i < TOUR_STEPS.length; i++) {
            if (state.isAborted) break;
            state.currentStepIndex = i;
            const step = TOUR_STEPS[i];

            updateCaption(i, TOUR_STEPS.length, step.title, step.description);

            const stepStartTime = Date.now();
            try {
                await step.actions();
            } catch (err) {
                console.error(`[EduGrade Demo] Error in Step ${i + 1}:`, err);
            }

            // Ensure minimum step duration >= 12 seconds
            const elapsed = Date.now() - stepStartTime;
            const remaining = CONFIG.stepMinDurationMs - elapsed;
            if (remaining > 0 && !state.isAborted) {
                await sleep(remaining);
            }
        }

        if (!state.isAborted) {
            showOutroOverlay();
        }
    }

    function togglePause() {
        state.isPaused = !state.isPaused;
        const btn = document.getElementById('edugrade-pause-label');
        if (btn) {
            btn.textContent = state.isPaused ? '▶ Resume' : '⏸ Pause';
        }
        if (state.isPaused) {
            stopNarration();
        } else {
            const step = TOUR_STEPS[state.currentStepIndex];
            if (step) speakNarration(`${step.title}. ${step.description}`);
        }
    }

    function skipStep() {
        console.log('[EduGrade Demo] Skipping to next step...');
        state.isPaused = false;
        // Trigger abort of current step sleep
        if (state.stepTimer) clearTimeout(state.stepTimer);
    }

    function toggleAudio() {
        CONFIG.enableAudioNarration = !CONFIG.enableAudioNarration;
        const btn = document.getElementById('edugrade-btn-audio');
        if (btn) {
            btn.classList.toggle('active', CONFIG.enableAudioNarration);
        }
        if (CONFIG.enableAudioNarration) {
            const step = TOUR_STEPS[state.currentStepIndex];
            if (step) speakNarration(`${step.title}. ${step.description}`);
        } else {
            stopNarration();
        }
    }

    async function exitTour() {
        state.isAborted = true;
        state.isRunning = false;
        state.isPaused = false;
        stopNarration();

        // Cleanup UI elements
        const cursor = document.getElementById('edugrade-fake-cursor');
        if (cursor) cursor.style.display = 'none';

        const caption = document.getElementById('edugrade-tour-caption-bar');
        if (caption) caption.remove();

        const controls = document.getElementById('edugrade-tour-controls');
        if (controls) controls.remove();

        hideIntroOverlay();
        hideOutroOverlay();

        // Clean up database / demo data
        try {
            await fetch('/api/demo/cleanup/', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
            console.log('[EduGrade Demo] Environment cleanly restored.');
        } catch (e) {
            console.warn('[EduGrade Demo] Cleanup call error:', e);
        }
    }

    // -------------------------------------------------------------
    // Intro & Outro Overlays
    // -------------------------------------------------------------
    function showIntroOverlay() {
        let intro = document.getElementById('edugrade-intro-overlay');
        if (!intro) {
            intro = document.createElement('div');
            intro.id = 'edugrade-intro-overlay';
            intro.innerHTML = `
                <div style="max-width:600px; border:3px solid #ff3316; background:#181818; padding:32px; box-shadow:0 12px 40px rgba(0,0,0,0.8);">
                    <div style="font-family:'IBM Plex Mono', monospace; font-size:12px; color:#ff3316; font-weight:bold; letter-spacing:2px; margin-bottom:8px;">
                        LIVE PROJECT PRESENTATION
                    </div>
                    <h1 style="font-size:32px; margin:0 0 12px 0; font-weight:bold; text-transform:uppercase;">EduGrade AI</h1>
                    <p style="font-family:'Inter', sans-serif; font-size:15px; color:#cccccc; line-height:1.6; margin-bottom:20px;">
                        Autonomous Academic Digital Twin & Career Readiness Platform Tour. Sit back while the app demonstrates each feature automatically.
                    </p>
                    <div style="display:flex; justify-content:center; gap:12px; font-family:'IBM Plex Mono', monospace; font-size:13px;">
                        <span style="background:#222222; border:1px solid #444444; padding:6px 12px;">14 Dynamic Steps</span>
                        <span style="background:#222222; border:1px solid #444444; padding:6px 12px;">Full Student Portal</span>
                        <span style="background:#222222; border:1px solid #444444; padding:6px 12px;">Esc to Exit</span>
                    </div>
                </div>
            `;
            document.body.appendChild(intro);
        }
        intro.style.display = 'flex';
    }

    function hideIntroOverlay() {
        const intro = document.getElementById('edugrade-intro-overlay');
        if (intro) intro.style.display = 'none';
    }

    function showOutroOverlay() {
        let outro = document.getElementById('edugrade-outro-overlay');
        if (!outro) {
            outro = document.createElement('div');
            outro.id = 'edugrade-outro-overlay';
            outro.innerHTML = `
                <div style="max-width:600px; border:3px solid #ff3316; background:#181818; padding:36px; box-shadow:0 12px 40px rgba(0,0,0,0.8);">
                    <div style="font-family:'IBM Plex Mono', monospace; font-size:12px; color:#ff3316; font-weight:bold; letter-spacing:2px; margin-bottom:8px;">
                        PRESENTATION COMPLETE
                    </div>
                    <h1 style="font-size:30px; margin:0 0 12px 0; font-weight:bold; text-transform:uppercase;">Academic Digital Twin Tour Completed</h1>
                    <p style="font-family:'Inter', sans-serif; font-size:15px; color:#cccccc; line-height:1.6; margin-bottom:24px;">
                        All 14 academic telemetry, future lab simulation, placement eligibility, and grounded mentor features successfully demonstrated.
                    </p>
                    <div style="display:flex; justify-content:center; gap:16px;">
                        <button class="edugrade-control-btn" id="edugrade-btn-replay" style="padding:10px 20px; font-size:13px;">
                            🔄 Replay Tour
                        </button>
                        <button class="edugrade-control-btn" id="edugrade-btn-finish" style="background:#ff3316; border-color:#ff3316; padding:10px 20px; font-size:13px;">
                            ✓ Exit to Portal
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(outro);

            document.getElementById('edugrade-btn-replay').addEventListener('click', () => {
                hideOutroOverlay();
                startTour();
            });
            document.getElementById('edugrade-btn-finish').addEventListener('click', () => {
                exitTour();
            });
        }
        outro.style.display = 'flex';
    }

    function hideOutroOverlay() {
        const outro = document.getElementById('edugrade-outro-overlay');
        if (outro) outro.style.display = 'none';
    }

    // -------------------------------------------------------------
    // Keyboard Shortcuts (Esc = Exit, Space = Pause/Resume)
    // -------------------------------------------------------------
    document.addEventListener('keydown', (e) => {
        if (!state.isRunning) return;
        if (e.key === 'Escape') {
            exitTour();
        } else if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            togglePause();
        }
    });

    // -------------------------------------------------------------
    // Public API & Auto-Start Detection
    // -------------------------------------------------------------
    window.startEduGradeDemo = startTour;
    window.stopEduGradeDemo = exitTour;

    // Attach click listener in capture phase to reliably handle Watch Auto-Play Demo button
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('#btn-hero-watch-demo, [data-demo="hero-watch-demo"]');
        if (btn) {
            e.preventDefault();
            e.stopPropagation();
            console.log('[EduGrade Demo] Starting tour from button click');
            startTour();
        }
    }, true);

    // Check for ?demo=1 or #demo auto-start
    if (urlParams.get('demo') === '1' || window.location.hash === '#demo') {
        console.log('[EduGrade Demo] Auto-start detected via query parameter.');
        window.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                startTour();
            }, 1200);
        });
    }
})();
