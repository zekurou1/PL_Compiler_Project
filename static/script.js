/**
 * script.js — Frontend logic for the toy language compiler.
 * Handles code editing, execution, samples, and output display.
 */

// ─── DOM Elements ───────────────────────────────────────────────────────────
const codeEditor      = document.getElementById('codeEditor');
const runBtn          = document.getElementById('runBtn');
const clearBtn        = document.getElementById('clearBtn');
const clearOutputBtn  = document.getElementById('clearOutputBtn');
const sampleSelect    = document.getElementById('sampleSelect');
const output          = document.getElementById('output');
const errorBox        = document.getElementById('error');

// Status bar elements
const outputIndicator = document.getElementById('outputIndicator');
const outputStatusTxt = document.getElementById('outputStatusText');
const charCount       = document.getElementById('charCount');
const lineCount       = document.getElementById('lineCount');

// Tab elements
const outputTabs      = document.querySelectorAll('.output-tab');
const tabContents     = document.querySelectorAll('.output-tab-content');
const stagesContainer = document.getElementById('stages');
const debugInfo       = document.getElementById('debug-info');
const tokensCount     = document.getElementById('tokens-count');
const execInfo        = document.getElementById('exec-info');

// ─── Event Listeners ────────────────────────────────────────────────────────
runBtn.addEventListener('click', runCode);
clearBtn.addEventListener('click', clearCode);
clearOutputBtn.addEventListener('click', clearOutput);
sampleSelect.addEventListener('change', loadSample);

// Tab switching
outputTabs.forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
});

window.addEventListener('DOMContentLoaded', loadSamples);
window.addEventListener('load', () => codeEditor.focus());

// Keyboard shortcut: Ctrl/Cmd+Enter to run
codeEditor.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        runCode();
    }
});

// Live editor stats
codeEditor.addEventListener('input', updateEditorStats);

// ─── Helpers ────────────────────────────────────────────────────────────────
function updateEditorStats() {
    const val = codeEditor.value;
    const chars = val.length;
    const lines = val ? val.split('\n').length : 0;
    if (charCount)  charCount.textContent  = `${chars} char${chars !== 1 ? 's' : ''}`;
    if (lineCount)  lineCount.textContent  = `${lines} line${lines !== 1 ? 's' : ''}`;
}

function setStatus(state, text) {
    if (!outputIndicator || !outputStatusTxt) return;
    outputIndicator.className = 'output-indicator';
    if (state) outputIndicator.classList.add(state);
    outputStatusTxt.textContent = text;
}

function switchTab(tabName) {
    // Update tab buttons
    outputTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    
    // Update tab content
    tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-content`);
    });
}

function displayStages(stages) {
    if (!stagesContainer) return;
    
    if (!stages || stages.length === 0) {
        stagesContainer.innerHTML = '<div class="stage-placeholder">No stage data available</div>';
        return;
    }
    
    stagesContainer.innerHTML = stages.map(stage => `
        <div class="stage-item ${stage.status}">
            <div class="stage-icon">
                ${stage.status === 'success' ? '✓' : stage.status === 'error' ? '✕' : '⟳'}
            </div>
            <div class="stage-info">
                <div class="stage-name">${stage.name}</div>
                <div class="stage-details">${stage.details}</div>
            </div>
        </div>
    `).join('');
}

function displayDebugInfo(tokensCount, executionInfo) {
    if (!tokensCount || !execInfo) return;
    
    tokensCount.textContent = `${executionInfo.tokens_count || 0} tokens generated`;
    execInfo.textContent = executionInfo.details || 'No execution data';
}

// ─── Run Code ───────────────────────────────────────────────────────────────
async function runCode() {
    const code = codeEditor.value.trim();

    if (!code) {
        clearOutput();
        return;
    }

    // Clear previous results
    output.textContent = '';
    output.style.color = '';
    errorBox.textContent = '';
    errorBox.classList.remove('active');
    stagesContainer.innerHTML = '<div class="stage-placeholder">Compiling...</div>';

    // Loading state
    runBtn.disabled = true;
    runBtn.classList.add('loading');
    runBtn.querySelector('.btn-label').textContent = 'Running';
    runBtn.querySelector('.btn-icon').textContent = '↻';
    setStatus('running', 'Compiling...');

    try {
        const response = await fetch('/api/compile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (data.success) {
            output.textContent = data.output.length > 0
                ? data.output.join('\n')
                : '(no output)';
            if (!data.output.length) output.style.color = 'var(--text-muted)';
            errorBox.classList.remove('active');
            
            // Display stages and debug info
            displayStages(data.stages);
            displayDebugInfo(tokensCount, {
                tokens_count: data.tokens_count,
                details: `${data.output.length} output line${data.output.length !== 1 ? 's' : ''}`
            });
            
            setStatus('success', `Done · ${data.output.length} line${data.output.length !== 1 ? 's' : ''}`);
        } else {
            errorBox.textContent = data.error || 'Unknown error';
            errorBox.classList.add('active');
            output.textContent = '';
            
            // Display stages (may be partial if error occurred)
            displayStages(data.stages);
            
            setStatus('error', 'Compilation failed');
        }
    } catch (err) {
        errorBox.textContent = `Network error: ${err.message}`;
        errorBox.classList.add('active');
        setStatus('error', 'Network error');
    } finally {
        runBtn.disabled = false;
        runBtn.classList.remove('loading');
        runBtn.querySelector('.btn-label').textContent = 'Run';
        runBtn.querySelector('.btn-icon').textContent = '▶';
    }
}

// ─── Clear Code ─────────────────────────────────────────────────────────────
function clearCode() {
    if (codeEditor.value && !confirm('Clear all code?')) return;
    codeEditor.value = '';
    updateEditorStats();
    codeEditor.focus();
}

// ─── Clear Output ───────────────────────────────────────────────────────────
function clearOutput() {
    output.textContent = '';
    output.style.color = '';
    errorBox.textContent = '';
    errorBox.classList.remove('active');
    setStatus(null, 'Ready');
}

// ─── Load Samples (dropdown population) ─────────────────────────────────────
async function loadSamples() {
    updateEditorStats();
    setStatus(null, 'Ready');

    try {
        const response = await fetch('/api/samples');
        const samples  = await response.json();

        for (const [key, sample] of Object.entries(samples)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = sample.name;
            sampleSelect.appendChild(option);
        }
    } catch (err) {
        console.error('Failed to load samples:', err);
    }
}

// ─── Load Selected Sample ────────────────────────────────────────────────────
async function loadSample() {
    const key = sampleSelect.value;
    if (!key) return;

    try {
        const response = await fetch('/api/samples');
        const samples  = await response.json();

        if (samples[key]) {
            codeEditor.value = samples[key].code;
            updateEditorStats();
            codeEditor.focus();
            clearOutput();
            sampleSelect.value = '';
        }
    } catch (err) {
        console.error('Failed to load sample:', err);
    }
}

console.log('%c CoolCompiler ready ', 'background:#0a0e27;color:#00d4ff;font-family:monospace;padding:4px 8px;border-radius:4px;text-shadow:0 0 10px #00d4ff;');
