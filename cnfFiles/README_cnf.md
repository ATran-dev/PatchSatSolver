# CNF file notes

These files are small illustrative DIMACS-style encodings for the internal node relation used in the demo.

## `spec_case1.txt`
Encodes:

```text
w = a AND b
```

## `impl_case1.txt`
Encodes:

```text
w = a OR b
```

These are not yet the full rectification flow by themselves.
They are small CNF building blocks that help explain the difference between the correct node relation and the buggy one.

For the actual project demo, the iterative SAT loop is shown in `iterative_patch_solver.py`.
