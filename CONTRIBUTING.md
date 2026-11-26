# Contributing

We welcome real engineering and software contributions. Start with an issue describing the use case, assumptions, intended reference, and proposed acceptance tests. Discuss substantial changes before implementing them. No artificial contribution targets, duplicate PRs, or automated trivial changes.

## Adding a benchmark

1. Specify governing equations, boundary conditions, sign convention, units and validity range.
2. Supply an independently derived expected result or openly licensed reference data, with source and provenance.
3. Implement a documented benchmark in `src/physcheck/benchmarks.py` and add parameter checks.
4. Add tests for a known solution, invalid parameters, zero/sign/boundary cases where relevant, and tolerance behaviour.
5. Add a runnable example and catalogue documentation. Label synthetic, analytical, and real solver-generated observations separately.
6. Submit the change for technical review. Run `python -m pytest -q` first.

## Useful first contributions

- Add a simply supported beam benchmark with independent expected values.
- Add pressure-driven pipe wall shear stress with units and sign conventions.
- Add a documented OpenFOAM extraction example using an actual public tutorial case.
- Add a CalculiX extraction example using an actual linear-elastic beam case.
- Add independent references and domain review for the existing benchmarks.
- Design a CSV result adapter with explicit column and SI conversion rules.

Do not submit proprietary solver files, confidential engineering data, unlicensed datasets or unverifiable simulation claims. Reviewers must understand and verify all changes, including AI-assisted changes.
