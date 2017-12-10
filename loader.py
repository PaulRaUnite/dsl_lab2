from typing import List, IO, Dict, Iterator

import itertools

import grammar


class ParsingError(Exception):
    pass


def parse_grammar(file: IO) -> grammar.Grammar:
    g = grammar.Grammar()
    str_nterm_map: Dict[str, int] = dict()
    nterm_seq = itertools.count(0)

    def map_nterm(s: str, sequence: Iterator) -> grammar.NonTerminal:
        if s in str_nterm_map:
            return str_nterm_map[s]
        else:
            nterm = next(sequence)
            str_nterm_map[s] = nterm
            return nterm

    for line in file.readlines():
        pieces = line.replace('\n', '').split("::=")
        if len(pieces) != 2:
            raise ParsingError
        nterm_raw = pieces[0].rstrip().lstrip()
        if len(nterm_raw) == 0 or nterm_raw[0] != '<' or nterm_raw[-1] != '>':
            raise ParsingError
        str_nterm = nterm_raw[1:-1]
        nterm = map_nterm(str_nterm, nterm_seq)

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
                        derivation += (map_nterm(nbody, nterm_seq),)
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
