# Aether - Lightweight Syntax and Affidability

**Studente:** Angelo Barone  
**Corso:** Ingegneria dei Linguaggi di Programmazione

Questo progetto implementa un compilatore completo per un linguaggio imperativo minimale ma robusto. Il sistema è scritto interamente in **Python** e genera codice intermedio **LLVM IR**, permettendo la compilazione in codice macchina.

Il compilatore include una pipeline moderna composta da: Lexer manuale, Parser ricorsivo discendente, Analisi Semantica (Scope & Arity check), Desugaring (Pipe & Repeat loop), Ottimizzatore (Constant Folding & DCE) e Code Generation.

---
## Perchè Aether?
Lo scopo del linguaggio trova fondamento nella realizzazione di un medium affidabile che connetta la leggerezza della sintassi alla potenza della macchina.

## 📋 Requisiti e Dipendenze

Per eseguire il compilatore e generare gli eseguibili finali sono necessari i seguenti strumenti:

### Software Richiesto
* **Python 3.8+**: Per eseguire il compilatore.
* **Clang**: Compilatore C/C++ (parte della suite LLVM). È necessario per:
    1.  Compilare il runtime di supporto (`runtime.c`).
    2.  Effettuare il linking dell'eseguibile finale.
* **GCC**: per Linking su Windows.

### Librerie Python
Il progetto dipende dalla libreria `llvmlite` per la generazione dell'IR.
  pip install llvmlite

## 📂 Struttura del Progetto
    /
    ├── main.py                   # Driver principale (Entry Point)
    ├── README.md                 # Documentazione
    ├── src/                      # Codice sorgente del compilatore
    │   ├── __init__.py
    │   ├── tokens.py             # Definizioni Token
    │   ├── lexer.py              # Analisi Lessicale 
    │   ├── ast_nodes.py          # Definizione nodi AST e NodeVisitor
    │   ├── parser.py             # Analisi Sintattica
    │   ├── semantic_analysis.py  # Validazione Semantica del codice
    │   ├── optimizer.py          # Ottimizzazione del codice
    │   ├── desugaring.py         # Trasformazione delle strutture complesse dell'AST
    │   └── codegen.py            # Generazione del codice LLVM IR
    └── tests/                    # Suite di test 
      ├── test_lexer.py
      ├── test_parser.py    
      ├── test_semantic.py
      ├── test_optimizer.py
      ├── test_desugaring.py
      └── test_codegen.py

## 🚀 Istruzioni per Build ed Esecuzione
Il processo di creazione di un eseguibile avviene in tre passaggi: compilazione del sorgente in IR, compilazione del runtime e linking finale.

### Compilazione Sorgente -> LLVM IR
Utilizza aether.py per compilare un file ".ae" . Puoi usare il flag --debug per vedere i dettagli delle fasi intermedie.

#### Generazione del codice intermedio del programma .ae
    python aether.py [programma].ae -o output.ll

#### Compilazione del programma
    clang --target=x86_64-pc-windows-gnu -c output.ll -o output.o

#### Compilazione delle funzioni esterne di supporto .c
    gcc -c runtime.c -o runtime.o

#### Linking del codice e generazione dell'eseguibile
    gcc output.o runtime.o -o [programma].exe

## 🧪 Testing
Il progetto include una suite di test completa basata su unittest.

Eseguire tutti i test:
 python -m unittest discover tests

## ✨ Funzionalità del Linguaggio
### Sintassi Base - .ae
    // Funzioni esterne (FFI)
    extern func print(n);

    // Funzioni utente
    func add(a, b) {
      return a + b;
    }
    
    func main() {
      let x = 10;
      let y = 20;
      
      // Pipe Operator
      let res = x |> add(y); // Equivale a add(x, y)
    
      // Repeat Loop (Zucchero sintattico)
        repeat(5) {
        print(res);
      }
    }

### ⚙️ Caratteristiche Tecniche
1. Architettura Custom: Frontend (Lexer e Parser) implementato manualmente senza generatori automatici, con Backend basato su LLVM IR.

2. Tipizzazione Ibrida: Sintassi a tipizzazione implicita nel frontend, compilata staticamente in interi a 64 bit (i64) per massimizzare le performance.

3. Gestione Memoria & Scope: Allocazione variabili sullo stack con supporto al Variable Shadowing (ridichiarazione sicura) e Flat Scope (visibilità estesa dai blocchi interni).

4. Pipeline di Ottimizzazione: Modulo dedicato per Constant Folding, Dead Code Elimination e Semplificazione Algebrica direttamente sull'AST.

5. Desugaring & Funzionalità Avanzate: Trasformazione automatica di costrutti sintattici (Pipe Operator |> e cicli repeat) e gestione delle funzioni anonime (Lambda Lifting).

6. FFI (Foreign Function Interface): Interoperabilità con librerie C native tramite la keyword extern per estendere le funzionalità di I/O.

## ⚠️ Note Implementative
### Gestione Memoria:
Per semplificare la generazione del codice e supportare la mutabilità senza SSA manuale, tutte le variabili locali sono allocate sullo stack tramite istruzioni alloca.

### Compatibilità: 
Il generatore di codice inietta l'attributo "stack-probe-size"="1048576" nelle funzioni LLVM per garantire la compatibilità con l'ABI di sistema (specialmente su Windows).
