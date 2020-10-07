# importing the requests library
import requests
import sys
import signal
import re
import time
import getopt
import classes
import init
#config
#

######################################
def usage():
    usage = '''
AnimeSaturn Usage:
    -k, --keyword (str):\tSpecify the keyword to search
    -s, --all (bool):\t\tDownload all seasons
    --jdownloadpath (Path):\tDestination folder for the anime dir. MUST be used in conjunction with --crawlpath
    --crawlpath (Path):\t\tDestination folder for the crawljobs. MUST be used in conjunction with -jdp
    -h, --help:\t\t\tShow this screen
        '''
    print(usage)

def cli():
    argv = sys.argv[1:]
    keyword = None
    try:
        opts = getopt.getopt(argv, 'k:hac', ['keyword=','jdownloadpath=', 'crawlpath=', 'downloadpath=', 'all='])
    except getopt.GetoptError:
        # stampa l'informazione di aiuto ed esce:ValueError: not enough values to unpack (expected 2, got 0)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-k', '--keyword']:
            keyword = arg
        if opt in ['--jdownloadpath']:
            init.config["DEFAULT"]['download_path'] = arg
        if opt in ['--crawlpath']:
            init.config["DEFAULT"]['crawl_path'] = arg
        if opt in ['-a', '--all']:
            if ('False' in str(arg)):
                init.config["DEFAULT"]['all'] = False
            if ('True' in str(arg)):
                init.config["DEFAULT"]['all'] = True
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)
    return keyword
##############################################

def create_crawl():
    crwd = ""
    #creo un file vuoto, se presente sovrascrivo
    if(not init.test_ID):
        classes.check_Path(init.config["DEFAULT"]['crawl_path']) #verifico che path esista
        with open("%s%s.crawljob"%(init.config["DEFAULT"]['crawl_path'],init.titolo), 'w') as f:
            f.write(crwd)
            f.close()
        print("Creo crawljob per %d episodi"%len(init.list_link))
        for link in init.list_link:
            sourcehtml = requests.get(link).text
            source = re.findall("file: \"(.*)\",",sourcehtml)
            try:
                mp4_link = source[0]
            except IndexError:
                mp4_link = ""
            if init.all_ep[link]=="-1":
                download = "%s%s/"%(init.config["DEFAULT"]['movie_folder'],init.titolo)
            else:
                download = "%s%s/Season_%s"%(init.config["DEFAULT"]['download_path'],init.titolo,init.all_ep[link])
            crwd = crwd + '''
            {
            text= %s
            downloadFolder= %s
            enabled= true
            autoStart= true
            autoConfirm= true
            }
            '''%(mp4_link,download)
        with open("%s%s.crawljob"%(init.config["DEFAULT"]['crawl_path'],init.titolo), 'a') as f:
            print(init.config["DEFAULT"]['crawl_path'])
            f.write(crwd)
            f.close()
        init.list_link.clear()
#riordino correlati e  selezionato in base alla data di uscita

def main():
    init.file_type = 0
    signal.signal(signal.SIGTERM, classes.sig_handler)
    signal.signal(signal.SIGINT, classes.sig_handler)
    classes.import_config()
    #key = cli()
    # rivedere funzione cli()
    key = None
    if (key is None):
        name = input("nome:")
    else:
        name = key
    if (init.debug):
        print(init.config)
    classes.search(name)
    return 1

def test(name):
    init.test_ID = True
    classes.search(name)
    return 1

if __name__ == "__main__":
    main()
