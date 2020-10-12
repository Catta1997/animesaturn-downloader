import signal
import functions
import  my_variables
def main():
    while True: #richiedere id se + sbagliato
        try:
            type_p = int(input("0: Crawljob 1:Standalone: "))
            if (type_p <  0 or type_p > 1):
                print("\x1b[31mScelta non valida, riprovare...\x1b[0m")
                continue
            break
        except ValueError:
            print("\x1b[31mScelta non valida, riprovare...\x1b[0m")
    my_variables.file_type = type_p
    signal.signal(signal.SIGTERM, functions.sig_handler)
    signal.signal(signal.SIGINT, functions.sig_handler)
    functions.import_config()
    name = input("nome:")
    functions.search(name)


def test(name):
    my_variables.file_type = 0
    my_variables.test_ID = True
    functions.search(name)
    return 1

if __name__ == "__main__":
    main()