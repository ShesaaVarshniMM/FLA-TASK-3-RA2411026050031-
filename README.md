# Context-Free Grammar & Pushdown Automata Lab – CLA-2 Task 3

## Project Overview

The **Context-Free Grammar and Pushdown Automata Lab** is an interactive web application developed using Python and Streamlit for the course 21CSC301T – Formal Language and Automata.

The application demonstrates three case studies using Context-Free Grammar (CFG), Deterministic Pushdown Automata (DPDA), and Nondeterministic Pushdown Automata (NPDA).

It provides interactive input validation, grammar productions, automaton diagrams, stack operations, and processing traces.

## Objectives

- Understand the practical applications of Context-Free Grammars.
- Demonstrate how Pushdown Automata use stacks for processing input.
- Understand the difference between deterministic and nondeterministic PDA.
- Validate structured strings and arithmetic expressions.
- Visualize grammar productions and stack-based processing.

## Case Studies Implemented

### 1. Balanced Parentheses Checker

**Automaton:** Deterministic Pushdown Automaton (DPDA)

Checks whether opening and closing parentheses are properly balanced.

**Grammar:**

```text
S → (S)S
S → ε
```

**Working Principle:**

- Push an opening parenthesis onto the stack.
- Pop an opening parenthesis when a closing parenthesis is encountered.
- Reject if a closing parenthesis has no matching opening parenthesis.
- Accept if the input ends with only the bottom-of-stack marker remaining.

**Example:**
- `()` – Accepted
- `(())` – Accepted
- `(()())` – Accepted
- `(()` – Rejected
- `())` – Rejected

### 2. Arithmetic Expression Validator

**Technique:** Context-Free Grammar (CFG) with Predictive LL(1) Parsing

Checks whether arithmetic expressions follow a defined grammar.

**Grammar:**

```text
E  → T E'
E' → + T E' | - T E' | ε
T  → F T'
T' → * F T' | / F T' | ε
F  → (E) | number
```

**Working Principle:**

- Tokenizes the arithmetic expression.
- Applies grammar production rules.
- Uses recursive-descent parsing.
- Checks operator placement and parentheses.
- Accepts only if all tokens are consumed successfully.

**Example:**
- `2+3*4` – Accepted
- `(10+5)*2` – Accepted
- `8/2-1` – Accepted
- `2+*3` – Rejected
- `(5+2` – Rejected

### 3. Palindrome Checker

**Automaton:** Nondeterministic Pushdown Automaton (NPDA)

Checks whether a string reads the same forwards and backwards.

**Language:**

```text
L = { w ∈ {a,b}* | w = wᴿ }
```

**Grammar:**

```text
Even-length:
S → aSa | bSb | ε

Odd-length:
S → aSa | bSb | a | b
```

**Working Principle:**

- Pushes the first half of the input onto the stack.
- Nondeterministically guesses the midpoint.
- Skips one middle symbol for odd-length strings.
- Matches the remaining input with the stack contents.
- Accepts if the entire input is consumed and the stack becomes empty.

**Example:**
- `abba` – Accepted
- `aba` – Accepted
- `a` – Accepted
- `abab` – Rejected
- `aab` – Rejected

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Automata and parsing implementation |
| Streamlit | Interactive web application |
| Graphviz | PDA and parser diagrams |
| Pandas | Processing trace representation |
| HTML & CSS | User interface styling |

## Features

- Three interactive case studies.
- Balanced parentheses validation.
- Arithmetic expression syntax validation.
- Palindrome checking using NPDA logic.
- CFG production rule visualization.
- PDA state diagrams.
- Stack operation traces.
- Parser execution traces.
- Predefined valid and invalid test cases.
- Accept and reject status display.

## Project Structure

```text
FLA_Task3/
│
├── Task3.py
├── README.md
└── requirements.txt
```

## Installation and Execution

### Step 1: Clone the Repository

```bash
git clone <your-repository-link>
```

### Step 2: Navigate to the Project Folder

```bash
cd Task3
```

### Step 3: Install Dependencies

```bash
pip install streamlit pandas graphviz
```

Graphviz must also be installed on your system and available in PATH for diagram rendering.

### Step 4: Run the Application

```bash
streamlit run Task3.py
```

The application will open in your default web browser.

## Working Principle

1. Select a case study from the application.
2. Enter an input string or choose a predefined example.
3. The application processes the input using the corresponding grammar or automaton logic.
4. Stack operations or parser procedures are executed.
5. The application determines whether the input is accepted or rejected.
6. The processing trace and corresponding diagram are displayed.

## Limitations

- Balanced parentheses validation supports only one bracket type: `(` and `)`.
- Arithmetic expression validation supports integers and basic arithmetic operators only. It does not evaluate the numerical result.
- The palindrome checker accepts only strings containing `a` and `b`.
- The palindrome implementation explores possible midpoint choices and uses a computation limit.

## Conclusion

The CFG and PDA Case Study Lab demonstrates the practical use of Context-Free Grammars and Pushdown Automata in validating structured input. The application helps understand grammar production rules, stack operations, parsing techniques, and nondeterministic computation through interactive examples.

**Course:** 21CSC301T – Formal Language and Automata  
**Assignment:** CLA-2 – Task 3\
**Done By:** SHESAA VARSHNI MM(RA2411026050031)
