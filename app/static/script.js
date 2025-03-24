document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const inputTabBtns = document.querySelectorAll('.input-tab-btn');
    const inputTabContents = document.querySelectorAll('.input-tab-content');
    const matchForm = document.getElementById('match-form');
    const fileMatchForm = document.getElementById('file-match-form');
    const loadingEl = document.getElementById('loading');
    const resultsEl = document.getElementById('results');
    const errorEl = document.getElementById('error');
    const errorMessageEl = document.getElementById('error-message');
    const backBtn = document.getElementById('back-btn');
    const errorBackBtn = document.getElementById('error-back-btn');
    const scoreValueEl = document.getElementById('score-value');
    const summaryTextEl = document.getElementById('summary-text');
    const strengthsListEl = document.getElementById('strengths-list');
    const gapsListEl = document.getElementById('gaps-list');
    const actionsListEl = document.getElementById('actions-list');
    const rawOutputEl = document.getElementById('raw-output');
    const refreshHistoryBtn = document.getElementById('refresh-history');
    const historyListEl = document.getElementById('history-list');
    const historyLoadingEl = document.getElementById('history-loading');
    const historyEmptyEl = document.getElementById('history-empty');
    const historyErrorEl = document.getElementById('history-error');
    
    // Current job description and match result for export
    let currentJobDescription = '';
    let currentMatchResult = null;

    // Main tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update active tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
            
            // Load history data when switching to history tab
            if (tabId === 'history') {
                loadHistoryData();
            }
        });
    });
    
    // Input method tab switching
    inputTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Update active tab button
            inputTabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Update active tab content
            inputTabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
        });
    });

    // Form submission
    matchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const resumeText = document.getElementById('resume').value.trim();
        const jobDescription = document.getElementById('job-description').value.trim();
        
        if (!resumeText || !jobDescription) {
            showError('Please fill in both the resume and job description fields.');
            return;
        }
        
        // Show loading state
        matchForm.classList.add('hidden');
        loadingEl.classList.remove('hidden');
        resultsEl.classList.add('hidden');
        errorEl.classList.add('hidden');
        
        try {
            const response = await fetch('/match', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    resume_text: resumeText,
                    job_description: jobDescription
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'An error occurred while processing your request.');
            }
            
            const data = await response.json();
            displayResults(data);
            
        } catch (error) {
            showError(error.message || 'An error occurred while processing your request.');
        }
    });

    // Back button
    backBtn.addEventListener('click', () => {
        resultsEl.classList.add('hidden');
        matchForm.classList.remove('hidden');
    });

    // File form submission
    fileMatchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const resumeFile = document.getElementById('resume-file').files[0];
        const jobDescription = document.getElementById('file-job-description').value.trim();
        
        if (!resumeFile || !jobDescription) {
            showError('Please select a resume file and fill in the job description field.');
            return;
        }
        
        // Check file type
        const fileExt = resumeFile.name.split('.').pop().toLowerCase();
        if (fileExt !== 'docx' && fileExt !== 'txt') {
            showError('Only .docx and .txt files are supported.');
            return;
        }
        
        // Show loading state
        fileMatchForm.classList.add('hidden');
        loadingEl.classList.remove('hidden');
        resultsEl.classList.add('hidden');
        errorEl.classList.add('hidden');
        
        try {
            // Create form data
            const formData = new FormData();
            formData.append('resume_file', resumeFile);
            formData.append('job_description', jobDescription);
            
            const response = await fetch('/match-file', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'An error occurred while processing your request.');
            }
            
            const data = await response.json();
            displayResults(data);
            
        } catch (error) {
            showError(error.message || 'An error occurred while processing your request.');
        }
    });

    // Error back button
    errorBackBtn.addEventListener('click', () => {
        errorEl.classList.add('hidden');
        
        // Determine which form to show based on active input tab
        if (document.getElementById('text-input').classList.contains('active')) {
            matchForm.classList.remove('hidden');
        } else {
            fileMatchForm.classList.remove('hidden');
        }
    });

    // Back button (from results)
    backBtn.addEventListener('click', () => {
        resultsEl.classList.add('hidden');
        
        // Determine which form to show based on active input tab
        if (document.getElementById('text-input').classList.contains('active')) {
            matchForm.classList.remove('hidden');
        } else {
            fileMatchForm.classList.remove('hidden');
        }
    });

    // Refresh history button
    refreshHistoryBtn.addEventListener('click', () => {
        loadHistoryData();
    });

    // Display match results
    function displayResults(data) {
        loadingEl.classList.add('hidden');
        resultsEl.classList.remove('hidden');
        
        // Display raw output
        rawOutputEl.textContent = data.raw_output;
        
        // Display structured data if available
        if (data.parsed_output) {
            const { score, summary, strengths, gaps, actions } = data.parsed_output;
            
            // Store current data for export
            currentJobDescription = document.getElementById('text-input').classList.contains('active') 
                ? document.getElementById('job-description').value 
                : document.getElementById('file-job-description').value;
            
            currentMatchResult = {
                score,
                summary,
                strengths,
                gaps,
                actions
            };
            
            // Update score
            scoreValueEl.textContent = score;
            
            // Update summary
            summaryTextEl.textContent = summary;
            
            // Update strengths
            strengthsListEl.innerHTML = '';
            
            if (strengths && strengths.length > 0) {
                strengths.forEach(strength => {
                    const li = document.createElement('li');
                    li.textContent = strength;
                    strengthsListEl.appendChild(li);
                });
            } else {
                strengthsListEl.innerHTML = '<li>No strengths identified</li>';
            }
            
            // Update gaps
            gapsListEl.innerHTML = '';
            
            if (gaps && gaps.length > 0) {
                gaps.forEach(gap => {
                    const li = document.createElement('li');
                    li.textContent = gap;
                    gapsListEl.appendChild(li);
                });
            } else {
                gapsListEl.innerHTML = '<li>No gaps identified</li>';
            }
            
            // Update actions
            actionsListEl.innerHTML = '';
            
            if (actions && actions.length > 0) {
                actions.forEach(action => {
                    const li = document.createElement('li');
                    li.textContent = action;
                    actionsListEl.appendChild(li);
                });
            } else {
                actionsListEl.innerHTML = '<li>No actions recommended</li>';
            }
            
            // Add export button if not already present
            if (!document.getElementById('export-markdown-btn')) {
                const exportBtn = document.createElement('button');
                exportBtn.id = 'export-markdown-btn';
                exportBtn.className = 'btn secondary-btn';
                exportBtn.innerHTML = '<i class="fas fa-file-export"></i> Export as Markdown';
                exportBtn.style.marginTop = '20px';
                
                exportBtn.addEventListener('click', exportToMarkdown);
                
                // Add the button after the raw output container
                document.querySelector('.raw-output-container').after(exportBtn);
            }
        } else {
            // If parsed output is not available, show raw output only
            scoreValueEl.textContent = 'N/A';
            summaryTextEl.textContent = 'Structured data not available. Please see raw output.';
            strengthsListEl.innerHTML = '<li>Structured data not available</li>';
            gapsListEl.innerHTML = '<li>Structured data not available</li>';
            actionsListEl.innerHTML = '<li>Structured data not available</li>';
            
            // Reset current data
            currentJobDescription = '';
            currentMatchResult = null;
            
            // Remove export button if present
            const exportBtn = document.getElementById('export-markdown-btn');
            if (exportBtn) {
                exportBtn.remove();
            }
        }
    }
    
    // Export match results to Markdown
    function exportToMarkdown() {
        if (!currentJobDescription || !currentMatchResult) {
            alert('No match data available to export.');
            return;
        }
        
        try {
            // Generate markdown
            const markdown = exportMatchToMarkdown(currentJobDescription, currentMatchResult);
            
            // Create a blob with the markdown content
            const blob = new Blob([markdown], { type: 'text/markdown' });
            
            // Create a download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'job-match-report.md';
            
            // Trigger the download
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);
        } catch (error) {
            console.error('Error exporting to Markdown:', error);
            alert('Error exporting to Markdown: ' + error.message);
        }
    }

    // Show error message
    function showError(message) {
        matchForm.classList.add('hidden');
        loadingEl.classList.add('hidden');
        resultsEl.classList.add('hidden');
        errorEl.classList.remove('hidden');
        errorMessageEl.textContent = message;
    }

    // Load match history data
    async function loadHistoryData() {
        historyListEl.innerHTML = '';
        historyLoadingEl.classList.remove('hidden');
        historyEmptyEl.classList.add('hidden');
        historyErrorEl.classList.add('hidden');
        
        try {
            const response = await fetch('/history');
            
            if (!response.ok) {
                throw new Error('Failed to load history data');
            }
            
            const data = await response.json();
            
            historyLoadingEl.classList.add('hidden');
            
            if (data.length === 0) {
                historyEmptyEl.classList.remove('hidden');
                return;
            }
            
            // Display history items
            data.forEach(item => {
                const historyItem = createHistoryItem(item);
                historyListEl.appendChild(historyItem);
            });
            
        } catch (error) {
            historyLoadingEl.classList.add('hidden');
            historyErrorEl.classList.remove('hidden');
            console.error('Error loading history:', error);
        }
    }

    // Create a history item element
    function createHistoryItem(item) {
        const div = document.createElement('div');
        div.className = 'history-item';
        
        const header = document.createElement('div');
        header.className = 'history-item-header';
        
        const score = document.createElement('span');
        score.className = 'history-score';
        score.textContent = item.score || 'N/A';
        
        const date = document.createElement('span');
        date.className = 'history-date';
        date.textContent = formatDate(item.timestamp);
        
        header.appendChild(score);
        header.appendChild(date);
        
        const summary = document.createElement('div');
        summary.className = 'history-summary';
        summary.textContent = item.summary || 'No summary available';
        
        const actions = document.createElement('div');
        actions.className = 'history-actions';
        
        const viewBtn = document.createElement('button');
        viewBtn.className = 'btn history-view-btn';
        viewBtn.textContent = 'View Details';
        viewBtn.addEventListener('click', () => {
            viewHistoryDetails(item);
        });
        
        actions.appendChild(viewBtn);
        
        div.appendChild(header);
        div.appendChild(summary);
        div.appendChild(actions);
        
        return div;
    }

    // View history item details
    function viewHistoryDetails(item) {
        // Switch to the match tab
        tabBtns.forEach(b => {
            if (b.getAttribute('data-tab') === 'new-match') {
                b.click();
            }
        });
        
        // Fill the form with the history item data
        document.getElementById('resume').value = item.resume_text;
        document.getElementById('job-description').value = item.job_description;
        
        // Store the job description for export
        currentJobDescription = item.job_description;
        
        // Create a result object that matches the structure expected by displayResults
        let parsedOutput = null;
        
        if (item.strengths && item.gaps && item.actions) {
            // New format
            parsedOutput = {
                score: item.score,
                summary: item.summary,
                strengths: item.strengths,
                gaps: item.gaps,
                actions: item.actions
            };
        } else if (item.highlights) {
            // Old format - convert highlights to strengths and gaps
            const strengths = [];
            const gaps = [];
            
            item.highlights.forEach(highlight => {
                if (highlight.type === 'match') {
                    strengths.push(highlight.description);
                } else if (highlight.type === 'gap') {
                    gaps.push(highlight.description);
                }
            });
            
            parsedOutput = {
                score: item.score,
                summary: item.summary,
                strengths: strengths,
                gaps: gaps,
                actions: ["Update your resume to address the identified gaps"]
            };
        }
        
        // Store the match result for export
        if (parsedOutput) {
            currentMatchResult = parsedOutput;
        }
        
        const result = {
            raw_output: item.raw_output,
            parsed_output: parsedOutput
        };
        
        // Hide the form and display the results
        matchForm.classList.add('hidden');
        displayResults(result);
    }

    // Format date for display
    function formatDate(dateString) {
        if (!dateString) return 'Unknown date';
        
        const date = new Date(dateString);
        return date.toLocaleString();
    }
});
