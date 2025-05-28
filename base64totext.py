from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import base64
import io

app = Flask(__name__)

with open("image.jpg", 'rb') as img_file:
    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    print(b64_string)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@app.route('/', methods=['POST'])
def index():
    try:
        data = request.get_json()

        image_data = base64.b64decode(data['image_base64'])

        image = Image.open(io.BytesIO(image_data))

        text = pytesseract.image_to_string(image, lang='rus')

        lines = [line.strip() for line in text.split('\n') if line.strip()]

        return jsonify({'текст': lines})

    except Exception as e:
        return jsonify({'ошибка': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
