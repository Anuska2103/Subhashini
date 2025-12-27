import ctranslate2
import transformers
import warnings
import logging

# SILENCE WARNINGS GLOBALLY
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*torch_dtype.*")

class TranslatorEngine:
    def __init__(self, model_path="nllb-200-ct2-int8"):
        # Ensure path exists
        self.translator = ctranslate2.Translator(model_path, device="cpu")
        
        # The warning often triggers here during config loading
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(
            "facebook/nllb-200-distilled-600M",
            use_fast=True  # Use fast tokenizer for better performance
        )

    def translate(self, text, src_lang="eng_Latn", tgt_lang="hin_Deva"):
        if not text or not text.strip(): return ""
        
        # Set source language
        self.tokenizer.src_lang = src_lang
        
        # Tokenize
        tokens = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(text))
        
        # Translate
        results = self.translator.translate_batch([tokens], target_prefix=[[tgt_lang]])
        target_tokens = results[0].hypotheses[0]
        
        # Cleanup language tags
        if tgt_lang in target_tokens:
            target_tokens.remove(tgt_lang)
            
        return self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(target_tokens))