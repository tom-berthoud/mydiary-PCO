# Semaine 06 — 2026-03-24

## [Systèmeexploitation] Ordonnanceur (scheduler)

L'ordonnanceur est un composant du système d'exploitation qui gère l'exécution des processus en décidant quel processus doit être exécuté à un moment donné. Il utilise des algorithmes pour déterminer l'ordre d'exécution des processus, en tenant compte de facteurs tels que la priorité, le temps d'exécution, et les ressources nécessaires.

### Algorithmes d'ordonnancement

- FIFO (First In, First Out) : Les processus sont exécutés dans l'ordre de leur arrivée.

- Round Robin : Chaque processus reçoit une quantité de temps fixe (quantum) pour s'exécuter, puis passe au processus suivant.

### Schémas FIFO

**File d'attente FIFO (ordre d'arrivée) :**

```{=latex}
\begin{center}
\begin{tikzpicture}[
  proc/.style={circle, draw, thick, minimum size=1cm, fill=blue!10},
  cpu/.style={rectangle, draw, thick, rounded corners, minimum size=1cm, fill=green!15},
  ->, >=Latex, thick
]
  \node[proc] (p1) at (0,0) {P1};
  \node[proc] (p2) at (2,0) {P2};
  \node[proc] (p3) at (4,0) {P3};
  \node[proc] (p4) at (6,0) {P4};
  \node[cpu]  (cpu) at (8.5,0) {CPU};
  \draw (p1) -- (p2);
  \draw (p2) -- (p3);
  \draw (p3) -- (p4);
  \draw (p4) -- (cpu);
\end{tikzpicture}
\end{center}
```

**Diagramme de Gantt FIFO :**

```{=latex}
\begin{center}
\begin{tikzpicture}[yscale=0.6]
  % Couleurs
  \definecolor{c1}{HTML}{60A5FA}
  \definecolor{c2}{HTML}{34D399}
  \definecolor{c3}{HTML}{FBBF24}
  \definecolor{c4}{HTML}{F87171}
  % Axe du temps
  \draw[->, thick] (0,-0.5) -- (10.5,-0.5) node[right] {temps};
  \foreach \x/\t in {0/0, 2/2, 5/5, 7/7, 10/10} {
    \draw (\x,-0.5) -- (\x,-0.7) node[below]{\small \t};
  }
  % Barres
  \fill[c1] (0,0) rectangle (2,0.7); \node at (1,0.35) {\textbf{P1}};
  \fill[c2] (2,0) rectangle (5,0.7); \node at (3.5,0.35) {\textbf{P2}};
  \fill[c3] (5,0) rectangle (7,0.7); \node at (6,0.35) {\textbf{P3}};
  \fill[c4] (7,0) rectangle (10,0.7); \node at (8.5,0.35) {\textbf{P4}};
  \draw[thick] (0,0) rectangle (10,0.7);
  \node[left] at (0,0.35) {\small CPU};
\end{tikzpicture}
\end{center}
```

### Schémas Round Robin (quantum $\Delta t$ = 10ms)

À chaque changement de processus, l'ordonnanceur effectue un **context switch** : sauvegarder l'état du processus courant (registres, pile, etc.) puis restaurer celui du suivant. Cela introduit une latence, surtout si le quantum est trop court.

**Étapes du context switch :**

```{=latex}
\begin{center}
\begin{tikzpicture}[
  stp/.style={rectangle, draw, thick, rounded corners=4pt, minimum height=0.8cm, minimum width=1.8cm, font=\scriptsize\bfseries, align=center},
  ->, >=Latex, thick
]****
  \definecolor{cKS}{HTML}{60A5FA}
  \definecolor{cSave}{HTML}{F87171}
  \definecolor{cRR}{HTML}{FBBF24}
  \definecolor{cLoad}{HTML}{34D399}
  \definecolor{cUS}{HTML}{A78BFA}

  \node[stp, fill=cKS!20]   (ks)   at (0,0)    {Kernel\\Space};
  \node[stp, fill=cSave!20] (save) at (2.8,0)  {Backup\\CTX};
  \node[stp, fill=cRR!20]   (rr)   at (5.6,0)  {Round\\Robin};
  \node[stp, fill=cLoad!20] (load) at (8.4,0)  {Load\\CTX};
  \node[stp, fill=cUS!20]   (us)   at (11.2,0) {User\\Space};

  \draw (ks) -- (save);
  \draw (save) -- (rr);
  \draw (rr) -- (load);
  \draw (load) -- (us);

  \draw[-, decorate, decoration={brace, amplitude=5pt, mirror}, gray]
    (0,-0.7) -- (11.2,-0.7)
    node[midway, below=6pt, font=\scriptsize, gray] {$\approx$ 50 à 500 ns};
\end{tikzpicture}
\end{center}
```

**File circulaire Round Robin :**

```{=latex}
\begin{center}
\begin{tikzpicture}[
  proc/.style={circle, draw, thick, minimum size=1cm, fill=blue!10},
  ->, >=Latex, thick
]
  \node[proc] (p1) at (90:1.5)  {P1};
  \node[proc] (p2) at (0:1.5)   {P2};
  \node[proc] (p3) at (270:1.5) {P3};
  \node[proc] (p4) at (180:1.5) {P4};
  \draw (p1) to[bend left=20] (p2);
  \draw (p2) to[bend left=20] (p3);
  \draw (p3) to[bend left=20] (p4);
  \draw (p4) to[bend left=20] (p1);
\end{tikzpicture}
\end{center}
```

**Diagramme de Gantt Round Robin (quantum = 2) :**

```{=latex}
\begin{center}
\begin{tikzpicture}[yscale=0.6]
  \definecolor{c1}{HTML}{60A5FA}
  \definecolor{c2}{HTML}{34D399}
  \definecolor{c3}{HTML}{FBBF24}
  \definecolor{c4}{HTML}{F87171}
  % Axe du temps
  \draw[->, thick] (0,-0.5) -- (14.5,-0.5) node[right] {temps};
  \foreach \x in {0,2,...,14} {
    \draw (\x,-0.5) -- (\x,-0.7) node[below]{\small \x};
  }
  % Barres
  \fill[c1] (0,0) rectangle (2,0.7);   \node at (1,0.35)  {\textbf{P1}};
  \fill[c2] (2,0) rectangle (4,0.7);   \node at (3,0.35)  {\textbf{P2}};
  \fill[c3] (4,0) rectangle (6,0.7);   \node at (5,0.35)  {\textbf{P3}};
  \fill[c4] (6,0) rectangle (8,0.7);   \node at (7,0.35)  {\textbf{P4}};
  \fill[c1] (8,0) rectangle (10,0.7);  \node at (9,0.35)  {\textbf{P1}};
  \fill[c2] (10,0) rectangle (12,0.7); \node at (11,0.35) {\textbf{P2}};
  \fill[c4] (12,0) rectangle (14,0.7); \node at (13,0.35) {\textbf{P4}};
  \draw[thick] (0,0) rectangle (14,0.7);
  \node[left] at (0,0.35) {\small CPU};
\end{tikzpicture}
\end{center}
```

### Interruptions et préemption

On peut demander une interruption ce qui permet de gagné en performance car maintenant le $\Delta t$ n'est plus fixe, il est dynamique et dépend de l'activité du processus. Par exemple, si un processus fait une opération d'entrée/sortie, il peut être interrompu pour laisser la place à un autre processus pendant que l'opération se termine.

### Liste des états d'un processus

- **Running** : le processus est en cours d'exécution sur le CPU.
- **Runnable** : le processus est prêt à être exécuté mais attend son tour.
- **Sleeping** : le processus attend un événement (ex. : entrée/sortie) et ne peut pas être exécuté.
- **Stopped** : le processus est suspendu (ex. : par un signal) et ne peut pas être exécuté.
- **Zombie** : le processus a terminé son exécution mais attend que son parent récupère son statut de sortie.

### Priorités et starvation

L'ordonnanceur peut attribuer des priorités aux processus pour favoriser certains types de tâches (ex. : temps réel). Cependant, cela peut entraîner une **starvation** : les processus à faible priorité peuvent ne jamais être exécutés s'il y a toujours des processus à haute priorité. Les priorités vont de -20 (la plus haute) à 19 (la plus basse). Plus la priorité est basse, plus le processus a de chances d'être exécuté et ne pas être interrompu.


## [Systèmeexploitation] Registres CPU et mémoire (Stack / Heap)

Les registres sont des petites cases mémoire ultra-rapides directement dans le CPU. Lors d'un **context switch**, l'ordonnanceur doit sauvegarder tous ces registres pour pouvoir restaurer l'état du processus plus tard.

- **R0–R3** : registres généraux (arguments, calculs temporaires)
- **SP** (Stack Pointer) : pointe vers le sommet de la pile
- **FP** (Frame Pointer) : pointe vers le début du cadre de la fonction courante
- **PC** (Program Counter) : adresse de l'instruction en cours d'exécution

```{=latex}
\begin{center}
\begin{tikzpicture}[
  reg/.style={rectangle, draw, thick, minimum width=1.8cm, minimum height=0.6cm, fill=blue!10, font=\small\ttfamily},
  lbl/.style={font=\small\bfseries},
  ->, >=Latex, thick
]
  % CPU
  \node[lbl] at (-0.5,3.5) {CPU};
  \draw[thick, rounded corners, fill=gray!5] (-1.5,-2.5) rectangle (0.5,3.2);
  \node[reg] (r0) at (-0.5,2.7) {R0};
  \node[reg] (r1) at (-0.5,2.0) {R1};
  \node[reg] (r2) at (-0.5,1.3) {R2};
  \node[reg] (r3) at (-0.5,0.6) {R3};
  \node[reg, fill=orange!20] (fp) at (-0.5,-0.1) {FP};
  \node[reg, fill=red!15] (sp) at (-0.5,-0.8) {SP};
  \node[reg, fill=green!15] (pc) at (-0.5,-1.5) {PC};

  % Mémoire
  \node[lbl] at (5.5,4.2) {Mémoire};
  % Stack
  \fill[red!8] (3.5,3.8) rectangle (7.5,1.5);
  \draw[thick] (3.5,3.8) rectangle (7.5,1.5);
  \node[lbl, red!70!black] at (5.5,3.5) {Stack (pile)};
  \node[font=\small] at (5.5,3.0) {variables locales};
  \node[font=\small] at (5.5,2.5) {adresses de retour};
  \node[font=\small] at (5.5,2.0) {cadres de fonctions};
  \draw[->, very thick, red!50] (5.5,1.5) -- (5.5,0.8) node[midway, right, font=\small] {$\downarrow$ croît};

  % Espace libre
  \node[font=\small\itshape, gray] at (5.5,0.4) {espace libre};

  % Heap
  \fill[green!8] (3.5,-0.2) rectangle (7.5,-2.2);
  \draw[thick] (3.5,-0.2) rectangle (7.5,-2.2);
  \node[lbl, green!50!black] at (5.5,-0.5) {Heap (tas)};
  \node[font=\small] at (5.5,-1.0) {malloc / new};
  \node[font=\small] at (5.5,-1.5) {allocations dynamiques};
  \draw[->, very thick, green!50!black] (5.5,-0.2) -- (5.5,0.1) node[midway, right, font=\small] {$\uparrow$ croît};

  % Code/Data
  \fill[gray!10] (3.5,-2.5) rectangle (7.5,-3.5);
  \draw[thick] (3.5,-2.5) rectangle (7.5,-3.5);
  \node[lbl] at (5.5,-2.8) {Code / Data};
  \node[font=\small] at (5.5,-3.2) {instructions, constantes};

  % Flèches registres -> mémoire
  \draw[red!60, dashed, thick] (sp.east) -- ++(1.5,0) |- (3.5,1.5) node[pos=0.3, above, font=\scriptsize\color{red!60}] {pointe vers le sommet};
  \draw[orange!70, dashed, thick] (fp.east) -- ++(2,0) |- (3.5,2.2) node[pos=0.25, above, font=\scriptsize\color{orange!70}] {pointe vers le cadre};

  % Adresses
  \node[font=\tiny, gray] at (8.2,3.8) {0xFFFF};
  \node[font=\tiny, gray] at (8.2,-3.5) {0x0000};
\end{tikzpicture}
\end{center}
```
