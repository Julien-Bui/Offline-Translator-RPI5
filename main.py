import customtkinter as ctk
import threading
import sys
import os

# On s'assure de bien trouver nos propres modules locaux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# On importe les trois cerveaux de notre traducteur (les oreilles, le cerveau, et la bouche)
from modules.asr_engine import VoiceRecognizer
from modules.translate_engine import LocalTranslator
from modules.tts_engine import VoiceGenerator

print("Démarrage du traducteur de poche. Réveil des modules en cours...")

class TraducteurPocheApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.deactivate_automatic_dpi_awareness()
        
        self.title("Traducteur de Poche IA")
        self.geometry("800x480") 
        
        self.init_ui()
        
        # On charge tout ça en arrière-plan pour que l'interface reste fluide
        threading.Thread(target=self.charger_moteurs_ia, daemon=True).start()
        
    def charger_moteurs_ia(self):
        self.lbl_source.configure(text="Les IA se chargent en mémoire, un petit instant...", text_color="#ffb703")
        
        # Mise en place des 3 composants clés
        self.asr = VoiceRecognizer(model_size="tiny")
        self.translator = LocalTranslator()
        self.tts = VoiceGenerator()
        
        self.lbl_source.configure(text=" Tout est prêt ! Touchez un bouton et parlez.", text_color="#aaaaaa")

    def init_ui(self):
        # Section supérieure : ce que l'utilisateur dit
        self.frame_source = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.frame_source.pack(fill="both", expand=True)
        
        self.lbl_source = ctk.CTkLabel(
            self.frame_source, 
            text="Lancement en cours...", 
            font=("Arial", 20), 
            wraplength=700,
            text_color="#aaaaaa"
        )
        self.lbl_source.pack(expand=True, padx=20, pady=20)
        
        # Section inférieure : le résultat traduit
        self.frame_trad = ctk.CTkFrame(self, fg_color="#111111", corner_radius=0)
        self.frame_trad.pack(fill="both", expand=True)
        
        self.lbl_trad = ctk.CTkLabel(
            self.frame_trad, 
            text="", 
            font=("Arial", 24, "bold"), 
            wraplength=700,
            text_color="#3a86ff"
        )
        self.lbl_trad.pack(expand=True, padx=20, pady=20)
        
        # Les gros boutons pour lancer la traduction
        self.frame_boutons = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_boutons.pack(side="bottom", fill="x", pady=20)
        
        self.btn_fr = ctk.CTkButton(
            self.frame_boutons, 
            text="Français", 
            font=("Arial", 18, "bold"),
            height=65,
            width=240,
            corner_radius=12,
            command=lambda: self.action_micro("fr")
        )
        self.btn_fr.pack(side="left", padx=30, expand=True)
        
        self.btn_en = ctk.CTkButton(
            self.frame_boutons, 
            text="English", 
            font=("Arial", 18, "bold"),
            height=65,
            width=240,
            fg_color="#2a9d8f",
            hover_color="#21867a",
            corner_radius=12,
            command=lambda: self.action_micro("en")
        )
        self.btn_en.pack(side="right", padx=30, expand=True)

    def action_micro(self, langue):
        if langue == "fr":
            self.lbl_source.configure(text="Écoute du Français... Parlez maintenant pendant 4s.", text_color="#3a86ff")
        else:
            self.lbl_source.configure(text="Listening to English... Speak now for 4s.", text_color="#2a9d8f")
            
        self.lbl_trad.configure(text="")
        
        # On délègue tout le travail à un arrière-plan pour que l'appli ne gèle pas
        threading.Thread(target=self.run_pipeline_ia, args=(langue,), daemon=True).start()

    def run_pipeline_ia(self, langue_source):
        try:
            # Étape 1 : On ouvre grand nos oreilles (le micro)
            texte_detecte = self.asr.listen_and_transcribe(duration=4, language=langue_source)
            
            if not texte_detecte:
                self.lbl_source.configure(text="Je n'ai rien entendu. On recommence ?", text_color="#e63946")
                return
                
            self.lbl_source.configure(text=texte_detecte, text_color="#ffffff")
            
            # Étape 2 : On réfléchit pour traduire la phrase
            langue_cible = "en" if langue_source == "fr" else "fr"
            
            texte_traduit = self.translator.translate(texte_detecte, from_lang=langue_source, to_lang=langue_cible)
            
            
            # Étape 3 : On affiche le résultat pour l'utilisateur
            self.lbl_trad.configure(text=texte_traduit)
            
            # Étape 4 : Et on le prononce à voix haute !
            self.tts.speak(texte_traduit, language=langue_cible)
            
        except Exception as e:
            
            self.lbl_source.configure(text=f"Oups, un petit souci technique : {e}", text_color="#e63946")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = TraducteurPocheApp()
    app.mainloop()
