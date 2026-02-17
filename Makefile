.PHONY: pdf clean new help

pdf:
	python3 build.py

clean:
	rm -f notes_progconcur.pdf

# Crée un nouveau fichier de semaine. Usage: make new WEEK=02
new:
	@if [ -z "$(WEEK)" ]; then \
		echo "Usage: make new WEEK=02"; \
		exit 1; \
	fi
	@if [ -f "semaine-$(WEEK).md" ]; then \
		echo "semaine-$(WEEK).md existe déjà"; \
		exit 1; \
	fi
	@echo "# Semaine $(WEEK) — $$(date +%Y-%m-%d)\n" > "semaine-$(WEEK).md"
	@echo "## [theme] Titre de la section\n" >> "semaine-$(WEEK).md"
	@echo "Notes ici...\n" >> "semaine-$(WEEK).md"
	@echo "Créé: semaine-$(WEEK).md"

help:
	@echo "Commandes disponibles:"
	@echo "  make pdf          Génère notes_progconcur.pdf (notes regroupées par thème)"
	@echo "  make clean        Supprime le PDF généré"
	@echo "  make new WEEK=XX  Crée un nouveau fichier semaine-XX.md"
	@echo "  make help         Affiche cette aide"
