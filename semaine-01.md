# Semaine 1 — 2026-02-17

## [introduction] Liste des connaissances

- Processeur
  - CPU (Central Processing Unit)
  - MCU (Microcontroller Unit)
  - GPU (Graphics Processing Unit)
- Mémoire
  - Mémoire VIVE (RAM)
  - Mémoire MORTE (ROM)
- Entrées/Sorties
- Horloge
- Bus de communication
- Interruption
- PSU (Power Supply Unit)
- Transistor
- ALU (Arithmetic Logic Unit)
- Registre
- Timers

### RISC vs CISC

- **RISC** : peu d'instructions, beaucoup de place dans les registres, instructions simples et rapides
- **CISC** : plein d'instructions, peu de place dans les registres, instructions complexes et lentes

## [hardware] Ordinateurs et systèmes d'exploitation

### RAM

```{=latex}
\begin{center}
\begin{tikzpicture}[
  block/.style={draw, thick, rounded corners=3pt, minimum width=1.6cm, minimum height=2.4cm, font=\bfseries\large},
  buslabel/.style={font=\small\bfseries, fill=white, inner sep=2pt},
]
  \node[block] (ram)  at (0,0)   {RAM};
  \node[block] (ctrl) at (5.5,0) {CTRL};
  \node[block] (cpu)  at (9.5,0) {CPU};

  % Bus d'adresses (A) — CTRL vers RAM
  \draw[thick, Latex-Latex] (4.7,0.5) -- node[buslabel, above] {A (adresses)} (0.8,0.5);

  % Bus de données (D) — bidirectionnel
  \draw[thick, Latex-Latex] (0.8,-0.5) -- node[buslabel, below] {D (données)} (4.7,-0.5);

  % Lien CTRL — CPU (double trait)
  \draw[thick, Latex-Latex] (6.3,0.3) -- (8.7,0.3);
  \draw[thick, Latex-Latex] (6.3,-0.3) -- (8.7,-0.3);
\end{tikzpicture}
\end{center}
```

La RAM est une mémoire volatile utilisée pour stocker les données et les programmes en cours d'exécution. Elle est rapide mais perd son contenu lorsque l'alimentation est coupée.
Plus la taille de la mémoire est petite, plus les données sont rapidement accessibles. Cependant, elle s'efface plus rapidement que les mémoires plus grandes.
On rafraicith la RAM en la réécrivant régulièrement pour éviter qu'elle ne perde son contenu, toute les 64ms environ.

- VDD : alimentation
- VSS : masse 

### Chipset
Le chipset est un ensemble de circuits intégrés qui gèrent les communications entre le processeur, la mémoire et les périphériques. Il est responsable de la gestion des entrées/sorties, de la mémoire et des interruptions.
Il est composé de deux parties :

- Northbridge : gère les communications entre le processeur, la mémoire et les cartes graphiques
- Southbridge : gère les communications entre les périphériques d'entrée/sortie

De nos jours, le chipset est souvent intégré dans le processeur lui-même, ce qui permet une communication plus rapide entre les composants.

### Système d'exploitation
Le système d'exploitation est un logiciel qui gère les ressources matérielles de l'ordinateur et fournit des services aux programmes. Il est responsable de la gestion de la mémoire, des processus, des fichiers et des périphériques.
Il existe différents types de systèmes d'exploitation, tels que Windows, macOS, Linux, etc. Chacun a ses propres caractéristiques et avantages, mais tous ont pour objectif de permettre aux utilisateurs d'interagir avec l'ordinateur de manière efficace et sécurisée.


