# DSL course: individual work #2
DSL context-free grammar work

## Tasks

- [x] a data structure for grammar;
- [x] remove useless non-terminal symbols(dead and unreachable);
- [x] determination of vanishing symbols;
- [x] removing of vanishing symbols;
- [x] determination of left-recursion in a grammar;
- [x] remove chain productions;
- [x] remove left-recursion;
- [x] factorization;
- [x] recursive descent parsing.

Additional:
- [x] left-recursion removing optimization(order based on distance to the initial non-terminal);
- [x] recursive descent parsing optimization(prediction using FIRST mapping).

## How to use

Clone/download the repository and execute `python app.py`.

Use `python3`(the project was tested by `python3.6`), because the whole project uses it features(type hints, print, next and etc built-in functions(!)).

It imports only standard libraries and local grammar library, no external dependencies.

## Testing

The application was tested by 3 grammars and related test cases:

- [simple HTML](./test1), [words](./samples1);
- [arithmetic operations](./test2), [words](./samples2);
- [positive integers](./test3), [words](./samples3)(this one executed really slow).

The application requires file of grammar and its file of words.

### Grammar format

The format is similar to BFN(`<>` describes non-terminal, `::=` separates non-terminal from its rules), except terminals are not written in quotes(') and there is limitation of using escaped symbols (for example, newline symbol separates production set one from another). But you can use escaped `\<`, `\>`, `\|` to present the symbols of `<`, `>` and `|` in your grammars (see HTML example).

As non-terminals you can use any strings, but for application representation they will be transformed into integers in the order they were met by grammar "parser".

Examples of grammars are listed above.

### Word format

Every line of the file is word to check. Every file must begins with `[true]` or `[false]` control sequences. They tell the application, should the words below be true or false (truth expectation). Also, you can write something like that:
```
[true]
...
[false]
...
[true]
...
```
where `...` is some words.

Also, limitations that have been described above are suitable here.

## Grammar definitions

[Context-free grammar](https://en.wikipedia.org/wiki/Context-free_grammar) consist of two main things:

- initial non-terminal;
- mapping from non-terminals to derivation sets, where derivation is a tuple of terminals or non-terminals.

Terminal is any character.
Non-terminal is represented as integer in the implementation, but formally it is symbol that can be replaced by its rules.

Formally grammar looks like:
```
S —> Aab|BC
A —> a|b
C —> c
```
where `S`,`A`, `B` and `C` &mdash; non-terminals, `a`,`b`,`c` &mdash; terminals. Here `B` is a dead symbol(there are no terminal derivations of any step from it) and should be deleted as well all productions where it occurs.
```
S —> Aab
A —> a|b
C —> c
```
where `C` became unreachable &mdash; there are no derivations from `S` that contain `C`.

There are left-recursion of two types: direct and indirect.

This is grammar with direct recursion.
```
S —> S|a|b
```

This is grammar with indirect recursion.
```
S —> A|a|b
A —> S
```

## Grammar implementation

The whole project is properly documented, so it is not needed to be brave to dig into it. :D

Project implements grammar class, related data types, and required in algorithms data structures.

The process of word checking consists of two parts:

- preparing grammar to recursive descent parsing;
- descent parsing itself.

Because recursive descent parsing is applied there, there is problem of left recursion. That and other cases are handled in `prepare_for_checking` method. It returns parsing-ready grammar, formed from input grammar.

The method does the following steps:

- determines left-recursion in the grammar;
- if yes:
    - remove vanishing symbols;
    - remove chain productions;
    - remove useless(because they can exist in the initial grammar and removing of vanishing and chain productions can generate some of them);
    - remove left-recursion;
    - add empty word to the grammar if it was in initial.
- if no:
    - left factorization;
- remove useless.

#### Removing of useless

Useless non-terminal symbol is dead or unreachable one.

To determine a dead symbol, undead must be determined. If some rule of the non-terminal symbol is fully terminal it is undead. If there is some terminal derivation from non-terminal, the symbol is undead too.

To determine a unreachable symbol, enough to run one of graph bypass algorithms.

#### Removing of vanishing

1. determine all `A` non-terminals with the following rules <code>A &mdash;> &epsilon;|...</code>;
2. if <code>A &mdash;> &alpha;|&beta;<sub>1</sub>... </code>, and <code>&alpha; := &gamma;<sub>1</sub>...&gamma;<sub>k</sub></code>, and all <code>&gamma;</code> are vanishing, `A` is also vanishing;
3. all productions of <code>A &mdash;> &epsilon; </code> must be deleted and all productions of form <code>B &mdash;> &alpha;A&beta; </code>, where <code>&alpha;</code> and <code>&beta;</code> some sequences of terminals, non-terminals or empty word, and `A` is vanishing, must be split into <code>B &mdash;> &alpha;A&beta; | &alpha;&beta;</code>. Repeat until all possible variants will be present.

#### Removing of chain productions

Example of chain productions.
```
A —> B |...
B —> C |...
C —> ...
```

`A` has indirect transition to `C` because of `A —> B` and `B —> C` and this are called chain productions.

1. determine all direct chain productions;
1. build all possible combinations of present chain productions;
1. for every pair `A` and `B`, remove `A —> B`, add all <code>&alpha; <sub>i</sub></code>from <code>B —> &alpha;<sub>1</sub>|...|&alpha;<sub>k</sub></code> to `A`.

#### Removing of left recursion

1. order non-terminals from 0 to n;
1. removing of indirect: for productions from 0 to n, if rule of `A` has non-terminal `B`, which less by the order than `A`, at the first position, replace it by `B` rules;
1. removing of direct: for all non-terminals of form <code>A —> A&alpha;<sub>1</sub>...A&alpha;<sub>k</sub>|&beta;<sub>1</sub>...&beta;<sub>n</sub></code>, remove rules starting with `A` and add rules <code>A —> &beta;<sub>1</sub>A'...&beta;<sub>k</sub>A'|&beta;<sub>1</sub>...&beta;<sub>n</sub></code> as well as <code>A' —> &alpha;<sub>1</sub>A'...&alpha;<sub>k</sub>A'|&alpha;<sub>1</sub>...&alpha;<sub>n</sub></code>.

#### Left factorization

Factorization select common prefixes in rules and transfer different suffixes as rules of new non-terminal symbol.

To achieve it, I used prefix tree and tree restoring algorithm which combines rules with common prefixes to new non-terminals recursively.

#### About optimizations

To speed up left-recursion removing algorithm, I used order based on distance to initial non-terminal. Initial non-terminal has number 0(has no effect with the current grammar parser, because it writes integer representations of non-terminal symbols in order of their appearing in rules).

To speed up recursively descent method, I used FIRST dictionary: it contains pairs of non-terminal and symbol which are mapped into a set of derivations that have that symbol at theirs first position. It means, that you can predict possible substitution rules using the dictionary.
