__all__ = ['Terminal', 'NonTerminal', 'Grammar', 'EmptyWord', 'Derivation']
from typing import Union, Dict, List, Set, Tuple
import copy
import itertools
import grammar

# Types
Terminal = chr
NonTerminal = int
Derivation = Tuple[Union[Terminal, NonTerminal]]
EmptyWord = tuple()
Rule = Tuple[NonTerminal, Derivation]
RawRules = Dict[NonTerminal, Set[Derivation]]

First = Dict[Tuple[NonTerminal, chr], Set[Derivation]]
empty_set = set()


def nt_format(x: NonTerminal) -> str:
    """
    NonTerminal formatting.
    :param x: NonTerminal
    :return: str
    """
    return "<{}>".format(x)


def symbols(x: int) -> int:
    """
    Returns length of int in symbols
    :param x:
    :return: int
    """
    if x == 0:
        return 1
    s = 0
    if x < 0:
        s = 1
    while x != 0:
        x = x // 10
        s += 1
    return s


def fully_propertiable(property: Set[NonTerminal], derivation: Derivation) -> bool:
    """
    Determines is the derivation can be instantiated by the property.
    :param property: used in derivation analysis.
    :param derivation: some Derivation.
    :return: bool
    """
    for symb in derivation:
        if type(symb) == NonTerminal and symb not in property:
            return False
    return True


class Grammar:
    """
    Grammar type.

    Encapsulates work on adding, removing and enumerating
    through non-terminals and their rules.
    """

    def __init__(self, initial: NonTerminal = 0, r: RawRules = None):
        """
        Constructs new instance of grammar.
        :param initial: starting non-terminal in the grammar.
        :param r: rules of the grammar, dictionary must satisfy RawRules constraints.
        """
        if r is None:
            r = dict()
        self.__inital = initial
        self.__rules = r

    def __eq__(self, other: 'Grammar') -> bool:
        """
        Checks equality of two grammars.
        :param other: Grammar.
        :return: bool
        """
        if self.__inital != other.__inital:
            return False
        for nterm, deriv_set in self.__rules.items():
            if nterm not in other.__rules:
                return False
            if deriv_set != other.__rules[nterm]:
                return False
        return True

    def max_nterm(self) -> NonTerminal:
        """
        Returns maximal(by natural integer order) non-terminal symbol.
        :return: NonTerminal
        """
        maximal: NonTerminal = self.__inital
        for nterm, derivation in self:
            if nterm > maximal:
                maximal = nterm
            for symbol in derivation:
                if type(symbol) == NonTerminal and symbol > maximal:
                    maximal = symbol
        return maximal

    def min_nterm(self) -> NonTerminal:
        """
        Returns minimal(by natural integer order) non-terminal symbol.
        :return: NonTerminal
        """
        minimal: NonTerminal = self.__inital
        for nterm, derivation in self:
            if nterm > minimal:
                minimal = nterm
            for symbol in derivation:
                if type(symbol) == NonTerminal and symbol < minimal:
                    minimal = symbol
        return minimal

    def add_rule(self, nterm: NonTerminal, *derivs):
        """
        Adds rules to the grammar.
        :param nterm: left side of production.
        :param derivs: rules of production.
        :return: None
        """
        for d in derivs:
            if nterm not in self.__rules:
                self.__rules[nterm] = set()
            self.__rules[nterm].add(d)

    def del_rule(self, nterm: NonTerminal, deriv: Derivation):
        """
        Removes the following rule.
        :param nterm: left side of production.
        :param deriv: right side of production.
        :return: None
        :raises: KeyError if nterm rules don't exist in grammar.
        """
        self.__rules[nterm].remove(deriv)
        if len(self.__rules[nterm]) == 0:
            del self.__rules[nterm]

    def copy(self) -> 'Grammar':
        """
        Copies the grammar entirely.
        :return: Grammar
        """
        return Grammar(self.__inital, copy.deepcopy(self.__rules))

    def __iter__(self):
        """
        Iterator through the grammar.
        :return: iterator
        """
        for s, rule_set in self.__rules.items():
            for subrule in rule_set:
                yield (s, subrule)

    def __str__(self):
        """
        String representation of the grammar.

        ->    -- production sign;
        <int> -- non-terminal;
        |     -- rule delimiter
        [n]   -- empty symbol

        Formats the rules into table with rows of <= 10 elements.
        :return: str
        """
        ret = "Grammar\nInitial non-terminal: {}\n".format(self.__inital)

        # pre-computing of table dimensions
        max_nterm_len = 0
        max_el_len = 0

        for nterm, deriv in self:
            t = symbols(nterm)
            if t > max_nterm_len:
                max_nterm_len = t
            sum = 0
            for symb in deriv:
                if type(symb) == NonTerminal:
                    sum += 2 + symbols(symb)
                else:
                    sum += 1
            if sum > max_el_len:
                max_el_len = sum
        el_fmt = "{:" + (max_el_len + 1).__str__() + "}"
        prod_fmt = "{:" + "{}".format(max_nterm_len) + "} -> {}\n"
        for nter, deriv_set in self.__rules.items():
            sder = ""
            i = 0
            for deriv in deriv_set:
                deriv_str = ""
                if len(deriv) != 0:
                    for symb in deriv:
                        if type(symb) == NonTerminal:
                            deriv_str += nt_format(symb)
                        else:
                            deriv_str += symb
                else:
                    deriv_str = "[n]"  # null
                # sder += "|{}".format(deriv_str)
                sder += el_fmt.format(deriv_str)
                if i % 10 == 9:
                    sder += '\n'
                    sder += ' ' * (max_nterm_len + 4)
                elif i % 10 >= 0 and i != len(deriv_set) - 1:
                    sder += '| '
                i += 1
            ret += prod_fmt.format(nter, sder)
        return ret

    def _remove_dead(self) -> 'Grammar':
        """
        Removes all dead non-terminals.

        Dead non-terminal means that the non-terminal
        hasn't any derivation that can be transformed
        into derivation of only terminal symbols.
        Such non-terminals are useless for grammar.

        :return: Grammar
        """
        has_terminal: Set[NonTerminal] = set()

        # Search for all non-terminals that already
        # has only terminal derivation(s).
        for nterm, derivation in self:
            term = True
            for symb in derivation:
                if type(symb) == NonTerminal:
                    term = False
                    break
            if term:
                has_terminal.add(nterm)

        # While there are changes,
        # try to transform derivations
        # applying non-terminals with
        # terminal derivations.
        changes = True
        while changes:
            changes = False
            for nterm, derivation in self:
                if nterm not in has_terminal and fully_propertiable(has_terminal, derivation):
                    changes = True
                    has_terminal.add(nterm)

        # Write only non-terminals and
        # rules that are terminable.
        g = Grammar(self.__inital)
        for nterm, derivation in self:
            if nterm in has_terminal and fully_propertiable(has_terminal, derivation):
                g.add_rule(nterm, derivation)
        return g

    def _remove_unreachable(self) -> 'Grammar':
        """
        Removes unreachable non-terminal symbols.

        Unreachable means that the non-terminal
        hasn't any derivation from initial symbol
        to be reached.

        :return: Grammar
        """
        reachable: Set[NonTerminal] = {self.__inital}
        queue: List[NonTerminal] = [self.__inital]

        # Start from initial non-terminal
        # and go through the graph
        # writing all met non-terminals.
        while len(queue) > 0:
            nterm = queue.pop()
            if nterm not in self.__rules:
                continue
            for deriv in self.__rules[nterm]:
                for symb in deriv:
                    if type(symb) == NonTerminal and symb not in reachable:
                        reachable.add(symb)
                        queue.append(symb)

        # Write only reached non-terminals
        # and their rules.
        g = Grammar(self.__inital)
        for nterm, deriv in self:
            if nterm in reachable:
                g.add_rule(nterm, deriv)
        return g

    def _rebuild_vanishing(self, vanishing: Set[NonTerminal]) -> 'Grammar':
        """
        Rebuild the grammar to the grammar that equals to the given
        except case if empty word can be derived from initial non-terminal.

        To handle the case, manually add new initial non-terminal symbol
        of the form S` -> S | none, where S` -- new initial, S -- old initial
        and none is empty word.

        :param vanishing: set of vanishing non-terminals.
        :return: Grammar
        """
        # At first removes all
        # rules of empty words.
        for nterm in vanishing:
            self.del_rule(nterm, EmptyWord)

        # Then for all derivations
        # with vanishing symbols
        # create new rules where
        # new rules are old rules
        # without the symbols in different
        # variants of placing.
        #
        # I mean, if there is
        # rule aAbAc, it becomes
        # abc, aAbc, abAc, aAbAc, abc.
        #
        # That's why it repeat the process
        # until was changed nothing.
        while len(vanishing) > 0:
            v = vanishing.pop()
            changes = False
            for nterm, deriv_set in self.__rules.items():
                rebuild_queue: List[Tuple[int, Derivation]] = list()
                for deriv in deriv_set:
                    i = 0  # index
                    for symb in deriv:
                        if symb == v:
                            rebuild_queue.append((i, deriv))
                        i += 1
                len_before = len(self.__rules[nterm])
                for [pos, deriv] in rebuild_queue:
                    new_deriv = deriv[:pos] + deriv[pos + 1:]
                    if len(new_deriv) != 0:
                        self.add_rule(nterm, new_deriv)
                if len_before != len(self.__rules[nterm]):
                    changes = True
            if changes:
                vanishing.add(v)
        return self

    def _vanishing(self) -> Set[NonTerminal]:
        """
        Determines vanishing non-terminals.

        Vanishing means that a non-terminal
        can be transformed into empty word.

        :return: Set[NonTerminal]
        """
        # At first, get all non-teminals
        # that has direct empty word
        # derivation.
        vanishing: Set[NonTerminal] = set()
        for nterm, deriv in self:
            if len(deriv) == 0:
                vanishing.add(nterm)

        # Than while there are changes
        # in vanishing set,
        # try to get all non-terminals
        # which rules can be nullable.
        changes = True
        while changes:
            changes = False
            for nterm, deriv in self:
                if nterm in vanishing:
                    continue
                v = True
                for symb in deriv:
                    if type(symb) == Terminal or symb not in vanishing:
                        v = False
                        break
                if v:
                    vanishing.add(nterm)
                    changes = True
        return vanishing

    def _remove_chain_productions(self) -> 'Grammar':
        """
        Returns grammar without chain productions,
        can leave behind useless non-terminals.

        Find all chain production pairs and replace
        their direct occurrences by their rules.

        The process can create unreachable non-terminals.

        Example:
        <S> --> <A>|a<B>
        <A> --> a|b
        <B> --> e|none

        Will be transformed into:
        <S> --> a|b|a<B>
        <A> --> a|b
        <B> --> e|none
        ,where <A> is unreachable.

        :return: Grammar
        """
        # Find all direct productions
        # of form (L, R).
        chain_pairs: Dict[NonTerminal, Set[NonTerminal]] = dict()
        for nterm, deriv in self:
            if len(deriv) == 1 and type(deriv[0]) == NonTerminal:
                if nterm not in chain_pairs:
                    chain_pairs[nterm] = set()
                chain_pairs[nterm].add(deriv[0])

        # Try to derive all a few
        # step chain transitions.
        # Repeat until nothing changes.
        changes = True
        while changes:
            changes = False
            for L, deriv_set in chain_pairs.items():
                for R in deriv_set:
                    if R in chain_pairs:
                        before = len(chain_pairs[L])
                        new_set = chain_pairs[L].union(chain_pairs[R])
                        chain_pairs[L] = new_set
                        if before < len(new_set):
                            changes = True

        # Enumerate all chain pairs
        # and for L non-terminals
        # replace L --> R by all
        # rules from R.
        for L, deriv_set in chain_pairs.items():
            for R in deriv_set:
                self.del_rule(L, (R,))
                for alpha in self.__rules[R]:
                    self.add_rule(L, alpha)

        return self

    def _has_cycle(self, v: NonTerminal, vanishing: Set[NonTerminal], grey: Set[NonTerminal],
                   black: Set[NonTerminal]) -> bool:
        """
        Returns existing of left-recursive cycle in the sub-graph,
        reachable by left-recursive transitions from the v point.

        :param v: current node.
        :param vanishing: vanishing symbols.
        :param grey: symbols possibly reachable in some cycle.
        :param black: symbols that hasn't cycles
        in any part of sub-graph that can be reachable from it.
        :return: bool
        """
        grey.add(v)
        if v in self.__rules:
            for derivation in self.__rules[v]:
                for symb in derivation:
                    # If symbols is Terminal
                    # left-recursion cannot
                    # exist.
                    if type(symb) == Terminal:
                        break
                    else:
                        # If symbols in grey set
                        # it means that we reach
                        # symb non-terminal
                        # from it by a few steps.
                        if symb in grey:
                            return True
                        # If it is not present
                        # in black, it means that
                        # the symbol can have
                        # return path.
                        elif symb not in black:
                            if self._has_cycle(symb, vanishing, grey, black):
                                return True
                        # if symbol cannot be
                        # vanished, further
                        # symbols can't be
                        # reachable by left-recursive
                        # transition.
                        if symb not in vanishing:
                            break
        # The confirmation
        # that the node
        # doesn't have
        # return paths.
        grey.remove(v)
        black.add(v)
        return False

    def _has_left_recursion(self, vanishing: Set[NonTerminal]) -> bool:
        """
        Returns existing of left-recursion in the whole
        transition grammar graph.

        It handles the case, when some cycle exist but can't
        be reached from the init point.

        Example:
        <S> --> a<A>|a|b
        <A> --> <A>|c
        Left-recursion exists for non-terminal A,
        but will be not recognized by _has_graph procedure.

        :param vanishing:
        :return: bool
        """
        grey = set()
        black = set()
        for nterm, _ in self.__rules.items():
            # Because, not all cycles can
            # be recognized, the loop
            # tries to probe all
            # non-terminals which
            # lack of cycles wasn't proved.
            if nterm not in black:
                if self._has_cycle(nterm, vanishing, grey, black):
                    return True
        return False

    def _remove_left_recursion(self) -> 'Grammar':
        """
        Removes left-recursion in the grammar

        Indirect left-recursion:
        A --> Bab|b|c
        B --> Aa|d|e

        A --> Aaab|dab|eab|b|c
        B --> Aa|d|e

        Direct left-recursion:
        A --> Aas|Ab|a|b

        A --> aA'|bA'|a|b
        A'--> asA'|bA'|as|b

        Detailed description below.

        :return: Grammar
        """
        order: Dict[NonTerminal, int] = dict()
        i = 0
        # Naive ordering.
        # for nterm in self.__rules.keys():
        #     order[nterm] = i
        #     i += 1

        # Ordering based on steps
        # from initial non-terminal.
        queue: List[NonTerminal] = [self.__inital]
        while len(queue) > 0:
            nterm = queue.pop()
            order[nterm] = i
            i += 1
            for deriv in self.__rules[nterm]:
                for symb in deriv:
                    if type(symb) == NonTerminal and symb not in order:
                        queue.append(symb)

        next_nonterm = self.max_nterm() + 1

        for A_i, A_order in order.items():
            # Remove indirect left recursion.
            #
            # For all rules, that has non-terminal
            # with ordering less than the A non-terminal,
            # that non-terminal is replaced by its rules.
            new_derive_set: Set[Derivation] = set()
            for deriv in self.__rules[A_i]:
                first = deriv[0]
                if type(first) == NonTerminal:
                    if order[first] >= A_order or first not in self.__rules:
                        new_derive_set.add(deriv)
                    else:
                        for jderiv in self.__rules[first]:
                            new_derive_set.add(jderiv + deriv[1:])
                else:
                    new_derive_set.add(deriv)

            # Remove direct recursion.
            #
            # For all A --> Aalpha|beta productions,
            # write alpha parts into alphas set,
            # and beta parts into betas set,
            # then if alphas exist, add new
            # non-terminal A', and transform
            # grammar into:
            # A  --> beta|betaA'
            # A' --> alpha|alphaA'
            # as you can see, where is no
            # left-recursion A --> A.
            alphas: List[Derivation] = list()
            betas: List[Derivation] = list()

            for deriv in new_derive_set:
                first = deriv[0]
                if first == A_i:
                    alphas.append(deriv[1:])
                else:
                    betas.append(deriv)
            if len(alphas) > 0:
                A_dot: NonTerminal = next_nonterm
                next_nonterm += 1

                A_i_derivs: Set[Derivation] = set(betas)
                for beta in betas:
                    A_i_derivs.add(beta + (A_dot,))
                A_dot_derivs: Set[Derivation] = set(alphas)
                for alpha in alphas:
                    A_dot_derivs.add(alpha + (A_dot,))

                self.__rules[A_i] = A_i_derivs
                self.__rules[A_dot] = A_dot_derivs

        return self

    def _factorize(self) -> 'Grammar':
        """
        Returns new factorized grammar.

        Factorization means, that if in set of rules
        A --> a1|a2|...|an|... there are a1|...|ak
        with common prefix p, this will be transformed into
        A --> pA'|ak+1|...|an|...
        A --> b1|...|bk, where bi is ai without prefix p.

        :return: Grammar
        """
        # The algorithm for every A --> a1|...|an
        # builds prefix tree, and then by the tree
        # finds maximum common prefixes and adds new
        # non-terminals.
        #
        # It uses itertools.count as counter for new
        # non-terminals to keep the grammar consistent.

        g = Grammar()
        tree: grammar.PrefixNode = dict()
        next_nterm = self.max_nterm() + 1
        for nterm, derivation_set in self.__rules.items():
            tree.clear()
            for derivation in derivation_set:
                grammar.analyze_derivation(tree, derivation)
            grammar.separate_prefixes(g, nterm, EmptyWord, tree, -1, itertools.count(start=next_nterm, step=1))

        return g

    def _remove_useless(self) -> "Grammar":
        """
        Removes dead adn unreachable non-terminals in right sequencing.

        It is matter, because _remove_dead can leave the unreachable.

        Example:
        <S> --> <A><B>|a
        <B> --> b|c
        Here: <A> -- dead, because it cannot generate only terminal derivation,
        <B> -- reachable and not dead, after _remove_dead, the grammar will be:
        <S> --> a
        <B> --> b|c
        because all rules, that contain dead must be removed, that's why
        <B> becomes unreachable and should be removed too as useless.

        :return: Grammar
        """
        return self._remove_dead()._remove_unreachable()

    def prepare_for_checking(self) -> 'Grammar':
        """
        Returns ready for recursive descent parsing.
        :return: Grammar
        """
        # At first find vanishing non-terminals,
        # and determine is the grammar left-recursive or not.
        g = self
        vanishing = g._vanishing()
        if g._has_left_recursion(vanishing):
            print("Has left-recursion.")

            # If it left-recursive,
            # vanishing symbols,
            # chain production and useless
            # non-terminals must be
            # removed, because they will
            # interfere right execution
            # of left-recursion removing.

            g = g._rebuild_vanishing(vanishing) \
                ._remove_chain_productions() \
                ._remove_useless() \
                ._remove_left_recursion()

            # If there was S -->+ none
            # production(-->+ means "derived by
            # finite amount of steps"),
            # we have to add it into outcome
            # grammar, just add new S' initial
            # non-terminal, with S' -> S|none rules,
            # where S -- old initial non-terminal.

            if g.__inital in vanishing:
                new_start = g.min_nterm() - 1
                g.add_rule(new_start, g.__inital)
                g.add_rule(new_start, EmptyWord)
                g.__inital = new_start
        else:
            print("Factorization performing.")
            # Don't know why, but can
            # spoil grammar after removing
            # of left-recursion.
            g = g._factorize()
        return g._remove_useless()

    def build_first(self) -> First:
        """
        Builds mapping of non-terminal ans symbols of rules to that rules.

        :return: dict
        """
        d = dict()
        for nterm, deriv in self:
            if len(deriv) > 0 and type(deriv[0]) == NonTerminal:
                continue

            if len(deriv) == 0:
                symb = ''
            else:
                symb = deriv[0]
            t = (nterm, symb)
            if t not in d:
                s = set()
                d[t] = s
            else:
                s = d[t]
            s.add(deriv)
        return d

    def recursive_descent_parsing(self, word: str, predicted: Derivation,
                                  first: Dict[Tuple[NonTerminal, chr], Set[Derivation]]) -> bool:
        len_word = len(word)
        len_predict = len(predicted)

        if len_predict == 0:
            if len_word == 0:
                return True
            else:
                return False
        for i in range(0, len_predict):
            symb = predicted[i]
            word_first = word[i:i + 1]
            if type(symb) == NonTerminal:
                if symb not in self.__rules:
                    return False
                pair = (symb, word_first)
                prediction = empty_set
                if pair in first:
                    prediction = first[pair]
                    for derivation in prediction:
                        if self.recursive_descent_parsing(word[i:], derivation + predicted[i + 1:], first):
                            return True
                for derivation in self.__rules[symb]:
                    if derivation not in prediction:
                        if self.recursive_descent_parsing(word[i:], derivation + predicted[i + 1:], first):
                            return True
                return False
            else:
                if i >= len_word:
                    return False
                if symb != word_first:
                    return False
        if len_predict != len_word:
            return False
        return True

    def check_word(self, word: str, first: First = None) -> bool:
        """
        Returns is the grammar contains such word or not.
        :param word: word for check.
        :param first: mapping of non-terminal and symbol to that
        non-terminal symbol rules where the symbol occurs at the
        first position. It's predictive element of the algorithm.
        :return: bool
        """
        if first is None:
            first = self.build_first()
        return self.recursive_descent_parsing(word, (self.__inital,), first)
