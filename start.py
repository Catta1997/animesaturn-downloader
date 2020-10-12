import signal
from animesaturn import AnimeSaturn
def main():
    animesaturn = AnimeSaturn()
    while True: #richiedere id se + sbagliato
        try:
            type_p = int(input("0: Crawljob 1:Standalone: "))
            if (type_p <  0 or type_p > 1):
                print("\x1b[31mScelta non valida, riprovare...\x1b[0m")
                continue
            break
        except ValueError:
            print("\x1b[31mScelta non valida, riprovare...\x1b[0m")
        
    animesaturn.file_type = type_p
    signal.signal(signal.SIGTERM, animesaturn.sig_handler)
    signal.signal(signal.SIGINT, animesaturn.sig_handler)
    name = input("nome:")
    animesaturn.search(name)


def test(name):
    animesaturn.file_type = 0
    animesaturn.test_ID = True
    animesaturn.search(name)
    return 1

if __name__ == "__main__":
    main()