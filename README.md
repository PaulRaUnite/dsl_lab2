# dsl_lab2
DSL context free grammar work

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
- [x] left-recursion removing optimization;
- [ ] recursive descent parsing optimization.

## How to use

Clone/download the repository and execute `python app.py`.

Please use at least `python3.6`, because the whole project uses it possibilities(type hints, print, next and etc built-in functions(!)).

## Testing

The application was tested by 3 grammars:

- [simple HTML](./test1);
- [arithmetic operations](./test2);
- [positive integers](./test3).

The application requires file of grammar and its file of words.

### Grammar format

The format is similar to BFN(`<>` describes non-terminal, `::=` separates non-terminal from its rules), except terminals are not written in quotes(') and there is limitation of using escaped symbols (for example, newline symbol separates production set one from another). But you can use escaped `\<`, `\>`, `\|` to present the symbols of `<`, `>` and `|` in your grammars (see HTML example).

As non-terminals you can use any strings, but for application representation they will be transformed into integers in the order they was met by grammar "parser".

Examples of grammars listed above.

### Word format

Every line of the file is word. Every file must begins with `[true]` or `[false]` control sequences. They tell the application, should the words below be true or false(truth expectation).

Also, limitations that have been described above are suitable here.
