// Wait for the HTML document to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {

    // --- GLOBAL STATE ---
    // A simple object to hold the data we get from the backend
    const appState = {
        consultationId: null,
        apiResponse: null,
    };

    // --- DOM ELEMENTS ---
    const processButton = document.getElementById('process-button');
    const transcriptInput = document.getElementById('transcript-input');
    const contentView = document.getElementById('content-view');

    // --- EVENT LISTENERS ---
    processButton.addEventListener('click', processConsultation);

    // --- CORE FUNCTIONS ---

    /**
     * Handles the main process of sending the transcript to the backend.
     */
    async function processConsultation() {
        const transcript = transcriptInput.value;
        if (!transcript.trim()) {
            alert('Transcript cannot be empty.');
            return;
        }

        // Update UI to show loading state
        processButton.disabled = true;
        processButton.textContent = 'Processing... Please Wait...';

        try {
            // Step 1: Create the consultation record to get an ID
            const createResponse = await fetch('/api/v1/consultations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patient_id: 'demo-patient', consent_given: true }),
            });

            if (!createResponse.ok) throw new Error('Failed to create consultation record.');

            const createData = await createResponse.json();
            appState.consultationId = createData.id;

            // Step 2: Send the transcript to the process endpoint
            const processResponse = await fetch(`/api/v1/consultations/${appState.consultationId}/process`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ transcript: transcript }),
            });

            if (!processResponse.ok) throw new Error('Failed to process transcript.');

            appState.apiResponse = await processResponse.json();

            // If successful, render the next view
            renderRoleSelection();

        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}`);
        } finally {
            // Reset button state
            processButton.disabled = false;
            processButton.textContent = 'Process Consultation';
        }
    }

    /**
     * Renders the role selection buttons after processing is complete.
     */
    function renderRoleSelection() {
        document.getElementById('input-view').style.display = 'none'; // Hide the input form
        contentView.innerHTML = `
            <div class="role-selection">
                <h2>2. Summaries Generated Successfully</h2>
                <p>Please select a view:</p>
                <button onclick="window.renderSummaryView('clinician')">View Clinician Summary</button>
                <button onclick="window.renderSummaryView('patient')">View Patient Summary</button>
            </div>
        `;
    }


    /**
     * Renders the final two-panel view with the transcript and selected summary.
     * *** THIS IS THE FIXED AND IMPROVED VERSION ***
     * @param {'clinician' | 'patient'} summaryType - The type of summary to display.
     */
    window.renderSummaryView = function(summaryType) {
        const { raw_transcript, summaries } = appState.apiResponse;
        const selectedSummary = summaries.find(s => s.summary_type === summaryType);

        if (!selectedSummary) {
            contentView.innerHTML = '<p>Error: Summary not found.</p>';
            return;
        }

        // --- Prepare Transcript with Span Wrappers ---
        // Create a sorted, unique list of all sentence spans
        const allSpans = summaries.flatMap(s => s.anchors)
            .map(a => ({ start: a.source_span_start, end: a.source_span_end, id: a.anchor_id }))
            .sort((a, b) => a.start - b.start);

        // Using a Map ensures we only have unique spans based on their ID
        const uniqueSpans = Array.from(new Map(allSpans.map(item => [item.id, item])).values());

        let transcriptHTML = '';
        let lastIndex = 0;
        uniqueSpans.forEach(span => {
            transcriptHTML += raw_transcript.substring(lastIndex, span.start);
            transcriptHTML += `<span id="span-${span.id}">${raw_transcript.substring(span.start, span.end)}</span>`;
            lastIndex = span.end;
        });
        transcriptHTML += raw_transcript.substring(lastIndex);


        // --- Prepare Summary with Clickable Links (THE FIX IS HERE!) ---
        const summaryContent = JSON.parse(selectedSummary.content);
        const formattedSummary = JSON.stringify(summaryContent, null, 2);

        // New, more powerful replacement logic
        const summaryHTML = formattedSummary.replace(/\[S[^\]]*\]/g, (match) => {
            // match will be a string like "[S0, S1, S3, S5]"

            // Extract all numbers from the match
            const numbers = match.match(/\d+/g) || [];

            // For each number, create a clickable link
            const links = numbers.map(num =>
                `<a href="#" class="anchor-link" onclick="window.highlightSentence('S${num}')">S${num}</a>`
            );

            // Join them back with commas and wrap in brackets
            return `[${links.join(', ')}]`;
        });

        // --- Render the final HTML ---
        contentView.innerHTML = `
            <h2>3. Summary and Provenance View</h2>
            <div class="summary-container">
                <div class="transcript-panel">
                    <h3>Original Transcript</h3>
                    <p>${transcriptHTML.replace(/\n/g, '<br>')}</p>
                </div>
                <div class="summary-panel">
                    <h3>${summaryType.charAt(0).toUpperCase() + summaryType.slice(1)} Summary</h3>
                    <pre class="content">${summaryHTML}</pre>
                </div>
            </div>
        `;
    }


    /**
     * Highlights a sentence in the transcript panel.
     * @param {string} anchorId - The ID of the anchor, e.g., "S3".
     */
    window.highlightSentence = function(anchorId) {
        // Remove previous highlights
        document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));

        // Add highlight to the new target
        const targetSpan = document.getElementById(`span-${anchorId}`);
        if (targetSpan) {
            targetSpan.classList.add('highlight');
            targetSpan.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
});