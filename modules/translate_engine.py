from transformers import MarianMTModel, MarianTokenizer
import os



class LocalTranslator:
    def __init__(self):
        
        # On va utiliser les excellents modèles hors-ligne d'Hugging Face
        self.model_fr_en_name = "Helsinki-NLP/opus-mt-fr-en"
        self.model_en_fr_name = "Helsinki-NLP/opus-mt-en-fr"
        
        self.models = {}
        self.tokenizers = {}
        
        # On précharge tout en mémoire (merci les 8 Go de RAM du Pi !)
        self.load_model("fr", "en", self.model_fr_en_name)
        self.load_model("en", "fr", self.model_en_fr_name)
        print("✅ Le cerveau bilingue est prêt à traduire.")

    def load_model(self, from_lang, to_lang, model_name):
        print(f"Ouverture du manuel de traduction : {from_lang.upper()} vers {to_lang.upper()}...")
        # Téléchargement au premier lancement, puis chargement direct depuis le disque
        self.tokenizers[f"{from_lang}_{to_lang}"] = MarianTokenizer.from_pretrained(model_name)
        self.models[f"{from_lang}_{to_lang}"] = MarianMTModel.from_pretrained(model_name)

    def translate(self, text, from_lang="fr", to_lang="en"):
        """Prend une phrase et la transforme dans l'autre langue, le tout sans internet"""
        if not text.strip():
            return ""
        
        key = f"{from_lang}_{to_lang}"
        if key not in self.models:
            return f"Oups, je n'ai pas le dictionnaire pour traduire de {from_lang} vers {to_lang}."
            
        try:
            tokenizer = self.tokenizers[key]
            model = self.models[key]
            
            # On découpe la phrase en petits morceaux compréhensibles par la machine
            inputs = tokenizer(text, return_tensors="pt", padding=True)
            # L'IA fait sa magie de traduction
            translated_tokens = model.generate(**inputs)
            # Et on recolle les morceaux pour en faire une belle phrase lisible pour nous
            result = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
            return result
        except Exception as e:
            return f"Mon cerveau a fait un nœud pendant la traduction : {e}"

if __name__ == "__main__":
    # Un petit test pour s'assurer que notre ami polyglotte fonctionne bien seul
    translator = LocalTranslator()
    
    test_fr = "Bonjour, ce traducteur fonctionne entièrement sans connexion internet !"
    print(f"\n[FR] : {test_fr}")
    print(f"[EN] : {translator.translate(test_fr, 'fr', 'en')}")
    
    test_en = "This Raspberry Pi 5 with 8 gigabytes of RAM is extremely powerful."
    print(f"\n[EN] : {test_en}")
    print(f"[FR] : {translator.translate(test_en, 'en', 'fr')}")
