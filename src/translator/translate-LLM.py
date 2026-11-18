# pip install --upgrade pip
# pip install mlx-lm

from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler

MODELS = {
    "Qwen3-8B": ("mlx-community/Qwen3-8B-4bit", 32_768, "~24,000 words"),
    "Qwen3-30B": ("mlx-community/Qwen3-30B-A3B-4bit", 32_768, "~24,000 words"),
    "Gemma3-27B": ("mlx-community/gemma-3-27b-it-4bit", 128_000, "~96,000 words"),
}

LOCALE_NAMES = {
    "pt-BR": "Brazilian Portuguese (pt-BR)",
    "pt-PT": "European Portuguese (pt-PT)",
    "en-US": "American English (en-US)",
    "en-GB": "British English (en-GB)",
    "en-AU": "Australian English (en-AU)",
    "es-ES": "Castilian Spanish from Spain (es-ES)",
    "es-MX": "Mexican Spanish (es-MX)",
    "es-AR": "Argentine Spanish (es-AR)",
    "es-419": "Neutral Latin American Spanish (es-419)",
    "fr-FR": "Metropolitan French (fr-FR)",
    "fr-CA": "Canadian French (fr-CA)",
    "de-DE": "Standard German (de-DE)",
    "it-IT": "Standard Italian (it-IT)",
    "ja-JP": "Natural Japanese (ja-JP)",
    "ko-KR": "Standard Korean (ko-KR)",
    "zh-CN": "Simplified Chinese (zh-CN)",
    "zh-TW": "Traditional Chinese for Taiwan (zh-TW)",
    "ru-RU": "Standard Russian (ru-RU)",
    "ar-SA": "Modern Standard / Saudi Arabic (ar-SA)",
    "hi-IN": "Standard Hindi (hi-IN)",
}

"""
Alternative Options (If You Want Even Lighter or Heavier)

• Lighter / Faster (~5 GB RAM): mlx-community/Qwen3-8B-4bit 
   — Uses a third of the RAM if you run heavy Docker containers or databases on
     the same Mac, with slightly lower nuance on rare idioms.

• Maximum Quality (~18 GB RAM): mlx-community/gemma-3-27b-it-4bit 
   — Dense 27B model with exceptional European and Asian translation fluency,
     though slower (~35–45 tokens/sec) than Qwen3's MoE architecture. 
     (Note: Gemma uses Google's commercial-friendly Gemma Terms of Use).
"""


class MLXTranslator:

    def __init__(self, model_choice: str = "Qwen3-8B"):

        # Unpack tuple if key exists in MODELS, otherwise treat model_choice as a custom HF repo ID
        if model_choice in MODELS:
            self.model_id, self.max_context, self.word_limit = MODELS[model_choice]
        else:
            self.model_id = model_choice
            self.max_context = 32_768
            self.word_limit = "~24,000 words"

        self.is_qwen = "qwen" in self.model_id.lower()

        # Allow shorthand ("qwen" / "gemma") or a direct Hugging Face repo ID
        # self.model_id = MODELS.get(model_choice, model_choice)
        # self.is_qwen = "qwen" in self.model_id

        print(f"Loading {self.model_id} onto Apple Silicon GPU...")
        self.model, self.tokenizer = load(self.model_id)
        self.sampler = make_sampler(temp=0.1)

        # Initial Download: ~/.cache/huggingface/hub/ ~ 17GB
        # Subsequent Runs_: ~/.cache/huggingface/hub/ ~ 2-3 secs 100% offline.
        self.model, self.tokenizer = load(self.model_id)
        self.sampler = make_sampler(temp=0.1)

    def translate(self, text: str, target_locale: str) -> str:
        if target_locale not in LOCALE_NAMES:
            raise ValueError(f"Unsupported locale: {target_locale}")

        target_desc = LOCALE_NAMES[target_locale]
        instruction = (
            f"You are a professional localization engine."
            f" Translate the user's text into {target_desc}."
            f" Preserve all formatting, placeholders, HTML/Markdown tags, and tone."
            f" Output ONLY the translated text with no explanations or quotes."
        )
        if self.is_qwen:
            # Qwen3 supports system prompts and /no_think for instant output
            messages = [
                {"role": "system", "content": f"{instruction} /no_think"},
                {"role": "user", "content": text},
            ]
        else:
            # Gemma 3 expects instructions inside the user turn
            messages = [{"role": "user", "content": f"{instruction}\n\nText:\n{text}"}]

        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        input_tokens = len(self.tokenizer.encode(prompt))
        # Leave room within the 32,768 native context window, capped at 16,384 output tokens
        available_budget = max(512, self.max_context - input_tokens - 128)
        dynamic_max_tokens = min(16384, available_budget, int(input_tokens * 2.5) + 256)

        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=dynamic_max_tokens,  # maximum number the output tokens.
            sampler=self.sampler,
            verbose=False,
        )

        return response.strip()


if __name__ == "__main__":
    translator = MLXTranslator(model_choice="Gemma3-27B")

    print(
        "pt-BR:",
        translator.translate("Click here to save your settings.", "pt-BR"),
    )
    print(
        "pt-PT:",
        translator.translate("Click here to save your settings.", "pt-PT"),
    )
    print(
        "ja-JP:",
        translator.translate("Click here to save your settings.", "ja-JP"),
    )

    x = """
    Ep 1 (Step 000115): 
Train loss 0.520, Val loss 0.665
Below is an instruction that describes a task. 
Write a response that appropriately completes the request.

### Instruction: 
# Convert the active sentence to passive: 
'The chef cooks the meal every day.' 
### Response:
The meal is prepared every day by the chef.<|endoftext|>
The following is an instruction that describes a task. 
Write a response that appropriately completes the request.  
### Instruction: 
Convert the active sentence to passive:
Ep 2 (Step 000120): Train loss 0.438, Val loss 0.670
Ep 2 (Step 000125): Train loss 0.453, Val loss 0.685
Ep 2 (Step 000130): Train loss 0.448, Val loss 0.681
Ep 2 (Step 000135): Train loss 0.408, Val loss 0.677
...
Ep 2 (Step 000230): 
Train loss 0.300, Val loss 0.657
Below is an instruction that describes a task. 
Write a response that appropriately completes the request.  
### Instruction: 
Convert the active sentence to passive: 
'The chef cooks the meal  every day.'  
### Response:
The meal is cooked every day by the chef.<|endoftext|>
The following is an instruction that describes a task. 
Write a response that appropriately completes the request.  
### Instruction: 
What is the capital of the United Kingdom
Training completed in 0.87 minutes.
"""

    print("-" * 30)
    print(
        "pt-BR:",
        translator.translate(x, "pt-BR"),
    )
    print("-" * 30)
    print(
        "ko-KR:",
        translator.translate(x, "ko-KR"),
    )
