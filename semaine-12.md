# Semaine 12 — 2026-05-12

## [introduction] Terminologie et concepts de base

### Section Critique (Critical Section)

Une section critique est une partie d'un programme qui accède à une ressource partagée (comme une variable, un fichier, ou une base de données) qui ne peut être utilisée que par un processus ou un thread à la fois. L'objectif de la section critique est de protéger cette ressource contre les accès concurrents qui pourraient entraîner des conditions de course, des incohérences ou des erreurs.

On utilise par exemple des mutex, des sémaphores ou des **moniteurs** pour gérer l'accès à la section critique et assurer que les processus ou threads accèdent à la ressource partagée de manière ordonnée et sécurisée.

### Condition de course (Race Condition)

Une condition de course se produit lorsque le comportement d'un programme dépend de l'ordre ou du timing des événements, comme l'accès concurrent à une ressource partagée. Si deux ou plusieurs processus ou threads accèdent à la même ressource sans synchronisation adéquate, cela peut entraîner des résultats imprévisibles ou incorrects.

### Deadlock (Interblocage)

Un deadlock, ou interblocage, se produit lorsque deux ou plusieurs processus ou threads sont bloqués indéfiniment, chacun attendant que l'autre libère une ressource dont il a besoin pour continuer. Cela peut se produire dans des situations où les processus ou threads détiennent des ressources et attendent d'autres ressources détenues par d'autres processus ou threads. Cela peut arriver si par exemple un mutex est verrouillé par un thread et qu'un autre thread attend ce mutex pour continuer, tandis que le premier thread attend une ressource détenue par le second thread.

### Starvation (Famine)

La starvation, ou famine, se produit lorsqu'un processus ou thread ne parvient pas à accéder à une ressource partagée pendant une période prolongée en raison de la concurrence avec d'autres processus ou threads. Cela peut se produire si un processus ou thread est constamment préempté par d'autres processus ou threads qui ont une priorité plus élevée, ou si les ressources sont allouées de manière injuste.

### Exclusion Mutuelle (Mutual Exclusion)

L'exclusion mutuelle est un principe de synchronisation qui garantit que lorsqu'un processus ou thread accède à une ressource partagée, aucun autre processus ou thread ne peut accéder à cette ressource en même temps. 

- Mutex (`std::mutex` en C++)
  - `std::lock_guard` pour une gestion automatique du verrouillage et du déverrouillage
  - `std::unique_lock` pour une gestion plus flexible du verrouillage, permettant de déverrouiller et de relock à volonté 
- Sémaphore
- Variable de condition (`std::condition_variable` en C++)
- Moniteur (Monitor)

### Atomicité

L'atomicité est une propriété d'une opération ou d'un ensemble d'opérations qui garantit qu'elles sont indivisibles. Cela signifie que lorsque l'opération est en cours d'exécution, elle ne peut pas être interrompue par un autre processus ou thread. Les opérations atomiques sont essentielles pour garantir la cohérence des données dans les environnements concurrents.

```cpp
std::atomic<int> counter(0);

void increment() {
    counter++;
}
```

### Moniteur

Un moniteur est un mécanisme de synchronisation qui combine un mutex et des variables de condition. Il permet de gérer l'accès à une ressource partagée de manière sécurisée et de coordonner les opérations entre différents threads. Il exploite la notion de RAII (Resource Acquisition Is Initialization) pour garantir que les ressources sont correctement libérées même en cas d'exception.

En résumé un moniteur est une classe qui gère elle-même son propre mutex et ses propres variables de condition pour synchroniser l'accès à ses méthodes et à ses données membres. Les threads peuvent appeler les méthodes du moniteur pour accéder à la ressource partagée, et le moniteur s'assure que les accès sont exclusifs et que les threads sont correctement synchronisés.

