import speech_recognition as sr
from translate import Translator

# Initialiser le morceau de code qui reconnaît la voix
r = sr.Recognizer()



traducteur = Translator(from_lang="fr", to_lang="en")

with sr.Microphone(device_index=1) as source:
    print("\n[INFO] Ajustement pour le bruit ambiant... Ne parlez pas pendant 2 secondes.")
    r.adjust_for_ambient_noise(source, duration=2)

    print("\n[PRÊT] Je vous écoute... Parlez maintenant !")
    audio = r.listen(source)

try:
    print("\n[IA] Analyse de la voix en cours...")
    # On utilise le moteur de reconnaissance en spécifiant la langue française
    texte = r.recognize_google(audio, language="fr-FR")


    print(f"\n[RÉSULTAT] Vous avez dit : \"{texte}\"")

    print("[IA] Traduction en cours...")
    traduction = traducteur.translate(texte)
    print(f"[TRADUCTION] Anglais : \"{traduction}\"\n")

except sr.UnknownValueError:
    print("\n[ERREUR] L'IA n'a pas compris ce que vous avez dit.")
except sr.RequestError:
    print("\n[ERREUR] Impossible de contacter le moteur de reconnaissance (problème internet).")
