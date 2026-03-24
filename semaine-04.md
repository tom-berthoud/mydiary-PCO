# Semaine 04 — 2026-03-10

## [threads] Threads et processus légers

Un thread, également appelé processus léger, est une unité d'exécution plus légère qu'un processus traditionnel. Contrairement à un processus, qui possède son propre espace mémoire et ses propres ressources, les threads partagent le même espace mémoire et les mêmes ressources à l'intérieur d'un processus.

## Caractéristiques des threads

Partage de l'espace mémoire  
Les threads d'un même processus utilisent le même espace mémoire. Cela permet une communication rapide entre eux mais nécessite une synchronisation pour éviter les conflits d'accès aux données.

Partage des ressources  
Les threads partagent plusieurs ressources du processus :
- descripteurs de fichiers
- variables globales
- données statiques
- heap

Légèreté  
Les threads sont plus légers que les processus car ils ne dupliquent pas tout l'espace mémoire du programme.

Concurrence  
Plusieurs threads peuvent s'exécuter en parallèle ou en pseudo-parallèle dans un même processus.

## Création de threads bas niveau avec `clone()`

**Flags importants de `clone()`**

| Flag | Effet |
|---|---|
| `CLONE_VM` | partage la mémoire entre le parent et le thread |
| `CLONE_FS` | partage les informations du système de fichiers (cwd, root) |
| `CLONE_FILES` | partage les descripteurs de fichiers |
| `CLONE_SIGHAND` | partage les handlers de signaux |
| `CLONE_THREAD` | fait partie du même groupe de threads |

Pour créer un thread similaire à un pthread :
```c
clone(thread_function, stack_top,
 CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD, arg);
```

Les threads POSIX (`pthread`) utilisent `clone()` en interne pour créer les threads au niveau du noyau.

**Comparaison `clone()` vs `pthread`**

| | `clone()` | `pthread` |
|---|---|---|
| Niveau | bas niveau (appel système) | haut niveau (bibliothèque) |
| Portabilité | Linux uniquement | POSIX (Linux, macOS, BSD) |
| Complexité | plus difficile | plus simple |
| Gestion de la stack | manuelle | automatique |
| Utilisation | systèmes, kernel | applications |$

## [memoire-virtuelle] La mémoire virtuelle

La mémoire virtuelle est une technique de gestion de la mémoire qui permet à un système d'exploitation de donner l'illusion d'avoir plus de mémoire physique que ce qui est réellement disponible. Elle utilise un espace d'adressage virtuel pour chaque processus, qui peut être plus grand que la mémoire physique réelle. Lorsque le processus accède à une adresse virtuelle, le système d'exploitation traduit cette adresse en une adresse physique correspondante, en utilisant des mécanismes tels que la pagination ou la segmentation.

```{=latex}
\begin{center}
\begin{tikzpicture}[
  scale=0.85, every node/.style={scale=0.85},
  lbl/.style={font=\small\bfseries},
  cell/.style={rectangle, draw, thick, minimum width=1.4cm, minimum height=0.45cm, font=\scriptsize},
  ->, >=Latex, thick
]
  \definecolor{cA}{HTML}{60A5FA}
  \definecolor{cB}{HTML}{34D399}
  \definecolor{cMMU}{HTML}{FBBF24}

  % === Processus A ===
  \node[lbl] at (0.5,4.2) {Processus A};
  \draw[thick, rounded corners, fill=cA!10] (-0.5,0.8) rectangle (1.5,3.9);
  \node[cell, fill=cA!25] (a4) at (0.5,3.5) {Code};
  \node[cell, fill=cA!25] (a3) at (0.5,2.9) {Data};
  \node[cell, fill=cA!25] (a2) at (0.5,2.3) {Heap};
  \node[cell, fill=cA!25] (a1) at (0.5,1.7) {Stack};

  % === Processus B ===
  \node[lbl] at (0.5,-1.3) {Processus B};
  \draw[thick, rounded corners, fill=cB!10] (-0.5,-5.0) rectangle (1.5,-1.6);
  \node[cell, fill=cB!25] (b4) at (0.5,-2.0) {Code};
  \node[cell, fill=cB!25] (b3) at (0.5,-2.6) {Data};
  \node[cell, fill=cB!25] (b2) at (0.5,-3.2) {Heap};
  \node[cell, fill=cB!25] (b1) at (0.5,-3.8) {Stack};

  % === Accolade gauche : même adresse virtuelle ===
  \draw[-, decorate, decoration={brace, amplitude=6pt, mirror}, thick, purple!70]
    (-0.7,3.9) -- (-0.7,-5.0)
    node[midway, left=8pt, align=center, font=\tiny\bfseries, purple!70] {Même @\\virtuelle\\0x7fff...};

  % === Mémoire virtuelle A ===
  \node[lbl] at (5,4.2) {Espace virtuel A};
  \fill[cA!8] (3.8,0.5) rectangle (6.2,3.9);
  \draw[thick] (3.8,0.5) rectangle (6.2,3.9);
  \foreach \y/\t in {3.5/0xFFFF, 2.9/page 3, 2.3/page 2, 1.7/page 1, 1.1/0x0000} {
    \draw[gray!50] (3.8,\y-0.25) -- (6.2,\y-0.25);
    \node[font=\tiny] at (5,\y) {\t};
  }

  % === Mémoire virtuelle B ===
  \node[lbl] at (5,-1.3) {Espace virtuel B};
  \fill[cB!8] (3.8,-5.0) rectangle (6.2,-1.6);
  \draw[thick] (3.8,-5.0) rectangle (6.2,-1.6);
  \foreach \y/\t in {-2.0/0xFFFF, -2.6/page 3, -3.2/page 2, -3.8/page 1, -4.4/0x0000} {
    \draw[gray!50] (3.8,\y-0.25) -- (6.2,\y-0.25);
    \node[font=\tiny] at (5,\y) {\t};
  }

  % === MMU ===
  \node[rectangle, draw, very thick, rounded corners, fill=cMMU!30,
        minimum width=1.8cm, minimum height=1.2cm, align=center, font=\bfseries]
        (mmu) at (9,1.2) {MMU};
  \node[font=\scriptsize, below] at (9,0.5) {traduction};
  \node[font=\scriptsize, below] at (9,0.1) {d'adresses};

  % Table des pages
  \node[rectangle, draw, thick, rounded corners, fill=cMMU!10,
        minimum width=1.8cm, minimum height=1.6cm, align=center]
        (ptable) at (9,-2.8) {};
  \node[lbl, font=\scriptsize\bfseries] at (9,-2.1) {Table des pages};
  \node[font=\tiny] at (9,-2.5) {virt $\rightarrow$ phys};
  \node[font=\tiny] at (9,-2.9) {0x7f $\rightarrow$ 0x3A};
  \node[font=\tiny] at (9,-3.3) {0x7f $\rightarrow$ 0x5C};
  \draw[thick] (mmu) -- (ptable);

  % === Mémoire physique (RAM) ===
  \node[lbl] at (13,4.2) {Mém. physique};
  \fill[gray!5] (11.6,-5.0) rectangle (14.4,3.9);
  \draw[very thick] (11.6,-5.0) rectangle (14.4,3.9);

  % Cadres physiques
  \fill[cA!25] (11.6,3.0) rectangle (14.4,3.6);
  \node[font=\tiny] at (13,3.3) {page A (0x3A)};
  \fill[gray!15] (11.6,2.4) rectangle (14.4,3.0);
  \node[font=\tiny, gray] at (13,2.7) {libre};
  \fill[cB!25] (11.6,1.8) rectangle (14.4,2.4);
  \node[font=\tiny] at (13,2.1) {page B (0x5C)};
  \fill[cA!25] (11.6,1.2) rectangle (14.4,1.8);
  \node[font=\tiny] at (13,1.5) {page A (0x3B)};
  \fill[gray!15] (11.6,0.6) rectangle (14.4,1.2);
  \node[font=\tiny, gray] at (13,0.9) {libre};
  \fill[cB!25] (11.6,0.0) rectangle (14.4,0.6);
  \node[font=\tiny] at (13,0.3) {page B (0x5D)};
  \fill[cA!25] (11.6,-0.6) rectangle (14.4,0.0);
  \node[font=\tiny] at (13,-0.3) {page A (0x3C)};
  \fill[gray!15] (11.6,-1.2) rectangle (14.4,-0.6);
  \node[font=\tiny, gray] at (13,-0.9) {libre};

  % Lignes de séparation
  \foreach \y in {3.6,3.0,2.4,1.8,1.2,0.6,0.0,-0.6,-1.2} {
    \draw[gray!40] (11.6,\y) -- (14.4,\y);
  }
  \node[font=\tiny, gray] at (13,-2.0) {...};

  % === Accolade droite : adresses physiques différentes ===
  \draw[-, decorate, decoration={brace, amplitude=6pt}, thick, red!70]
    (14.6,3.6) -- (14.6,-0.6)
    node[midway, right=8pt, align=center, font=\tiny\bfseries, red!70] {@ phys.\\différentes};

  % === Flèches processus -> virtuel ===
  \draw[cA!70, thick] (1.5,2.6) -- (3.8,2.6);
  \draw[cB!70, thick] (1.5,-2.9) -- (3.8,-2.9);

  % === Flèches virtuel -> MMU ===
  \draw[cA!70, thick] (6.2,2.6) .. controls (7.3,2.6) and (7.8,2.0) .. (8.1,1.6);
  \draw[cB!70, thick] (6.2,-2.9) .. controls (7.3,-2.9) and (7.8,-0.5) .. (8.1,0.8);

  % === Flèches MMU -> physique ===
  \draw[cA!70, thick, dashed] (9.9,1.6) .. controls (10.5,2.5) and (11.0,3.0) .. (11.6,3.3);
  \draw[cB!70, thick, dashed] (9.9,0.8) .. controls (10.5,0.8) and (11.0,1.5) .. (11.6,2.1);
\end{tikzpicture}
\end{center}
```

Ce schéma illustre que deux processus distincts peuvent utiliser la même adresse virtuelle apparente, alors que la MMU la traduit vers des emplacements physiques différents.
