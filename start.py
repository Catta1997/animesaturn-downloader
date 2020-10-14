import signal
import sys
from animesaturn import AnimeSaturn
def main():
    animesaturn = AnimeSaturn()
    signal.signal(signal.SIGTERM, animesaturn.sig_handler)
    signal.signal(signal.SIGINT, animesaturn.sig_handler)

def test(fixthetester):
    animesaturn = AnimeSaturn(debug=True)
    return 0

if __name__ == "__main__":
    main()
