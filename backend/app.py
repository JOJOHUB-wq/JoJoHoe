import subprocess
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

# The frontend directory is three levels up from this file
# backend/app.py -> backend/ -> root/ -> frontend/
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')


app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

@app.route('/')
def serve_index():
    """
    Serves the main index.html file from the frontend directory.
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """
    Serves static files (like CSS and JS) from the frontend directory.
    """
    return send_from_directory(app.static_folder, path)


@app.route('/execute', methods=['POST'])
def execute_code():
    """
    Executes a snippet of Python code and returns its output.

    This endpoint receives a POST request containing a JSON object
    with a 'code' field. The value of this field is expected to be
    a string of Python code. The code is executed in a separate
    process, and the standard output and standard error are captured.

    Returns:
        A JSON response containing the 'output' and 'error' from the
        executed code. If the code executes successfully, 'output' will
        contain the standard output, and 'error' will be empty. If an

        error occurs, 'error' will contain the standard error, and
        'output' will be empty.
    """
    data = request.get_json()
    code = data.get('code', '')

    if not code:
        return jsonify({'error': 'No code provided'}), 400

    try:
        process = subprocess.Popen(
            ['python', '-c', code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = process.communicate(timeout=15)

        return jsonify({'output': output, 'error': error})

    except subprocess.TimeoutExpired:
        process.kill()
        output, error = process.communicate()
        return jsonify({
            'output': output,
            'error': 'Execution timed out after 15 seconds.'
        }), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
