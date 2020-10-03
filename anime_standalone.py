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
import wget
from tqdm import tqdm

#config
movie_folder = "download/"
download_path = "download/"
leng = True #solo anime in italiano (utile per gli anime doppiati, es: SAO)
all = True #anime correlati
#

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

def checkDownload_Path(crawl_path):
    if(not os.path.isdir(crawl_path)):
        os.makedirs(crawl_path)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def download(url, file_name):
    print(os.path.join(download_path,file_name.split("_")[0]))
    checkDownload_Path(os.path.join(download_path,file_name.split("_")[0]))
    with open(os.path.join(download_path,file_name.split("_")[0],file_name), "wb") as file:
        response = requests.get(url, stream=True)
        with tqdm.wrapattr(open(os.path.join(download_path,file_name.split("_")[0],file_name), "wb"), "write", miniters=1, desc=url.split('/')[-1], total=int(response.headers.get('content-length', 0))) as fout:
            for chunk in response.iter_content(chunk_size=4096):
                fout.write(chunk)
        file.write(response.content)

def create_crawl():
    #creo un file vuoto, se presente sovrascrivo
    checkDownload_Path(download_path) #verifico che path esista
    print("Rilevati %d episodi"%len(list_link))
    while True:
        try:
            wantedEps = input("Dammi Range Episodi (1:%d) "%len(list_link)).split(":")
            start, finish = int(wantedEps[0]), int(wantedEps[1])
            if(start > 0 and finish > 0):
                break
            print("Invalido!")
        except:
            print("Invalido!")

    for episodedata in list_link:
        if(start <= int(episodedata[1]) <= finish):
            sourcehtml = requests.get(episodedata[0]).text
            source = find_between(sourcehtml, "file:",",").replace("\"","")
            print(source)    
            download(source,source.split("/")[-1])
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
        if(leng and is_lang):
            if("-ITA" in anime):
                correlati_list.append(anime)
        else: correlati_list.append(anime)
    reorder_correlati()

def one_link(ep):
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
        print(os.getpid())
        for t in pool._threads:
            print(t)
        results = pool.map(one_link, ep_list)
    ep_list.clear()

start = time.time()
def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    name = input("nome:")
    #name = "dxd"
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
    if(all):
        get_correlati(URL)
    else:
        season = 1
        selected_anime(URL)
    create_crawl()

if __name__ == "__main__":
    main()
    start_time = start
    print("--- %s seconds ---" % (time.time() - start_time))
