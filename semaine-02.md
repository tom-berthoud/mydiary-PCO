# Semaine 02 — 2026-02-24

## [linux] Linux et la base de la programmation système

### Fichiers de base

- `home` : Contient les répertoires personnels des utilisateurs.
- `root` : Répertoire utilisateur du super-utilisateur (admin).
- `sys` : Contient des fichiers système propres au noyau et aux périphériques.
- `var` : Contient les données variables, comme les logs et les fichiers temporaires.
- `tmp` : Données temporaires
- `bin` : Programmes globaux
- `sbin` : Programmes système
- `dev` : Contient les fichiers de périphériques
- `proc` : Informations sur les processus en cours d'exécution
- `usr` : Contient la majorité des programmes et bibliothèques utilisateur.
- `etc` : Contient les fichiers de configuration du système
- `mnt` : Point de montage pour les systèmes de fichiers temporaires
- `media` : Point de montage pour les médias amovibles

Tout est un fichier sous Linux, même les périphériques et les processus sont représentés comme des fichiers dans le système de fichiers. Cela permet une grande flexibilité et une facilité d'accès aux ressources du système.

### Terminal

Pour écrire sur un autre terminal, on peut utiliser la commande `echo` suivie du message à afficher et du chemin du terminal cible. Par exemple, pour écrire "Hello, World!" sur le terminal `/dev/pts/1`, on peut utiliser la commande suivante :

```bash
echo "Hello, World!" > /dev/pts/1
```
