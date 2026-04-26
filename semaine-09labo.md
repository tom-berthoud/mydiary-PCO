# Semaine 09 — 2026-04-21

## [docker] Docker c'est quoi ?

Docker est une plateforme de conteneurisation qui permet de créer, déployer et exécuter des applications dans des conteneurs légers et portables. Un conteneur est une unité standardisée de logiciel qui regroupe le code de l'application et toutes ses dépendances, garantissant ainsi que l'application fonctionne de manière cohérente dans n'importe quel environnement.

**En une phrase** : un conteneur Linux n'est rien d'autre qu'un processus (ou groupe de processus) lancé avec une vue restreinte du système : un système de fichiers à lui (`chroot`), ses propres PIDs/réseau/hostname (`namespaces`), et une limite sur les ressources qu'il peut consommer (`cgroups`). Docker n'est qu'un outil qui automatise tout ça.

Les quatre briques noyau utilisées :

| Brique | Année | Rôle |
| --- | --- | --- |
| `chroot` | 1979 | Isole le système de fichiers vu par le processus |
| `namespaces` | 2002–2008 | Isolent PIDs, réseau, hostname, IPC, mounts, users |
| `cgroups` | 2007 | Limitent les ressources (CPU, mémoire, PIDs, I/O) |
| `OverlayFS` | 2014 | Couches de FS en copy-on-write (images Docker) |

### Questions générales

1. Quelle est la différence entre un conteneur et un simple processus ?

Un conteneur est une instance isolée d'une application qui partage le noyau du système d'exploitation avec d'autres conteneurs, tandis qu'un processus est une instance d'un programme en cours d'exécution.

2. Pourquoi dit-on que les conteneurs sont plus légers que les machines virtuelles ? 

Les conteneurs partagent le noyau du système d'exploitation, ce qui les rend plus légers que les machines virtuelles qui nécessitent un système d'exploitation complet pour chaque instance.

3. Donnez une exemple concret où l'isolation offerte par Docker est utile en développement? 

Par exemple, si vous développez une application qui nécessite une version spécifique de Python, cela permet d'éviter les conflits de dépendances avec d'autres projets sur votre machine.

4. Quels sont les mécanismes du noyau Linux utilisés par Docker pour assurer l'isolation des conteneurs ?

| Mécanisme | Description |
|---|---|
| chroot | Change la racine du système de fichiers pour isoler les conteneurs. |
| Namespaces | Isolent les ressources système (processus, réseau, utilisateurs) pour chaque conteneur. |
| Cgroups | Limite les ressources (CPU, mémoire) utilisées par chaque conteneur. |
| OverlayFS | Permet de créer des systèmes de fichiers en lecture-écriture pour les conteneurs à partir d'images en lecture seule. |

### L'isolation

**Concept** : la conteneurisation cherche à isoler un programme du reste du système. On distingue plusieurs **niveaux** d'isolation, et chacun s'appuie sur un mécanisme noyau différent :

| Niveau | Mécanisme | Sans conteneur ? |
| --- | --- | --- |
| Mémoire | MMU + espace d'adressage virtuel | **Oui**, natif |
| Utilisateur | UID/GID + permissions FS | **Oui**, natif |
| Système de fichiers | `chroot` / `pivot_root` + mount namespace | Non |
| Processus (PIDs) | PID namespace | Non |
| Réseau | NET namespace + `veth` + NAT | Non |
| Hostname / IPC | UTS namespace, IPC namespace | Non |
| Ressources (CPU, RAM) | cgroups | Non |
| Environnement | variables d'environnement, FS isolé | Non |

L'idée importante : un processus Linux **standard** est déjà isolé en mémoire et par utilisateur (la MMU empêche l'accès à la mémoire d'autres processus, les permissions empêchent un user de lire les fichiers d'un autre). Tout le reste (PIDs, réseau, FS, ressources) demande des mécanismes supplémentaires que Docker active automatiquement.

1. Un processus Linux classique bénéficie-t-il déjà de certains de ces niveaux d'isolation ? 

Oui, un processus Linux bénéficie déjà de certains niveaux d'isolation grâce aux mécanismes du noyau tels que les namespaces et les cgroups, même sans utiliser Docker. Cependant, Docker utilise ces mécanismes de manière plus efficace pour créer des environnements isolés et portables pour les applications.

2. Pourquoi l'isolation réseau est-elle importante pour un serveur web ?

L'isolation réseau est importante pour un serveur web car elle permet de protéger les applications contre les attaques potentielles, de gérer les ressources réseau de manière efficace et d'assurer que les applications ne peuvent pas interférer les unes avec les autres.

3. Quel est le risque de deux programmes différents qui utilisent des fichiers temporaires?

Le risque est que les deux programmes puissent écraser ou corrompre les fichiers temporaires de l'autre, ce qui peut entraîner des erreurs ou des comportements inattendus. L'isolation des conteneurs permet d'éviter ce genre de conflits en fournissant des espaces de noms de fichiers séparés pour chaque conteneur.


### Créer un conteneur à la main

**Concept** : pour isoler le système de fichiers, il faut d'abord en construire un. `debootstrap` télécharge depuis les dépôts Debian/Ubuntu un système racine **minimal** (`bash`, `ls`, `apt`, `python3`…) dans un dossier choisi, par exemple `~/mycontainer-rootfs/`. Ce dossier ressemble à `/` d'un vrai Linux : `bin/`, `etc/`, `usr/`, `var/`…

```bash
ROOTFS=$HOME/mycontainer-rootfs
sudo debootstrap --variant=minbase noble "$ROOTFS" \
    http://archive.ubuntu.com/ubuntu/
```

Vérification GPG : chaque paquet téléchargé est signé. Sans cette vérification, un attaquant en *man-in-the-middle* pourrait injecter du code malveillant dans l'image de base — c'est exactement la même logique que `apt-get` sur l'hôte.

À ce stade, **`$ROOTFS` n'est qu'un dossier**. Aucune isolation : un processus root peut écrire dedans librement, et le contenu de `$ROOTFS` n'est pas plus protégé que `/home`.

Rappel des deux dossiers spéciaux :

- `/dev` contient des fichiers spéciaux qui représentent les périphériques (`/dev/null`, `/dev/sda`, `/dev/tty`). Linux les expose comme des fichiers via le filesystem virtuel `devtmpfs`.
- `/etc` contient les **fichiers de configuration** texte du système (`/etc/passwd`, `/etc/hostname`, `/etc/resolv.conf`).

1. Que se passerait-il si un programme malveillant dans le conteneur essayait de modifier les fichiers de l'hôte ? Par exemple, s'il modifiait le fichier `/etc/passwd` ?
   
Si un programme malveillant dans le conteneur essayait de modifier les fichiers de l'hôte, il ne pourrait pas le faire directement en raison de l'isolation fournie par Docker. Le conteneur n'a pas accès aux fichiers de l'hôte, donc il ne pourrait pas modifier des fichiers comme `/etc/passwd` sur l'hôte. Cependant, si le conteneur est mal configuré et a des privilèges élevés, il pourrait potentiellement causer des dommages à l'hôte.

2. Pourquoi est-il important que `debootstrap` vérifie la signature GPG des paquets téléchargés ? Quels risques cela évite-t-il ?

Il est important que `debootstrap` vérifie la signature GPG des paquets téléchargés pour s'assurer que les paquets proviennent d'une source fiable et n'ont pas été altérés. Cela évite les risques de télécharger et d'installer des logiciels malveillants ou compromis qui pourraient compromettre la sécurité du conteneur ou de l'hôte.

3. Que contient le fichier `/dev` et `/etc` dans un système Linux ? 

Le fichier `/dev` contient des fichiers de périphériques qui représentent les périphériques matériels et virtuels du système, tandis que le fichier `/etc` contient des fichiers de configuration pour le système et les applications.

### Chrooter dans le conteneur

**Concept** : `chroot` (*change root*) est un appel système qui modifie ce que **le noyau considère comme `/`** pour un processus et ses enfants. Quand le programme appelle `open("/etc/passwd")`, le noyau résout le chemin à partir de la nouvelle racine, pas de la vraie. Les chemins absolus deviennent donc relatifs au dossier choisi.

```bash
sudo chroot "$ROOTFS" /bin/bash
# le shell ouvre /bin/bash de $ROOTFS, ne voit plus /home, /tmp...
```

**Limites importantes** :

- `chroot` n'isole **que** le système de fichiers. Les PIDs, le réseau, les utilisateurs, les ressources : rien n'est isolé.
- Depuis l'intérieur, `ps -ax` voit toujours **tous** les processus de l'hôte (parce que `/proc` n'est pas isolé non plus si on le monte dans le conteneur).
- Un root dans un chroot peut s'évader (`chroot` n'est pas une frontière de sécurité réelle).

C'est pour ça qu'on combinera `chroot` avec `unshare` à l'étape suivante.

1. `chroot` isole-t-il les processus ? Depuis le conteneur, pouvez-vous voir les processus de l'hôte ? avec `ps -ax` ?
   
`chroot` isole le système de fichiers, mais il ne fournit pas une isolation complète des processus. Depuis le conteneur, vous pouvez voir les processus de l'hôte avec `ps -ax`, car `chroot` ne limite pas l'accès aux processus du système.

2. `chroot` isole-t-il le réseau ? Pouvez-vous faire un `ping` vers l'extérieur du conteneur ?
   
`chroot` n'isole pas le réseau. Vous pouvez faire un `ping` vers l'extérieur du conteneur, car `chroot` ne limite pas l'accès au réseau.

3. Est-il possible de chrooter depuis un autre utilisateur ?
   
Il est possible de chrooter depuis un autre utilisateur, mais cela nécessite des privilèges élevés (généralement root) pour exécuter la commande `chroot`. Un utilisateur non privilégié ne peut pas chrooter sans les permissions appropriées.

### Mount

**Concept** : `mount` attache un système de fichiers (une partition de disque, une image, un FS virtuel) à un **point de montage**, c'est-à-dire un dossier déjà présent. Une fois monté, le contenu original du dossier est **masqué** par le nouveau FS jusqu'au `umount`.

Sous Linux, beaucoup de choses sont en réalité des FS *virtuels* présentés à travers `mount` :

| Point | Type | Contenu |
| --- | --- | --- |
| `/proc` | `procfs` | Vue noyau des processus en cours (`/proc/<pid>/...`) |
| `/sys` | `sysfs` | Vue noyau du matériel et des cgroups |
| `/dev` | `devtmpfs` | Fichiers de périphériques |
| `/` | `ext4`, `btrfs`… | Le vrai disque |

Ce mécanisme est utilisé par les conteneurs pour **monter `/proc` à l'intérieur** : sans ça, `ps`, `top`, `cat /proc/self/...` ne fonctionnent pas. C'est aussi le mécanisme qui rend OverlayFS possible (cf. plus bas).

```bash
# Exemple : créer une partition de 100 Mo, la formater, la monter
fallocate -l 100M mydisk.img
mkfs.ext4 mydisk.img
sudo mount -o loop mydisk.img $HOME/mydisk
mount   # liste tous les FS montés
sudo umount $HOME/mydisk
```

1. Que se passe-t-il si vous essayez de monter un système de fichier sur un dossier qui n'existe pas ?

Si vous essayez de monter un système de fichiers sur un dossier qui n'existe pas, vous obtiendrez une erreur indiquant que le point de montage n'existe pas. Le montage échouera et le système de fichiers ne sera pas accessible.

2. Que se passe-t-il si vous essayez de monter un système de fichier sur un dossier qui contient déjà des fichiers ? Sont-ils perdus ?

Si vous essayez de monter un système de fichiers sur un dossier qui contient déjà des fichiers, les fichiers existants ne seront pas perdus, mais ils seront temporairement inaccessibles tant que le système de fichiers est monté. Une fois que vous démontez le système de fichiers, les fichiers d'origine du dossier seront à nouveau accessibles.
Voir exemple du labo chapitre 4.5.

3. Comment pouvez-vous vérifier quels systèmes de fichiers sont actuellement montés sur votre système ?

Vous pouvez vérifier quels systèmes de fichiers sont actuellement montés sur votre système en utilisant la commande `mount` sans arguments.

### Unshare

**Concept** : un *namespace* est un mécanisme noyau qui partitionne une ressource système en "vues" indépendantes. Chaque processus appartient à exactement un namespace de chaque type. La syscall `unshare` (et `clone` avec `CLONE_NEW*`) crée de nouveaux namespaces et y place le processus.

Linux définit **7 types** de namespaces :

| Namespace | Option `unshare` | Ce qu'il isole |
| --- | --- | --- |
| PID | `--pid` | Numérotation des processus (le PID 1 du conteneur n'est pas le PID 1 de l'hôte) |
| NET | `--net` | Interfaces réseau, table de routage, iptables |
| MNT | `--mount` | Points de montage (chaque conteneur peut monter ses propres FS) |
| UTS | `--uts` | Hostname et domainname |
| IPC | `--ipc` | Files de messages, sémaphores SysV, mémoire partagée |
| USER | `--user` | UID/GID (root dans le conteneur ≠ root sur l'hôte) |
| CGROUP | `--cgroup` | Vue de la hiérarchie cgroup |

La commande complète qui monte un mini-conteneur isolé est :

```bash
sudo unshare --fork --pid --mount --uts --ipc --net --cgroup --mount-proc \
    chroot "$ROOTFS" /bin/bash
```

Une fois dedans, `ps -ax` ne voit plus que les processus du conteneur, `ip a` ne voit que `lo`, `hostname X` ne change que dans le conteneur. Pour sortir : `exit`.

1. Que se passe-t-il si vous omettez l'option `--pid` lors de l'exécution de `unshare` ? Pouvez-vous voir les processus de l'hôte avec `ps -ax` ?

Oui, si vous omettez l'option `--pid` lors de l'exécution de `unshare`, vous pourrez voir les processus de l'hôte avec `ps -ax`, car les namespaces de processus ne seront pas isolés.

2. À quoi sert `--uts` ? Essayez de changer le hostname depuis le conteneur (`hostname monconteneur`) et vérifiez que cela ne change pas le hostname de l'hôte.

L'option `--uts` isole le namespace UTS (UNIX Time-sharing System), qui contient le hostname et le domainname du système. En lançant `hostname monconteneur` dans le conteneur, on change le hostname **vu uniquement** par les processus de ce namespace UTS ; l'hôte garde son hostname intact.

3. Quelle option de `unshare` correspond à l'isolation réseau que vous observez avec ip a ?

L'option de `unshare` qui correspond à l'isolation réseau que vous observez avec `ip a` est `--net`. Cette option isole le namespace réseau, ce qui signifie que les interfaces réseau et les adresses IP du conteneur sont séparées de celles de l'hôte.

### Etablir le réseau dans le conteneur

**Concept** : après `unshare --net`, le conteneur a son propre namespace réseau, mais **vide** : seule l'interface `lo` existe. Pour le brancher sur Internet, on construit à la main ce que Docker fait avec `docker0`.

Architecture cible :

```{=latex}
\begin{center}
\begin{tikzpicture}[
  node distance=0.6cm,
  every node/.style={font=\small},
  box/.style={draw, rounded corners, minimum height=0.8cm, minimum width=2.2cm}
]
  \node[box, fill=blue!10] (cont) {Conteneur};
  \node[below=0cm of cont, font=\footnotesize] {ns réseau dédié};
  \node[box, right=1.4cm of cont, fill=gray!15] (host) {Hôte};
  \node[box, right=1.4cm of host, fill=orange!20] (net) {Internet};

  \draw[<->] (cont) -- node[above, font=\footnotesize] {veth1 $\leftrightarrow$ veth0} (host);
  \draw[->] (host) -- node[above, font=\footnotesize] {NAT MASQUERADE} node[below, font=\footnotesize] {via eth0} (net);
\end{tikzpicture}
\end{center}
```

Étapes (correspondent au labo) :

1. **Paire veth** : `ip link add veth0 type veth peer name veth1` crée deux interfaces virtuelles connectées comme un câble.
2. **Déplacement de `veth1`** dans le namespace du conteneur : `ip link set veth1 netns cont`.
3. **Adresses IP** : `10.200.1.1/24` côté hôte, `10.200.1.2/24` côté conteneur, **même sous-réseau**.
4. **Route par défaut** dans le conteneur vers l'hôte : `ip route add default via 10.200.1.1`.
5. **IP forwarding** sur l'hôte : `sysctl -w net.ipv4.ip_forward=1` (sans ça, l'hôte ne route pas les paquets venus de `veth0` vers `eth0`).
6. **NAT MASQUERADE** : `iptables -t nat -A POSTROUTING -s 10.200.1.0/24 -o eth0 -j MASQUERADE` réécrit l'IP source du paquet sortant avec celle de l'hôte. Métaphore : standard téléphonique d'entreprise — le poste interne `1234` est remplacé par le numéro public quand on appelle l'extérieur.

Sans (5) ou (6), `ping 8.8.8.8` depuis le conteneur échoue avec `Network is unreachable` ou un timeout (les paquets sortent mais les réponses ne reviennent pas, l'extérieur ne connaît pas `10.200.1.2`).

1. Pourquoi est-il nécessaire d'activer le forwarding IP sur l'hôte pour que le conteneur puisse accéder à Internet ? Que se passerait-il si vous oubliez cette étape ?

Il est nécessaire d'activer le forwarding IP sur l'hôte pour permettre au conteneur de router le trafic réseau vers Internet. Si vous oubliez cette étape, le conteneur ne pourra pas accéder à Internet, car les paquets réseau ne seront pas acheminés correctement entre le conteneur et l'hôte. 

2. Que fait excatement --net dans `unshare` ? Pourquoi le conteneur n'a-t-il que l'interface de loopback (lo) après `unshare --net` ?
   
L'option `--net` dans `unshare` crée un namespace réseau isolé pour le conteneur. Après exécution de `unshare --net`, le conteneur n'a que l'interface de loopback (lo) parce que les interfaces réseau physiques de l'hôte ne sont pas partagées avec le conteneur. Le conteneur doit être configuré pour créer et connecter des interfaces réseau virtuelles pour accéder à Internet ou à d'autres réseaux.

3. A quoi sert la règle `MASQUERADE` dans `iptables` ? Que se passerait-il si vous oubliez cette règle ?

La règle `MASQUERADE` dans `iptables` est utilisée pour masquer l'adresse IP source des paquets sortants du conteneur, en les remplaçant par l'adresse IP de l'hôte. Cela permet au conteneur d'accéder à Internet en utilisant l'adresse IP de l'hôte. Si vous oubliez cette règle, le conteneur ne pourra pas accéder à Internet, car les paquets sortants ne seront pas correctement routés et les réponses ne pourront pas être reçues par le conteneur.

### Cgroups

**Concept** : les *control groups* (cgroups) sont une hiérarchie noyau qui permet de **regrouper des processus et leur appliquer des limites de ressources**. Sans cgroups, un processus peut monopoliser le CPU, faire exploser la RAM, ou *fork-bomber* la machine.

Cgroups v2 (Ubuntu 22+, Fedora récent) unifie tout sous `/sys/fs/cgroup/`. Les contrôleurs disponibles sont listés dans `cgroup.controllers` :

| Contrôleur | Limite |
| --- | --- |
| `cpu` | Temps CPU (`cpu.max = quota period` en µs) |
| `memory` | Mémoire (`memory.max = 256M`) |
| `pids` | Nombre de processus (`pids.max = 42`) |
| `io` | Bande passante disque |
| `cpuset` | Affinité CPU/NUMA |

Recette pour appliquer une limite :

```bash
# 1. Créer le cgroup
CG=/sys/fs/cgroup/demo-ctr
sudo mkdir -p "$CG"

# 2. Activer les contrôleurs au niveau parent (sinon les limites enfants
#    sont ignorées silencieusement)
echo "+cpu +memory +pids" | sudo tee /sys/fs/cgroup/cgroup.subtree_control

# 3. Poser les limites
echo "12000 100000" | sudo tee "$CG/cpu.max"   # 12% d'un cœur
echo "256M"          | sudo tee "$CG/memory.max"
echo 42              | sudo tee "$CG/pids.max"

# 4. Attacher un processus (par son PID)
echo $$ | sudo tee "$CG/cgroup.procs"
```

L'**ordre est critique** : sans (2), les écritures dans `cpu.max` etc. n'ont aucun effet.

Tester la limite mémoire : `python3 -c "a = ' ' * (300 * 1024**2)"` se fait `Killed` par l'OOM killer du cgroup, sans toucher à l'hôte.

1. Pourquoi on écrit-on 256M dans memory.max mais un nombre seul dans pids.max ? Qu'est-ce qui se passe si on écrit max dans un des deux fichiers ?

Dans `memory.max`, on écrit `256M` pour spécifier une limite de mémoire de 256 mégaoctets, tandis que dans `pids.max`, on écrit un nombre seul pour spécifier une limite sur le nombre de processus. Si on écrit `max` dans l'un des deux fichiers, cela signifie qu'il n'y a pas de limite, et le conteneur pourra utiliser autant de mémoire ou créer autant de processus que nécessaire, ce qui peut potentiellement entraîner des problèmes de performance ou de stabilité si les ressources sont épuisées.

2. Que se passe-t-il si on crée un cgroup avec mkdir mais qu'on n'écrit rien dans cgroup.subtree_control du parent ? Pourquoi cette étape est-elle nécessaire avant de poser des limites ?
   
Si on crée un cgroup avec `mkdir` mais qu'on n'écrit rien dans `cgroup.subtree_control` du parent, le cgroup ne sera pas activé pour les contrôleurs de ressources, et les limites que vous essayez de poser ne seront pas appliquées. Cette étape est nécessaire pour activer les contrôleurs de ressources dans le cgroup parent, ce qui permet aux cgroups enfants de fonctionner correctement et d'appliquer les limites définies.

3. Pourquoi est-il important d'attacher le processus du conteneur au groupe de contrôle ? Que se passerait-il si on oublie cette étape ?

Il est important d'attacher le processus du conteneur au groupe de contrôle pour que les limites de ressources définies dans le cgroup soient appliquées au processus. Si on oublie cette étape, le processus du conteneur ne sera pas soumis aux limites de ressources définies, ce qui peut entraîner une utilisation excessive des ressources et potentiellement affecter la performance ou la stabilité de l'hôte.

4. Pourquoi les 60 sleep n'échouent-ils qu'après 37-38 réussis alors que la limite est 42 ? D'où viennent les processus "invisibles" qui occupent les PIDs restants ?

Les 60 processus `sleep` n'échouent qu'après 37-38 réussis parce que le système d'exploitation réserve certains PIDs pour des processus système ou d'autres processus invisibles qui ne sont pas directement liés au conteneur. Ces processus "invisibles" peuvent inclure des processus de gestion du cgroup, des processus de surveillance ou d'autres processus système qui utilisent des PIDs et occupent les ressources disponibles, ce qui explique pourquoi les limites de PID sont atteintes avant que tous les processus `sleep` ne soient créés.

5. Après le unshare --cgroup, la commande cat `/proc/self/cgroup` dans le container afficher 0::/. Pourquoi pas 0::/demo-ctr ? Qu'est-ce que ça révèle sur le fonctionnement des cgroup namespaces ?

Après le `unshare --cgroup`, la commande `cat /proc/self/cgroup` dans le conteneur affiche `0::/` au lieu de `0::/demo-ctr` parce que les cgroups ne sont pas isolés dans un namespace de cgroup. Cela révèle que les cgroups sont partagés entre l'hôte et le conteneur, ce qui signifie que les processus du conteneur peuvent voir et être affectés par les cgroups de l'hôte. Les namespaces de cgroup ne sont pas encore largement supportés, ce qui limite l'isolation des ressources entre les conteneurs et l'hôte.

### overlayFS

**Concept** : OverlayFS est un système de fichiers en *copy-on-write* qui empile plusieurs couches. Il permet à plusieurs conteneurs de **partager** la même image de base en lecture seule, et d'avoir chacun leurs propres modifications dans une couche au-dessus.

Quatre dossiers entrent en jeu :

| Dossier | Rôle |
| --- | --- |
| `lower` | Image de base, **lecture seule**. Correspond à l'image Docker. |
| `upper` | Modifications spécifiques au conteneur (créations, suppressions, écritures). |
| `work` | Espace de travail interne d'OverlayFS (à ne pas toucher). |
| `merged` | Vue **combinée** de `lower` + `upper`. C'est ce que voit le conteneur. |

Mécanisme de copy-on-write :

- **Lecture** d'un fichier inchangé : le noyau le sert depuis `lower`.
- **Modification** : le fichier est d'abord copié dans `upper`, puis modifié là. `lower` reste intact.
- **Suppression** : un *whiteout* est créé dans `upper` (un nœud spécial qui dit "ce fichier n'existe plus dans la vue"). `lower` reste intact.
- **Création** : nouveau fichier directement dans `upper`.

```bash
mkdir -p overlay-demo/{lower,upper,work,merged}
echo "Hello Bob" > overlay-demo/lower/hello.txt

sudo mount -t overlay overlay \
    -o lowerdir=overlay-demo/lower,upperdir=overlay-demo/upper,workdir=overlay-demo/work \
    overlay-demo/merged

cat overlay-demo/merged/hello.txt        # Hello Bob (vient de lower)
echo "Hello Alice" > overlay-demo/merged/hello.txt
cat overlay-demo/lower/hello.txt          # Hello Bob (intact)
cat overlay-demo/upper/hello.txt          # Hello Alice (la modif)
```

Pourquoi Docker l'utilise : une image `ubuntu` de 80 Mo n'est stockée **qu'une seule fois** sur le disque. Mille conteneurs Ubuntu peuvent tourner simultanément, chacun avec sa couche `upper` de quelques Ko. OverlayFS supporte aussi plusieurs `lower` empilés (`-o lowerdir=l3:l2:l1`), ce qui correspond à chaque instruction `RUN` d'un Dockerfile = une couche.

1. Que se passe-t-il si vous supprimez un fichier dans merged ? Est-il supprimé dans lower ?

Si vous supprimez un fichier dans le répertoire `merged`, il ne sera pas supprimé dans le répertoire `lower`. Le système de fichiers OverlayFS utilise une approche de copie sur écriture, ce qui signifie que les modifications apportées dans le répertoire `merged` n'affectent pas directement les fichiers dans le répertoire `lower`. Lorsque vous supprimez un fichier dans `merged`, il est simplement marqué comme supprimé dans la vue du conteneur, mais le fichier original dans `lower` reste intact.

2. Que se passe-t-il si vous créez un nouveau fichier dans merged ? Où est-il créé ?

Si vous créez un nouveau fichier dans le répertoire `merged`, il est créé dans le répertoire `upper`. Le système de fichiers OverlayFS redirige les opérations d'écriture vers le répertoire `upper`, ce qui permet de conserver les fichiers originaux dans le répertoire `lower` intacts. Ainsi, les nouveaux fichiers créés dans `merged` sont stockés dans `upper`, tandis que les fichiers existants dans `lower` restent inchangés.

3. Pourquoi Docker utilise-t-il OverlayFS pour gérer les systèmes de fichiers de ses conteneurs ? Quels avantages cela offre-t-il en termes de performance et de stockage ?

Docker utilise OverlayFS pour gérer les systèmes de fichiers de ses conteneurs car il offre plusieurs avantages en termes de performance et de stockage. OverlayFS permet de créer des images de conteneurs légères en utilisant une approche de copie sur écriture, ce qui signifie que les conteneurs peuvent partager des fichiers communs sans dupliquer les données. Cela réduit considérablement l'utilisation du stockage et améliore les performances, car les conteneurs peuvent démarrer plus rapidement en utilisant des images partagées. De plus, OverlayFS permet une gestion efficace des modifications apportées aux fichiers dans les conteneurs, ce qui facilite la maintenance et la mise à jour des applications déployées dans les conteneurs.

### Container Mini Docker

**Concept** : `mdocker` est un script Bash de ~250 lignes qui assemble **toutes les briques précédentes** pour reproduire le comportement de `docker run`. Il fait, dans l'ordre :

1. **`pull`** (la première fois) : `debootstrap` → `/tmp/mdocker/ubuntu/` (image `lower`).
2. **Cgroups** : crée `/sys/fs/cgroup/mdocker-$PID` et configure `memory.max`, `cpu.max`.
3. **Réseau** : crée le bridge `mdocker0` (analogue à `docker0`), une paire `veth`, configure les IPs (`10.200.1.1` côté hôte, `10.200.1.2` côté conteneur), active le forwarding et le NAT.
4. **OverlayFS** : monte `lower=$ROOTFS, upper=/tmp/mdocker-$PID/upper, work=…` sur `merged`.
5. **Lancement** : `nsenter` dans le namespace réseau + `unshare` pour les autres namespaces + `chroot` dans `merged` + exécute la commande demandée.
6. **Nettoyage** (trap EXIT) : démonte l'overlay, supprime `upper`, supprime la veth, supprime le cgroup, retire la règle iptables.

Conséquence directe : les modifications faites dans le conteneur (un `apt install vim`) sont écrites dans `upper`, qui est **supprimé à la sortie**. C'est pourquoi `vim` disparaît au prochain `mdocker run`. C'est exactement le comportement de Docker sans `-v` (volume) ou `commit`.

Schéma simplifié de l'enchaînement :

```
mdocker run → cgroup mkdir → bridge + veth + NAT
            → mount overlay
            → nsenter + unshare + chroot → bash dans le conteneur
            ← (sortie) trap cleanup
```

### Mini Docker

1. Ouvrez le script `mdocker` et repérez la commande `mount -t overlay`. Quels sont les quatre répertoires utilisés ? Lequel correspond à l'image de base en lecture seule, lequel reçoit les modifications, et lequel est la vue combinée dans laquelle le processus s'exécute ?

Les quatre répertoires utilisés par OverlayFS sont :

- `lowerdir="$ROOTFS"` : correspond à l'image de base en lecture seule.
- `upperdir="$OVL/upper"` : reçoit les modifications faites dans le conteneur.
- `workdir="$OVL/work"` : répertoire de travail interne utilisé par OverlayFS.
- `"$OVL/merged"` : vue combinée dans laquelle le processus s'exécute.

Le conteneur est lancé dans `"$OVL/merged"` avec `chroot`. C'est donc ce répertoire qui représente le système de fichiers visible depuis le conteneur.

2. Pourquoi `vim` disparaît-il entre deux `mdocker run` ? Tracez le chemin exact : dans quel répertoire `apt install vim` écrit-il ses fichiers, et que fait le script à la sortie du conteneur avec ce répertoire ?

`vim` disparaît entre deux exécutions car les modifications du conteneur sont stockées dans la couche temporaire `upper`.

Quand on lance :

```bash
apt install vim
```

les fichiers installés sont visibles dans :

```bash
/tmp/mdocker-<PID>/merged
```

mais ils sont réellement écrits dans :

```bash
/tmp/mdocker-<PID>/upper
```

À la sortie du conteneur, la fonction `cleanup` supprime le dossier temporaire :

```bash
rm -rf "$OVL"
```

Donc le dossier `/tmp/mdocker-<PID>/upper` est supprimé. Comme l'image de base dans `/tmp/mdocker/ubuntu` n'est jamais modifiée, `vim` n'est pas présent au prochain `mdocker run`.

3. Depuis le conteneur, exécutez `ip a` et `ip route`. Quelle est l'adresse IP du conteneur ? Quelle est la passerelle ? Pouvez-vous pinguer `8.8.8.8` ? Pourquoi le conteneur a-t-il accès à internet alors qu'il est dans un namespace réseau isolé ?

L'adresse IP du conteneur est :

```bash
10.200.1.2/24
```

La passerelle par défaut est :

```bash
10.200.1.1
```

Cette adresse correspond au bridge `mdocker0` côté hôte.

Le conteneur peut pinguer `8.8.8.8` si la configuration réseau fonctionne correctement. Il a accès à internet même s'il est dans un namespace réseau isolé, car le script crée une paire `veth`, connecte une extrémité au bridge `mdocker0`, active le forwarding IP sur l'hôte et ajoute une règle NAT avec `iptables`.

Le paquet sort donc du conteneur par `eth0`, passe par le bridge `mdocker0`, puis l'hôte le traduit avec le masquerading avant de l'envoyer vers internet.

4. Regardez dans le script la section cgroups. Quelle valeur est écrite dans `cpu.max` si vous passez `--cpus=0.5` ? Que signifie ce couple de nombres pour le scheduler Linux ?

Avec :

```bash
--cpus=0.5
```

le script utilise :

```bash
PERIOD=100000
QUOTA=50000
```

Il écrit donc dans `cpu.max` :

```bash
50000 100000
```

Cela signifie que les processus du conteneur peuvent utiliser au maximum `50000` microsecondes de CPU toutes les `100000` microsecondes.

Autrement dit, le conteneur est limité à 50% d'un CPU. Le scheduler Linux applique cette limite avec les cgroups.

5. Le script utilise `unshare` sans l'option `--user`. Pourquoi faut-il lancer `mdocker` avec `sudo` ?

Il faut lancer `mdocker` avec `sudo` parce que le script effectue plusieurs opérations privilégiées.

Par exemple, il crée des namespaces réseau, configure des interfaces `veth`, crée un bridge, modifie les règles `iptables`, monte un OverlayFS, écrit dans `/sys/fs/cgroup` et utilise `chroot`.

Comme le script n'utilise pas `--user`, il ne crée pas de user namespace permettant de simuler les privilèges root à l'intérieur du conteneur. Les privilèges root de l'hôte sont donc nécessaires pour effectuer ces opérations.

### Machines virtuelles vs conteneurs

| Critère | Machine Virtuelle | Conteneur |
| ------- | :---------------: | :-------: |
| Noyau | Propre noyau invité | Partagé avec l'hôte |
| Démarrage | Quelques minutes | Quelques secondes |
| Taille typique | Plusieurs Go | Quelques dizaines de Mo |
| Isolation | Forte (niveau matériel) | Moyenne (namespaces noyau) |
| Overhead CPU/mémoire | Élevé (hyperviseur) | Faible |
| Portabilité | Dépend de l'hyperviseur | Standard Docker/OCI |
| Cas d'usage typique | Isolation forte, OS différents | Microservices, déploiement rapide |


### Conteneurs vs machines virtuelles

1. Quels sont les avantages et les inconvénients des conteneurs par rapport aux machines virtuelles en termes de performance, d'isolation et de portabilité ?

Les conteneurs sont généralement plus performants que les machines virtuelles, car ils ne lancent pas un système d'exploitation complet avec son propre noyau. Ils partagent le noyau de l'hôte, ce qui les rend plus légers, plus rapides à démarrer et moins coûteux en mémoire et en stockage.

En revanche, l'isolation est moins forte que celle d'une machine virtuelle. Dans une VM, chaque système invité possède son propre noyau, séparé de l'hôte par un hyperviseur. Dans un conteneur, les processus sont isolés avec des mécanismes du noyau Linux comme les namespaces et les cgroups, mais ils utilisent toujours le noyau de l'hôte.

Pour la portabilité, les conteneurs sont très pratiques car ils embarquent l'application et ses dépendances. Cependant, ils restent dépendants du type de noyau utilisé. Un conteneur Linux a besoin d'un noyau Linux, alors qu'une machine virtuelle peut faire tourner un système d'exploitation complètement différent de celui de l'hôte.

2. Est-il possible de faire tourner un conteneur Windows sur un hôte Linux ? Pourquoi ?

Non, pas directement. Un conteneur Windows a besoin du noyau Windows, alors qu'un hôte Linux fournit un noyau Linux. Comme un conteneur partage le noyau de l'hôte, il ne peut pas utiliser un noyau d'un autre système d'exploitation.

Pour exécuter un environnement Windows sur un hôte Linux, il faut passer par une machine virtuelle Windows. La VM fournit alors le noyau Windows nécessaire.

3. Docker utilise-t-il des machines virtuelles pour faire tourner les conteneurs ? Pourquoi ou pourquoi pas ?

Sur Linux, Docker n'utilise pas de machine virtuelle pour faire tourner les conteneurs Linux. Les conteneurs sont des processus Linux isolés avec les mécanismes du noyau : namespaces, cgroups, chroot ou pivot_root, et OverlayFS.

Docker automatise donc la création de ces environnements isolés, mais les conteneurs partagent toujours le noyau de l'hôte.

Sur Windows ou macOS, Docker peut utiliser une machine virtuelle Linux en arrière-plan pour faire tourner des conteneurs Linux, car ces systèmes ne fournissent pas directement un noyau Linux compatible.
