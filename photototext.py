from flask import Flask, jsonify
from PIL import Image
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    try:
        image_path = os.path.join(os.path.dirname(__file__), 'image.jpg')
        image = Image.open(image_path)

        text = pytesseract.image_to_string(image, lang='rus')

        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip() != '']

        return jsonify({'текст': lines})

    except Exception as e:
        return jsonify({'ошибка': str(e)})


if __name__ == '__main__':
    app.run(debug=True)