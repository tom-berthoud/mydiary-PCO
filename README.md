# Programmation Concurrente — Notes de cours

Notes hebdomadaires du cours de Programmation Concurrente (HEIG-VD, 2025-2026).

Les fichiers `semaine-*.md` contiennent les notes brutes. Le script `build.py` les regroupe par thème et génère un PDF via Pandoc + XeLaTeX.

## PDF généré automatiquement

Le PDF est publié à chaque push sur `main` via GitHub Actions + GitHub Pages :

- [Ouvrir la dernière version du PDF](https://tomb.github.io/mydiary/notes_progconcur.pdf)

## Générer le PDF

```bash
make pdf
```

### Dépendances

- Python 3 avec `pyyaml`
- Pandoc
- XeLaTeX (fourni par `texlive-xetex`)
- Paquets LaTeX : `tcolorbox`, `fancyhdr`, `booktabs`

### Autres commandes

```bash
make new WEEK=02   # Créer un nouveau fichier de semaine
make clean         # Supprimer le PDF généré
make help          # Aide
```

## Structure

```
semaine-*.md     Notes hebdomadaires (sections taguées par thème)
themes.yaml      Définition et ordre des thèmes
metadata.yaml    Métadonnées LaTeX/Pandoc
build.py         Script de génération
```

Chaque section dans un fichier de semaine est taguée avec `## [theme] Titre`, où `theme` correspond à un identifiant défini dans `themes.yaml`.
