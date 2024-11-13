import os
import io
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from gtts import gTTS
from pdfminer.high_level import extract_text
from docx import Document
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def generate_audio(text, lang='pt-br'):
    tts = gTTS(text, lang=lang, tld='com')
    audio = io.BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid or missing file'})

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(filepath)

    if filepath.endswith(('pdf')):
        text = extract_text_from_pdf(filepath)
    elif filepath.endswith('docx'):
        text = extract_text_from_docx(filepath)
    else:
        return jsonify({'error': 'Unsupported file type'})

    if text:
        language = request.form.get('language', 'pt-br')
        audio = generate_audio(text, language)
        return send_file(audio, mimetype='audio/mp3', as_attachment=True, download_name="audio.mp3")
    return jsonify({'error': 'Failed to extract text from file'})

if __name__ == '__main__':
    app.run(debug=True)
