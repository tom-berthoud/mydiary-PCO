# Semaine 15 — 2026-06-02

## [async] Exemples d'utilisation de `std::async`

```cpp
#include <vector>
#include <iostream>
#include <cmath>
#include <future>
 
double compute(const std::vector<double>& data, size_t start, size_t end) {
    double sum = 0.;
    for (size_t i = start; i < end; ++i)
        sum += std::sqrt(data[i] * std::sin(data[i]));
    std::cout << "J'ai fini\n";
    return sum;
}
 
int main() {
    std::vector<double> data(10'000'000, 2.0);
    size_t half = data.size() / 2;
 
    std::future<double> f = std::async(std::launch::async, compute, std::cref(data), 0, half);
 
    double part_high = compute(data, half, data.size());
 
    std::cout << (f.get() + part_high) << "\n";
}
```
## [performance] Loi de Amdahl

La loi de Amdahl est une formule qui permet d'estimer le gain de performance d'un programme lorsqu'on parallélise une partie de son code. Elle s'exprime comme suit :

$$
\boxed{
S(n) = \frac{1}{(1 - P) + \frac{P}{n}}
}
$$

où :

- \(S(n)\) est le gain de performance avec \(n\) processeurs ou threads ;
- \(P\) est la proportion du programme qui est parallélisable ;
- \(1 - P\) est la partie qui reste séquentielle.

Par exemple, si 80% du code est parallélisable (\(P = 0.8\)) et 20% est séquentiel, alors le gain de performance avec 16 threads serait :

$$
S(16)
= \frac{1}{(1 - 0.8) + \frac{0.8}{16}}
= \frac{1}{0.2 + 0.05}
= 4
$$

Avec un nombre infini de threads, la partie parallélisable devient négligeable :

$$
S_{\max}
= \lim_{n \to \infty} S(n)
= \frac{1}{(1 - 0.8) + \frac{0.8}{\infty}}
= \frac{1}{0.2}
= 5
$$

La comparaison montre qu'avec 16 threads on obtient déjà un speedup de 4, mais que le maximum théorique reste limité à 5 à cause de la partie séquentielle. La loi de Amdahl souligne donc l'importance de minimiser la partie séquentielle d'un programme pour maximiser les gains de performance lors du parallélisme.


## [synchronisation] Barrières de synchronisation

Une Barrier est un mécanisme de synchronisation qui permet à un groupe de threads d'attendre que tous les membres du groupe atteignent un certain point d'exécution avant de continuer. C'est particulièrement utile dans les algorithmes parallèles où les threads doivent se synchroniser à des étapes spécifiques.

En C++20, la classe `std::barrier` fournit une implémentation de ce concept. Voici un exemple d'utilisation :

```cpp
#include <barrier>
#include <iostream>
#include <string>
#include <syncstream>
#include <thread>
#include <vector>
 
int main()
{
    const auto workers = {"Anil", "Busara", "Carl"};
 
    auto on_completion = []() noexcept
    {
        // locking not needed here
        static auto phase =
            "... done\n"
            "Cleaning up...\n";
        std::cout << phase;
        phase = "... done\n";
    };
 
    std::barrier sync_point(std::ssize(workers), on_completion);
 
    auto work = [&](std::string name)
    {
        std::string product = "  " + name + " worked\n";
        std::osyncstream(std::cout) << product;  // ok, op<< call is atomic
        sync_point.arrive_and_wait();
 
        product = "  " + name + " cleaned\n";
        std::osyncstream(std::cout) << product;
        sync_point.arrive_and_wait();
    };
 
    std::cout << "Starting...\n";
    std::vector<std::jthread> threads;
    threads.reserve(std::size(workers));
    for (auto const& worker : workers)
        threads.emplace_back(work, worker);
}
```

## [hardware] Anatomie d'un processeur multicœur

Un processeur moderne regroupe sur une même puce plusieurs **cœurs** d'exécution indépendants, capables de faire tourner des threads en parallèle. Chaque cœur possède ses caches privés (L1, L2), tandis qu'un grand **cache L3 partagé** sert de point de cohérence entre tous les cœurs. Autour des cœurs, l'« uncore » intègre les contrôleurs mémoire (DDR5), les liens d'E/S (PCIe, DMI/QPI, USB) et un agent système (gestion d'alimentation, capteurs de tension/température, horloges, contrôleur d'interruptions APIC).

![Die shot d'un processeur multicœur : on distingue les blocs de cœurs réguliers et les zones de cache.](assets/dieshot.png){width=65%}
