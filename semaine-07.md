# Semaine 07 — 2026-03-31

## [semaphores] Sémaphores

Un sémaphore est un compteur synchronisé utilisé pour contrôler l'accès à une ressource partagée dans un environnement concurrent. Il peut être utilisé pour résoudre des problèmes de synchronisation tels que les conditions de course.
Un sémaphore expose typiquement trois opérations : initialiser, `P`/`wait` (décrémenter ou bloquer si la valeur est déjà à 0) et `V`/`post` (incrémenter et réveiller un thread en attente). 
![Schéma de sémaphore](assets/2147d6c6ab884c6dc8ae477cb2b16ed7.png){width=200px}


### Pourquoi deux sémaphores ? Le problème producteur-consommateur

Pour résoudre ce problème avec un tampon borné, on utilise ici deux sémaphores de comptage :
- `places_libres`, initialisé à `FRIGO_MAX`, qui représente le nombre de places encore disponibles ;
- `bieres_dispo`, initialisé à `0`, qui représente le nombre de bières déjà présentes.

Le producteur doit attendre qu'il reste au moins une place libre avant d'ajouter une bière. Le consommateur doit attendre qu'au moins une bière soit disponible avant d'en retirer une. Ces deux sémaphores suffisent dans cet exemple parce qu'on ne manipule qu'un simple compteur logique de contenu. Dans une version plus générale avec un vrai buffer partagé et plusieurs producteurs/consommateurs, on ajoute souvent aussi un `mutex` pour protéger l'accès à la structure de données.

On a besoin de deux sémaphores car il faut représenter deux conditions différentes : 
le producteur doit être bloqué si le frigo est plein, et le consommateur doit être bloqué si le frigo est vide.

### Implémentation en C++
Voici une implémentation simple du problème producteur-consommateur en C++ utilisant des sémaphores :

```cpp
#include <semaphore.h>
#include <pthread.h>
#include <stdio.h>

#define FRIGO_MAX 12

sem_t places_libres;
sem_t bieres_dispo;

void* acheteur(void* arg) {
    while (1) {
        sem_wait(&places_libres); // -1 (Proberen)
        acheter_biere_au_landi();
        traverser_couloir();
        mettre_biere_dans_frigo();
        sem_post(&bieres_dispo); // +1 (Verhogen, signaler)
    }
    return NULL;
}
void* buveur(void* arg) {
    while (1) {
        sem_wait(&bieres_dispo); // -1 (Proberen, attendre une bière)
        traverser_couloir();
        prendre_biere_dans_frigo();
        sem_post(&places_libres);
        boire_biere();
    }
    return NULL;
}

int main() {
    pthread_t t_acheteur, t_buveur;

    sem_init(&places_libres, 0, FRIGO_MAX);
    sem_init(&bieres_dispo,  0, 0);

    pthread_create(&t_acheteur, NULL, acheteur, NULL);
    pthread_create(&t_buveur,   NULL, buveur,   NULL);

    pthread_join(t_acheteur, NULL);
    pthread_join(t_buveur,   NULL);

    sem_destroy(&places_libres);
    sem_destroy(&bieres_dispo);

    return 0;
}
```

Et avec sémaphores C++20 :

```cpp
#include <semaphore>
#include <thread>

constexpr int FRIGO_MAX = 12;
std::counting_semaphore<FRIGO_MAX> places_libres(FRIGO_MAX);
std::counting_semaphore<FRIGO_MAX> bieres_dispo(0);

void acheteur() {
    while (true) {
        places_libres.acquire();
        acheter_biere_au_landi();
        mettre_biere_dans_frigo();
        bieres_dispo.release();
    }
}

void buveur() {
    while (true) {
        bieres_dispo.acquire();
        prendre_biere_dans_frigo();
        places_libres.release();
        boire_biere();
    }
}

int main() {
    std::jthread t_acheteur(acheteur);
    std::jthread t_buveur(buveur);
}
```

Ou avec variable conditionnelle :

```cpp
#include <condition_variable>
#include <mutex>

std::mutex m;
std::condition_variable cv;
int bieres = 0;
constexpr int FRIGO_MAX = 12;

void acheteur() {
    std::unique_lock<std::mutex> lock(m);
    cv.wait(lock, [] { return bieres < FRIGO_MAX; });
    ++bieres;
    cv.notify_one();
}

void buveur() {
    std::unique_lock<std::mutex> lock(m);
    cv.wait(lock, [] { return bieres > 0; });
    --bieres;
    cv.notify_one();
}
```


### Test-and-set

Cette technique permet de vérifier et de modifier une variable atomiquement. Elle est souvent utilisée pour implémenter des verrous (locks) et des sémaphores. L'idée est de tester la valeur d'une variable et de la mettre à jour en une seule opération atomique, ce qui évite les conditions de course.

