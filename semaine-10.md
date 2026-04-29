# Semaine 10 — 2026-04-28

## [docker] Utilisation de Docker pour le développement

Après avoir vu les mécanismes bas niveau (`chroot`, namespaces, cgroups, OverlayFS), Docker fournit une interface plus simple pour les utiliser au quotidien. On ne manipule plus directement les namespaces : on décrit une image, puis on lance des conteneurs à partir de cette image.

Le cycle de base est toujours le même :

```bash
docker build -t mon-image .
docker run --rm -it mon-image
```

`docker build` construit une **image** à partir d'un `Dockerfile`. L'image est le modèle en lecture seule : elle contient le système de fichiers de base, les dépendances et la commande de démarrage. `docker run` crée un **conteneur**, c'est-à-dire une instance isolée de cette image avec sa propre couche d'écriture.

Options fréquentes :

| Option | Rôle |
|:----|:-------------|
| `--rm` | supprime le conteneur quand la commande se termine |
| `-it` | lance un terminal interactif |
| `-v "$PWD":/work` | monte le dossier courant dans le conteneur |
| `-p 8080:80` | expose le port `80` du conteneur sur le port `8080` de l'hôte |

Pour observer ce qui tourne :

```bash
docker ps
docker logs <conteneur>
docker exec -it <conteneur> bash
```

### Images, conteneurs et Compose

Une **image** est un modèle immuable. Elle est construite une fois, puis réutilisée pour créer un ou plusieurs conteneurs. Un **conteneur** est une exécution concrète de cette image : il a un état, peut être démarré, arrêté, supprimé, et possède sa propre couche d'écriture.

Commandes utiles pour inspecter l'état local :

| Commande | Rôle |
|:----|:-------------|
| `docker image ls` | liste les images présentes sur la machine |
| `docker ps` | liste les conteneurs en cours d'exécution |
| `docker ps -a` | liste aussi les conteneurs arrêtés |
| `docker inspect <nom-ou-id>` | affiche la configuration détaillée d'une image ou d'un conteneur |
| `docker rm <conteneur>` | supprime un conteneur arrêté |
| `docker rmi <image>` | supprime une image inutilisée |

Docker Compose sert à décrire plusieurs conteneurs dans un fichier `compose.yaml` ou `docker-compose.yml`. Au lieu de lancer chaque conteneur à la main avec une longue commande `docker run`, on décrit les services, leurs ports, volumes et variables d'environnement dans un fichier.

Exemple minimal :

```yaml
services:
  app:
    image: nginx
    ports:
      - "8080:80"
```

Les commandes principales sont :

```bash
docker compose up
docker compose up -d
docker compose ps
docker compose logs
docker compose down
```

`docker compose up` crée et démarre les conteneurs décrits dans le fichier. L'option `-d` les lance en arrière-plan. `docker compose down` arrête les services et supprime les conteneurs créés par Compose, mais ne supprime pas automatiquement les images.

La différence importante avec une machine virtuelle est que le conteneur ne démarre pas un nouveau noyau. Il reste un processus Linux de l'hôte, isolé par les mécanismes vus précédemment.

## [cache] Mémoire cache

### Hiérarchie L1/L2/L3 et RAM

Le cache est une mémoire rapide située entre le processeur et la mémoire principale (RAM). Il est organisé en plusieurs niveaux (L1, L2, L3) avec des tailles et des vitesses différentes. Le cache stocke les données et instructions les plus fréquemment utilisées pour réduire le temps d'accès.

Plus on s'éloigne de l'ALU, plus la mémoire est grande mais lente. Les niveaux L1 et L2 sont privés à chaque cœur, alors que L3 est partagé entre les cœurs et sert de tampon avant la RAM.

```{=latex}
\begin{center}
\begin{tikzpicture}[
  alu/.style={rectangle, draw, thick, minimum width=1.2cm, minimum height=1.4cm, fill=green!20, font=\small\bfseries, align=center},
  l1/.style={rectangle, draw, thick, minimum width=1.5cm, minimum height=0.55cm, fill=blue!30, font=\scriptsize, align=center},
  l2/.style={rectangle, draw, thick, minimum width=1.3cm, minimum height=1.4cm, fill=blue!12, font=\small\bfseries, align=center},
  l3/.style={rectangle, draw, thick, minimum width=1.5cm, minimum height=4.4cm, fill=orange!30, font=\small\bfseries, align=center},
  ram/.style={rectangle, draw, thick, minimum width=1.8cm, minimum height=2cm, fill=red!25, font=\small\bfseries, align=center},
  link/.style={<->, thick},
  >=Latex
]
  % Coeur 1
  \node[alu] (alu1) at (0, 2)    {ALU};
  \node[l1]  (l1d1) at (2, 2.5)  {L1 Données};
  \node[l1]  (l1i1) at (2, 1.5)  {L1 Instr.};
  \node[l2]  (l21)  at (4, 2)    {Cache\\L2};
  % Coeur 2
  \node[alu] (alu2) at (0, -2)   {ALU};
  \node[l1]  (l1d2) at (2, -1.5) {L1 Données};
  \node[l1]  (l1i2) at (2, -2.5) {L1 Instr.};
  \node[l2]  (l22)  at (4, -2)   {Cache\\L2};
  % L3 partagé et RAM
  \node[l3]  (l3)  at (6,   0)   {Cache\\L3};
  \node[ram] (ram) at (8.5, 0)   {RAM};
  % Connexions coeur 1
  \draw[link] (alu1.east) -- (l1d1.west);
  \draw[link] (alu1.east) -- (l1i1.west);
  \draw[link] (l1d1.east) -- (l21.west |- l1d1);
  \draw[link] (l1i1.east) -- (l21.west |- l1i1);
  % Connexions coeur 2
  \draw[link] (alu2.east) -- (l1d2.west);
  \draw[link] (alu2.east) -- (l1i2.west);
  \draw[link] (l1d2.east) -- (l22.west |- l1d2);
  \draw[link] (l1i2.east) -- (l22.west |- l1i2);
  % L2 vers L3
  \draw[link] (l21.east) -- (l3.west |- l21);
  \draw[link] (l22.east) -- (l3.west |- l22);
  % L3 vers RAM
  \draw[link] (l3.east) -- (ram.west);
  % Cadre processeur
  \node[draw=red, thick, dashed, rounded corners, inner sep=8pt,
        fit=(alu1)(l1i1)(l21)(alu2)(l1i2)(l22)] (proc) {};
  \node[red, font=\bfseries\small, anchor=south west]
    at ([xshift=4pt]proc.north west) {Processeur};
  % Flèche d'accès lent vers RAM
  \draw[->, red, thick] ([xshift=-1.2cm]proc.north east)
    to[bend left=30]
    node[midway, above, right, font=\small\bfseries] {Tps d'accès trop long !}
    (ram.north);
  % Accolades sous chaque niveau
  \draw[-, decorate, decoration={brace, amplitude=5pt, mirror}, gray]
    (1.2, -3.45) -- (2.8, -3.45)
    node[midway, below=6pt, font=\scriptsize, gray, align=center]
      {\textbf{L1}\\$\sim$1 ns, 32 KB};
  \draw[-, decorate, decoration={brace, amplitude=5pt, mirror}, gray]
    (3.3, -3.45) -- (4.7, -3.45)
    node[midway, below=6pt, font=\scriptsize, gray, align=center]
      {\textbf{L2}\\$\sim$3 ns, 256 KB};
  \draw[-, decorate, decoration={brace, amplitude=5pt, mirror}, gray]
    (5.2, -3.45) -- (6.8, -3.45)
    node[midway, below=6pt, font=\scriptsize, gray, align=center]
      {\textbf{L3}\\$\sim$10 ns, 8 MB};
  \draw[-, decorate, decoration={brace, amplitude=5pt, mirror}, gray]
    (7.5, -3.45) -- (9.5, -3.45)
    node[midway, below=6pt, font=\scriptsize, gray, align=center]
      {\textbf{RAM}\\$\sim$100 ns, 16 GB};
\end{tikzpicture}
\end{center}
```

Deux choses à retenir :

- **Fréquence CPU.** Quand on dit "CPU 4 GHz", c'est la fréquence de l'ALU et des caches L1/L2 — pas celle de L3 ni de la RAM, qui tournent plus lentement.
- **Coût.** Le cache coûte beaucoup plus cher (par octet) que la RAM. C'est pour ça qu'on en met peu, en hiérarchie : un L1 minuscule mais ultra-rapide près de l'ALU, puis L2/L3 progressivement plus gros et plus lents.
