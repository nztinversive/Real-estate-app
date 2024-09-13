import os
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        return file_path
    return None

def extract_text(file_path):
    file_extension = file_path.split('.')[-1].lower()
    if file_extension == 'pdf':
        pages = convert_from_path(file_path)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page)
    else:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
    return text

def generate_tags(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word.lower() for word in word_tokens if word.isalnum() and word.lower() not in stop_words]
    freq_dist = nltk.FreqDist(filtered_text)
    return ','.join([word for word, _ in freq_dist.most_common(5)])