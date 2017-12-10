from typing import List, IO

import grammar


class ParsingError(Exception):
    pass


def parse_grammar(file: IO) -> grammar.Grammar:
    g = grammar.Grammar()
    for line in file.readlines():
        pieces = line.replace('\n', '').split("::=")
        if len(pieces) != 2:
            raise ParsingError
        nterm_raw = pieces[0].rstrip().lstrip()
        if len(nterm_raw) == 0 or nterm_raw[0] != '<' or nterm_raw[-1] != '>':
            raise ParsingError
        nterm = int(nterm_raw[1:-1])
        rules = pieces[1].split('|')
        for rule in rules:
            derivation = tuple()
            nterm_flag = False
            nbody = ""
            escaped = False
            for symb in rule:
                if nterm_flag:
                    if escaped:
                        raise ParsingError
                    if symb == '<':
                        raise ParsingError
                    elif symb == '>':
                        nterm_flag = False
                        derivation += (int(nbody),)
                        nbody = ""
                    else:
                        nbody += symb
                else:
                    if escaped:
                        if symb not in {'<', '>', '|'}:
                            raise ParsingError
                        derivation += (symb,)
                        escaped = False
                        continue
                    if symb == '<':
                        nterm_flag = True
                    elif symb == '>':
                        raise ParsingError
                    elif symb == '\\':
                        escaped = True
                    else:
                        derivation += (symb,)
            g.add_rule(nterm, derivation)

    return g
