// DOM Elements
const form = document.getElementById('meetingForm');
const recipientsTextarea = document.getElementById('recipients');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const bodyFile = document.getElementById('bodyFile');
const filePreview = document.getElementById('filePreview');
const fileContent = document.getElementById('fileContent');
const apiEndpoint = document.getElementById('apiEndpoint');
const generateBtn = document.getElementById('generateBtn');
const generatedPreview = document.getElementById('generatedPreview');
const generatedContent = document.getElementById('generatedContent');
const bodyText = document.getElementById('bodyText');
const isHtml = document.getElementById('isHtml');
const templateSelect = document.getElementById('templateSelect');
const refreshTemplates = document.getElementById('refreshTemplates');
const templatePreview = document.getElementById('templatePreview');
const templateContent = document.getElementById('templateContent');
const templateName = document.getElementById('templateName');
const saveTemplateBtn = document.getElementById('saveTemplateBtn');
const statusMessage = document.getElementById('statusMessage');
const loadingIndicator = document.getElementById('loadingIndicator');

// State
let currentBodyText = '';
let currentBodyType = 'write';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeRecipientHandling();
    initializeFileHandling();
    initializeApiGeneration();
    initializeTemplateSystem();
    initializeFormSubmission();
    loadTemplates();
});

// Tab System
function initializeTabs() {
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
}

function switchTab(targetTab) {
    // Update buttons
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === targetTab) {
            btn.classList.add('active');
        }
    });

    // Update content
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    const targetContent = document.getElementById(`${targetTab}-tab`);
    if (targetContent) {
        targetContent.classList.add('active');
        currentBodyType = targetTab;
    }
}

// Recipient Handling
function initializeRecipientHandling() {
    recipientsTextarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            // Check if current line contains an email
            const cursorPos = this.selectionStart;
            const textBeforeCursor = this.value.substring(0, cursorPos);
            const currentLine = textBeforeCursor.split('\n').pop();
            
            // Simple email regex
            const emailRegex = /\S+@\S+\.\S+/;
            if (emailRegex.test(currentLine) && !currentLine.includes(',')) {
                e.preventDefault();
                // Add comma and space
                const newValue = this.value.substring(0, cursorPos) + ', ' + this.value.substring(cursorPos);
                this.value = newValue;
                this.setSelectionRange(cursorPos + 2, cursorPos + 2);
            }
        }
    });
}

// File Handling
function initializeFileHandling() {
    bodyFile.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });
}

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        showLoading(true);
        const response = await fetch('/upload_file', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        showLoading(false);

        if (result.success) {
            currentBodyText = result.content;
            fileContent.innerHTML = `<pre>${escapeHtml(result.content.substring(0, 500))}${result.content.length > 500 ? '...' : ''}</pre>`;
            filePreview.classList.remove('hidden');
            showStatus('File uploaded and parsed successfully', 'success');
        } else {
            showStatus('Error parsing file: ' + result.error, 'error');
        }
    } catch (error) {
        showLoading(false);
        showStatus('Error uploading file: ' + error.message, 'error');
    }
}

// API Generation
function initializeApiGeneration() {
    generateBtn.addEventListener('click', async function() {
        const endpoint = apiEndpoint.value.trim();
        if (!endpoint) {
            showStatus('Please enter an API endpoint', 'warning');
            return;
        }

        try {
            showLoading(true);
            const response = await fetch('/generate_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ endpoint: endpoint })
            });

            const result = await response.json();
            showLoading(false);

            if (result.success) {
                currentBodyText = result.content;
                generatedContent.innerHTML = `<pre>${escapeHtml(result.content)}</pre>`;
                generatedPreview.classList.remove('hidden');
                showStatus('Text generated successfully', 'success');
            } else {
                showStatus('Error generating text: ' + result.error, 'error');
            }
        } catch (error) {
            showLoading(false);
            showStatus('Error calling API: ' + error.message, 'error');
        }
    });
}

// Template System
function initializeTemplateSystem() {
    templateSelect.addEventListener('change', function() {
        if (this.value) {
            loadTemplate(this.value);
        } else {
            templatePreview.classList.add('hidden');
        }
    });

    refreshTemplates.addEventListener('click', loadTemplates);
    saveTemplateBtn.addEventListener('click', saveTemplate);
}

async function loadTemplates() {
    try {
        const response = await fetch('/list_templates');
        const result = await response.json();

        templateSelect.innerHTML = '<option value="">-- Select a template --</option>';
        
        if (result.success && result.templates.length > 0) {
            result.templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template;
                option.textContent = template;
                templateSelect.appendChild(option);
            });
        }
    } catch (error) {
        showStatus('Error loading templates: ' + error.message, 'error');
    }
}

async function loadTemplate(templateName) {
    try {
        const response = await fetch(`/get_template?name=${encodeURIComponent(templateName)}`);
        const result = await response.json();

        if (result.success) {
            currentBodyText = result.content;
            templateContent.innerHTML = `<pre>${escapeHtml(result.content)}</pre>`;
            templatePreview.classList.remove('hidden');
        } else {
            showStatus('Error loading template: ' + result.error, 'error');
        }
    } catch (error) {
        showStatus('Error loading template: ' + error.message, 'error');
    }
}

async function saveTemplate() {
    const name = templateName.value.trim();
    if (!name) {
        showStatus('Please enter a template name', 'warning');
        return;
    }

    let textToSave = '';
    switch (currentBodyType) {
        case 'upload':
            textToSave = currentBodyText;
            break;
        case 'generate':
            textToSave = currentBodyText;
            break;
        case 'write':
            textToSave = bodyText.value;
            break;
        case 'template':
            textToSave = currentBodyText;
            break;
    }

    if (!textToSave.trim()) {
        showStatus('No content to save as template', 'warning');
        return;
    }

    try {
        const response = await fetch('/save_template', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                content: textToSave
            })
        });

        const result = await response.json();

        if (result.success) {
            showStatus('Template saved successfully', 'success');
            templateName.value = '';
            loadTemplates();
        } else {
            showStatus('Error saving template: ' + result.error, 'error');
        }
    } catch (error) {
        showStatus('Error saving template: ' + error.message, 'error');
    }
}

// Form Submission
function initializeFormSubmission() {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        const formData = new FormData();
        
        // Add basic fields
        formData.append('recipients', recipientsTextarea.value);
        formData.append('subject', document.getElementById('subject').value);
        formData.append('startDateTime', document.getElementById('startDateTime').value);
        formData.append('endDateTime', document.getElementById('endDateTime').value);
        formData.append('location', document.getElementById('location').value);
        formData.append('organizer', document.getElementById('organizer').value);
        
        // Add body content based on current tab
        let bodyContent = '';
        let htmlContent = false;
        
        switch (currentBodyType) {
            case 'upload':
                bodyContent = currentBodyText;
                break;
            case 'generate':
                bodyContent = currentBodyText;
                break;
            case 'write':
                bodyContent = bodyText.value;
                htmlContent = isHtml.checked;
                break;
            case 'template':
                bodyContent = currentBodyText;
                break;
        }
        
        formData.append('bodyContent', bodyContent);
        formData.append('isHtml', htmlContent);
        formData.append('bodyType', currentBodyType);

        try {
            showLoading(true);
            const response = await fetch('/generate_invitations', {
                method: 'POST',
                body: formData
            });

            showLoading(false);

            if (response.ok) {
                // Handle file download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'meeting_invitations.zip';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                showStatus('Meeting invitations generated successfully!', 'success');
            } else {
                const result = await response.json();
                showStatus('Error generating invitations: ' + result.error, 'error');
            }
        } catch (error) {
            showLoading(false);
            showStatus('Error submitting form: ' + error.message, 'error');
        }
    });
}

// Form Validation
function validateForm() {
    const recipients = recipientsTextarea.value.trim();
    const subject = document.getElementById('subject').value.trim();
    const startDateTime = document.getElementById('startDateTime').value;
    const endDateTime = document.getElementById('endDateTime').value;

    if (!recipients) {
        showStatus('Please enter at least one recipient', 'error');
        return false;
    }

    if (!subject) {
        showStatus('Please enter a meeting subject', 'error');
        return false;
    }

    if (!startDateTime || !endDateTime) {
        showStatus('Please select start and end date/time', 'error');
        return false;
    }

    if (new Date(startDateTime) >= new Date(endDateTime)) {
        showStatus('End time must be after start time', 'error');
        return false;
    }

    // Validate recipients format
    const recipientLines = recipients.split('\n').filter(line => line.trim());
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    for (let line of recipientLines) {
        const parts = line.split(',').map(part => part.trim());
        if (parts.length !== 2 || !emailRegex.test(parts[0]) || !parts[1]) {
            showStatus('Invalid recipient format. Use: email, first name (one per line)', 'error');
            return false;
        }
    }

    // Check if body content exists
    let hasBodyContent = false;
    switch (currentBodyType) {
        case 'upload':
            hasBodyContent = currentBodyText.trim().length > 0;
            break;
        case 'generate':
            hasBodyContent = currentBodyText.trim().length > 0;
            break;
        case 'write':
            hasBodyContent = bodyText.value.trim().length > 0;
            break;
        case 'template':
            hasBodyContent = currentBodyText.trim().length > 0;
            break;
    }

    if (!hasBodyContent) {
        showStatus('Please provide meeting body content', 'error');
        return false;
    }

    return true;
}

// Utility Functions
function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.classList.remove('hidden');
    
    // Auto-hide success messages
    if (type === 'success') {
        setTimeout(() => {
            statusMessage.classList.add('hidden');
        }, 5000);
    }
}

function showLoading(show) {
    if (show) {
        loadingIndicator.classList.remove('hidden');
    } else {
        loadingIndicator.classList.add('hidden');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-fill current date/time for convenience
window.addEventListener('load', function() {
    const now = new Date();
    const startTime = new Date(now.getTime() + 24 * 60 * 60 * 1000); // Tomorrow
    const endTime = new Date(startTime.getTime() + 60 * 60 * 1000); // 1 hour later
    
    document.getElementById('startDateTime').value = startTime.toISOString().slice(0, 16);
    document.getElementById('endDateTime').value = endTime.toISOString().slice(0, 16);
});