from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)

model_name = "deepseek-ai/deepseek-llm-1.3b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    prompt = data.get("Запрос", "")

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=False,
        temperature=0,
        eos_token_id=tokenizer.eos_token_id
    )
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    result = result.replace(prompt, "").strip()

    return jsonify({"Ответ": result})

if __name__ == "__main__":
    app.run(debug=True)
