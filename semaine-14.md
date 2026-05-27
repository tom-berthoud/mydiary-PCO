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
## [async] thread vs async

- `std::thread` : Permet de créer et de gérer des threads manuellement. Vous devez gérer la synchronisation, la communication entre les threads, et vous assurer que les threads sont correctement joints ou détachés.
- `std::async` : Fournit une interface plus haut niveau pour exécuter des tâches de manière asynchrone. Il gère automatiquement la création et la gestion des threads, ainsi que la synchronisation des résultats à l'aide de `std::future`. C'est souvent plus simple à utiliser que `std::thread` pour les tâches qui nécessitent un résultat ou une synchronisation.
  








