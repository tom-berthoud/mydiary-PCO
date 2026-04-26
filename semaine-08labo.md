# Semaine 08 — 2026-04-14

## [threads] Thread Pool

### Le problème : créer un thread coûte cher

Lancer un `std::thread` n'est pas gratuit. Le système doit allouer une pile (typiquement 1 à 8 Mo), enregistrer le thread auprès du scheduler et faire un appel système. Sur le labo Mandelbrot, si on découpe l'image en `N` bandes et qu'on crée un `std::thread` par bande, deux scénarios sont mauvais :

- **Trop peu de bandes** (`N` = nombre de threads physiques) : si une bande tombe sur une zone très "lourde" (beaucoup d'itérations), un thread bosse pendant que les autres ont fini. Mauvaise répartition.
- **Trop de bandes** (`N` = 80, 100, 1000…) : on amortit mal le coût de création/destruction des threads. On passe plus de temps à créer des threads qu'à calculer.

Le **thread pool** résout ce dilemme : on crée `N` threads une seule fois au démarrage, et on leur fait consommer une queue de tâches beaucoup plus fine. Ainsi le découpage du travail est indépendant du nombre de threads.

### Pattern Master/Worker

```{=latex}
\begin{center}
\begin{tikzpicture}[
  node distance=1.2cm,
  every node/.style={font=\small},
  worker/.style={draw, rounded corners, minimum width=1.6cm, minimum height=0.8cm, fill=blue!10},
  task/.style={draw, minimum width=0.5cm, minimum height=0.5cm, fill=orange!30},
  master/.style={draw, rounded corners, minimum width=1.8cm, minimum height=0.8cm, fill=green!15}
]
  \node[master] (m) {Master};
  \node[draw, rounded corners, right=1.2cm of m, minimum height=0.9cm] (q) {
    \begin{tikzpicture}
      \node[task] {T1}; \node[task, right=0.05cm] (t2) {T2};
      \node[task, right=0.05cm of t2] {T3};
    \end{tikzpicture}
  };
  \node[above=0cm of q, font=\footnotesize] {queue de tâches};

  \node[worker, right=1.5cm of q, yshift=0.9cm]  (w1) {Worker 1};
  \node[worker, right=1.5cm of q]                (w2) {Worker 2};
  \node[worker, right=1.5cm of q, yshift=-0.9cm] (w3) {Worker 3};

  \draw[->] (m) -- node[above, font=\footnotesize] {enqueue} (q);
  \draw[->] (q) -- (w1);
  \draw[->] (q) -- (w2);
  \draw[->] (q) -- (w3);
\end{tikzpicture}
\end{center}
```

Le **master** pousse des tâches dans la queue, les **workers** dorment sur une `condition_variable` et se réveillent quand une tâche arrive. Quand la queue est vide, ils retournent dormir.

### Implémentation minimale en C++

Le code ci-dessous est celui de `threadpool.hpp` du labo Mandelbrot (branches `pool2`, `pixelshader`).

```cpp
#include <condition_variable>
#include <functional>
#include <mutex>
#include <queue>
#include <thread>
#include <vector>

class ThreadPool {
public:
  explicit ThreadPool(size_t numThreads) : stop(false), activeTasks(0) {
    for (size_t i = 0; i < numThreads; ++i) {
      workers.emplace_back([this] {
        while (true) {
          std::function<void()> task;
          {
            std::unique_lock<std::mutex> lock(queueMutex);
            condition.wait(lock, [this] { return stop || !tasks.empty(); });
            if (stop && tasks.empty()) return;
            task = std::move(tasks.front());
            tasks.pop();
            ++activeTasks;
          }
          task();
          {
            std::unique_lock<std::mutex> lock(queueMutex);
            --activeTasks;
          }
          condition.notify_all();
        }
      });
    }
  }

  void enqueue(std::function<void()> task) {
    {
      std::unique_lock<std::mutex> lock(queueMutex);
      tasks.push(std::move(task));
    }
    condition.notify_one();
  }

  void waitAll() {
    std::unique_lock<std::mutex> lock(queueMutex);
    condition.wait(lock, [this] {
        return tasks.empty() && activeTasks == 0;
    });
  }

  ~ThreadPool() {
    {
      std::unique_lock<std::mutex> lock(queueMutex);
      stop = true;
    }
    condition.notify_all();
    for (auto &worker : workers) worker.join();
  }

private:
  std::vector<std::thread> workers;
  std::queue<std::function<void()>> tasks;
  std::mutex queueMutex;
  std::condition_variable condition;
  bool stop;
  int activeTasks;
};
```

### Points clés

- **`queueMutex`** protège à la fois `tasks`, `stop` et `activeTasks`. Toute lecture/écriture de ces variables se fait sous ce mutex.
- **`condition.wait(lock, predicate)`** libère le mutex pendant l'attente et le reprend au réveil. Le prédicat évite les *spurious wakeups* (réveils sans cause).
- **`activeTasks`** distingue "queue vide" de "tout est fini". Sans ce compteur, `waitAll()` reviendrait dès que la queue est vide, alors que des workers sont peut-être encore en train d'exécuter une tâche.
- **`notify_one`** sur `enqueue` (un seul worker à réveiller), **`notify_all`** sur la fin d'une tâche (`waitAll` doit être réveillé) et au shutdown.
- Le destructeur fait un *graceful shutdown* : flag `stop`, `notify_all`, `join` de tous les workers. Les tâches encore en queue ne sont **pas** exécutées (le worker quitte si `stop && tasks.empty()`).

### Application sur Mandelbrot

Au lieu de créer `t` threads pour `t` bandes, on découpe l'image en `t × decomposition_factor` bandes plus fines et on les pousse toutes dans le pool. Les workers se les arrachent au fur et à mesure. Une bande "lourde" ne bloque plus tout le calcul.

```cpp
int decomposition_factor = 10;
int total = threads * decomposition_factor;

ThreadPool pool(threads);
auto dv = std::div((int)ctx.height, total);
int start = 0;
for (int i = 0; i < total; ++i) {
    int end = start + dv.quot + (i == total - 1 ? dv.rem : 0);
    pool.enqueue([start, end, &data, &ctx, i] {
        fillMandelbrotRegion(start, end, data.data(), ctx, i);
    });
    start = end;
}
pool.waitAll();
```

### Alternative : `boost::asio::thread_pool`

La bibliothèque Boost fournit déjà la même chose. Mon `mandelbrot.cpp` actuel l'utilise :

```cpp
#include <boost/asio/thread_pool.hpp>
#include <boost/asio/post.hpp>

boost::asio::thread_pool pool(threads);
boost::asio::post(pool, [&] { fillMandelbrotRegion(...); });
pool.wait();
```

Avantages : code testé, gère plus finement le shutdown, intègre les opérations asynchrones d'`asio` (réseau, timers). Inconvénient : dépendance lourde, moins pédagogique.

### Pourquoi le decomposition factor améliore le speedup

Sans décomposition (`factor = 1`), si une bande contient une zone dense (proche de la frontière de Mandelbrot, où on va jusqu'à `iterations` max), ce thread devient le goulot. Tous les autres ont fini et l'attendent. Avec `factor = 10`, cette bande dense est elle-même découpée en 10 sous-bandes ; les autres workers se partagent les neuf restantes pendant que le premier traite la plus chère. Le speedup mesuré dans `report.ipynb` se rapproche du speedup linéaire idéal.

### Conclusion

Certe le thread pool permet d'être plus efficace mais il faut surtout ce rappeler que améliorer l'algorithme est souvent plus payant que d'améliorer la parallélisation. En effet, si on améliore l'algorithme de calcul de Mandelbrot pour qu'il soit plus rapide, on peut réduire le temps de calcul de manière significative sans même toucher à la parallélisation.