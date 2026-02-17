#!/usr/bin/env python3
"""
Regroupe les notes hebdomadaires par thème pour générer un PDF.

Lit les fichiers semaine-*.md, extrait les sections taguées [theme],
et produit un fichier Markdown combiné organisé par thème.
"""

import glob
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
THEMES_FILE = SCRIPT_DIR / "themes.yaml"
METADATA_FILE = SCRIPT_DIR / "metadata.yaml"
OUTPUT_PDF = SCRIPT_DIR / "notes_progconcur.pdf"

# Regex pour capturer ## [tag] Titre
SECTION_RE = re.compile(r"^## \[(\S+)\]\s+(.+)$")


def load_themes():
    with open(THEMES_FILE, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["themes"]


def parse_week_file(filepath):
    """Parse un fichier semaine et retourne les sections taguées.

    Retourne une liste de dicts:
      {tag, title, content, week_num, week_title, filepath}
    """
    path = Path(filepath)
    # Extraire le numéro de semaine du nom de fichier
    match = re.search(r"semaine-(\d+)", path.stem)
    week_num = int(match.group(1)) if match else 0

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    # Trouver le titre de la semaine (H1)
    week_title = ""
    for line in lines:
        if line.startswith("# "):
            week_title = line.strip("# \n")
            break

    sections = []
    current_tag = None
    current_title = None
    current_lines = []

    for line in lines:
        m = SECTION_RE.match(line.rstrip())
        if m:
            # Sauvegarder la section précédente
            if current_tag:
                sections.append({
                    "tag": current_tag,
                    "title": current_title,
                    "content": "".join(current_lines).strip(),
                    "week_num": week_num,
                    "week_title": week_title,
                    "filepath": str(path),
                })
            current_tag = m.group(1)
            current_title = m.group(2)
            current_lines = []
        elif current_tag:
            current_lines.append(line)

    # Dernière section
    if current_tag:
        sections.append({
            "tag": current_tag,
            "title": current_title,
            "content": "".join(current_lines).strip(),
            "week_num": week_num,
            "week_title": week_title,
            "filepath": str(path),
        })

    return sections


def build_combined_markdown(themes, all_sections):
    """Construit le Markdown combiné organisé par thème."""
    output = []

    for theme in themes:
        tid = theme["id"]
        title = theme["title"]

        # Filtrer et trier les sections pour ce thème
        theme_sections = [s for s in all_sections if s["tag"] == tid]
        theme_sections.sort(key=lambda s: s["week_num"])

        if not theme_sections:
            continue

        output.append(f"# {title}\n")

        for section in theme_sections:
            output.append(f"## {section['title']}")
            output.append(f"*Semaine {section['week_num']}*\n")
            output.append(section["content"])
            output.append("")  # ligne vide

        output.append("")  # séparation entre thèmes

    return "\n".join(output)


def main():
    # Charger les thèmes
    themes = load_themes()

    # Trouver et parser tous les fichiers de semaine
    week_files = sorted(glob.glob(str(SCRIPT_DIR / "semaine-*.md")))
    if not week_files:
        print("Aucun fichier semaine-*.md trouvé.", file=sys.stderr)
        sys.exit(1)

    all_sections = []
    for wf in week_files:
        all_sections.extend(parse_week_file(wf))

    if not all_sections:
        print("Aucune section taguée trouvée dans les fichiers.", file=sys.stderr)
        sys.exit(1)

    # Vérifier les tags inconnus
    known_tags = {t["id"] for t in themes}
    unknown_tags = {s["tag"] for s in all_sections} - known_tags
    if unknown_tags:
        print(f"Tags inconnus (non définis dans themes.yaml): {unknown_tags}",
              file=sys.stderr)
        print("Ces sections seront ignorées dans le PDF.", file=sys.stderr)

    # Construire le Markdown combiné
    combined = build_combined_markdown(themes, all_sections)

    # Lire le metadata et l'intégrer comme en-tête YAML du markdown
    with open(METADATA_FILE, encoding="utf-8") as f:
        metadata_content = f.read().strip()

    full_content = f"---\n{metadata_content}\n---\n\n{combined}"

    # Écrire dans un fichier temporaire et appeler Pandoc
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(full_content)
        tmp_path = tmp.name

    try:
        cmd = [
            "pandoc",
            tmp_path,
            "-o", str(OUTPUT_PDF),
            "--pdf-engine=xelatex",
            "--highlight-style=tango",
        ]
        print(f"Génération du PDF: {OUTPUT_PDF}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Erreur Pandoc:\n{result.stderr}", file=sys.stderr)
            sys.exit(1)
        print("PDF généré avec succès.")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
