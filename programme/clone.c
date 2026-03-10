#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sched.h>
#include <sys/syscall.h>
#include <sys/types.h>

int thread_function(void *arg) {
    printf("Je suis un thread : PID = %d, TID = %ld\n",
           getpid(), syscall(SYS_gettid));
    return 0;
}

int main() {
    const int STACK_SIZE = 1024 * 1024;   // 1 Mio
    char *stack = malloc(STACK_SIZE);
    if (stack == NULL) {
        perror("malloc failed");
        return 1;
    }

    pid_t tid = clone(thread_function,
                      stack + STACK_SIZE,
                      CLONE_VM | CLONE_FS | CLONE_FILES |
                      CLONE_SIGHAND | CLONE_THREAD,
                      NULL);

    if (tid == -1) {
        perror("clone failed");
        free(stack);
        return 1;
    }

    printf("Main : PID = %d, TID = %ld\n", getpid(), syscall(SYS_gettid));

    // Petite attente pour laisser le thread finir
    sleep(1);

    free(stack);
    return 0;
}