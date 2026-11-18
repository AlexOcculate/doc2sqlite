import sqlite3
from typing import Tuple
from mlx_lm import generate, load
from mlx_lm.sample_utils import make_sampler

MODELS = {
    "Qwen3-8B": ("mlx-community/Qwen3-8B-4bit", 32_768, "~24,000 words"),
    "Qwen3-30B": ("mlx-community/Qwen3-30B-A3B-4bit", 32_768, "~24,000 words"),
    "Gemma-3-27B": ("mlx-community/gemma-3-27b-it-4bit", 128_000, "~96,000 words"),
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
}

#   Input Token : 643,160
# Output Tokens : 259,269
#       Runtime : ~37 minutes


class MLXTranslator:

    def __init__(self, model_choice: str = "Qwen3-30B"):
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

    def translate_with_metrics(
        self, text: str, source_locale: str = "en-US", target_locale: str = "pt-BR"
    ) -> Tuple[str, int, int, int, int]:
        """
        Translates text and returns:
        (translated_text, input_tokens, available_tokens, dynamic_max_tokens, output_tokens)
        """
        if target_locale not in LOCALE_NAMES:
            raise ValueError(f"Unsupported target locale: {target_locale}")

        source_desc = LOCALE_NAMES.get(source_locale, source_locale)
        target_desc = LOCALE_NAMES[target_locale]

        instruction = (
            "You are a professional localization engine. Translate the text from"
            f" {source_desc} into {target_desc}. Preserve all formatting,"
            " placeholders, HTML/Markdown tags, and tone. Output ONLY the"
            " translated text with no explanations or quotes."
        )

        if self.is_qwen:
            messages = [
                {"role": "system", "content": f"{instruction} /no_think"},
                {"role": "user", "content": text},
            ]
        else:
            messages = [{"role": "user", "content": f"{instruction}\n\nText:\n{text}"}]

        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        # Calculate token budgets dynamically
        input_tokens = len(self.tokenizer.encode(prompt))
        available_tokens = max(512, self.max_context - input_tokens - 128)
        max_output_cap = min(16_384, available_tokens)
        dynamic_max_tokens = min(max_output_cap, int(input_tokens * 1.5) + 256)

        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=dynamic_max_tokens,
            sampler=self.sampler,
            verbose=False,
        )

        translated_text = response.strip()
        output_tokens = len(self.tokenizer.encode(translated_text))

        return (
            translated_text,
            input_tokens,
            available_tokens,
            dynamic_max_tokens,
            output_tokens,
        )


def run_translation_batch(
    db_path: str,
    model_choice: str = "Qwen3-30B",
    source_locale: str = "en-US",
    target_locale: str = "pt-BR",
):
    translator = MLXTranslator(model_choice=model_choice)

    # Use two connections/cursors or fetchall so reading doesn't lock writing
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        read_cursor = conn.cursor()
        write_cursor = conn.cursor()

        # Optional: Skip blocks that have already been translated for this version & locale
        select_sql = """
            SELECT T.PAGE_PHYSICAL_NUMBER
                 , T.BLOCK_NO
                 , T.VERSION
                 , T.CREATED_AT
                 , T.TEXT_LEN
                 , T.BLOCK_TEXT
              FROM PAGE_BLOCK_VERSIONED T
             WHERE T.BLOCK_TEXT IS NOT NULL
               AND T.BLOCK_TYPE_CODE = 0
               AND trim(T.BLOCK_TEXT) != ''
               AND NOT EXISTS (
                   SELECT 1
                     FROM PAGE_BLOCK_TRANSLATED X
                    WHERE X.PAGE_PHYSICAL_NUMBER = T.PAGE_PHYSICAL_NUMBER
                      AND X.BLOCK_NO = T.BLOCK_NO
                      AND X.VERSION = T.VERSION
                      AND X."IETF-BCP-47_RFC-5646" = ?
               )
        """

        insert_sql = """
            INSERT INTO PAGE_BLOCK_TRANSLATED (
                PAGE_PHYSICAL_NUMBER,
                BLOCK_NO,
                VERSION,
                "IETF-BCP-47_RFC-5646",
                BLOCK_TEXT,
                INPUT_TOKENS,
                AVAILABLE_TOKENS,
                DYNAMIC_MAX_TOKENS,
                OUTPUT_TOKENS
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        read_cursor.execute(select_sql, (target_locale,))
        rows = read_cursor.fetchall()
        print(f"Found {len(rows)} blocks to translate to {target_locale}...")

        for idx, row in enumerate(rows, start=1):
            print(
                f" --> {row["PAGE_PHYSICAL_NUMBER"]}.{row["BLOCK_NO"]}:{row["VERSION"]} {row["TEXT_LEN"]}"
            )
            (
                translated_text,
                input_tokens,
                available_tokens,
                dynamic_max_tokens,
                output_tokens,
            ) = translator.translate_with_metrics(
                text=row["BLOCK_TEXT"],
                source_locale=source_locale,
                target_locale=target_locale,
            )

            write_cursor.execute(
                insert_sql,
                (
                    row["PAGE_PHYSICAL_NUMBER"],
                    row["BLOCK_NO"],
                    row["VERSION"],
                    target_locale,
                    translated_text,
                    input_tokens,
                    available_tokens,
                    dynamic_max_tokens,
                    output_tokens,
                ),
            )

            # Commit every 25 rows to preserve progress on large batches
            if idx % 25 == 0:
                conn.commit()
                print(f"Processed {idx}/{len(rows)} blocks...")

        conn.commit()
        print(f"Completed! {len(rows)} blocks saved to PAGE_BLOCK_TRANSLATED.")


# SAVE THE LLM MODEL
# SAVE PROMPT
# CREATE VIEW THE SHOW PPG,LPG, PGTEXT, IMAGE, ...

if __name__ == "__main__":
    run_translation_batch(
        db_path="~/Desktop/doc2sqlite/DBs/MAIN.db",
        model_choice="Qwen3-30B",  # Or "Qwen3-8B" / "gemma"
        source_locale="en-US",
        target_locale="pt-BR",
    )
