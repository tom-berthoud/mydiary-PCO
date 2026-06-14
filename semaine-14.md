# Semaine 14 — 2026-05-27

## [openmp] OpenMP

OpenMP (Open Multi-Processing) est une API (Application Programming Interface) qui permet de paralléliser des programmes en utilisant des directives de compilation. Elle est principalement utilisée pour le parallélisme de données, où les tâches sont divisées en morceaux plus petits qui peuvent être exécutés simultanément sur plusieurs threads.

```cpp
#include <omp.h>
#include <iostream>

int main() {
    #pragma omp parallel // Le prochain bloc de code sera exécuté en parallèle par plusieurs threads
    {
        int thread_id = omp_get_thread_num();
        std::cout << "Hello from thread " << thread_id << std::endl;

    }
    return 0;
}
```

À la compilation, il faut activer OpenMP avec `-fopenmp` (sinon les `#pragma` sont simplement ignorés et le code tourne en séquentiel) :

```bash
g++ -fopenmp -O2 hello.cpp -o hello
```

> **Note perso.** On n'a fait que survoler OpenMP en une fois, mais c'est une bibliothèque vraiment intéressante qui vaut le coup d'y revenir et d'étoffer ces notes. Là où `std::thread` demande de tout gérer à la main (création, `join`, mutex, partage), OpenMP fait la même chose en **une ligne de pragma**, sans toucher à la logique du code. C'est un outil très utilisé en pratique (calcul scientifique, traitement d'image, simulation, HPC) — à reprendre tranquillement pour creuser `tasks`, `sections`, le `nowait`, etc.

### `parallel for` — paralléliser une boucle

Le cas le plus courant : répartir automatiquement les itérations d'une boucle sur les threads. Aucune dépendance entre les itérations n'est requise (sinon condition de course).

```cpp
#include <omp.h>
#include <vector>

int main() {
    std::vector<double> v(1'000'000);

    #pragma omp parallel for
    for (size_t i = 0; i < v.size(); ++i) {
        v[i] = i * 2.0;   // chaque itération est indépendante
    }
}
```

OpenMP découpe la plage `[0, size)` en blocs et donne un bloc à chaque thread. C'est l'équivalent « gratuit » du découpage en bandes qu'on faisait à la main dans le labo Mandelbrot.

### `reduction` — le piège de la somme partagée

Si plusieurs threads accumulent dans une même variable, on retombe sur la race condition vue avec `counter`. La clause `reduction` règle ça proprement : chaque thread a sa **copie privée**, et OpenMP combine les copies à la fin.

```cpp
double sum = 0.0;

#pragma omp parallel for reduction(+:sum)
for (size_t i = 0; i < v.size(); ++i) {
    sum += v[i];        // pas de race : chaque thread accumule dans sa copie
}
// sum contient le total correct, sans mutex
```

Sans `reduction(+:sum)`, le résultat serait faux (incréments perdus) — exactement le problème du compteur sans mutex.

### `critical` et `atomic` — section critique

Quand une opération ne peut pas être exprimée en `reduction`, on protège la section partagée. `critical` est l'équivalent OpenMP d'un mutex ; `atomic` est plus léger mais limité aux opérations simples (`++`, `+=`…).

```cpp
#pragma omp parallel for
for (int i = 0; i < n; ++i) {
    int r = compute(i);
    #pragma omp critical      // un seul thread à la fois ici
    {
        results.push_back(r);
    }
}
```

### `schedule` et `num_threads`

On peut régler la répartition du travail et le nombre de threads :

```cpp
#pragma omp parallel for num_threads(4) schedule(dynamic, 100)
for (int i = 0; i < n; ++i) { heavy_work(i); }
```

| Clause | Effet |
|:----|:-------------|
| `schedule(static)` | blocs égaux fixés à l'avance — idéal si chaque itération coûte pareil |
| `schedule(dynamic, k)` | les threads piochent des paquets de `k` itérations à la demande — idéal si le coût varie (ex. Mandelbrot) |
| `num_threads(n)` | force `n` threads pour cette région |

`schedule(dynamic)` joue le même rôle que le *decomposition factor* du thread pool du labo Mandelbrot : il évite qu'un thread tombé sur une zone « lourde » devienne le goulot pendant que les autres ont fini.

## [async] thread vs async

- `std::thread` : Permet de créer et de gérer des threads manuellement. Vous devez gérer la synchronisation, la communication entre les threads, et vous assurer que les threads sont correctement joints ou détachés.
- `std::async` : Fournit une interface plus haut niveau pour exécuter des tâches de manière asynchrone. Il gère automatiquement la création et la gestion des threads, ainsi que la synchronisation des résultats à l'aide de `std::future`. C'est souvent plus simple à utiliser que `std::thread` pour les tâches qui nécessitent un résultat ou une synchronisation.
  
## promise et future

- `std::promise` : Permet de stocker une valeur qui sera disponible à un moment donné dans le futur. Il est utilisé pour communiquer des résultats entre threads.
- `std::future` : Permet de récupérer la valeur stockée dans une `std::promise`. Il est utilisé pour attendre et obtenir le résultat d'une opération asynchrone.


```cpp
#include <iostream>
#include <thread>
#include <future>

void worker(std::promise<int> p) {
    // Simuler un travail
    std::this_thread::sleep_for(std::chrono::seconds(2));
    p.set_value(42); // Stocker le résultat dans la promise
}

int main() {
    std::promise<int> p;
    std::future<int> f = p.get_future(); // Obtenir le future associé à la promise

    std::thread t(worker, std::move(p)); // Lancer le thread avec la promise

    std::cout << "Waiting for result..." << std::endl;
    int result = f.get(); // Attendre et récupérer le résultat de la promise
    std::cout << "Result: " << result << std::endl;

    t.join(); // Attendre que le thread se termine
    return 0;
}
```
On ne peut pas écrire dans une `std::future` directement, car elle est conçue pour être un objet de lecture seule qui reçoit sa valeur d'une `std::promise`. La `std::promise` est l'objet qui permet de stocker une valeur qui sera accessible via la `std::future`. La `std::future` est utilisée pour récupérer la valeur une fois qu'elle a été définie dans la `std::promise`. Cela garantit une séparation claire entre la production et la consommation de la valeur, et permet une synchronisation efficace entre les threads.
Une `std::promise` ne peut pas être copiée, mais elle peut être déplacée (move). Cela signifie que vous pouvez transférer la propriété d'une `std::promise` d'un thread à un autre, mais vous ne pouvez pas en créer une copie. C'est pourquoi dans l'exemple ci-dessus, nous utilisons `std::move(p)` pour passer la `std::promise` au thread worker.
