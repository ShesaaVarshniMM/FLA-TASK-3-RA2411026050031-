import re
from collections import deque

import pandas as pd
import streamlit as st
from graphviz import Digraph

# ============================================================
# CLA-2 TASK 3: CFG + PDA CASE STUDY LAB
# Balanced parentheses | Arithmetic expressions | Palindromes
# ============================================================

st.set_page_config(
    page_title="CFG & PDA Lab | CLA-2 Task 3",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------- AUTOMATA / PARSERS ----------------------------

def balanced_parentheses(text):
    """Deterministic PDA for one bracket type: ( and )."""
    stack = ["Z0"]
    trace = []

    for pos, ch in enumerate(text, start=1):
        before = "".join(stack)

        if ch not in "()":
            trace.append({
                "Step": pos, "Read": repr(ch), "Stack before": before,
                "Operation": "Invalid input symbol", "Stack after": "REJECT"
            })
            return False, trace, "DEAD", "Only '(' and ')' are allowed."

        if ch == "(":
            stack.append("(")
            operation = "Push '('"
        elif len(stack) > 1 and stack[-1] == "(":
            stack.pop()
            operation = "Pop '('"
        else:
            trace.append({
                "Step": pos, "Read": repr(ch), "Stack before": before,
                "Operation": "No opening '(' available to pop", "Stack after": "REJECT"
            })
            return False, trace, "DEAD", "A closing parenthesis has no matching opening parenthesis."

        trace.append({
            "Step": pos, "Read": repr(ch), "Stack before": before,
            "Operation": operation, "Stack after": "".join(stack)
        })

    accepted = stack == ["Z0"]
    trace.append({
        "Step": len(text) + 1, "Read": "ε", "Stack before": "".join(stack),
        "Operation": "Input ended; check bottom marker",
        "Stack after": "ACCEPT" if accepted else "REJECT"
    })
    if accepted:
        return True, trace, "q_accept", "Input ended with only the bottom-of-stack marker Z0."
    return False, trace, "q_reject", "An opening parenthesis remains unmatched."


# Arithmetic grammar:
# E  -> T E'
# E' -> + T E' | - T E' | ε
# T  -> F T'
# T' -> * F T' | / F T' | ε
# F  -> ( E ) | number

def tokenize_arithmetic(text):
    tokens = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
        elif text[i].isdigit():
            j = i
            while j < len(text) and text[j].isdigit():
                j += 1
            tokens.append(text[i:j])
            i = j
        elif text[i] in "+-*/()":
            tokens.append(text[i])
            i += 1
        else:
            raise ValueError(f"Unsupported character {text[i]!r}. Use integers and + - * / ( ).")
    tokens.append("$")
    return tokens


class PredictiveParser:
    """Recursive-descent LL(1) parser implementing the CFG above."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.trace = []

    def current(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else "$"

    def record(self, procedure, production):
        self.trace.append({
            "Step": len(self.trace) + 1,
            "Remaining input": " ".join(self.tokens[self.index:]),
            "Parser procedure": procedure,
            "Production / action": production
        })

    def match(self, expected):
        found = self.current()
        if found != expected:
            raise ValueError(f"Expected {expected!r}, but found {found!r}.")
        self.record("match()", f"Match terminal {found!r}")
        self.index += 1

    def E(self):
        self.record("E()", "E → T E′")
        self.T()
        self.E_prime()

    def E_prime(self):
        if self.current() in ("+", "-"):
            op = self.current()
            self.record("E′()", f"E′ → {op} T E′")
            self.match(op)
            self.T()
            self.E_prime()
        else:
            self.record("E′()", "E′ → ε")

    def T(self):
        self.record("T()", "T → F T′")
        self.F()
        self.T_prime()

    def T_prime(self):
        if self.current() in ("*", "/"):
            op = self.current()
            self.record("T′()", f"T′ → {op} F T′")
            self.match(op)
            self.F()
            self.T_prime()
        else:
            self.record("T′()", "T′ → ε")

    def F(self):
        if self.current() == "(":
            self.record("F()", "F → ( E )")
            self.match("(")
            self.E()
            self.match(")")
        elif self.current().isdigit():
            self.record("F()", "F → number")
            self.match(self.current())
        else:
            raise ValueError(f"Expected a number or '(', but found {self.current()!r}.")

    def parse(self):
        self.E()
        if self.current() != "$":
            raise ValueError(f"Unexpected token {self.current()!r} after the expression.")
        self.record("accept()", "All tokens consumed; expression accepted")
        return self.trace


def arithmetic_expression(text):
    try:
        tokens = tokenize_arithmetic(text)
        parser = PredictiveParser(tokens)
        trace = parser.parse()
        return True, trace, "q_accept", "The complete input follows the arithmetic CFG."
    except (ValueError, RecursionError) as exc:
        partial_trace = parser.trace if "parser" in locals() else []
        return False, partial_trace, "q_reject", str(exc)


def palindrome_npda(text):
    """
    NPDA for L = { w in {a,b}* : w = reverse(w) }.
    It pushes a guessed first half, nondeterministically guesses
    the midpoint (epsilon for even length, one symbol for odd),
    then matches and pops the second half.
    """
    if any(ch not in "ab" for ch in text):
        return False, [], "q_reject", "The palindrome alphabet is {a, b}; other symbols are not allowed."

    # Configuration: (input_position, mode, stack_contents)
    start = (0, "push", "")
    queue = deque([(start, [])])
    visited = {start}

    while queue and len(visited) < 50000:
        (pos, mode, stack), path = queue.popleft()

        if pos == len(text) and mode == "pop" and stack == "":
            final_path = path + [{
                "Step": len(path) + 1,
                "Input position": "end",
                "Read": "ε",
                "Mode": "pop",
                "Stack after": "∅",
                "NPDA choice": "Accept: input consumed and stack empty"
            }]
            return True, final_path, "q_accept", "At least one nondeterministic path matches the entire string."

        if mode == "push":
            # Guess even-length midpoint using epsilon.
            nxt = (pos, "pop", stack)
            if nxt not in visited:
                visited.add(nxt)
                row = {
                    "Step": len(path) + 1, "Input position": pos, "Read": "ε",
                    "Mode": "pop", "Stack after": stack or "∅",
                    "NPDA choice": "Guess even-length midpoint"
                }
                queue.append((nxt, path + [row]))

            # Guess odd-length midpoint by consuming one middle symbol.
            if pos < len(text):
                nxt = (pos + 1, "pop", stack)
                if nxt not in visited:
                    visited.add(nxt)
                    row = {
                        "Step": len(path) + 1, "Input position": pos, "Read": text[pos],
                        "Mode": "pop", "Stack after": stack or "∅",
                        "NPDA choice": "Skip one middle symbol (odd length)"
                    }
                    queue.append((nxt, path + [row]))

                # Continue pushing first-half symbols.
                nxt = (pos + 1, "push", stack + text[pos])
                if nxt not in visited:
                    visited.add(nxt)
                    row = {
                        "Step": len(path) + 1, "Input position": pos, "Read": text[pos],
                        "Mode": "push", "Stack after": stack + text[pos],
                        "NPDA choice": f"Push {text[pos]}"
                    }
                    queue.append((nxt, path + [row]))

        elif pos < len(text) and stack and stack[-1] == text[pos]:
            nxt = (pos + 1, "pop", stack[:-1])
            if nxt not in visited:
                visited.add(nxt)
                row = {
                    "Step": len(path) + 1, "Input position": pos, "Read": text[pos],
                    "Mode": "pop", "Stack after": stack[:-1] or "∅",
                    "NPDA choice": f"Match {text[pos]} and pop"
                }
                queue.append((nxt, path + [row]))

    return False, [], "q_reject", "No accepting NPDA computation path was found."


# ---------------------------- DIAGRAMS ----------------------------

def graph_base():
    dot = Digraph("Automaton", engine="dot")
    dot.attr(
        rankdir="LR", bgcolor="transparent", pad="0.3",
        nodesep="0.55", ranksep="0.75", splines="spline"
    )
    dot.attr(
        "node", shape="circle", style="filled",
        fillcolor="#EAF1FF", color="#31527D", fontcolor="#183153",
        fontname="Arial", fontsize="11", penwidth="1.7"
    )
    dot.attr(
        "edge", color="#536B8A", fontcolor="#294568",
        fontname="Arial", fontsize="10", penwidth="1.4", arrowsize="0.8"
    )
    dot.node("start", "", shape="point", width="0.13", color="#183153")
    return dot


def parentheses_diagram():
    dot = graph_base()
    dot.node("q0", "q0\\nStart", fillcolor="#EAF1FF")
    dot.node("q1", "q1\\nStack has '('", fillcolor="#EAF1FF")
    dot.node("qf", "q_accept\\nACCEPT", shape="doublecircle",
             fillcolor="#C9F2D7", color="#198754", penwidth="2.2")
    dot.node("qd", "q_reject\\nREJECT", fillcolor="#FDE2E2", color="#C0392B")
    dot.edge("start", "q0")
    dot.edge("q0", "q1", label="'(' / push")
    dot.edge("q1", "q1", label="'(' / push")
    dot.edge("q1", "q0", label="')' / pop")
    dot.edge("q0", "qf", label="end + stack Z0")
    dot.edge("q0", "qd", label="')' / underflow")
    dot.edge("q1", "qd", label="end + '(' remains", style="dashed")
    return dot


def arithmetic_diagram():
    dot = graph_base()
    nodes = [
        ("E", "E\\nExpression"),
        ("T", "T\\nTerm"),
        ("F", "F\\nFactor"),
        ("A", "E′ / T′\\nContinue or ε"),
        ("qf", "q_accept\\nACCEPT"),
    ]
    for key, label in nodes:
        if key == "qf":
            dot.node(key, label, shape="doublecircle",
                     fillcolor="#C9F2D7", color="#198754", penwidth="2.2")
        else:
            dot.node(key, label)
    dot.node("qd", "q_reject\\nREJECT", fillcolor="#FDE2E2", color="#C0392B")
    dot.edge("start", "E")
    dot.edge("E", "T", label="E → T E′")
    dot.edge("T", "F", label="T → F T′")
    dot.edge("F", "A", label="F → number | (E)")
    dot.edge("A", "T", label="* or / then F")
    dot.edge("A", "E", label="+ or − then T")
    dot.edge("A", "qf", label="input fully consumed")
    dot.edge("E", "qd", label="syntax error", style="dashed", color="#C0392B")
    return dot


def palindrome_diagram():
    dot = graph_base()
    dot.node("push", "q_push\\nPush first half")
    dot.node("pop", "q_pop\\nMatch second half")
    dot.node("qf", "q_accept\\nACCEPT", shape="doublecircle",
             fillcolor="#C9F2D7", color="#198754", penwidth="2.2")
    dot.node("qd", "q_reject\\nREJECT", fillcolor="#FDE2E2", color="#C0392B")
    dot.edge("start", "push")
    dot.edge("push", "push", label="a / push a; b / push b")
    dot.edge("push", "pop", label="ε: even midpoint")
    dot.edge("push", "pop", label="read 1 middle symbol: odd")
    dot.edge("pop", "pop", label="matching a or b / pop")
    dot.edge("pop", "qf", label="input end + empty stack")
    dot.edge("pop", "qd", label="mismatch", style="dashed", color="#C0392B")
    return dot


# ---------------------------- APP CONTENT ----------------------------

CASES = {
    "Balanced Parentheses": {
        "subtitle": "Check whether opening and closing parentheses are correctly matched.",
        "default": "(()())",
        "examples": ["()", "(())", "(()())", "(()", "())", "((()))"],
        "alphabet": "Σ = { (, ) }",
        "grammar": ["S → (S)S", "S → ε"],
        "method": "A deterministic PDA pushes '(' onto its stack. When ')' appears, it pops one '('. It accepts when the input ends and only the bottom marker Z0 remains.",
        "limitation": "This example supports one bracket type only. Supporting (), [] and {} requires storing bracket types on the stack and checking matching pairs.",
        "ambiguity": "The grammar S → (S)S | ε generates balanced-parentheses strings. The grammar is unambiguous for this language.",
        "determinism": "A deterministic PDA is sufficient for this one-type balanced-parentheses language: the next action is determined by the next input symbol and stack top.",
        "diagram": parentheses_diagram,
        "validator": balanced_parentheses,
    },
    "Arithmetic Expression Validator": {
        "subtitle": "Validate arithmetic syntax using a context-free grammar and predictive parser.",
        "default": "(10+5)*2",
        "examples": ["2+3*4", "(10+5)*2", "8/2-1", "2+*3", "(5+2", "3++4"],
        "alphabet": "Integers, +, −, *, /, (, ), and whitespace",
        "grammar": [
            "E  → T E′",
            "E′ → + T E′ | − T E′ | ε",
            "T  → F T′",
            "T′ → * F T′ | / F T′ | ε",
            "F  → (E) | number",
        ],
        "method": "A predictive, recursive-descent parser applies CFG productions and matches terminals against the input. Its procedure calls represent the grammar expansion and parsing stack behavior.",
        "limitation": "The app validates syntax, not the numerical result. It does not evaluate expressions, detect division by zero, or support variables and decimal numbers.",
        "ambiguity": "This grammar separates addition/subtraction from multiplication/division, so multiplication and division have higher precedence. The repetition rules make operators left-associative. This avoids the ambiguity of E → E+E | E*E | (E) | number.",
        "determinism": "The grammar is designed for predictive LL(1) parsing with one-token lookahead. The parser chooses a production based on the next token.",
        "diagram": arithmetic_diagram,
        "validator": arithmetic_expression,
    },
    "Palindrome Checker": {
        "subtitle": "Check whether a string reads the same forwards and backwards.",
        "default": "abba",
        "examples": ["abba", "aba", "a", "b", "abab", "aab"],
        "alphabet": "Σ = { a, b }",
        "grammar": [
            "Even-length form: S → aSa | bSb | ε",
            "Odd-length form: S → aSa | bSb | a | b",
        ],
        "method": "The NPDA pushes symbols while reading the first half, nondeterministically guesses the midpoint, then matches and pops symbols from the second half. It accepts if a path consumes the entire input and empties the stack.",
        "limitation": "This palindrome example accepts only strings over {a,b}. The NPDA must guess the midpoint, so the model is nondeterministic.",
        "ambiguity": "The language definition is L = { w ∈ {a,b}* | w = wᴿ }. The two grammar forms distinguish even and odd lengths. This is a language description and production scheme for palindromes.",
        "determinism": "A nondeterministic PDA is used because the machine cannot know the midpoint before reading the rest of the input. It explores possible midpoint choices.",
        "diagram": palindrome_diagram,
        "validator": palindrome_npda,
    },
}

# ---------------------------- STYLING ----------------------------

st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"] {
    background: #F3F6FB !important;
    color: #18263D !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container {
    max-width: 1500px !important;
    padding-top: 1.3rem !important;
    padding-bottom: 3rem !important;
}
.hero {
    background: linear-gradient(115deg, #18365D, #28558B);
    color: white !important; padding: 25px 29px; border-radius: 17px;
    margin-bottom: 20px; box-shadow: 0 10px 26px rgba(24,54,93,.14);
}
.hero * { color: white !important; }
.hero h1 { font-size: 29px; margin: 0 0 7px 0; font-weight: 760; }
.hero p { color: #DCE8F7 !important; margin: 0; font-size: 14px; }
.kicker {
    color: #6C83A3 !important; font-size: 11px; font-weight: 800;
    letter-spacing: .12em; text-transform: uppercase; margin-bottom: 7px;
}
.panel {
    background: #FFFFFF; border: 1px solid #E0E7F0; border-radius: 16px;
    padding: 21px 22px; box-shadow: 0 5px 18px rgba(30,55,90,.05);
}
.section-title { color: #1B3558 !important; font-size: 20px; font-weight: 750; }
.section-subtitle { color: #71819A !important; font-size: 13px; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
    background: #FFFFFF !important; border: 1px solid #CAD5E3 !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] *, div[data-baseweb="input"] input {
    color: #172B4D !important;
}
div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label {
    color: #40536F !important; font-weight: 650 !important;
}
.stButton > button {
    background: #F5F8FC !important; color: #24466F !important;
    border: 1px solid #D7E1ED !important; border-radius: 10px !important;
    font-weight: 650 !important; min-height: 41px;
}
.stButton > button:hover {
    background: #E8F0FA !important; border-color: #8EACD0 !important;
}
.accept {
    background: #E6F6EC; border: 1px solid #B9E5C8; color: #17663A !important;
    border-radius: 11px; padding: 13px 15px; font-weight: 750; margin: 10px 0;
}
.reject {
    background: #FDECEC; border: 1px solid #F4C3C3; color: #A52A2A !important;
    border-radius: 11px; padding: 13px 15px; font-weight: 750; margin: 10px 0;
}
.accept *, .reject * { color: inherit !important; }
.rule-card {
    background: #F7F9FC; border: 1px solid #E4EAF2;
    border-radius: 11px; padding: 12px 14px; margin-top: 10px;
}
.rule-card b { color: #1E3C63 !important; }
.rule-card p { color: #536780 !important; font-size: 13px; margin: 5px 0 0; }
div[data-testid="stDataFrame"] { border: 1px solid #E0E7F0; border-radius: 10px; }
hr { border-color: #E5EAF1 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="kicker" style="color:#BFD4EE !important">21CSC301T · Formal Language and Automata · CLA-2 Task 3</div>
  <h1>Context-Free Grammar & Pushdown Automata Lab</h1>
  <p>Interactive case studies with grammar productions, automaton diagrams, stack traces and test cases</p>
</div>
""", unsafe_allow_html=True)

if "task3_case" not in st.session_state:
    st.session_state.task3_case = "Balanced Parentheses"

case_name = st.selectbox(
    "SELECT CASE STUDY",
    list(CASES.keys()),
    key="task3_case",
)
case = CASES[case_name]

if st.session_state.get("last_task3_case") != case_name:
    st.session_state.task3_input = case["default"]
    st.session_state.last_task3_case = case_name

left, right = st.columns([0.9, 1.6], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="kicker">01 · Interactive case study</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Test your input</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-subtitle">{case["subtitle"]}</div>', unsafe_allow_html=True)

    user_input = st.text_input("INPUT STRING", key="task3_input", placeholder="Enter a string to validate")
    accepted, trace, final_state, message = case["validator"](user_input)

    if accepted:
        st.markdown(f'<div class="accept">✓ ACCEPTED · Final state: {final_state}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="reject">✕ REJECTED · Final state: {final_state}</div>', unsafe_allow_html=True)
    st.caption(message)

    st.markdown("---")
    st.markdown("**Try an example**")
    for start in range(0, len(case["examples"]), 2):
        cols = st.columns(2)
        for offset, example in enumerate(case["examples"][start:start + 2]):
            with cols[offset]:
                st.button(
                    example if example else "(empty string)",
                    key=f"t3_{case_name}_{start}_{offset}",
                    use_container_width=True,
                    on_click=lambda x=example: st.session_state.update(task3_input=x),
                )

    st.markdown("---")
    st.markdown("**Input alphabet**")
    st.markdown(f'<div class="rule-card"><p>{case["alphabet"]}</p></div>', unsafe_allow_html=True)
    st.markdown("**What the model checks**")
    st.markdown(f'<div class="rule-card"><p>{case["method"]}</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="kicker">02 · Visual model</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">PDA / parser state diagram</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">The diagram illustrates the main states and stack-related transitions.</div>', unsafe_allow_html=True)
    st.graphviz_chart(case["diagram"](), use_container_width=True)
    st.markdown("---")
    st.markdown("**Live processing trace**")
    if trace:
        st.dataframe(pd.DataFrame(trace), use_container_width=True, hide_index=True)
    else:
        st.info("No processing steps to display. Enter an input string.")
    st.markdown('</div>', unsafe_allow_html=True)
