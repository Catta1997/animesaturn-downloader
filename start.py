import signal
import sys
from animesaturn import AnimeSaturn
def sig_handler(_signo, _stack_frame):
    print("\n")
    sys.exit(0)
def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    AnimeSaturn()

def test(fixthetester):
    AnimeSaturn(debug=True)
    return 0

if __name__ == "__main__":
    main()
