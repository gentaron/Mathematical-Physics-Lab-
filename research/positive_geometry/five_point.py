"""Run with: python -m research.positive_geometry.five_point"""

from .associahedron import amplitude, triangulations, verify_residues


def main() -> None:
    polygon = (1, 2, 3, 4, 5)
    checks = verify_residues(polygon)
    if len(triangulations(polygon)) != 5 or not all(c["passed"] for c in checks):
        raise RuntimeError("Five-point reproduction failed")
    print("Triangulations:", len(triangulations(polygon)))
    print("Amplitude:", amplitude(polygon))
    print("All five residue tests: PASS")


if __name__ == "__main__":
    main()
