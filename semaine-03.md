# Semaine 03 — 2026-03-03



## [processus] La fonction `fork`

La fonction `fork` est utilisée pour créer un nouveau processus en dupliquant le processus appelant. Le processus nouvellement créé est appelé processus enfant, tandis que le processus original est appelé processus parent.
Voici comment `fork` fonctionne :

1. Lorsque `fork` est appelé, le système d'exploitation crée une copie du processus parent, y compris son espace mémoire, ses descripteurs de fichiers et son état d'exécution.
2. Le processus enfant reçoit une copie de l'espace mémoire du parent, mais les deux processus ont des espaces mémoire séparés. Cela signifie que les modifications apportées à l'espace mémoire du parent n'affectent pas l'espace mémoire du processus enfant, et vice versa.
3. Après l'appel à `fork`, les deux processus (parent et enfant) continuent à s'exécuter à partir de l'instruction suivante à l'appel de `fork`. Cependant, ils peuvent différencier leur comportement en fonction de la valeur de retour de `fork` :
   - Si `fork` retourne une valeur de 0, cela signifie que le processus en cours d'exécution est le processus enfant.
   - Si `fork` retourne une valeur positive, cela signifie que le processus en cours d'exécution est le processus parent, et la valeur retournée est l'identifiant du processus enfant.
   - Si `fork` retourne une valeur négative, cela signifie qu'une erreur s'est produite lors de la création du processus enfant.

### exemple de code utilisant `fork`

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

int main() {
    pid_t pid = fork();

    if (pid < 0) {
        // Erreur lors de la création du processus enfant
        perror("fork failed");
        return 1;
    } else if (pid == 0) {
        // Code exécuté par le processus enfant
        printf("Je suis le processus enfant avec PID %d\n", getpid());
    } else {
        // Code exécuté par le processus parent
        printf("Je suis le processus parent avec PID %d, et mon enfant a PID %d\n", getpid(), pid);
    }

    return 0;
}
```



## [processus] La fonction `exec`

La fonction `exec` est utilisée pour remplacer l'image d'un processus en cours d'exécution par une nouvelle image de programme. Cela signifie que le processus actuel est remplacé par un nouveau programme, et que le code, les données et les ressources du processus sont remplacés par ceux du nouveau programme.
Voici comment `exec` fonctionne :

1. Lorsque `exec` est appelé, le processus actuel est remplacé par le nouveau programme spécifié dans les arguments de `exec`.
2. Le processus conserve son identifiant de processus (PID) et ses descripteurs de fichiers ouverts, mais son code, ses données et son état d'exécution sont remplacés par ceux du nouveau programme.
3. Après l'appel à `exec`, le processus continue à s'exécuter le nouveau programme à partir de son point d'entrée, et le code du processus original n'est plus exécuté.
4. Si `exec` réussit, il ne retourne jamais, car le processus est remplacé par le nouveau programme. Si `exec` échoue, il retourne une valeur négative pour indiquer une erreur.

### exemple de code utilisant `exec`

```c
#include <stdio.h>
#include <unistd.h>

int main() {
    // Exemple d'utilisation de exec
    execl("/bin/ls", "ls", NULL);
    // Si exec échoue, on arrive ici
    perror("execl failed");
    return 1;
}
```

## [processus] Les pipes 

Les pipes sont un mécanisme de communication inter-processus (IPC) qui permet à deux processus de communiquer entre eux en utilisant un flux de données unidirectionnel. Un pipe est créé à l'aide de la fonction `pipe`, qui crée un canal de communication entre deux processus.
Voici comment les pipes fonctionnent :

1. Lorsqu'un pipe est créé, il génère deux descripteurs de fichiers : un pour la lecture et un pour l'écriture. Le processus qui écrit dans le pipe utilise le descripteur d'écriture, tandis que le processus qui lit du pipe utilise le descripteur de lecture.
2. Les données écrites dans le pipe par le processus d'écriture sont stockées dans un tampon de mémoire géré par le système d'exploitation. Le processus de lecture peut lire les données à partir du pipe en utilisant le descripteur de lecture.
3. Les pipes sont unidirectionnels, ce qui signifie que les données ne peuvent être écrites que dans une direction (de l'écrivain vers le lecteur). Si les deux processus ont besoin de communiquer dans les deux sens, ils doivent créer deux pipes distincts.
4. Les pipes sont souvent utilisés pour permettre à un processus de produire des données qui sont ensuite consommées par un autre processus. Par exemple, un processus peut générer des données et les envoyer à un autre processus pour traitement, ou un processus peut exécuter une commande et envoyer sa sortie à un autre processus pour analyse.

### exemple de code utilisant les pipes

```c
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main() {
    int pipefd[2];
    char buffer[100];

    // Créer un pipe
    if (pipe(pipefd) == -1) {
        perror("pipe failed");
        return 1;
    }

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        return 1;
    } else if (pid == 0) {
        // Processus enfant : écrit dans le pipe
        close(pipefd[0]); // Fermer le descripteur de lecture
        const char *message = "Hello from the child process!";
        write(pipefd[1], message, strlen(message) + 1);
        close(pipefd[1]); // Fermer le descripteur d'écriture
    } else {
        // Processus parent : lit du pipe
        close(pipefd[1]); // Fermer le descripteur d'écriture
        read(pipefd[0], buffer, sizeof(buffer));
        printf("Message reçu du processus enfant: %s\n", buffer);
        close(pipefd[0]); // Fermer le descripteur de lecture
    }

    return 0;
}
```

## [processus] Les signaux

Les signaux sont un autre mécanisme de communication entre processus sous POSIX. Ils sont utilisés pour notifier un processus qu'un événement s'est produit et, le cas échéant, réveiller un processus dormant. Les signaux peuvent être envoyés par le noyau, par un autre processus, ou par le processus lui-même. Les signaux sont utilisés pour gérer les interruptions, les erreurs, et les événements asynchrones.

Voici une liste des signaux que nous allons voir :

- `SIGINT` : signal d'interruption, généralement envoyé lorsque l'utilisateur appuie sur `Ctrl+C`.
- `SIGQUIT` : signal de sortie, généralement envoyé lorsque l'utilisateur appuie sur `Ctrl+\`.
- `SIGKILL` : signal de terminaison forcée, qui ne peut pas être intercepté ou ignoré.
- `SIGSTOP` : signal de suspension, qui suspend l'exécution d'un processus, mais ne le termine pas.
- `SIGTSTP` : signal de suspension interactive, généralement envoyé lorsque l'utilisateur appuie sur `Ctrl+Z`.
- `SIGCONT` : signal de reprise, qui reprend l'exécution d'un processus suspendu.
- `SIGTERM` : signal de terminaison, qui demande à un processus de se terminer proprement.
- `SIGUSR1` et `SIGUSR2` : signaux définis par l'utilisateur, qui peuvent être utilisés pour des communications personnalisées entre processus.
  
Par exemple, on peut envoyer le signal `SIGKILL` à un processus pour le terminer immédiatement en utilisant la commande `kill` :

```bash
kill -SIGKILL <pid>
```

On peut récupérer le PID (Process ID) d'un processus en utilisant la commande `ps` ou `pgrep`. Par exemple, pour trouver le PID d'un processus nommé `myprocess`, on peut utiliser :

```
pgrep myprocess
```

### exemple de code utilisant les signaux

```c
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>

void handle_sigint(int sig) {
    printf("Signal SIGINT reçu, arrêt du processus.\n");
    exit(0);
}

int main() {
    // Installer le gestionnaire de signal pour SIGINT
    signal(SIGINT, handle_sigint);

    printf("Processus en cours d'exécution. Appuyez sur Ctrl+C pour envoyer SIGINT.\n");

    // Boucle infinie pour maintenir le processus en vie
    while (1) {
        pause(); // Attendre un signal
    }

    return 0;
}
```

