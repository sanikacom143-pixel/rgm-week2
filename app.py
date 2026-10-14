from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                return f"<h1>Success! File uploaded: {file.filename}</h1><a href='/'>Go Back</a>"
        return "<h1>No file selected</h1><a href='/'>Go Back</a>"
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                return f"<h1>Success! File uploaded: {file.filename}</h1><a href='/'>Go Back</a>"
        return "<h1>No file selected</h1><a href='/'>Go Back</a>"
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
