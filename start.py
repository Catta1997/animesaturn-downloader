"""AnimeSaturn-downloader by Catta1997."""
import os
import signal
import sys

from animesaturn import AnimeSaturn

def sig_handler(_signo, _stack_frame):
    """Funzione eseguita prima di una terminazione forzata."""
    print("\n")
    AnimeSaturn.kill_child_processes(os.getpid())
    sys.exit(0)

def main():
    """Avvio."""
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGHUP, sig_handler)
    AnimeSaturn()

def test():
    """Funzione travis."""
    AnimeSaturn(debug = True)
    return 0

if __name__ == "__main__":
    main()
