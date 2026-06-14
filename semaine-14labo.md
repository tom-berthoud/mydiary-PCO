# Semaine 14 labo — 2026-05-27

## [patrons] Producteur-consommateur et lecteurs-rédacteurs

La semaine 8 introduisait le **thread pool** : un master pousse des tâches dans une queue, et des workers les prennent dès qu'ils sont libres. Ce mécanisme est une application directe du patron **producteur-consommateur**. Deux patrons reviennent très souvent en programmation concurrente :

- **Producteur-consommateur** : découpler ceux qui créent du travail de ceux qui l'exécutent.
- **Lecteurs-rédacteurs** : permettre plusieurs lectures simultanées, mais garder l'écriture exclusive.

### Patron producteur-consommateur

Le problème : plusieurs threads produisent des éléments, plusieurs threads les consomment, et une zone partagée sert de tampon. Cette zone doit être protégée pour éviter les conditions de course, et les threads doivent dormir proprement quand il n'y a rien à faire.

```{=latex}
\begin{center}
\begin{tikzpicture}[
  >=Latex,
  every node/.style={font=\small},
  actor/.style={draw, rounded corners=5pt, minimum width=2.0cm, minimum height=0.75cm, align=center},
  buffer/.style={draw, rounded corners=5pt, minimum width=3.4cm, minimum height=1.05cm, align=center, fill=orange!12},
  item/.style={draw, minimum width=0.42cm, minimum height=0.42cm, fill=orange!35},
  note/.style={font=\footnotesize, align=center}
]
  \node[actor, fill=green!12] (p1) at (0, 0.75) {Producteur 1};
  \node[actor, fill=green!12] (p2) at (0,-0.75) {Producteur 2};

  \node[buffer] (b) at (4,0) {
    \begin{tikzpicture}[baseline=-0.5ex]
      \node[item] (i1) at (0,0) {};
      \node[item] (i2) at (0.5,0) {};
      \node[item] (i3) at (1.0,0) {};
      \node[item, fill=gray!12] (i4) at (1.5,0) {};
      \node[item, fill=gray!12] (i5) at (2.0,0) {};
    \end{tikzpicture}\\
    \footnotesize tampon borné
  };

  \node[actor, fill=blue!10] (c1) at (8, 0.75) {Consommateur 1};
  \node[actor, fill=blue!10] (c2) at (8,-0.75) {Consommateur 2};

  \draw[->, thick] (p1.east) -- node[above, note] {push} (b.west);
  \draw[->, thick] (p2.east) -- (b.west);
  \draw[->, thick] (b.east) -- node[above, note] {pop} (c1.west);
  \draw[->, thick] (b.east) -- (c2.west);

  \node[note, below=0.65cm of b] {
    mutex: protege la queue \quad
    not\_empty: reveille les consommateurs \quad
    not\_full: reveille les producteurs
  };
\end{tikzpicture}
\end{center}
```

Dans un thread pool, le **master** joue le rôle de producteur et les **workers** jouent le rôle de consommateurs. La queue de tâches est le tampon partagé. Si la queue est vide, les workers attendent sur une variable de condition ; quand une nouvelle tâche arrive, le master réveille un worker.

### Tampon borné avec moniteur

Un tampon borné impose une capacité maximale. Il faut donc gérer deux attentes :

- un producteur attend si le tampon est plein ;
- un consommateur attend si le tampon est vide.

```cpp
#include <condition_variable>
#include <cstddef>
#include <mutex>
#include <queue>
#include <utility>

template <typename T>
class BoundedBuffer {
public:
  explicit BoundedBuffer(size_t capacity) : capacity(capacity) {}

  void push(T value) {
    std::unique_lock<std::mutex> lock(mutex);
    notFull.wait(lock, [this] { return queue.size() < capacity; });

    queue.push(std::move(value));
    notEmpty.notify_one();
  }

  T pop() {
    std::unique_lock<std::mutex> lock(mutex);
    notEmpty.wait(lock, [this] { return !queue.empty(); });

    T value = std::move(queue.front());
    queue.pop();
    notFull.notify_one();
    return value;
  }

private:
  std::mutex mutex;
  std::condition_variable notEmpty;
  std::condition_variable notFull;
  std::queue<T> queue;
  size_t capacity;
};
```

Points importants :

- Les prédicats de `wait` sont indispensables : ils évitent les réveils inutiles et les *spurious wakeups*.
- Le mutex protège toujours la queue et la condition logique associée (`empty`, `full`, taille).
- `notify_one()` suffit souvent : une place libérée ne permet qu'à un producteur d'avancer, un élément ajouté ne permet qu'à un consommateur d'avancer.
- Si le tampon n'est pas borné, on peut supprimer `notFull`, mais on risque une croissance mémoire incontrôlée si les producteurs vont plus vite que les consommateurs.

### Patron lecteurs-rédacteurs

> **Note perso** Nous n'avons pas parlé de ce patron en cours, mais il est très utile pour les caches et les bases de données. Vu qu'il est également dans la fiche de cours, j'ai décidé de l'inclure dans ce résumé.

Le problème : une ressource partagée est très souvent lue et rarement modifiée. Si on utilise un simple `std::mutex`, même deux lectures indépendantes se bloquent mutuellement. Le patron lecteurs-rédacteurs autorise donc :

- plusieurs lecteurs en même temps ;
- un seul rédacteur ;
- aucun lecteur pendant qu'un rédacteur modifie la ressource.

```{=latex}
\begin{center}
\begin{tikzpicture}[
  >=Latex,
  every node/.style={font=\small},
  actor/.style={draw, rounded corners=5pt, minimum width=1.8cm, minimum height=0.7cm, align=center},
  resource/.style={draw, rounded corners=5pt, minimum width=2.6cm, minimum height=1.15cm, align=center, fill=yellow!15},
  note/.style={font=\footnotesize, align=center}
]
  \node[resource] (r) at (4,0) {Ressource\\partagée};

  \node[actor, fill=blue!10] (l1) at (0, 1.25) {Lecteur 1};
  \node[actor, fill=blue!10] (l2) at (0, 0.25) {Lecteur 2};
  \node[actor, fill=blue!10] (l3) at (0,-0.75) {Lecteur 3};
  \node[actor, fill=red!10]  (w)  at (9, 0) {Rédacteur};

  \draw[->, thick, blue!70!black] (l1.east) -- node[above right, note, xshift=-9] {read lock partagé} (r.west);
  \draw[->, thick, blue!70!black] (l2.east) -- (r.west);
  \draw[->, thick, blue!70!black] (l3.east) -- (r.west);

  \draw[->, thick, red!75!black] (w.west) -- node[above, note] {write lock exclusif} (r.east);

  \node[note, below=0.8cm of r] {
    Lecture: N threads en parallèle \quad
    Ecriture: 1 thread seul, aucun lecteur actif
  };
\end{tikzpicture}
\end{center}
```

En C++ moderne, le cas simple se code avec `std::shared_mutex` :

```cpp
#include <shared_mutex>
#include <string>
#include <unordered_map>
#include <mutex>
#include <utility>

class Cache {
public:
  std::string get(int key) const {
    std::shared_lock<std::shared_mutex> lock(mutex);
    return values.at(key);
  }

  void put(int key, std::string value) {
    std::unique_lock<std::shared_mutex> lock(mutex);
    values[key] = std::move(value);
  }

private:
  mutable std::shared_mutex mutex;
  std::unordered_map<int, std::string> values;
};
```

`std::shared_lock` prend un verrou partagé : plusieurs lecteurs peuvent le posséder en même temps. `std::unique_lock` prend le verrou exclusif : il bloque tant que des lecteurs sont actifs, puis empêche les nouveaux lecteurs d'entrer pendant l'écriture.
