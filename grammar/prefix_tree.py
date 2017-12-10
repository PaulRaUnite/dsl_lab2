__all__ = ['PrefixNode', 'analyze_derivation', 'separate_prefixes']
from typing import Dict, Union, Iterator
import grammar

PrefixNode = Dict[Union[grammar.Terminal, grammar.NonTerminal], Union['Node', None]]


def analyze_derivation(prefixes: PrefixNode, deriv: grammar.Derivation):
    """
    Disassemble the derivation into the prefix tree.

    :param prefixes: prefix tree.
    :param deriv: derivation that should be analyzed.
    :return: none.
    """
    if len(deriv) == 0:
        prefixes[deriv] = None
    elif len(deriv) == 1:
        prefixes[deriv[0]] = None
    else:
        first = deriv[0]
        if first in prefixes:
            if prefixes[first] is None:
                prefixes[first] = {grammar.EmptyWord: None}
            analyze_derivation(prefixes[first], deriv[1:])
        else:
            node = dict()
            prefixes[first] = node
            analyze_derivation(node, deriv[1:])


def separate_prefixes(g: grammar.Grammar, layer: grammar.NonTerminal, prefix: grammar.Derivation,
                      root: PrefixNode, common_depth: int, nterm_sequence: Iterator):
    """
    Separate written into tree derivations by common prefixes.

    Uses recursion, maximal depth of it can be as big as
    depth of tree plus 1.

    :param g: Grammar, to which derivations will be recorded.
    :param layer: non-terminal symbol to which the derivation belong.
    :param prefix: common prefix.
    :param root: prefix tree.
    :param common_depth: depth of common prefix.
    :param nterm_sequence: sequence of new non-terminals.
    :return: none.
    """
    # Root in None means that it's leaf.
    if root is None:
        g.add_rule(layer, prefix)
        return

    # Common depth can be only in beginning.
    if common_depth == -1:
        common_depth = 1
    else:
        if len(root) == 1:
            common_depth += 1
        else:
            common_depth = 0

    if common_depth >= 1:
        new_layer = layer
    else:
        # If there is fork, we have to write
        # production of form
        # Layer --> prefixNewLayer
        # where NewLayer non-terminal
        # will keep symbols of the fork.
        new_layer = next(nterm_sequence)
        g.add_rule(layer, prefix + (new_layer,))

    for symb, next_node in root.items():
        # Handling case of the EmptyWord.
        if type(symb) == tuple:
            t_symb = symb
        else:
            t_symb = (symb,)
        # Prefix assembling.
        if common_depth >= 1:
            new_prefix = prefix + t_symb
        else:
            new_prefix = t_symb

        separate_prefixes(g, new_layer, new_prefix,
                          next_node, common_depth, nterm_sequence)
