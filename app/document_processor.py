import os
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading necessary NLTK data...")
    nltk.download('punkt')
    nltk.download('stopwords')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    return file_path

def extract_text(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension in ['.png', '.jpg', '.jpeg', '.gif']:
        return extract_text_from_image(file_path)
    elif file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.txt', '.doc', '.docx']:
        # For simplicity, we'll just read the content of these files
        # In a real-world scenario, you might want to use libraries like python-docx for .docx files
        with open(file_path, 'r') as file:
            return file.read()
    else:
        return ""

def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def generate_tags(text):
    try:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text.lower())
        filtered_tokens = [w for w in word_tokens if not w in stop_words and w.isalnum()]
        return list(set(filtered_tokens))[:10]  # Return top 10 unique tags
    except LookupError:
        print("NLTK data is not available. Using a simple tokenization method.")
        # Simple fallback tokenization
        words = text.lower().split()
        filtered_words = [w for w in words if len(w) > 2 and w.isalnum()]
        return list(set(filtered_words))[:10]