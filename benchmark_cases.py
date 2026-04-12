"""
Small benchmark descriptions for the repo.
These are simple hand-written cases that are easy to explain in the report.
"""

BENCHMARKS = [
    {
        "name": "and_or_xor_case",
        "spec": "(a AND b) XOR c",
        "buggy": "(a OR b) XOR c",
        "patch_support": ["a", "b"],
        "expected_patch": "a AND b",
        "notes": "Primary demo case for iterative SAT patch synthesis."
    },
    {
        "name": "and_nand_case",
        "spec": "(a AND b) XOR c",
        "buggy": "(NOT(a AND b)) XOR c",
        "patch_support": ["a", "b"],
        "expected_patch": "a AND b",
        "notes": "A second buggy variant you can implement next."
    }
]


if __name__ == "__main__":
    for bench in BENCHMARKS:
        print(bench)
