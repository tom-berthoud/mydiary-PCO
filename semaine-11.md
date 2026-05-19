# Semaine 11 — 2026-05-05

## [performance] Ruptures de pipeline et prédiction de branchement / processeur

```c
if (a == 0)
    b = 1;
else
    b = 2;
```

```
JZ a,
MOV b, 2
JUMP LA
LA:
MOV b, 1
```

si a = 0, alors il faut 6 instructions, sinon 3.

etape d'un appel:
1. fetch
2. decode
3. execute
4. memory access

Plusieurs intruciton en parallele :
étape: 1 2 3 4

   1  2  3  4  1  2  3  4
      1  2  3  4  1  2  3  4
         1  2  3  4  1  2  3  4
            1  2  3  4  1  2  3  4
        
pipeline : 4 cycles pour 4 instructions, au lieu de 16 cycles pour 4 instructions séquentielles
si la 2ème et 3èeme ligne vienne chercher le movee b =2 et jump la, si a = 0, alors on perd 2 cycles, car on doit attendre que b soit mis à jour avant de faire le jump.

1  2  3 | 4
   1  2 | 1    - id: cache
    title: "Mémoire cache, prédiction de branchement et MMU"
      1 |
      rupture de pipeline, on perd 2 cycles 

Dessin microcontroleur :

|  Alu  mémoire  registre
