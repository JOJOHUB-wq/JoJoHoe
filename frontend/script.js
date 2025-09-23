/**
 * @fileoverview This script handles the frontend logic for the Python code executor.
 * It sends the code from the editor to the backend for execution and displays the result.
 */

document.addEventListener('DOMContentLoaded', () => {
    /**
     * The text area element for code input.
     * @type {HTMLTextAreaElement}
     */
    const codeEditor = document.getElementById('code-editor');

    /**
     * The button to trigger code execution.
     * @type {HTMLButtonElement}
     */
    const runBtn = document.getElementById('run-btn');

    /**
     * The pre element to display the output of the executed code.
     * @type {HTMLPreElement}
     */
    const outputArea = document.getElementById('output');

    /**
     * Handles the click event for the 'Run Code' button.
     * Fetches the code from the editor, sends it to the backend,
     * and displays the output or error.
     */
    runBtn.addEventListener('click', () => {
        const code = codeEditor.value;
        outputArea.textContent = 'Executing...';

        fetch('/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code: code }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                outputArea.textContent = `Error: ${data.error}`;
            } else {
                outputArea.textContent = data.output;
            }
        })
        .catch(error => {
            outputArea.textContent = `An error occurred: ${error}`;
        });
    });
});
