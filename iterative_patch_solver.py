from itertools import product
from pysat.solvers import Solver

"""
Iterative SAT-based patch synthesis demo.

Spec circuit:
    f_spec(a,b,c) = (a AND b) XOR c

Buggy circuit:
    f_bug(a,b,c) = (a OR b) XOR c

Patch target:
    Replace the buggy internal node with P(a,b).

This demonstrates the iterative-SAT idea discussed in the proposal:
    1) guess a patch,
    2) find a counterexample,
    3) add constraints from the counterexample,
    4) repeat until no counterexample remains.
"""


def spec(a: int, b: int, c: int) -> int:
    return (a & b) ^ c


def buggy_original(a: int, b: int, c: int) -> int:
    return (a | b) ^ c


def fixed_with_patch(a: int, b: int, c: int, patch: dict[tuple[int, int], int]) -> int:
    w = patch[(a, b)]
    return w ^ c


def find_counterexample_for_buggy():
    for a, b, c in product([0, 1], repeat=3):
        if buggy_original(a, b, c) != spec(a, b, c):
            return (a, b, c)
    return None


def find_counterexample_for_patch(patch: dict[tuple[int, int], int]):
    for a, b, c in product([0, 1], repeat=3):
        if fixed_with_patch(a, b, c, patch) != spec(a, b, c):
            return (a, b, c)
    return None


class PatchSynthesizer:
    def __init__(self):
        self.varmap = {(0, 0): 1, (0, 1): 2, (1, 0): 3, (1, 1): 4}
        self.clauses: list[list[int]] = []

    def add_constraint_from_counterexample(self, a: int, b: int, c: int) -> None:
        desired_patch_value = (a & b)
        # desired_patch_value = 1 - (a & b)
        var = self.varmap[(a, b)]
        self.clauses.append([var] if desired_patch_value else [-var])

    def solve(self):
        with Solver(name="glucose3") as solver:
            for clause in self.clauses:
                solver.add_clause(clause)
            if not solver.solve():
                return None
            model = set(solver.get_model())
            return {key: 1 if var in model else 0 for key, var in self.varmap.items()}


def print_patch_table(patch: dict[tuple[int, int], int]) -> None:
    print(" a b | P(a,b)")
    print("-----+-------")
    for a, b in product([0, 1], repeat=2):
        print(f" {a} {b} |   {patch[(a, b)]}")
    print()


def verify_patch(patch: dict[tuple[int, int], int]) -> bool:
    ok = True
    print(" a b c | spec | fixed")
    print("-------+------+------")
    for a, b, c in product([0, 1], repeat=3):
        s = spec(a, b, c)
        f = fixed_with_patch(a, b, c, patch)
        print(f" {a} {b} {c} |  {s}   |   {f}")
        ok = ok and (s == f)
    print()
    return ok


def run():
    
    seen_ces = set()
    
    print("=== Iterative SAT Patch Synthesis Demo ===")
    print("Spec circuit : f(a,b,c) = (a AND b) XOR c")
    print("Buggy circuit: f(a,b,c) = (a OR  b) XOR c")
    print()

    ce0 = find_counterexample_for_buggy()
    print("Initial buggy counterexample:", ce0)
    print()

    synth = PatchSynthesizer()
    iteration = 0

    while True:
        iteration += 1
        print(f"--- Iteration {iteration} ---")
        patch = synth.solve()
        if patch is None:
            print("UNSAT: no patch exists under current constraints.")
            return

        print("Current patch candidate:")
        print_patch_table(patch)

        ce = find_counterexample_for_patch(patch)
        if ce is None:
            print("No counterexample found. Patch is correct.\n")
            print("Final patch:")
            print_patch_table(patch)
            passed = verify_patch(patch)
            print("Verification passed." if passed else "Verification failed.")
            return
        
        if ce in seen_ces:
            print("Repeated counterexample detected:", ce)
            print("Stopping to avoid infinite loop.")
            print("Patch is unable to be Found.")
            return
        
        seen_ces.add(ce)

        print("Counterexample found:", ce)
        a, b, c = ce
        synth.add_constraint_from_counterexample(a, b, c)
        print(f"Added constraint forcing P({a},{b}) = {a & b}\n")


if __name__ == "__main__":
    run()
