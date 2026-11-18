# pip install --upgrade pip
# pip install torch transformers sentencepiece accelerate sacremoses
# pip install mlx-lm

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class LocalTranslator:

    # Neural Machine Translation (NMT)
    # LLM (like mlx-community/Qwen3-8B-4bit or mlx-community/gemma-3-12b-it-4bit )
    # facebook/nllb-200-distilled-600M
    # mlx-community/Qwen3-8B-4bit or mlx-community/gemma-3-12b-it-4bit
    # Any multilingual instruct model works. Smaller = faster.
    # MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3" or "unsloth/llama-3-8b-bnb-4bit", etc.
    # MAX_NEW_TOKENS = 1024
    # SYSTEM_PROMPT = (
    #     "You are a professional translator. Translate the user's text from English "
    #     "to Brazilian Portuguese. Return ONLY the translation, no explanations."
    # )
    def __init__(self, model_name: str = "Helsinki-NLP/opus-mt-tc-big-en-pt"):
        # https://github.com/AlexOcculate/Tatoeba-Challenge
        # Automatically use Apple Silicon GPU (mps) if available, otherwise fallback to CPU
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Loading {model_name} on device: {self.device}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        self.model.eval()  # Set to evaluation mode for faster inference

    def translate(self, texts: list[str], target_lang: str = "pt-BR") -> list[str]:
        # Map your SQL locale codes to Helsinki-NLP dialect tokens
        prefix = ">>pob<< " if target_lang == "pt-BR" else ">>por<< "
        formatted_texts = [f"{prefix}{text}" for text in texts]

        # Tokenize and move tensors to the Mac GPU/CPU
        inputs = self.tokenizer(
            formatted_texts, return_tensors="pt", padding=True, truncation=True
        ).to(self.device)

        # Disable gradient calculation to save RAM and speed up inference
        with torch.no_grad():
            # translated_tokens = self.model.generate(**inputs, max_new_tokens=8192)
            translated_tokens = self.model.generate(
                **inputs,
                max_new_tokens=8192,
                do_sample=True,  # Required to enable temperature
                temperature=0.1,  # Controls randomness (e.g., 0.1 = conservative, 1.2 = creative)
                top_p=0.9,  # Recommended alongside temperature to prevent nonsensical words
                num_beams=1,  # Disable beam search when using pure sampling
            )

        return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)


# --- Example Usage in Backend ---
translator = LocalTranslator()

# Supports batching multiple strings at once
results = translator.translate(
    texts=[
        "Welcome to our platform!",
        "Your order has been shipped.",
        """
 I would also like to thank the wonderful staff at Manning Publications, including
Michael Stephens, for the many productive discussions that helped shape the direc-
tion of this book, and Dustin Archibald, whose constructive feedback and guidance in
adhering to the Manning guidelines have been crucial. I also appreciate your flexibil-
ity in accommodating the unique requirements of this unconventional from-scratch
approach. A special thanks to Aleksandar Dragosavljevic´, Kari Lucke, and Mike Beady
for their work on the professional layouts and to Susan Honeywell and her team for
refining and polishing the graphics.
    """,
    ],
    target_lang="pt-BR",
)

for r in results:
    print("-" * 40)
    print(r)
# Output: ['Bem-vindo à nossa plataforma!', 'Seu pedido foi enviado.']
