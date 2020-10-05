# importing the requests library 
import requests,os,subprocess
import sys
import signal, psutil
from bs4 import BeautifulSoup
import re
from datetime import datetime
import locale
import time
import concurrent.futures
import ast
import getopt
#config
config = {'crawl_path': None, 'download_path': None, 'movie_folder' : None, 'all': True, 'only_ITA':True}
debug = False
#
def import_config():
    global config
    with open('config.txt') as f:
            config = (f.read())
            #converte da stringa a  dizionario
            config = ast.literal_eval(config)
            f.close()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if (config['crawl_path'] is None):
        config['crawl_path'] = dir_path + '/'
    if (config['download_path'] is None):
        config['download_path'] = dir_path + '/'
    if (config['movie_folder'] is None):
        config['movie_folder'] = dir_path + '/'
def usage():
    usage = f"AnimeSaturn Usage:\n" \
            f"\t-k, --keyword (str):\t\tSpecify the keyword to search\n" \
            f"\t-s, --all (bool):\t\tDownload all seasons\n" \
            f"\t--jdownloadpath (Path):\t\tDestination folder for the anime dir. MUST be used in conjunction with --crawlpath\n" \
            f"\t--crawlpath (Path):\t\tDestination folder for the crawljobs. MUST be used in conjunction with -jdp\n" \
            f"\t-h, --help:\t\t\tShow this screen\n"
    print(usage)
def cli():
    argv = sys.argv[1:]
    keyword = None
    try:
        opts, args = getopt.getopt(argv, 'k:hac', ['keyword=','jdownloadpath=', 'crawlpath=', 'downloadpath=', 'all='])
    except getopt.GetoptError:
        # stampa l'informazione di aiuto ed esce:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-k', '--keyword']:
            keyword = arg
        if opt in ['--jdownloadpath']:
            config['download_path'] = arg
        if opt in ['--crawlpath']:
            config['crawl_path'] = arg
        if opt in ['-a', '--all']:
            if ('False' in str(arg)):
                config['all'] = False
            if ('True' in str(arg)):
                config['all'] = True
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)
    return keyword


only_link = list()
list_link = list()
correlati_list = list()
anime = {}
all_ep = {}
titolo = ""
season = 0
season_num = 0
def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)

def checkCrawl_Path(crawl_path):
    print(crawl_path)
    if(not os.path.isdir(crawl_path)):
        print("kjk")
        os.makedirs(crawl_path)


def create_crawl():
    crwd = ""
    #creo un file vuoto, se presente sovrascrivo
    checkCrawl_Path(config['crawl_path']) #verifico che path esista
    with open("%s%s.crawljob"%(config['crawl_path'],titolo), 'w') as f:
        f.write(crwd)
        f.close()
    print("Creo crawljob per %d episodi"%len(list_link))
    for link in list_link:
        sourcehtml = requests.get(link).text
        source = re.findall("file: \"(.*)\",",sourcehtml)
        try:
            mp4_link = source[0]
        except IndexError:
            mp4_link = ""
        if all_ep[link]=="-1":
            download = "%s%s/"%(config['movie_folder'],titolo)
        else:
            download = "%s%s/Season_%s"%(config['download_path'],titolo,all_ep[link])
        crwd = crwd + '''
        {
        text= %s
        downloadFolder= %s
        enabled= true
        autoStart= true
        autoConfirm= true
        }
        '''%(mp4_link,download)
    with open("%s%s.crawljob"%(config['crawl_path'],titolo), 'a') as f:
        print(config['crawl_path'])
        f.write(crwd)
        f.close()
    list_link.clear()
#riordino correlati e  selezionato in base alla data di uscita
def reorder_correlati():
    global titolo
    for URL in correlati_list:
        new_r = requests.get(url = URL, params = {})
        pastebin_url = new_r.text 
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        anno = parsed_html.find('div', attrs={'class':'container shadow rounded bg-dark-as-box mb-3 p-3 w-100 text-white'})
        release = re.findall("(?<=<b>Data di uscita:</b> )(.*)(?=<br/>)",str(anno))
        anime[release[0]] = URL
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    ordered_data = sorted(anime.items(), key = lambda x:datetime.strptime(x[0], "%d %B %Y"), reverse=False)
    titolo = re.findall("(?<=anime/)(.*)", ordered_data[0][1])[0]
    for x in ordered_data:
        only_link.append(x[1])
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(only_link)) as pool:
        if(debug):
            for t in pool._threads:
                print(t)
        results = pool.map(selected_anime, only_link)

def sig_handler(_signo, _stack_frame):
    print("\n")
    kill_child_processes(os.getpid())
    sys.exit(0)
def get_correlati(URL):
    is_lang = "-ITA" in URL #controlla se il link supporta la lingua ita
    #analizzo url e cerco la sezione "correlati" e richiamo la funzione per trovare gli episodi per gonuno di essi
    new_r = requests.get(url = URL, params = {})
    pastebin_url = new_r.text 
    parsed_html = BeautifulSoup(pastebin_url,"html.parser")
    correlati = parsed_html.find_all('div', attrs={'class':'owl-item anime-card-newanime main-anime-card'})
    correlati_list.append(URL)
    for dim in correlati:
        anime = dim.find('a')['href']
        if(config['only_ITA'] and is_lang):
            if("-ITA" in anime):
                correlati_list.append(anime)
        else: correlati_list.append(anime)
    reorder_correlati()

def one_link(ep):
    x = ep.split("§")
    new_r = requests.get(url = x[0], params = {})
    pastebin_url = new_r.text
    parsed_html = BeautifulSoup(pastebin_url,"html.parser")
    anime_page = parsed_html.find('div', attrs={'class':'card bg-dark-as-box-shadow text-white'})
    is_link = anime_page.find('a')['href']
    if 'watch' in is_link: 
        episode = is_link+'&s=alt'
    all_ep[episode] = x[1]
    list_link.append(episode)

def selected_anime(URL):
    global season
    global season_num
    ep_list = list()
    mutex = False
    #visito la pagina, trovo il tasto per l'episodio. Sucessivamente analizzo quella  pagina e ottengo il link di streaming
    new_r = requests.get(url = URL, params = {})
    pastebin_url = new_r.text 
    parsed_html = BeautifulSoup(pastebin_url,"html.parser")
    all_info = parsed_html.find('div', attrs={'class':'container shadow rounded bg-dark-as-box mb-3 p-3 w-100 text-white'})
    info = re.findall("(?<=<b>Episodi:</b> )(.*)(?=<br/>)",str(all_info))
    anime_type = anime_page = parsed_html.find('span', attrs={'class':'badge badge-secondary'})
    while (mutex):
        time.sleep(0.5)
    mutex = True
    if ('OVA' in anime_type.text or "Special" in info[0]): 
        season_num = 0
    elif "Movie" in info[0]:
        season_num = -1
    else: 
        season +=1
        season_num = season
    anime_ep = parsed_html.find_all('div', attrs={'class':'btn-group episodes-button episodi-link-button'})
    list_link.clear()
    for dim in anime_ep:
        episode = dim.find('a')['href']
        episode = episode +"§%d"%season_num
        ep_list.append(episode)
    mutex = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ep_list)) as pool:
        if(debug):
            print(os.getpid())
            for t in pool._threads:
                print(t)
        results = pool.map(one_link, ep_list)
    ep_list.clear()

start = time.time()
def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    key = None
    import_config()
    key = cli()
    if (key is None):
        name = input("nome:")
    else:
        name = key
    if (debug):
        print(config)
    search(name)

def search(name):
    global start
    global season
    anime_list  = list()
    URL = "https://www.animesaturn.it/animelist"
    r = requests.get(url = URL, params = {"search":name})
    pastebin_url = r.text 
    html = pastebin_url
    parsed_html = BeautifulSoup(html,"html.parser")
    animes = parsed_html.find_all('ul', attrs={'class':'list-group'})
    x = 1
    if (len(animes)) == 0:
        print("\x1b[31mNessun Anime trovato per %s\x1b[0m"%name)
        exit(0)
    for dim in animes:
        print("--------")
        print(x)
        print("TITOLO:")
        print("\x1b[32m" + dim.find('a',attrs={'class':'badge badge-archivio badge-light'}).text + "\x1b[0m")
        print("TRAMA:")
        print("\x1b[37m" + dim.find('p',attrs={'class':'trama-anime-archivio text-white rounded'}).text +"\x1b[0m")
        anime_list.append(dim.find('a')['href'])
        print("--------")
        x+=1
    while True: #richiedere id se + sbagliato
        try:
            selected = int(input("ID ('0' per uscire):"))
            if(selected == 0) : exit(0)

            if (selected >  len(animes) or selected < 0):
                print("\x1b[31mCi sono solo %d risultati\x1b[0m"%len(animes))
                continue
            break
        except ValueError:
            print("\x1b[31mNon è un ID valido, riprovare...\x1b[0m")
        
    #selected = 2
    selected -=1 #la lista parte da 0
    start = time.time()
    URL = anime_list[selected]
    if(config['all']):
        get_correlati(URL)
    else:
        season = 1
        selected_anime(URL)
    create_crawl()

if __name__ == "__main__":
    main()
    start_time = start
    if(debug):
        print("--- %s seconds ---" % (time.time() - start_time))