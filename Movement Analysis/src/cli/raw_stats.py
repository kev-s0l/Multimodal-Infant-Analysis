import argparse
from src.plots.plot_raw_stats import main  

if __name__ == "__main__":
    import sys
    from subprocess import call

    call([sys.executable, "-m", "src.plots.plot_raw_accel"] + sys.argv[1:])
