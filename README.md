# Python Code Execution Website

This project is a web-based application that allows users to write and execute Python code directly in their browser. It's a simple, self-contained website built with a Flask backend and a vanilla JavaScript frontend.

## Features

-   **In-browser Code Editing**: A simple textarea-based code editor to write Python code.
-   **Real-time Execution**: Execute Python code on the server and see the output in real-time.
-   **Standard Output and Error Display**: Captures and displays both standard output and standard error from the executed code.
-   **Responsive Design**: A clean and simple interface that works on different screen sizes.
-   **Secure**: Code is executed in a separate process with a timeout to prevent malicious or long-running scripts from harming the server.

## Project Structure

The repository is organized into two main directories:

-   `backend/`: Contains the Flask application that handles code execution.
    -   `app.py`: The main Flask server file.
    -   `requirements.txt`: The Python dependencies for the backend.
-   `frontend/`: Contains the static files for the user interface.
    -   `index.html`: The main HTML file.
    -   `style.css`: The stylesheet for the application.
    -   `script.js`: The JavaScript file that handles user interactions.

## Setup and Installation

To run this project locally, you'll need to have Python and `pip` installed.

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install the backend dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```

## Usage

To start the application, run the Flask server from the root of the project:

```bash
python backend/app.py
```

This will start a web server on `http://127.0.0.1:5000`. Open this URL in your web browser to use the application.

You can now:
1.  Enter your Python code in the text editor.
2.  Click the "Run Code" button.
3.  The output or any errors from your code will be displayed in the output area below.
