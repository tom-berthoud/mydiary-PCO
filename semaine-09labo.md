# Semaine 09 — 2026-04-21

## [docker] Docker c'est quoi ?

Docker est une plateforme de conteneurisation qui permet d'exécuter des applications dans des environnements isolés et portables.

**En une phrase** : un conteneur Linux n'est rien d'autre qu'un processus (ou groupe de processus) lancé avec une vue restreinte du système : un système de fichiers à lui (`chroot`), ses propres PIDs/réseau/hostname (`namespaces`), et une limite sur les ressources qu'il peut consommer (`cgroups`). Docker n'est qu'un outil qui automatise tout ça.

Les quatre briques noyau utilisées :

| Brique | Année | Rôle |
|:------------|:----------|:-----------------------------------------------------------|
| `chroot` | 1979 | Isole le système de fichiers vu par le processus |
| `namespaces` | 2002–2008 | Isolent PIDs, réseau, hostname, IPC, mounts, users |
| `cgroups` | 2007 | Limitent les ressources (CPU, mémoire, PIDs, I/O) |
| `OverlayFS` | 2014 | Couches de FS en copy-on-write (images Docker) |

### L'isolation

La conteneurisation cherche à isoler un programme du reste du système. On distingue plusieurs **niveaux** d'isolation, et chacun s'appuie sur un mécanisme noyau différent :

| Niveau | Mécanisme | Sans conteneur ? |
|:-----------------------|:---------------------------------------------|:----------------|
| Mémoire | MMU + espace d'adressage virtuel | **Oui**, natif |
| Utilisateur | UID/GID + permissions FS | **Oui**, natif |
| Système de fichiers | `chroot` / `pivot_root` + mount namespace | Non |
| Processus (PIDs) | PID namespace | Non |
| Réseau | NET namespace + `veth` + NAT | Non |
| Hostname / IPC | UTS namespace, IPC namespace | Non |
| Ressources (CPU, RAM) | cgroups | Non |
| Environnement | variables d'environnement, FS isolé | Non |

L'idée importante : un processus Linux **standard** est déjà isolé en mémoire et par utilisateur (la MMU empêche l'accès à la mémoire d'autres processus, les permissions empêchent un user de lire les fichiers d'un autre). Tout le reste (PIDs, réseau, FS, ressources) demande des mécanismes supplémentaires que Docker active automatiquement.

### Le rootfs (debootstrap)

Pour isoler le système de fichiers, il faut d'abord en construire un. `debootstrap` télécharge depuis les dépôts Debian/Ubuntu un système racine **minimal** (`bash`, `ls`, `apt`, `python3`…) dans un dossier choisi. Ce dossier ressemble à `/` d'un vrai Linux : `bin/`, `etc/`, `usr/`, `var/`…

La vérification GPG des paquets est essentielle : sans elle, un attaquant en *man-in-the-middle* pourrait injecter du code malveillant dans l'image de base — c'est exactement la même logique que `apt-get` sur l'hôte.

Tant qu'on n'a fait que `debootstrap`, **le rootfs n'est qu'un dossier**. Aucune isolation : un processus root peut écrire dedans librement.

Deux dossiers spéciaux dans tout système Linux :

- `/dev` contient des fichiers spéciaux qui représentent les périphériques (`/dev/null`, `/dev/sda`, `/dev/tty`). Linux les expose comme des fichiers via le filesystem virtuel `devtmpfs`.
- `/etc` contient les **fichiers de configuration** texte du système (`/etc/passwd`, `/etc/hostname`, `/etc/resolv.conf`).

### chroot

`chroot` (*change root*) est un appel système qui modifie ce que **le noyau considère comme `/`** pour un processus et ses enfants. Quand le programme appelle `open("/etc/passwd")`, le noyau résout le chemin à partir de la nouvelle racine, pas de la vraie. Les chemins absolus deviennent donc relatifs au dossier choisi.

**Limites importantes** :

- `chroot` n'isole **que** le système de fichiers. Les PIDs, le réseau, les utilisateurs, les ressources : rien n'est isolé.
- Depuis l'intérieur, `ps -ax` voit toujours **tous** les processus de l'hôte (parce que `/proc` n'est pas isolé non plus si on le monte dans le conteneur).
- Un root dans un chroot peut s'évader : `chroot` n'est pas une frontière de sécurité réelle.

C'est pour ça qu'on combine `chroot` avec `unshare`.

### mount

`mount` attache un système de fichiers (une partition de disque, une image, un FS virtuel) à un **point de montage**, c'est-à-dire un dossier déjà présent. Une fois monté, le contenu original du dossier est **masqué** par le nouveau FS jusqu'au `umount` (les fichiers cachés ne sont pas perdus, juste invisibles le temps du montage).

Sous Linux, beaucoup de choses sont en réalité des FS *virtuels* présentés à travers `mount` :

| Point | Type | Contenu |
|:--------|:----------------|:----------------------------------------------------------|
| `/proc` | `procfs` | Vue noyau des processus en cours (`/proc/<pid>/...`) |
| `/sys` | `sysfs` | Vue noyau du matériel et des cgroups |
| `/dev` | `devtmpfs` | Fichiers de périphériques |
| `/` | `ext4`, `btrfs`… | Le vrai disque |

Ce mécanisme est utilisé par les conteneurs pour **monter `/proc` à l'intérieur** : sans ça, `ps`, `top`, `cat /proc/self/...` ne fonctionnent pas. C'est aussi le mécanisme qui rend OverlayFS possible (cf. plus bas).

### Namespaces (unshare)

Un *namespace* est un mécanisme noyau qui partitionne une ressource système en "vues" indépendantes. Chaque processus appartient à exactement un namespace de chaque type. La syscall `unshare` (et `clone` avec `CLONE_NEW*`) crée de nouveaux namespaces et y place le processus.

Linux définit **7 types** de namespaces :

| Namespace | Option `unshare` | Ce qu'il isole |
|:----------|:------------------|:----------------------------------------------------------|
| PID | `--pid` | Numérotation des processus (le PID 1 du conteneur n'est pas le PID 1 de l'hôte) |
| NET | `--net` | Interfaces réseau, table de routage, iptables |
| MNT | `--mount` | Points de montage (chaque conteneur peut monter ses propres FS) |
| UTS | `--uts` | Hostname et domainname |
| IPC | `--ipc` | Files de messages, sémaphores SysV, mémoire partagée |
| USER | `--user` | UID/GID (root dans le conteneur ≠ root sur l'hôte) |
| CGROUP | `--cgroup` | Vue de la hiérarchie cgroup |

La commande qui monte un mini-conteneur isolé combine `unshare` (pour les namespaces) et `chroot` (pour le FS) :

```bash
sudo unshare --fork --pid --mount --uts --ipc --net --cgroup --mount-proc \
    chroot "$ROOTFS" /bin/bash
```

Une fois dedans, `ps -ax` ne voit plus que les processus du conteneur, `ip a` ne voit que `lo`, `hostname X` ne change que dans le conteneur.

### Réseau du conteneur

Après `unshare --net`, le conteneur a son propre namespace réseau, mais **vide** : seule l'interface `lo` existe. Pour le brancher sur Internet, on construit à la main ce que Docker fait avec `docker0`.

Architecture cible :

```{=latex}

\begin{tikzpicture}[
  >=Latex,
  every node/.style={font=\small},
  ns/.style={draw, rounded corners=3pt, dashed, inner sep=0.35cm},
  box/.style={draw, rounded corners=6pt, minimum height=1.15cm, minimum width=3.0cm, align=center},
  iface/.style={font=\footnotesize\ttfamily},
  note/.style={font=\footnotesize, align=center}
]
  \node[box, fill=blue!12, draw=blue!55, xshift=-1.8cm] (cont) {\textbf{Conteneur}\\
    \texttt{veth1}\\
    \texttt{10.200.1.2/24}\\
    route: \texttt{default via 10.200.1.1}};

  \node[box, fill=green!12, draw=green!45!black, right=2.3cm of cont] (host) {\textbf{Hôte}\\
    \texttt{veth0}\\
    \texttt{10.200.1.1/24}\\
    \texttt{ip\_forward=1}};

  \node[box, fill=orange!20, draw=orange!60!black, right=2.3cm of host] (eth) {\textbf{Sortie hôte}\\
    \texttt{eth0}\\
    IP publique / LAN};

  \node[box, fill=gray!12, draw=gray!60, minimum width=2.0cm, right=1.6cm of eth] (net) {Internet};

  \node[ns, fit=(cont), label={[font=\footnotesize]above:namespace réseau du conteneur}] (contns) {};
  \node[ns, fit=(host)(eth), label={[font=\footnotesize]above:namespace réseau de l'hôte}] (hostns) {};

  \draw[<->, thick] (cont.east) -- node[above, note] {paire \texttt{veth}\\``câble'' virtuel} (host.west);
  \draw[->, thick] (host.east) -- node[above, note] {routage} node[below, note] {\texttt{veth0} $\rightarrow$ \texttt{eth0}} (eth.west);
  \draw[->, thick] (eth.east) -- (net.west);

  \draw[->, thick, orange!80!black]
    ([yshift=-0.45cm]cont.east) -- ([yshift=-0.45cm]host.west)
    node[midway, below, note] {src: \texttt{10.200.1.2}};
  \draw[->, thick, orange!80!black]
    ([yshift=-0.45cm]host.east) -- ([yshift=-0.45cm]eth.west)
    node[midway, below, note] {POSTROUTING};
  \draw[->, thick, orange!80!black]
    ([yshift=-0.45cm]eth.east) -- ([yshift=-0.45cm]net.west)
    node[yshift=-0.1cm,midway, below, note] {src devient IP de \texttt{eth0}};

  \node[note, fill=orange!10, draw=orange!55!black, rounded corners=4pt,
        below=0.65cm of eth, inner sep=3pt] (nat) {
    \texttt{iptables -t nat -A POSTROUTING -s 10.200.1.0/24 -o eth0 -j MASQUERADE}
  };
  \draw[->, orange!70!black] (nat.north) -- ([yshift=-0.55cm]eth.south);
\end{tikzpicture}

```

Six éléments à mettre en place pour donner Internet au conteneur :

| # | Élément | Rôle |
|:--|:-----------------------------------------------|:----------------------------------------------------------|
| 1 | Paire `veth` (`veth0`/`veth1`) | "câble" virtuel entre les deux namespaces |
| 2 | `veth1` déplacé dans le namespace conteneur | une extrémité chez chacun |
| 3 | Adresses IP `10.200.1.1` et `10.200.1.2` | même sous-réseau de chaque côté |
| 4 | Route par défaut vers l'hôte | `default via 10.200.1.1` côté conteneur |
| 5 | IP forwarding (`net.ipv4.ip_forward=1`) | l'hôte route les paquets de `veth0` vers `eth0` |
| 6 | NAT MASQUERADE (`iptables`) | réécrit l'IP source avec celle de l'hôte |

Sans (5) ou (6), `ping 8.8.8.8` depuis le conteneur échoue : les paquets sortent mais les réponses ne reviennent pas, l'extérieur ne connaît pas `10.200.1.2`. Métaphore du MASQUERADE : standard téléphonique d'entreprise — le poste interne `1234` est remplacé par le numéro public quand on appelle l'extérieur.

### Cgroups

Les *control groups* (cgroups) sont une hiérarchie noyau qui permet de **regrouper des processus et leur appliquer des limites de ressources**. Sans cgroups, un processus peut monopoliser le CPU, faire exploser la RAM, ou *fork-bomber* la machine.

Cgroups v2 (Ubuntu 22+, Fedora récent) unifie tout sous `/sys/fs/cgroup/`. Les contrôleurs disponibles sont listés dans `cgroup.controllers` :

| Contrôleur | Limite | Exemple |
|:------------|:-----------------------------|:---------------------------------------------|
| `cpu` | Temps CPU | `cpu.max = "12000 100000"` (12% d'un cœur) |
| `memory` | Mémoire | `memory.max = 256M` |
| `pids` | Nombre de processus | `pids.max = 42` |
| `io` | Bande passante disque | — |
| `cpuset` | Affinité CPU/NUMA | — |

Trois étapes obligatoires, dans cet ordre :

1. **Créer** le cgroup (`mkdir /sys/fs/cgroup/demo-ctr`).
2. **Activer** les contrôleurs au niveau parent (`echo "+cpu +memory +pids" > .../cgroup.subtree_control`). Sans ça, les écritures dans `cpu.max` et compagnie n'ont **aucun effet** (elles sont silencieusement ignorées).
3. **Attacher** le processus (`echo $PID > .../cgroup.procs`). Sans ça, le processus n'est soumis à aucune des limites posées.

Quand la limite mémoire est atteinte, l'OOM killer du cgroup tue le processus fautif sans toucher à l'hôte.

### OverlayFS

OverlayFS est un système de fichiers en *copy-on-write* qui empile plusieurs couches. Il permet à plusieurs conteneurs de **partager** la même image de base en lecture seule, et d'avoir chacun leurs propres modifications dans une couche au-dessus.

Quatre dossiers entrent en jeu :

| Dossier | Rôle |
|:---------|:----------------------------------------------------------------|
| `lower` | Image de base, **lecture seule**. Correspond à l'image Docker. |
| `upper` | Modifications spécifiques au conteneur (créations, suppressions, écritures). |
| `work` | Espace de travail interne d'OverlayFS (à ne pas toucher). |
| `merged` | Vue **combinée** de `lower` + `upper`. C'est ce que voit le conteneur. |

Mécanisme de copy-on-write :

- **Lecture** d'un fichier inchangé : le noyau le sert depuis `lower`.
- **Modification** : le fichier est d'abord copié dans `upper`, puis modifié là. `lower` reste intact.
- **Suppression** : un *whiteout* est créé dans `upper` (un nœud spécial qui dit "ce fichier n'existe plus dans la vue"). `lower` reste intact.
- **Création** : nouveau fichier directement dans `upper`.

Pourquoi Docker l'utilise : une image `ubuntu` de 80 Mo n'est stockée **qu'une seule fois** sur le disque. Mille conteneurs Ubuntu peuvent tourner simultanément, chacun avec sa couche `upper` de quelques Ko. OverlayFS supporte aussi plusieurs `lower` empilés (`-o lowerdir=l3:l2:l1`), ce qui correspond à chaque instruction `RUN` d'un Dockerfile = une couche.

### Mini Docker (`mdocker`)

`mdocker` est un script Bash de ~250 lignes qui assemble **toutes les briques précédentes** pour reproduire le comportement de `docker run`. Dans l'ordre :

1. **`pull`** (la première fois) : `debootstrap` → `/tmp/mdocker/ubuntu/` (image `lower`).
2. **Cgroups** : crée `/sys/fs/cgroup/mdocker-$PID` et configure `memory.max`, `cpu.max`.
3. **Réseau** : crée le bridge `mdocker0` (analogue à `docker0`), une paire `veth`, configure les IPs (`10.200.1.1` côté hôte, `10.200.1.2` côté conteneur), active le forwarding et le NAT.
4. **OverlayFS** : monte `lower=$ROOTFS, upper=/tmp/mdocker-$PID/upper, work=…` sur `merged`.
5. **Lancement** : `nsenter` dans le namespace réseau + `unshare` pour les autres namespaces + `chroot` dans `merged` + exécute la commande demandée.
6. **Nettoyage** (trap EXIT) : démonte l'overlay, supprime `upper`, supprime la veth, supprime le cgroup, retire la règle iptables.

Conséquence directe : les modifications faites dans le conteneur (un `apt install vim`) sont écrites dans `upper`, qui est **supprimé à la sortie**. C'est pourquoi `vim` disparaît au prochain `mdocker run`. C'est exactement le comportement de Docker sans `-v` (volume) ou `commit`.

### Machines virtuelles vs conteneurs

| Critère | Machine Virtuelle | Conteneur |
|:------------------------|:-------------------------------------|:-------------------------------------|
| Noyau | Propre noyau invité | Partagé avec l'hôte |
| Démarrage | Quelques minutes | Quelques secondes |
| Taille typique | Plusieurs Go | Quelques dizaines de Mo |
| Isolation | Forte (niveau matériel) | Moyenne (namespaces noyau) |
| Overhead CPU/mémoire | Élevé (hyperviseur) | Faible |
| Portabilité | Dépend de l'hyperviseur | Standard Docker/OCI |
| Cas d'usage typique | Isolation forte, OS différents | Microservices, déploiement rapide |

Conséquence pratique : un conteneur Linux **ne peut pas** tourner directement sur un noyau d'un autre OS (un conteneur Windows nécessite un noyau Windows). Sur macOS/Windows, Docker utilise une VM Linux en arrière-plan. Sur Linux, en revanche, Docker n'utilise **aucune** VM : les conteneurs sont juste des processus du noyau hôte, isolés via namespaces, cgroups, chroot et OverlayFS.
