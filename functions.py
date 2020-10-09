import requests
import os
import sys
import signal
import psutil
from bs4 import BeautifulSoup
import re
from datetime import datetime
import locale
import time
import concurrent.futures
import my_variables
from anime import create_crawl
from anime_standalone import downloader

def selected_anime(URL):
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
        my_variables.season_num = 0
    elif "Movie" in info[0]:
        my_variables.season_num = -1
    else:
        my_variables.season +=1
        my_variables.season_num = my_variables.season
    anime_ep = parsed_html.find_all('div', attrs={'class':'btn-group episodes-button episodi-link-button'})
    my_variables.list_link.clear()
    for dim in anime_ep:
        episode = dim.find('a')['href']
        episode = episode +"§%d"%my_variables.season_num
        ep_list.append(episode)
    mutex = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ep_list)) as pool:
        if(my_variables.debug):
            print(os.getpid())
            for t in pool._threads:
                print(t)
        pool.map(one_link, ep_list)
    ep_list.clear()

def one_link(ep):
    x = ep.split("§")
    new_r = requests.get(url = x[0], params = {})
    pastebin_url = new_r.text
    parsed_html = BeautifulSoup(pastebin_url,"html.parser")
    anime_page = parsed_html.find('div', attrs={'class':'card bg-dark-as-box-shadow text-white'})
    is_link = anime_page.find('a')['href']
    if 'watch' in is_link:
        episode = is_link+'&s=alt'
    my_variables.all_ep[episode] = x[1]
    my_variables.list_link.append(episode)

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
    my_variables.correlati_list.append(URL)
    for dim in correlati:
        anime = dim.find('a')['href']
        if(my_variables.config["DEFAULT"].getboolean('only_ITA') and is_lang):
            if("-ITA" in anime):
                my_variables.correlati_list.append(anime)
        else: my_variables.correlati_list.append(anime)
    reorder_correlati()


def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for process in children:
        process.send_signal(sig)


def import_config():
    if (my_variables.config["DEFAULT"].get("crawl_path") is (None or "")):
        my_variables.config["DEFAULT"]['crawl_path'] = my_variables.dir_path + "crawl_path/"
    if (my_variables.config["DEFAULT"].get("download_path") is (None or "")):
        my_variables.config["DEFAULT"]['download_path'] = my_variables.dir_path + "download_path/"
    if (my_variables.config["DEFAULT"].get("movie_folder") is (None or "")):
        my_variables.config["DEFAULT"]['movie_folder'] = my_variables.dir_path + "movie_folder/"

def reorder_correlati():
    #global titolo
    for URL in my_variables.correlati_list:
        new_r = requests.get(url = URL, params = {})
        pastebin_url = new_r.text
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        anno = parsed_html.find('div', attrs={'class':'container shadow rounded bg-dark-as-box mb-3 p-3 w-100 text-white'})
        release = re.findall("(?<=<b>Data di uscita:</b> )(.*)(?=<br/>)",str(anno))
        my_variables.anime[release[0]] = URL
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    ordered_data = sorted(my_variables.anime.items(), key = lambda x:datetime.strptime(x[0], "%d %B %Y"), reverse=False)
    my_variables.titolo = re.findall("(?<=anime/)(.*)", ordered_data[0][1])[0]
    for x in ordered_data:
        my_variables.only_link.append(x[1])
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(my_variables.only_link)) as pool:
        if(my_variables.debug):
            for t in pool._threads:
                print(t)
        pool.map(selected_anime, my_variables.only_link)

def check_Path(crawl_path):
    if(not os.path.isdir(crawl_path)):
        os.makedirs(crawl_path)


def search(name):
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
    if(my_variables.test_ID):
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
    #selected = 2
    selected -=1 #la lista parte da 0
    URL = anime_list[selected]
    if(my_variables.config["DEFAULT"].getboolean('all')):
        get_correlati(URL)
    else:
        my_variables.season = 1
        selected_anime(URL)
    if  (my_variables.file_type == 0):
        anime.create_crawl()
    elif  (my_variables.file_type == 1):
        anime_standalone.downloader()
    else:
        sys.exit(0)