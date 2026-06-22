import os
import subprocess
from piper import PiperVoice

class VoiceGenerator:
    def __init__(self):
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models_tts")
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.voices = {
            "fr": os.path.join(self.model_dir, "fr_FR-upmc-medium.onnx"),
            "en": os.path.join(self.model_dir, "en_US-lessac-medium.onnx")
        }
        
        # Petit repère pour trouver ton haut-parleur USB (souvent la carte numéro 2)
        self.alsa_device = "hw:2,0" 
        
        self.download_voices_if_needed()
        self.loaded_voices = {}
        self.load_voices()

    def download_voices_if_needed(self):
        urls = {
            "fr": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx",
            "fr_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json",
            "en": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
            "en_config": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
        }
        
        for lang, path in self.voices.items():
            if not os.path.exists(path):
                os.system(f"wget -O {path} {urls[lang]}")
                os.system(f"wget -O {path}.json {urls[lang+'_config']}")

    def load_voices(self):
        for lang, path in self.voices.items():
            config_path = path + ".json"
            self.loaded_voices[lang] = PiperVoice.load(path, config_path)
        print("✅ Cordes vocales prêtes à vibrer.")

    def speak(self, text, language="fr"):
        if not text.strip():
            return

        voice = self.loaded_voices.get(language)
        if not voice:
            return

        try:
            # Étape 1 : On demande à Piper de générer le son brut
            raw_data = b""
            for chunk in voice.synthesize(text):
                if isinstance(chunk, bytes):
                    raw_data += chunk
                elif isinstance(chunk, tuple) or isinstance(chunk, list):
                    raw_data += chunk[0]
                elif hasattr(chunk, 'audio_data'):
                    raw_data += chunk.audio_data
                elif hasattr(chunk, 'audio'):
                    raw_data += chunk.audio
                elif hasattr(chunk, 'wave_data'):
                    raw_data += chunk.wave_data
                else:
                    for attr in dir(chunk):
                        if not attr.startswith('__'):
                            val = getattr(chunk, attr)
                            if isinstance(val, bytes):
                                raw_data += val
                                break

            if not raw_data:
                return

            # Étape 2 : On garde ça au chaud dans la mémoire temporaire (/tmp)
            temp_raw = "/tmp/output.raw"
            with open(temp_raw, "wb") as f:
                f.write(raw_data)
            
            # Étape 3 : On donne le son au haut-parleur USB pour qu'il le diffuse
            # L'option -D plughw:2,0 pointe vers ton haut-parleur
            # Et on lui laisse faire le reste du travail d'adaptation
            cmd = f"aplay -D plughw:2,0 -r {voice.config.sample_rate} -f S16_LE -c 1 {temp_raw}"
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
        except Exception as e:
            print(f"J'ai eu un chat dans la gorge pendant que je parlais : {e}")

if __name__ == "__main__":
    generator = VoiceGenerator()
    generator.speak("Bonjour Julien, ton haut parleur fonctionne correctement.", "fr")
