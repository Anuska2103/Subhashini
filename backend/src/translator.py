import ctranslate2
import transformers

class TranslatorEngine:
    def __init__(self, model_path="nllb-200-distilled-600M-int8"):
        self.translator = ctranslate2.Translator(model_path, device="cpu")
        self.tokenizer = transformers.AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")

    def translate(self, text, src_lang="eng_Latn", tgt_lang="hin_Deva"):
        if not text: return ""
        
        # Tokenize with NLLB specific source language
        self.tokenizer.src_lang = src_lang
        tokens = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(text))
        
        # Translate with target prefix
        results = self.translator.translate_batch([tokens], target_prefix=[[tgt_lang]])
        target_tokens = results[0].hypotheses[0]
        
        # Clean up and decode (removing the language tag from output)
        if tgt_lang in target_tokens: target_tokens.remove(tgt_lang)
        return self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(target_tokens))