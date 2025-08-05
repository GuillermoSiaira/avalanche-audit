import os
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

app = Flask(__name__)

model = None
tokenizer = None
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/deepseek-coder-6.7b-base")

def load_model():
    global model, tokenizer
    if model is None:
        print(f"🔄 Loading model {MODEL_NAME} on GPU with 4-bit quantization...")

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            quantization_config=bnb_config
        )

        print("✅ Model loaded successfully.")

@app.route("/audit", methods=["POST"])
def audit_contract():
    global model, tokenizer
    if model is None:
        load_model()

    data = request.json
    contract_code = data.get("code", "")

    if not contract_code:
        return jsonify({"error": "No contract code provided"}), 400

    inputs = tokenizer(contract_code, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_length=256)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return jsonify({"audit_result": result})

@app.route("/", methods=["GET"])
def home():
    return "🚀 GPU Auditor is running and ready to receive contracts."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
