# Semaine 13 — 2026-05-19

## [protocoles] Protocoles de communication

Un protocole de communication définit les règles utilisées par deux machines pour échanger des données : format des messages, adresses utilisées, ordre des échanges, gestion des erreurs, etc.

Les protocoles sont organisés en couches. Chaque couche ajoute ses propres informations autour des données qu'elle reçoit de la couche supérieure.

### Pile de protocoles

Dans la pratique, on parle souvent de TCP/IP plutôt que du modèle OSI complet. Les couches importantes pour programmer un échange réseau sont surtout :

| Couche | Rôle | Exemples |
|:---:|:---|:---|
| 7 / application | protocole métier utilisé par le programme | HTTP, Modbus TCP, DNS |
| 4 / transport | communication entre processus | TCP, UDP |
| 3 / réseau | communication entre machines/réseaux | IP |
| 2 / liaison | communication sur un réseau local | Ethernet, Wi-Fi |
| 1 / physique | transport du signal | câble, fibre, ondes |

```{=latex}
\begin{center}
\begin{tikzpicture}[
  layer/.style={rectangle, draw, thick, minimum width=4.3cm, minimum height=0.65cm, font=\small\bfseries, align=center},
  note/.style={font=\footnotesize, align=left},
  >=Latex
]
  \node[layer, fill=purple!12] (app) at (0, 4.0) {Application\\\footnotesize Modbus TCP/IP, HTTP, DNS};
  \node[layer, fill=green!14]  (tcp) at (0, 3.0) {TCP \hspace{0.8cm} UDP};
  \node[layer, fill=yellow!20] (ip)  at (0, 2.0) {IP};
  \node[layer, fill=blue!12]   (eth) at (0, 1.0) {Ethernet / Wi-Fi};
  \node[layer, fill=gray!15]   (phy) at (0, 0.0) {Câble, fibre, ondes};

  \foreach \n/\y in {7/4.0,4/3.0,3/2.0,2/1.0,1/0.0} {
    \node[circle, draw, thick, minimum size=0.45cm, font=\small\bfseries] at (-3.0,\y) {\n};
  }

  \draw[->, thick] (app.south) -- (tcp.north);
  \draw[->, thick] (tcp.south) -- (ip.north);
  \draw[->, thick] (ip.south) -- (eth.north);
  \draw[->, thick] (eth.south) -- (phy.north);

  \node[note, right=1.1cm of app] {message de l'application};
  \node[note, right=1.1cm of tcp] {ports source/destination};
  \node[note, right=1.1cm of ip] {adresses IP};
  \node[note, right=1.1cm of eth] {adresses MAC};
  \node[note, right=1.1cm of phy] {bits sur le support};
\end{tikzpicture}
\end{center}
```

### MAC address

Une adresse MAC identifie une interface réseau sur un réseau local. Elle appartient à la couche 2. Exemple :

```text
00:1A:2B:3C:4D:5E
```

Elle sert à livrer une trame à la bonne machine dans le même réseau local. Un switch apprend quelles adresses MAC se trouvent derrière chacun de ses ports et transmet les trames au bon endroit.

Important : une adresse MAC ne permet pas de traverser Internet. Dès qu'on passe par un routeur, l'enveloppe Ethernet change. Les adresses MAC sont donc locales au lien courant.

### IP address

Une adresse IP identifie une machine au niveau réseau. Elle appartient à la couche 3 et permet le routage entre réseaux.

Adresses privées fréquentes :

- IPv4 : `192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`
- IPv4 loopback : `127.0.0.1`
- IPv6 link-local : `fe80::/10`
- IPv6 loopback : `::1`

La différence importante :

| Adresse | Couche | Portée | Utilisée par |
|:---|:---:|:---|:---|
| MAC | 2 | réseau local | switch |
| IP | 3 | inter-réseaux | routeur |
| Port | 4 | machine locale | système d'exploitation / programme |

### Encapsulation

Quand une application envoie un message, chaque couche ajoute son en-tête :

- TCP/UDP ajoute les ports source et destination ;
- IP ajoute les adresses IP source et destination ;
- Ethernet ajoute les adresses MAC source et destination.

```{=latex}
\begin{center}
\begin{tikzpicture}[
  field/.style={rectangle, draw, thick, minimum height=0.52cm, font=\footnotesize\bfseries, align=center},
  box/.style={rectangle, draw, thick},
  layerlabel/.style={font=\footnotesize\bfseries, align=right},
  >=Latex
]
  % Couche 2 : trame Ethernet
  \draw[box, draw=black, fill=gray!4] (0,0) rectangle (10.5,5.2);
  \node[field, fill=blue!12, minimum width=4.8cm] at (2.8,4.65) {MAC source};
  \node[field, fill=blue!12, minimum width=4.8cm] at (7.7,4.65) {MAC destination};

  % Couche 3 : paquet IP
  \draw[box, draw=orange!80!black, fill=orange!4] (0.4,0.35) rectangle (10.1,4.25);
  \node[field, draw=orange!80!black, fill=orange!12, minimum width=4.55cm] at (2.75,3.75) {IP source};
  \node[field, draw=orange!80!black, fill=orange!12, minimum width=4.55cm] at (7.65,3.75) {IP destination};

  % Couche 4 : segment TCP/UDP
  \draw[box, draw=green!60!black, fill=green!4] (0.75,0.65) rectangle (9.75,3.25);
  \node[field, draw=green!60!black, fill=green!12, minimum width=4.35cm] at (2.95,2.75) {Port source};
  \node[field, draw=green!60!black, fill=green!12, minimum width=4.35cm] at (7.55,2.75) {Port destination};

  % Données applicatives
  \node[field, fill=purple!10, minimum width=8.55cm, minimum height=1.55cm] at (5.25,1.55) {Données applicatives};

  % Accolades et labels
  \draw[decorate, decoration={brace, amplitude=5pt}, thick, blue!70!black]
    (-0.3,4.25) -- (-0.3,5.2)
    node[midway, left=7pt, layerlabel, blue!70!black] {2\\Ethernet};
  \draw[decorate, decoration={brace, amplitude=5pt}, thick, orange!80!black]
    (-0.3,3.25) -- (-0.3,4.25)
    node[midway, left=7pt, layerlabel, orange!80!black] {3\\IP};
  \draw[decorate, decoration={brace, amplitude=5pt}, thick, green!60!black]
    (-0.3,0.65) -- (-0.3,3.25)
    node[midway, left=7pt, layerlabel, green!60!black] {4\\TCP/UDP};

  \node[font=\footnotesize, align=left] at (5.25,-0.45)
    {Une couche ne regarde normalement que son propre en-tête.};
\end{tikzpicture}
\end{center}
```

Un switch travaille principalement avec les adresses MAC. Un routeur regarde les adresses IP pour décider vers quel réseau envoyer le paquet. Le système d'exploitation utilise ensuite le port de destination pour remettre les données au bon programme.

### TCP vs UDP

TCP fournit une connexion fiable entre deux programmes :

- les données arrivent dans l'ordre ;
- les pertes sont retransmises ;
- le flux est contrôlé pour éviter de saturer le récepteur.

UDP est plus simple :

- pas de connexion ;
- pas de garantie de livraison ;
- moins d'en-tête et moins de latence ;
- utile quand l'application sait gérer les pertes ou préfère aller vite.

Exemples typiques :

| TCP | UDP |
|:---|:---|
| HTTP/HTTPS | DNS |
| SSH | DHCP |
| Modbus TCP | voix/vidéo temps réel |

### Socket

Une socket est le point d'entrée utilisé par un programme pour communiquer sur le réseau. Elle est liée à un protocole de transport, une adresse IP et un port.

Un serveur TCP suit généralement ce cycle :

```text
socket() -> bind() -> listen() -> accept() -> read()/write() -> close()
```

Un client TCP fait plutôt :

```text
socket() -> connect() -> read()/write() -> close()
```

Pour UDP, il n'y a pas de connexion persistante : on envoie et reçoit des datagrammes avec `sendto()` et `recvfrom()`.
