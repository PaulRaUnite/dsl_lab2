from loader import parse_grammar


def main():
    while True:
        print("Input filename with grammar or q to exit")
        filename = input()
        if filename == "q":
            break
        print("Input filename with test sequences")
        testname = input()
        grammar_file = open(filename)
        g = parse_grammar(grammar_file)
        print("Initial grammar.")
        print(g)
        print("Preparations.")
        g = g.prepare_for_checking()
        print(g)
        passed = True
        test_file = open(testname)
        first = g.build_first()
        mode: bool = None
        for raw_line in test_file.readlines():
            line = raw_line.replace('\n', '')
            if line == "[true]":
                mode = True
                continue
            elif line == "[false]":
                mode = False
                continue
            if mode is None:
                raise Exception("Test file must have verity declaration at its beginning")
            if g.check_word(line, first) != mode:
                passed = False
                print(not mode, line)
        if passed:
            print("All cases passed")


main()
