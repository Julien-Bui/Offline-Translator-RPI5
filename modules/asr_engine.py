import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from scipy.signal import resample
import os



class VoiceRecognizer:
    def __init__(self, model_size="base"):
        
        self.model = WhisperModel(model_size, device="cpu", compute_type="float32")
        
        # Astuce : on s'adapte aux micros standards pour ensuite lui parler dans sa langue (16000Hz)
        self.hardware_sample_rate = 44100  # Fréquence standard acceptée par 99% des micros USB
        self.whisper_sample_rate = 16000   # Fréquence exigée par l'IA
        print("✅ Le cerveau vocal est bien éveillé et prêt à écouter.")

    def listen_and_transcribe(self, duration=4, language="fr"):
        
        try:
            # Enregistrement à la fréquence native du micro
            audio_data = sd.rec(
                int(duration * self.hardware_sample_rate), 
                samplerate=self.hardware_sample_rate, 
                channels=1, 
                dtype='float32'
            )
            sd.wait()
        except Exception as e:
            
            # Plan B : le micro est peut-être capricieux et ne jure que par le 48kHz
            self.hardware_sample_rate = 48000
            audio_data = sd.rec(
                int(duration * self.hardware_sample_rate), 
                samplerate=self.hardware_sample_rate, 
                channels=1, 
                dtype='float32'
            )
            sd.wait()

        audio_flat = audio_data.flatten()
        
        # On remodèle le son pour que l'IA le comprenne bien sans effort
        
        num_samples = int(len(audio_flat) * self.whisper_sample_rate / self.hardware_sample_rate)
        audio_resampled = resample(audio_flat, num_samples).astype(np.float32)
        
        
        segments, info = self.model.transcribe(audio_resampled, language=language, beam_size=5)
        
        text_result = "".join([segment.text for segment in segments])
        return text_result.strip()

if __name__ == "__main__":
    recognizer = VoiceRecognizer(model_size="tiny")
    print("Allez-y, dites-moi quelques mots en français...")
    texte = recognizer.listen_and_transcribe(duration=4, language="fr")
    print(f"\n[Je crois avoir entendu] : {texte}")
