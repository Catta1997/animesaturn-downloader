# importing the requests library
import requests
import sys
import signal
import re
import time
import getopt
import os

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
