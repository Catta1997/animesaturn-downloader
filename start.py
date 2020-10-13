from bs4 import BeautifulSoup
import concurrent.futures
import configparser
from datetime import datetime
import locale
import os
import psutil
import re
import requests
import signal
import sys
import time
from tqdm import tqdm

correlati_list = list()
list_link = list()
only_link = list()
file_type = -1
season = 0
season_num = 0
all_ep = {}
anime = {}
titolo = ""
debug = False
test_ID = False

# config.ini
config = configparser.ConfigParser()
if ( not os.path.isfile('config.ini')):
    default_ini= '''
[DEFAULT]
# watchdir .crawljob
crawl_path =

# path di salvataggio standalone e dei file scaricati con JDownloader
download_path =

# path in cui vengono salvati i film (solo se scaricato con JDownloader)
movie_folder =

# scarica tutte le stagioni di un anime
all = True

# negli anime doppiati (es SAO) scarica solo gli episodi in italiano
only_ITA = False

# 0 = crawljob, 1 = standalone, -1  = chiedi
type = 0
'''
    with open("config.ini", 'w') as f:
        f.write(default_ini)
        f.close()
    print("non c'è ")
config.read('config.ini')
dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'

def check_ini_integrity():
    global config
    ini_fix = ""
    if (not config.has_option("DEFAULT", "crawl_path")):
        ini_fix += '''
# watchdir .crawljob
crawl_path =
'''
        #config["DEFAULT"]['crawl_path'] = ""
    if (not config.has_option("DEFAULT", "download_path")):
        ini_fix += '''
# path di salvataggio standalone e dei file scaricati con JDownloader
download_path =
'''
        #config["DEFAULT"]['download_path'] = ""
    if (not config.has_option("DEFAULT", "movie_folder")):
        ini_fix += '''
# path in cui vengono salvati i film (solo se scaricato con JDownloader)
movie_folder =
'''
        config["DEFAULT"]['movie_folder'] = ""
    if (not config.has_option("DEFAULT", "all")):
        ini_fix += '''
# scarica tutte le stagioni di un anime
all = True
'''
        #config["DEFAULT"]['all'] = str(False)
    if (not config.has_option("DEFAULT", "only_ITA")):
        ini_fix += '''
# negli anime doppiati (es SAO) scarica solo gli episodi in italiano
only_ITA = False
'''
        #config["DEFAULT"]['only_ITA'] = str(False)
    if (not config.has_option("DEFAULT", "type")):
        ini_fix += '''
# 0 = crawljob, 1 = standalone, -1  = chiedi
type = 0
'''
        #config["DEFAULT"]['type'] = -1
    with open("config.ini", 'a') as f:
        f.write(ini_fix)
        f.close()
def import_config():
    global config
    check_ini_integrity()
    if (config["DEFAULT"].get("crawl_path") is (None or "")):
        config["DEFAULT"]['crawl_path'] = dir_path + "crawl_path/"
    if (config["DEFAULT"].get("download_path") is (None or "")):
        config["DEFAULT"]['download_path'] = dir_path + "download_path/"
    if (config["DEFAULT"].get("movie_folder") is (None or "")):
        config["DEFAULT"]['movie_folder'] = dir_path + "movie_folder/"
    if (config["DEFAULT"].get("type") is None):
        config["DEFAULT"]['type'] = -1

def check_Path(crawl_path):
    #print(crawl_path)
    if(not os.path.isdir(crawl_path)):
        os.makedirs(crawl_path)

def create_crawl():
    crwd = ""
    #creo un file vuoto, se presente sovrascrivo
    if(not test_ID):
        check_Path(config["DEFAULT"]['crawl_path']) #verifico che path esista
        with open("%s%s.crawljob"%(config["DEFAULT"]['crawl_path'],titolo), 'w') as f:
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
                download = "%s%s/"%(config["DEFAULT"]['movie_folder'],titolo)
            else:
                download = "%s%s/Season_%s"%(config["DEFAULT"]['download_path'],titolo,all_ep[link])
            crwd = crwd + '''
            {
            text= %s
            downloadFolder= %s
            enabled= true
            autoStart= true
            autoConfirm= true
            }
            '''%(mp4_link,download)
        with open("%s%s.crawljob"%(config["DEFAULT"]['crawl_path'],titolo), 'a') as f:
            f.write(crwd)
            f.close()
        list_link.clear()

def download(url):
    file_name = url.split("/")[-1]
    check_Path(os.path.join(config["DEFAULT"]['download_path'],file_name.split("_")[0]))
    with open(os.path.join(config["DEFAULT"]['download_path'],file_name.split("_")[0],file_name), "wb") as file:
        response = requests.get(url, stream=True)
        with tqdm.wrapattr(open(os.path.join(config["DEFAULT"]['download_path'],file_name.split("_")[0],file_name), "wb"), "write", miniters=1, desc=url.split('/')[-1], total=int(response.headers.get('content-length', 0))) as fout:
            for chunk in response.iter_content(chunk_size=4096):
                fout.write(chunk)
        file.write(response.content)

def downloader():
    check_Path(str(config["DEFAULT"]['download_path'])) #verifico che path esista
    print("Rilevati %d episodi"%len(list_link))
    episodes = []
    while True:
        try:
            wantedEps = input("Dammi Range Episodi (1:%d) "%len(list_link)).split(":")
            if("all" in (wantedEps[0].lower())):
                start, finish = 1, len(list_link)
            elif(len(wantedEps) == 1):
                start, finish = int(wantedEps[0]), int(wantedEps[0])
            else:
                start, finish = int(wantedEps[0]), int(wantedEps[1])
            if(start > 0 and finish > 0 and finish <= len(list_link) and start <= len(list_link)):
                break
            print("Invalido!")
        except ValueError:
            print("Invalido!")
    for episodedata in list_link:
        if(start <= int(episodedata[1]) <= finish):
            sourcehtml = requests.get(episodedata[0]).text
            source = re.findall("file: \"(.*)\",",sourcehtml)
            try:
                mp4_link = source[0]
            except IndexError:
                mp4_link = ""
            episodes.append(mp4_link)
    print("\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        pool.map(download, episodes)
    list_link.clear()
#riordino correlati e  selezionato in base alla data di uscita

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
    anime_type = parsed_html.find('span', attrs={'class':'badge badge-secondary'})
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
        pool.map(one_link, ep_list)
    ep_list.clear()

def one_link(ep):
    if  (file_type == 0): #crawljob
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
    elif  (file_type == 1): # standalone
        epnumber = ep.replace("§1","").split("-")[-1]
        x = ep.replace("§1","")
        new_r = requests.get(url = x, params = {})
        pastebin_url = new_r.text
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        anime_page = parsed_html.find('div', attrs={'class':'card bg-dark-as-box-shadow text-white'})
        is_link = anime_page.find('a')['href']
        if 'watch' in is_link:
            episode = is_link+'&s=alt'
        list_link.append([episode,epnumber])

def sig_handler(_signo, _stack_frame):
    print("\n")
    kill_child_processes(os.getpid())
    sys.exit(0)

def get_correlati(URL):
    is_lang = "-ITA" in URL #controlla se il link supporta la lingua ita
    #analizzo url e cerco la sezione "correlati" e richiamo la funzione per trovare gli episodi per ognuno di essi
    new_r = requests.get(url = URL, params = {})
    pastebin_url = new_r.text
    parsed_html = BeautifulSoup(pastebin_url,"html.parser")
    correlati = parsed_html.find_all('div', attrs={'class':'owl-item anime-card-newanime main-anime-card'})
    correlati_list.append(URL)
    for dim in correlati:
        anime = dim.find('a')['href']
        if(config["DEFAULT"].getboolean('only_ITA') and is_lang):
            if("-ITA" in anime):
                correlati_list.append(anime)
        else: correlati_list.append(anime)
    reorder_correlati()

def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)

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
        pool.map(selected_anime, only_link)

def search(name):
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
    print("--------")
    for dim in animes:
        print("ID: \x1b[36m" + str(x) + "\x1b[0m")
        print("TITOLO:")
        print("\x1b[32m" + dim.find('a',attrs={'class':'badge badge-archivio badge-light'}).text + "\x1b[0m")
        print("TRAMA:")
        print("\x1b[37m" + dim.find('p',attrs={'class':'trama-anime-archivio text-white rounded'}).text +"\x1b[0m")
        anime_list.append(dim.find('a')['href'])
        print("--------")
        x+=1
    if(test_ID):
        selected = 1
    else:
        while True: #richiedere id se + sbagliato
            try:
                selected = int(input("ID ('0' per uscire):"))
                if (selected == 0):
                    exit(0)
                if (selected >  len(animes) or selected < 0):
                    print("\x1b[31mCi sono solo %d risultati\x1b[0m"%len(animes))
                    continue
                break
            except ValueError:
                print("\x1b[31mNon è un ID valido, riprovare...\x1b[0m")
    selected -=1 #la lista parte da 0
    URL = anime_list[selected]
    if(config["DEFAULT"].getboolean('all')):
        get_correlati(URL)
    else:
        season = 1
        selected_anime(URL)
    if  (file_type == 0):
        create_crawl()
    elif  (file_type == 1):
        downloader()
    else:
        sys.exit(0)

def seleziona():
    while True: #richiedere id se + sbagliato
            try:
                file_type = int(input("0: Crawljob 1:Standalone: "))
                if (file_type <  0 or file_type > 1):
                    print("\x1b[31mScelta non valida, riprovare...\x1b[0m")
                    continue
                break
            except ValueError:
                print("\x1b[31mScelta non valida, riprovare...\x1b[0m")
    return file_type

def main():
    global file_type
    import_config()
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    try:
        file_type = int(config["DEFAULT"]['type'])
        if(file_type == 1):
            print("\x1b[4mUtilizzo tipologia standalone\x1b[0m")
            print()
        if(file_type == 0):
            print("\x1b[4mUtilizzo tipologia crawljob\x1b[0m")
            print()
        if(file_type == -1):
            file_type = seleziona()
        elif(file_type > 1 or file_type < -1):
            print("\x1b[31mValore inserito nel config.ini non valido\x1b[0m")
            print("Inserire manualmente la tipologia di programma: ")
            file_type = seleziona()
    except ValueError:
        print("\x1b[31mValore inserito nel config.ini non valido\x1b[0m")
        print("Inserire manualmente la tipologia di programma: ")
        file_type = seleziona()
    name = input("nome:")
    search(name)

def test(name):
    global file_type
    global test_ID
    file_type = 0
    test_ID = True
    search(name)
    return 1

if __name__ == "__main__":
    main()