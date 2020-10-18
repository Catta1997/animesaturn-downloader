import concurrent.futures
import configparser
import locale
import os
import psutil
import re
import requests
import signal
import sys
import time

from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm

class AnimeSaturn:
    #config stuff
    dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    verbose = False
    titolo = ""
    only_link = list()
    list_link = list()
    correlati_list = list()
    anime = {}
    all_ep = {}
    season = 0
    season_num = 0

    def __init__(self, debug = False):
        if(debug):
            self.test_ID = True
            self.file_type = 0
        else:
            self.test_ID = False
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.import_config()
        try:
            if(not self.test_ID):
                if(self.file_type == 1):
                    print("\x1b[4mUtilizzo tipologia standalone\x1b[0m")
                    print()
                elif(self.file_type == 0):
                    print("\x1b[4mUtilizzo tipologia crawljob\x1b[0m")
                    print()
                elif(self.file_type == -1):
                    self.seleziona()
                elif(self.file_type > 1 or self.file_type < -1):
                    print("\x1b[31mValore inserito nel config.ini non valido\x1b[0m")
                    print("Inserire manualmente la tipologia di programma: ")
                    self.seleziona()
        except ValueError:
            print("\x1b[31mValore inserito nel config.ini non valido\x1b[0m")
            print("Inserire manualmente la tipologia di programma: ")
            self.seleziona()
        if(self.verbose):
            print(self.test_ID)
        if(self.test_ID):
            self.search("love is war")
        else:
            name = input("nome:")
            self.search(name)

    def seleziona(self):
        while True: #richiedere id se + sbagliato
                try:
                    self.file_type = int(input("0: Crawljob 1:Standalone: "))
                    if (self.file_type <  0 or self.file_type > 1):
                        print("\x1b[31mScelta non valida, riprovare...\x1b[0m")
                        continue
                    break
                except ValueError:
                    print("\x1b[31mScelta non valida, riprovare...\x1b[0m")

    def import_config(self):
        if (self.config["DEFAULT"].getint("limit") is (None or "")):
            self.limit = -1
        else:
            try:
                self.limit = int(self.config["DEFAULT"].getint("limit"))
            except ValueError:
                self.limit = -1
        if (self.config["DEFAULT"].get("crawl_path") is (None or "")):
            self.crawl_path = self.dir_path + "crawl_path/"
        else:
            self.crawl_path = self.config["DEFAULT"]['crawl_path']
        if (self.config["DEFAULT"].get("download_path") is (None or "")):
            self.download_path = self.dir_path + "download_path/"
        else:
            self.download_path = self.config["DEFAULT"]['download_path']
        if (self.config["DEFAULT"].get("movie_folder") is (None or "")):
            self.movie_path = self.dir_path + "movie_folder/"
        else:
            self.movie_path = self.config["DEFAULT"].get("movie_folder")
        try:
            self.file_type
        except AttributeError:
            if (self.config["DEFAULT"].getint("type") is (None or "")):
                self.file_type = -1
            else:
                try:
                    self.file_type = int(self.config["DEFAULT"].getint("type"))
                except ValueError:
                    self.file_type = -1

    def selected_anime(self, url):
        ep_list = list()
        mutex = False
        if(self.verbose):
            print(url)
        #visito la pagina, trovo il tasto per l'episodio. Sucessivamente analizzo quella  pagina e ottengo il link di streaming
        new_r = requests.get(url = url, params = {})
        pastebin_url = new_r.text
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        self.titolo = url.split("/")[-1]
        all_info = parsed_html.find('div', attrs={'class':'container shadow rounded bg-dark-as-box mb-3 p-3 w-100 text-white'})
        info = re.findall("(?<=<b>Episodi:</b> )(.*)(?=<br/>)",str(all_info))
        anime_type = parsed_html.find('span', attrs={'class':'badge badge-secondary'})
        while (mutex):
            time.sleep(0.5)
        mutex = True
        if ('OVA' in anime_type.text or "Special" in info[0]):
            self.season_num = 0
        elif "Movie" in info[0]:
            self.season_num = -1
        else:
            self.season +=1
            self.season_num = self.season
        anime_ep = parsed_html.find_all('div', attrs={'class':'btn-group episodes-button episodi-link-button'})
        self.list_link.clear()
        for dim in anime_ep:
            episode = dim.find('a')['href']
            episode = episode +"§%d"%self.season_num
            ep_list.append(episode)
        mutex = False
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(ep_list)) as pool:
            if(self.verbose):
                print(os.getpid())
                for t in pool._threads:
                    print(t)
            pool.map(self.one_link, ep_list)
        ep_list.clear()

    def one_link(self, ep):
        x = ep.split("§")
        new_r = requests.get(url = x[0], params = {})
        pastebin_url = new_r.text
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        anime_page = parsed_html.find('div', attrs={'class':'card bg-dark-as-box-shadow text-white'})
        is_link = anime_page.find('a')['href']
        if 'watch' in is_link:
            episode = is_link+'&s=alt'
        self.all_ep[episode] = x[1]
        self.list_link.append([episode,int(x[0].split("-")[-1])])

    def get_correlati(self, url):
        is_lang = "-ITA" in url #controlla se il link supporta la lingua ita
        #analizzo url e cerco la sezione "correlati" e richiamo la funzione per trovare gli episodi per gonuno di essi
        new_r = requests.get(url = url, params = {})
        pastebin_url = new_r.text
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        correlati = parsed_html.find_all('div', attrs={'class':'owl-item anime-card-newanime main-anime-card'})
        self.correlati_list.append(url)
        for dim in correlati:
            anime = dim.find('a')['href']
            if(self.config["DEFAULT"].getboolean('only_ITA') and is_lang):
                if("-ITA" in anime):
                    self.correlati_list.append(anime)
            else:
                self.correlati_list.append(anime)
        self.reorder_correlati()

    def kill_child_processes(self, parent_pid):
        try:
            parent = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            return
        children = parent.children(recursive=True)
        for process in children:
            process.send_signal(signal.SIGTERM)
        if(self.verbose):
            print("Killed %d processes"%len(children))

    def reorder_correlati(self):
        for URL in self.correlati_list:
            new_r = requests.get(url = URL, params = {})
            pastebin_url = new_r.text
            parsed_html = BeautifulSoup(pastebin_url,"html.parser")
            anno = parsed_html.find('div', attrs={'class':'container shadow rounded bg-dark-as-box mb-3 p-3 w-100 text-white'})
            release = re.findall("(?<=<b>Data di uscita:</b> )(.*)(?=<br/>)",str(anno))
            self.anime[release[0]] = URL
        locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
        ordered_data = sorted(self.anime.items(), key = lambda x:datetime.strptime(x[0], "%d %B %Y"), reverse=False)
        self.titolo = re.findall("(?<=anime/)(.*)", ordered_data[0][1])[0]
        for x in ordered_data:
            self.only_link.append(x[1])
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.only_link)) as pool:
            if(self.verbose):
                for t in pool._threads:
                    print(t)
            pool.map(self.selected_anime, self.only_link)

    def search(self,name):
        anime_list  = list()
        URL = "https://www.animesaturn.it/animelist"
        r = requests.get(url = URL, params = {"search":name})
        pastebin_url = r.text
        html = pastebin_url
        parsed_html = BeautifulSoup(html,"html.parser")
        animes = parsed_html.find_all('ul', attrs={'class':'list-group'})
        id_num = 1
        if (len(animes)) == 0:
            print("\x1b[31mNessun Anime trovato per %s\x1b[0m"%name)
            exit(0)
            print("--------")
        for dim in animes:
            print("\x1b[36mID:")
            print(str(id_num) + "\x1b[0m")
            print("TITOLO:")
            print("\x1b[32m" + dim.find('a',attrs={'class':'badge badge-archivio badge-light'}).text + "\x1b[0m")
            print("TRAMA:")
            print("\x1b[37m" + dim.find('p',attrs={'class':'trama-anime-archivio text-white rounded'}).text +"\x1b[0m")
            anime_list.append(dim.find('a')['href'])
            print("--------")
            id_num += 1
        if(self.test_ID):
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
        self.season = 1
        self.selected_anime(URL)
        if  (self.file_type == 0):
            self.create_crawl()
        elif  (self.file_type == 1):
            self.downloader()
        else:
            sys.exit(0)

    def check_Path(self, crawl_path):
        if(self.verbose):
            print(crawl_path)
        if(not os.path.isdir(crawl_path)):
            os.makedirs(crawl_path)

    def create_crawl(self):
        crwd = ""
        #creo un file vuoto, se presente sovrascrivo
        if(not self.test_ID):
            self.check_Path(self.crawl_path) #verifico che path esista
            with open("%s%s.crawljob"%(self.crawl_path,self.titolo), 'w') as f:
                f.write(crwd)
                f.close()
            print("Creo crawljob per %d episodi..."%len(self.list_link))
            for link in self.list_link:
                sourcehtml = requests.get(link[0]).text
                source = re.findall("file: \"(.*)\",",sourcehtml)
                try:
                    mp4_link = source[0]
                except IndexError:
                    mp4_link = ""
                if self.all_ep[link[0]]=="-1":
                    download = "%s%s/"%(self.movie_path,self.titolo)
                else:
                    download = "%s%s/Season_%s"%(self.download_path,self.titolo,self.all_ep[link[0]])
                crwd = crwd + '''
                {
                text= %s
                downloadFolder= %s
                enabled= true
                autoStart= true
                autoConfirm= true
                }
                '''%(mp4_link,download)
            with open("%s%s.crawljob"%(self.crawl_path,self.titolo), 'a') as f:
                if(self.verbose):
                    print(self.crawl_path)
                f.write(crwd)
                f.close()
            self.list_link.clear()

    def downloader(self):
        download_link = list()
        #creo un file vuoto, se presente sovrascrivo
        self.check_Path(str(self.download_path)) #verifico che path esista
        print("Rilevati %d episodi"%len(self.list_link))
        episodes = []
        while True:
            try:
                wantedEps = input("Dammi Range Episodi (1:%d) "%len(self.list_link)).split(":")
                if("all" in (wantedEps[0].lower())):
                    start, finish = 1, len(self.list_link)
                elif(len(wantedEps) == 1):
                    start, finish = int(wantedEps[0]), int(wantedEps[0])
                else:
                    start, finish = int(wantedEps[0]), int(wantedEps[1])
                if(start > 0 and finish > 0 and finish <= len(self.list_link) and start <= len(self.list_link)):
                    break
                print("Invalido!")
            except ValueError:
                print("Invalido!")
        for episodedata in self.list_link:
            if(start <= episodedata[1] <= finish):
                sourcehtml = requests.get(episodedata[0]).text
                try:
                    mp4_link =  re.findall("file: \"(.*)\",",sourcehtml)
                except IndexError:
                    mp4_link = ""
                episodes.append(mp4_link)
        print("\n")
        for ep in sorted(episodes):
            download_link.append(ep[0])
        if(self.limit == -1):
            limite = len(download_link)
        else:
            limite = self.limit
        with concurrent.futures.ThreadPoolExecutor(max_workers=limite) as pool:
            pool.map(self.download, download_link)
        self.list_link.clear()
    #riordino correlati e  selezionato in base alla data di uscita


    def download(self,url):
        if(self.verbose):
            print(url)
        file_name = url.split("/")[-1]
        self.check_Path(os.path.join(self.download_path,file_name.split("_")[0]))
        with open(os.path.join(self.download_path,file_name.split("_")[0],file_name), "wb"):
            response = requests.get(url, stream=True)
            with tqdm.wrapattr(open(os.path.join(self.download_path,file_name.split("_")[0],file_name), "wb"), "write", desc=url.split('/')[-1], total=int(response.headers.get('content-length', 0))) as fout:
                for chunk in response.iter_content(chunk_size=4096):
                    fout.write(chunk)
