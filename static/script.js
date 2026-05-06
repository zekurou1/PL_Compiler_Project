/**
 * script.js — IDE Frontend Logic for CoolCompiler
 * Handles: tabs, panels, editor, compilation, Find & Replace
 */

// ─── DOM Elements ───────────────────────────────────────────────────────────
const codeEditor    = document.getElementById('codeEditor');
const lineNumbers   = document.getElementById('lineNumbers');
const runBtn        = document.getElementById('runBtn');
const clearBtn      = document.getElementById('clearBtn');
const output        = document.getElementById('output');
const errorText     = document.getElementById('error');
const stagesDiv     = document.getElementById('stages');
const charCount     = document.getElementById('charCount');
const lineCount     = document.getElementById('lineCount');
const tokensCountEl = document.getElementById('tokens-count');
const execStatusEl  = document.getElementById('exec-status');
const outputStatus  = document.getElementById('outputStatus');
const bottomPanel   = document.getElementById('bottomPanel');
const bottomToggle  = document.getElementById('bottomToggle');

// Tabs
const panelTabs = document.querySelectorAll('.panel-tab');
const panelTabContents = document.querySelectorAll('.panel-tab-content');

// ─── Initialization ────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', initialize);

function initialize() {
    // Editor events
    codeEditor.addEventListener('input', () => {
        updateEditorStats();
        updateLineNumbers();
    });
    
    codeEditor.addEventListener('scroll', syncScroll);
    
    // Keyboard shortcuts
    codeEditor.addEventListener('keydown', handleKeyboard);
    
    // Buttons
    runBtn.addEventListener('click', runCode);
    clearBtn.addEventListener('click', clearEditor);
    bottomToggle.addEventListener('click', toggleBottomPanel);
    
    // Panel tabs
    panelTabs.forEach(tab => {
        tab.addEventListener('click', () => switchPanelTab(tab.dataset.tab));
    });
    
    // Find & Replace modal
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            openFindReplace();
        }
    });
    
    // Initial setup
    updateEditorStats();
    updateLineNumbers();
    setOutputStatus('Ready', null);
}

// ─── Editor Stats ────────────────────────────────────────────────────────────
function updateEditorStats() {
    const text = codeEditor.value;
    charCount.textContent = text.length;
    lineCount.textContent = text ? text.split('\n').length : 1;
}

function updateLineNumbers() {
    const lines = codeEditor.value.split('\n').length;
    let html = '';
    for (let i = 1; i <= lines; i++) {
        html += i + '\n';
    }
    lineNumbers.textContent = html;
}

function syncScroll() {
    lineNumbers.scrollTop = codeEditor.scrollTop;
}

// ─── Keyboard Shortcuts ──────────────────────────────────────────────────────
function handleKeyboard(e) {
    // Ctrl/Cmd + Enter: Run
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        runCode();
    }
    
    // Tab: Insert 4 spaces
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = codeEditor.selectionStart;
        const end = codeEditor.selectionEnd;
        codeEditor.value = codeEditor.value.substring(0, start) + '    ' + codeEditor.value.substring(end);
        codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
        updateEditorStats();
        updateLineNumbers();
    }
}

// ─── Run Code ────────────────────────────────────────────────────────────────
async function runCode() {
    const code = codeEditor.value.trim();
    
    if (!code) {
        clearOutput();
        return;
    }
    
    // Clear previous output
    output.textContent = '';
    errorText.textContent = '';
    errorText.classList.remove('active');
    stagesDiv.innerHTML = '<div class="stage-placeholder">Compiling...</div>';
    
    // Loading state
    runBtn.disabled = true;
    runBtn.textContent = '⟳ Running...';
    setOutputStatus('Running', 'running');
    
    try {
        const response = await fetch('/api/compile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display output
            output.textContent = data.output.length > 0
                ? data.output.join('\n')
                : '// (no output)';
            
            // Display stages
            displayStages(data.stages || []);
            
            // Update debug info
            tokensCountEl.textContent = data.tokens_count || 0;
            execStatusEl.textContent = 'Success';
            
            // Status
            setOutputStatus(`Success · ${data.output.length} line(s)`, 'success');
        } else {
            // Error
            errorText.textContent = data.error || 'Unknown error';
            errorText.classList.add('active');
            output.textContent = '';
            
            // Display partial stages if available
            displayStages(data.stages || []);
            
            tokensCountEl.textContent = data.tokens_count || 0;
            execStatusEl.textContent = 'Error';
            
            setOutputStatus('Error', 'error');
        }
    } catch (err) {
        errorText.textContent = `Network error: ${err.message}`;
        errorText.classList.add('active');
        setOutputStatus('Network error', 'error');
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = '▶ Run';
    }
}

// ─── Display Stages ──────────────────────────────────────────────────────────
function displayStages(stages) {
    if (!stages || stages.length === 0) {
        stagesDiv.innerHTML = '<div class="stage-placeholder">Run code to see compilation stages</div>';
        return;
    }
    
    stagesDiv.innerHTML = stages.map(s => {
        const icon = s.status === 'success' ? '✓' : s.status === 'error' ? '✕' : '⟳';
        return `
            <div style="padding:8px;border-bottom:1px solid #3e3e42;font-size:11px;color:#b0b0b0;font-family:monospace;">
                <strong>${icon} ${s.name}</strong>: ${s.details || 'OK'}
            </div>
        `;
    }).join('');
}

// ─── Set Output Status ───────────────────────────────────────────────────────
function setOutputStatus(text, type) {
    outputStatus.textContent = text;
    outputStatus.className = 'status-badge';
    if (type === 'success') outputStatus.classList.add('success');
    else if (type === 'error') outputStatus.classList.add('error');
    else if (type === 'running') outputStatus.classList.add('warning');
}

// ─── Clear Editor ────────────────────────────────────────────────────────────
function clearEditor() {
    if (codeEditor.value && !confirm('Clear all code?')) return;
    codeEditor.value = '';
    updateEditorStats();
    updateLineNumbers();
    clearOutput();
    codeEditor.focus();
}

// ─── Clear Output ────────────────────────────────────────────────────────────
function clearOutput() {
    output.textContent = '';
    errorText.textContent = '';
    errorText.classList.remove('active');
    stagesDiv.innerHTML = '<div class="stage-placeholder">Run code to see compilation stages</div>';
    tokensCountEl.textContent = '0';
    execStatusEl.textContent = 'Ready';
    setOutputStatus('Ready', null);
}

// ─── Switch Panel Tabs ───────────────────────────────────────────────────────
function switchPanelTab(tabName) {
    // Deactivate all tabs and contents
    panelTabs.forEach(tab => tab.classList.remove('active'));
    panelTabContents.forEach(content => content.classList.remove('active'));
    
    // Activate selected
    document.querySelector(`.panel-tab[data-tab="${tabName}"]`)?.classList.add('active');
    document.getElementById(`${tabName}-tab`)?.classList.add('active');
}

// ─── Toggle Bottom Panel ─────────────────────────────────────────────────────
function toggleBottomPanel() {
    bottomPanel.classList.toggle('collapsed');
}

// ─── Find & Replace ──────────────────────────────────────────────────────────
function openFindReplace() {
    const modal = document.getElementById('findReplaceModal');
    if (modal) {
        modal.classList.add('active');
        document.getElementById('findInput')?.focus();
    }
}

function closeFindReplace() {
    const modal = document.getElementById('findReplaceModal');
    if (modal) modal.classList.remove('active');
}

// Find & Replace event listeners
document.getElementById('closeFindReplace')?.addEventListener('click', closeFindReplace);

document.getElementById('findNextBtn')?.addEventListener('click', () => {
    const findText = document.getElementById('findInput')?.value;
    if (findText) {
        const pos = codeEditor.value.indexOf(findText, codeEditor.selectionEnd);
        if (pos !== -1) {
            codeEditor.setSelectionRange(pos, pos + findText.length);
            codeEditor.focus();
        }
    }
});

document.getElementById('replaceBtn')?.addEventListener('click', () => {
    const findText = document.getElementById('findInput')?.value;
    const replaceText = document.getElementById('replaceInput')?.value;
    
    if (codeEditor.selectionStart !== codeEditor.selectionEnd) {
        if (codeEditor.value.substring(codeEditor.selectionStart, codeEditor.selectionEnd) === findText) {
            codeEditor.value = codeEditor.value.substring(0, codeEditor.selectionStart) +
                             replaceText +
                             codeEditor.value.substring(codeEditor.selectionEnd);
            updateEditorStats();
            updateLineNumbers();
        }
    }
});

document.getElementById('replaceAllBtn')?.addEventListener('click', () => {
    const findText = document.getElementById('findInput')?.value;
    const replaceText = document.getElementById('replaceInput')?.value;
    
    if (findText) {
        codeEditor.value = codeEditor.value.replaceAll(findText, replaceText);
        updateEditorStats();
        updateLineNumbers();
    }
});

// Close Find & Replace on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeFindReplace();
    }
});

// ─── Ready ────────────────────────────────────────────────────────────────────
console.log('%c CoolCompiler IDE Ready ', 'background:#1e1e1e;color:#007acc;font-family:monospace;padding:4px 8px;border-radius:4px;font-weight:bold;');
