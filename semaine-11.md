# Semaine 11 — 2026-05-05

## [performance] Pipeline d'exécution et prédiction de branchement

### Étapes d'exécution d'une instruction

Une instruction passe par quatre étapes dans le processeur :

1. **Fetch** — récupération de l'instruction depuis la mémoire
2. **Decode** — décodage de l'opération et des opérandes
3. **Execute** — exécution dans l'ALU
4. **Memory access** — lecture/écriture mémoire si nécessaire

Sans pipeline, ces quatre étapes sont exécutées séquentiellement : il faut donc 4 cycles pour terminer une seule instruction, soit 16 cycles pour 4 instructions.

### Exemple : compilation d'un `if/else`

Un branchement simple en C :

```c
if (a == 0)
    b = 1;
else
    b = 2;
```

se traduit en assembleur par quelque chose comme :

```asm
    JZ  a, LA    ; saut si a == 0
    MOV b, 2
    JUMP FIN
LA: MOV b, 1
FIN:
```

Selon la valeur de `a`, le processeur ne suit pas le même chemin : le saut conditionnel `JZ` rompt l'enchaînement linéaire des instructions, ce qui pose problème quand on veut paralléliser leur exécution.

### Principe du pipeline

L'idée du pipeline est de chevaucher les étapes : pendant que l'instruction 1 est en phase *decode*, l'instruction 2 peut déjà être en phase *fetch*. Avec 4 étages, on traite donc une nouvelle instruction par cycle une fois le pipeline rempli.

```{=latex}
\begin{center}
\begin{tikzpicture}[
  cell/.style={rectangle, draw, thick, minimum width=0.9cm, minimum height=0.7cm, font=\small, align=center},
  fetch/.style={cell, fill=blue!20},
  decode/.style={cell, fill=green!20},
  exec/.style={cell, fill=orange!25},
  mem/.style={cell, fill=red!20},
  label/.style={font=\small\bfseries, anchor=east},
  cyc/.style={font=\scriptsize, anchor=south},
  >=Latex
]
  % Entête : numéros de cycle
  \foreach \c in {1,...,7}{
    \node[cyc] at ({\c*0.9 - 0.45}, 2.9) {Cycle \c};
  }
  % Instruction 1
  \node[label] at (0, 2.4) {I1};
  \node[fetch]  at (0.45, 2.4) {F};
  \node[decode] at (1.35, 2.4) {D};
  \node[exec]   at (2.25, 2.4) {E};
  \node[mem]    at (3.15, 2.4) {M};
  % Instruction 2
  \node[label] at (0, 1.7) {I2};
  \node[fetch]  at (1.35, 1.7) {F};
  \node[decode] at (2.25, 1.7) {D};
  \node[exec]   at (3.15, 1.7) {E};
  \node[mem]    at (4.05, 1.7) {M};
  % Instruction 3
  \node[label] at (0, 1.0) {I3};
  \node[fetch]  at (2.25, 1.0) {F};
  \node[decode] at (3.15, 1.0) {D};
  \node[exec]   at (4.05, 1.0) {E};
  \node[mem]    at (4.95, 1.0) {M};
  % Instruction 4
  \node[label] at (0, 0.3) {I4};
  \node[fetch]  at (3.15, 0.3) {F};
  \node[decode] at (4.05, 0.3) {D};
  \node[exec]   at (4.95, 0.3) {E};
  \node[mem]    at (5.85, 0.3) {M};
  % Accolade : 4 instructions en 7 cycles
  \draw[-, decorate, decoration={brace, amplitude=5pt, mirror}, gray]
    (0.05, -0.1) -- (6.25, -0.1)
    node[midway, below=6pt, font=\small, gray]
      {4 instructions terminées en 7 cycles (au lieu de 16)};
\end{tikzpicture}
\end{center}
```

### Rupture de pipeline lors d'un branchement

Le pipeline suppose que la prochaine instruction est connue à l'avance. Or, pour un saut conditionnel comme `JZ`, on ne sait pas quelle instruction charger ensuite tant que la condition n'a pas été évaluée (étape *execute*).

Si le processeur a déjà commencé à *fetch* / *decode* les instructions qui suivent `JZ` et que le saut est finalement pris, ces instructions doivent être abandonnées : c'est la **rupture de pipeline**, qui coûte typiquement 2 cycles perdus pour un pipeline à 4 étages.

| Situation | Coût |
|:----|:-------------|
| Pipeline rempli, pas de saut | 1 instruction / cycle |
| Saut bien prédit | 1 instruction / cycle |
| Saut mal prédit (rupture) | ~2 cycles perdus |

### Prédiction de branchement

Pour limiter les ruptures, le processeur **prédit** le résultat du branchement avant de le connaître, et continue à remplir le pipeline avec les instructions de la branche présumée. Si la prédiction est juste, aucun cycle n'est perdu ; sinon, le pipeline est vidé (*flush*) et on repart de l'autre branche.

Les prédicteurs modernes s'appuient sur l'historique des sauts précédents pour atteindre des taux de réussite supérieurs à 95 %.
