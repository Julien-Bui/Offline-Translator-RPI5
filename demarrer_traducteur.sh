#!/bin/bash
# Attendre 2 secondes que le système graphique soit totalement stable
sleep 2

# Se placer dans le bon dossier
cd "$(dirname "$0")"

# Lancer l'application avec le Python de l'environnement virtuel
./venv/bin/python main.py
