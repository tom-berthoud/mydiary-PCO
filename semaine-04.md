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

## Création de threads avec pthreads

La manière la plus courante de créer des threads en C est d'utiliser la bibliothèque POSIX Threads appelée pthread.

Bibliothèque :

```c
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

void* thread_function(void* arg) {
    int thread_id = *((int*)arg);
    printf("Hello from thread %d\n", thread_id);
    return NULL;
}

int main() {
    pthread_t threads[5];
    int thread_ids[5];

    for (int i = 0; i < 5; i++) {
        thread_ids[i] = i + 1;
        pthread_create(&threads[i], NULL, thread_function, &thread_ids[i]);
    }

    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}
```

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

\begin{center}
\begin{tikzpicture}[
  proc/.style={draw, thick, minimum width=4.6cm, minimum height=3.2cm},
  mem/.style={draw, thick, minimum width=1.3cm, minimum height=4.0cm},
  mmu/.style={draw, thick, minimum width=2.0cm, minimum height=1.2cm, align=center},
  box/.style={draw, thick, minimum width=2.0cm, minimum height=2.2cm},
  lab/.style={font=\bfseries},
  arr/.style={->, thick, >=Latex},
  map/.style={->, thick, rounded corners=4pt, >=Latex}
]
  % Processus
  \node[proc] (procA) at (0,3.0) {};
  \node[lab] at (-1.2,3.2) {A};
  \node[proc] (procB) at (0,-2.1) {};
  \node[lab] at (-1.2,-1.9) {B};

  % Structures internes des processus
  \draw[thick] (0.9,4.2) rectangle (1.5,2.0);
  \draw[thick] (0.9,3.8) -- (1.5,3.8);
  \draw[thick] (0.9,3.4) -- (1.5,3.4);
  \draw[thick] (0.9,3.0) -- (1.5,3.0);
  \draw[thick] (0.9,2.6) -- (1.5,2.6);

  \draw[thick] (0.9,-0.9) rectangle (1.5,-3.1);
  \draw[thick] (0.9,-1.3) -- (1.5,-1.3);
  \draw[thick] (0.9,-1.7) -- (1.5,-1.7);
  \draw[thick] (0.9,-2.1) -- (1.5,-2.1);
  \draw[thick] (0.9,-2.5) -- (1.5,-2.5);

  % Mémoire virtuelle
  \node[mem] (virtA) at (7.0,3.0) {};
  \node[mem] (virtB) at (7.0,-2.1) {};
  \node[lab] at (7.0,5.4) {Virtual Memory};

  \draw[thick] (6.35,3.4) -- (7.65,3.4);
  \draw[thick] (6.35,3.25) -- (7.65,3.25);
  \draw[thick] (6.35,3.1) -- (7.65,3.1);

  \draw[thick] (6.35,-1.7) -- (7.65,-1.7);
  \draw[thick] (6.35,-1.85) -- (7.65,-1.85);
  \draw[thick] (6.35,-2.0) -- (7.65,-2.0);

  % MMU et table
  \node[mmu] (mmu) at (11.0,2.8) {MMU};
  \node[box] (ptable) at (11.0,-0.8) {};
  \draw[thick] (10.55,-0.65) rectangle (11.05,-0.15);
  \draw[thick] (11.25,-0.65) rectangle (11.75,-0.15);
  \draw[arr] (11.05,-0.4) -- (11.25,-0.4);

  % Mémoire physique
  \node[mem, minimum height=6.8cm] (phys) at (14.8,0.35) {};
  \node[lab] at (14.8,5.4) {Physical Memory};
  \draw[thick] (14.15,3.2) -- (15.45,3.2);
  \draw[thick] (14.15,3.05) -- (15.45,3.05);
  \draw[thick] (14.15,2.9) -- (15.45,2.9);
  \draw[thick] (14.15,-0.4) -- (15.45,-0.4);
  \draw[thick] (14.15,-0.55) -- (15.45,-0.55);
  \draw[thick] (14.15,-0.7) -- (15.45,-0.7);

  % Flèches et annotations
  \draw[map] (1.55,3.6) .. controls (3.4,4.4) and (4.8,4.2) .. node[above] {0x7fffeude} (6.2,3.45);
  \draw[map] (1.55,-1.6) .. controls (3.4,-0.8) and (4.8,-1.0) .. node[above] {0x7fffeude} (6.2,-1.75);

  \draw[arr] (7.65,3.2) -- (9.95,3.0);
  \draw[arr] (7.65,-1.85) .. controls (8.7,-1.85) and (9.4,-0.6) .. (10.0,-0.5);
  \draw[arr] (12.0,2.8) .. controls (13.0,2.8) and (13.3,3.2) .. (14.1,3.05);
  \draw[arr] (12.0,-0.8) .. controls (13.0,-0.8) and (13.3,-0.4) .. (14.1,-0.55);
  \draw[thick] (11.0,1.7) -- (11.0,0.35);
\end{tikzpicture}
\end{center}

Ce schéma illustre que deux processus distincts peuvent utiliser la même adresse virtuelle apparente, alors que la MMU la traduit vers des emplacements physiques différents.
