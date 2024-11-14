import os
import io
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from gtts import gTTS
import pytesseract
from pdfminer.high_level import extract_text
from docx import Document
from PIL import Image
import fitz  # PyMuPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image_file(file):
    image = Image.open(file.stream)
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(pdf_path):
    # Extrair texto diretamente (caso haja)
    pdf_text = extract_text(pdf_path)
    
    # Extração de imagens com OCR para qualquer imagem encontrada no PDF
    images_text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                images_text += pytesseract.image_to_string(image) + "\n"
    
    # Concatenar texto extraído e OCR de imagens
    return pdf_text + "\n" + images_text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def generate_audio(text, lang='pt-br'):
    tts = gTTS(text, lang=lang)
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

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    if filename.endswith(('png', 'jpg', 'jpeg')):
        text = extract_text_from_image_file(file)
    elif filename.endswith('pdf'):
        text = extract_text_from_pdf(filepath)
    elif filename.endswith('docx'):
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
