from flask import Flask, request, jsonify
from PIL import Image
from transformers import AutoTokenizer, AutoModelForCausalLM
from io import BytesIO
import pytesseract
import torch
import re
import json
import pdfplumber
import fitz

# указываем путь к tesseract
pytesseract.pytesseract.tesseract_cmd = r'c:\program files\tesseract-ocr\tesseract.exe'

app = Flask(__name__)


model_name = "thebloke/mistral-7b-instruct-v0.2-gptq" # загружаем модель
device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # cpu/gpu


tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
).to(device)


def generate_structured_data(text): # создаем запрос
    prompt = f""" 
    ты ии-секретарь. проанализируй текст доверенности и строго верни только json-объект в таком виде:

    {{
      "кто_выдал": "",
      "кому_выдана": "",
      "тема": "",
      "дата_начала": "",
      "дата_окончания": ""
    }}

    !!! обязательно заполни поле "тема" — это то, что доверенное лицо должно сделать (например, «получить выписку», «представлять интересы» и т.п.)

    вот текст доверенности:

    \"\"\"{text}\"\"\"
    """

    # переделываем запрос в токены и отправляем в модель
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=False,
        temperature=0.5,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # ищем в ответе все json-блоки
    json_objects = re.findall(r'{[\s\S]*?}', result)

    # перебираем найденные json с конца, пытаясь найти нужный формат
    for json_candidate in reversed(json_objects):
        try:
            parsed = json.loads(json_candidate)
            required_keys = {"кто_выдал", "кому_выдана", "тема", "дата_начала", "дата_окончания"}
            if required_keys.issubset(set(parsed.keys())):
                return parsed
        except json.JSONDecodeError:
            continue

    return {
        "ошибка": "не удалось извлечь корректный json",
        "ответ_модели": result
    }

# достаем текст из pdf с помощью pymupdf и ocr
def ocr_pdf_with_pymupdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = []
    for page in doc:
        # превращаем страницу в картинку с dpi 300
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("rgb", [pix.width, pix.height], pix.samples)
        # распознаём текст из картинки
        text = pytesseract.image_to_string(img, lang='rus')
        full_text.append(text)
    return "\n".join(full_text)

@app.route("/", methods=["POST"])
def extract_and_structure():
    if 'file' not in request.files:
        return jsonify({"ошибка": "файл не передан"})

    file = request.files['file']
    filename = file.filename.lower()

    try:
        if filename.endswith(".pdf"):
            pdf_bytes = file.read()
            # попытка достать текст из pdf напрямую если с текстом
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                texts = [page.extract_text() for page in pdf.pages]
            text = "\n".join(filter(None, texts))

            # если текста нет(<20), делаем через ocr
            if len(text.strip()) < 20:
                text = ocr_pdf_with_pymupdf(pdf_bytes)
        else:
            # если не pdf, тогда картинка
            image = Image.open(BytesIO(file.read()))
            text = pytesseract.image_to_string(image, lang='rus')

        structured_data = generate_structured_data(text)

        # конечный ответ
        return jsonify({
            "распознанный_текст": text,
            "структура": structured_data
        })

    # вывод ошибки если ты лох и не запустилось
    except Exception as e:
        return jsonify({"ошибка": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
