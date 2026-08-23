"""Backward-compatible entry point for the canonical refined Figure 5 script."""

from make_fig5_semantics_refined import main


if __name__ == "__main__":
    for output in main():
        print(output)
