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
    "ja-JP": "Natural Japanese (ja-JP)",
}

class MLXTranslator:

    def __init__(self, model_choice: str = "Qwen3-8B"):

        if model_choice in MODELS:
            self.model_id, self.max_context, self.word_limit = MODELS[model_choice]
        else:
            self.model_id = model_choice
            self.max_context = 32_768
            self.word_limit = "~24,000 words"

        self.is_qwen = "qwen" in self.model_id.lower()

        print(f"Loading {self.model_id} onto Apple Silicon GPU...")
        self.model, self.tokenizer = load(self.model_id)
        self.sampler = make_sampler(temp=0.1)

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
    print("pt-BR:",translator.translate("Click here to save your settings.", "pt-BR"),)
    print("pt-PT:",translator.translate("Click here to save your settings.", "pt-PT"),)
    print("ja-JP:",translator.translate("Click here to save your settings.", "ja-JP"),)



Biased variance 
In our variance calculation method, we use an implementation detail by setting
unbiased=False. 
For those curious about what this means, in the variance calcula-
tion, we divide by the number of inputs n in the variance formula. 

This approach does not apply Bessel’s correction, which typically uses n – 1 instead of n in the denomi-
nator to adjust for bias in sample variance estimation. 

This decision results in a so-
called biased estimate of the variance. For LLMs, where the embedding dimension n
is significantly large, the difference between using n and n – 1 is practically negligible.

I chose this approach to ensure compatibility with the GPT-2 model’s normalization
layers and because it reflects TensorFlow’s default behavior, which was used to
implement the original GPT-2 model. 

Using a similar setting ensures our method is
compatible with the pretrained weights we will load in chapter 6. 

<think>

</think>

Variância viesada
No nosso método de cálculo da variância, usamos um detalhe de implementação definindo unbiased=False. 
Para aqueles que estão curiosos sobre o que isso significa, no cálculo da variância, dividimos pelo número de entradas n na fórmula da variância. 
Esse método não aplica a correção de Bessel, que normalmente usa n – 1 em vez de n no denominador para ajustar o viés na estimativa da variância da amostra. Essa decisão resulta em uma estimativa chamada de viesada da variância. 
Para LLMs, onde a dimensão de embeddings n é significativamente grande, a diferença entre usar n e n – 1 é praticamente insignificante. 
Escolhi esse método para garantir compatibilidade com as camadas de normalização do modelo GPT-2 e porque reflete o comportamento padrão do TensorFlow, que foi usado para implementar o modelo GPT-2 original. 
Usar uma configuração semelhante garante que nosso método seja compatível com os pesos pré-treinados que carregaremos no capítulo 6.
