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
On ne peut pas écrire dans une `std::future` directement, car elle est conçue pour être un objet de lecture seule qui reçoit sa valeur d'une `std::promise`. La `std::promise` est l'objet qui permet de stocker une valeur qui sera accessible via la `std::future`. La `std::future` est utilisée pour récupérer la valeur une fois qu'elle a été définiee dans la `std::promise`. Cela garantit une séparation claire entre la production et la consommation de la valeur, et permet une synchronisation efficace entre les threads.
Une `std::promise` ne peut pas être copiée, mais elle peut être déplacée (move). Cela signifie que vous pouvez transférer la propriété d'une `std::promise` d'un thread à un autre, mais vous ne pouvez pas en créer une copie. C'est pourquoi dans l'exemple ci-dessus, nous utilisons `std::move(p)` pour passer la `std::promise` au thread worker.
