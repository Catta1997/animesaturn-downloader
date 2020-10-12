# importing the requests library
import requests
import sys
import signal
import re
import time
import getopt
import my_variables
import os
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
            my_variables.config["DEFAULT"]['download_path'] = arg
        if opt in ['--crawlpath']:
            my_variables.config["DEFAULT"]['crawl_path'] = arg
        if opt in ['-a', '--all']:
            if ('False' in str(arg)):
                my_variables.config["DEFAULT"]['all'] = False
            if ('True' in str(arg)):
                my_variables.config["DEFAULT"]['all'] = True
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)
    return keyword
##############################################

def check_Path(crawl_path):
    print(crawl_path)
    if(not os.path.isdir(crawl_path)):
        os.makedirs(crawl_path)

def create_crawl():
    crwd = ""
    #creo un file vuoto, se presente sovrascrivo
    if(not my_variables.test_ID):
        check_Path(my_variables.config["DEFAULT"]['crawl_path']) #verifico che path esista
        with open("%s%s.crawljob"%(my_variables.config["DEFAULT"]['crawl_path'],my_variables.titolo), 'w') as f:
            f.write(crwd)
            f.close()
        print("Creo crawljob per %d episodi"%len(my_variables.list_link))
        for link in my_variables.list_link:
            sourcehtml = requests.get(link).text
            source = re.findall("file: \"(.*)\",",sourcehtml)
            try:
                mp4_link = source[0]
            except IndexError:
                mp4_link = ""
            if my_variables.all_ep[link]=="-1":
                download = "%s%s/"%(my_variables.config["DEFAULT"]['movie_folder'],my_variables.titolo)
            else:
                download = "%s%s/Season_%s"%(my_variables.config["DEFAULT"]['download_path'],my_variables.titolo,my_variables.all_ep[link])
            crwd = crwd + '''
            {
            text= %s
            downloadFolder= %s
            enabled= true
            autoStart= true
            autoConfirm= true
            }
            '''%(mp4_link,download)
        with open("%s%s.crawljob"%(my_variables.config["DEFAULT"]['crawl_path'],my_variables.titolo), 'a') as f:
            print(my_variables.config["DEFAULT"]['crawl_path'])
            f.write(crwd)
            f.close()
        my_variables.list_link.clear()
#riordino correlati e  selezionato in base alla data di uscita