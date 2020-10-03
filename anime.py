# importing the requests library 
import requests,os,subprocess
import sys
import signal
from bs4 import BeautifulSoup
import re
from datetime import datetime
import locale

#config
download_path = "/share/Plex/ANIME/"
crawl_path = "CrawlDefaultDir/" 
leng = True
all = True #anime correlati
#

list_link = list()
correlati_list = list()
anime = {}
titolo = ""
season = 0
season_num = 0

def checkCrawl_Path(crawl_path):
    if(not os.path.isdir(crawl_path)):
        os.makedirs(crawl_path)

def create_crawl():
    crwd = ""
    checkCrawl_Path(crawl_path) #verifico che path esista
    for link in list_link:
        sourcehtml = requests.get(link).text
        source = re.findall("file: \"(.*)\",",sourcehtml)
        crwd = crwd + '''
        {
        text= %s
        downloadFolder= %s%s/Season_%d
        enabled= true
        autoStart= true
        autoConfirm= true
        }
        '''%(source[0],download_path,titolo,season_num)
    with open("%s%s.crawljob"%(crawl_path,titolo), 'a') as f:
        f.write(crwd)
        f.close()
def reorder_correlati():
    global titolo
    for URL in correlati_list:
        new_r = requests.get(url = URL, params = {})
        pastebin_url = new_r.text 
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        anno = parsed_html.find('div', attrs={'class':'container shadow rounded bg-dark-as-box mb-3 p-3 w-100 text-white'})
        release = re.findall("(?<=<b>Data di uscita:</b> )(.*)(?=<br/>)",str(anno))
        anime[release[0]] = URL
        #release = anno.find('b','Data di uscita:')
        #print(release)
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    ordered_data = sorted(anime.items(), key = lambda x:datetime.strptime(x[0], "%d %B %Y"), reverse=False)
    titolo = re.findall("(?<=anime/)(.*)", ordered_data[0][1])[0]
    for x in ordered_data:
        #print(x[1])
        #print(".-.-")
        selected_anime(x[1])

def sig_handler(_signo, _stack_frame):
    print("\n")
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
        #print("Season %d -> Titolo %s"%(season,anime))
        #selected_anime(anime)
        if(leng and is_lang):
            if("-ITA" in anime):
                correlati_list.append(anime)
        else: correlati_list.append(anime)
    reorder_correlati()
def selected_anime(URL):
    global season
    global season_num
    #visito la pagina, trovo il tasto per l'episodio. Sucessivamente analizzo quella  pagina e ottengo il link di streaming
    new_r = requests.get(url = URL, params = {})
    pastebin_url = new_r.text 
    parsed_html = BeautifulSoup(pastebin_url,"html.parser")
    all_info = parsed_html.find('div', attrs={'class':'container shadow rounded bg-dark-as-box mb-3 p-3 w-100 text-white'})
    info = re.findall("(?<=<b>Episodi:</b> )(.*)(?=<br/>)",str(all_info))
    anime_type = anime_page = parsed_html.find('span', attrs={'class':'badge badge-secondary'})
    if ('OVA' in anime_type.text or "Special" in info[0] or "Movie" in info[0]): 
        season_num = 0
    else: 
        season +=1
        season_num = season
    if season_num == 0: print("OVA")
    else : print("Stagione %d"%season_num)
    anime_ep = parsed_html.find_all('div', attrs={'class':'btn-group episodes-button episodi-link-button'})
    list_link.clear()
    for dim in anime_ep:
        episode = dim.find('a')['href']
        title = dim.find('a',attrs={})
        new_r = requests.get(url = episode, params = {})
        pastebin_url = new_r.text
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        anime_page = parsed_html.find('div', attrs={'class':'card bg-dark-as-box-shadow text-white'})
        is_link = anime_page.find('a')['href']
        if 'watch' in is_link: episode = is_link+'&s=alt'
        new_r = requests.get(url = episode, params = {})
        pastebin_url = new_r.text
        parsed_html = BeautifulSoup(pastebin_url,"html.parser")
        splotted_title = re.findall('(\w+ \d+)',title.text)
        list_link.append(episode)
    create_crawl()
def main():
    global season
    #titoli_anime = list()
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    anime_list  = list()
    name = input("nome:")
    URL = "https://www.animesaturn.it/animelist"
    r = requests.get(url = URL, params = {"search":name})
    pastebin_url = r.text 
    html = pastebin_url
    parsed_html = BeautifulSoup(html,"html.parser")
    animes = parsed_html.find_all('ul', attrs={'class':'list-group'})

    x = 1
    for dim in animes:
        print(x)
        print("TITOLO:")
        title = dim.find('a',attrs={'class':'badge badge-archivio badge-light'})
        trama = dim.find('p',attrs={'class':'trama-anime-archivio text-white rounded'})
        link = dim.find('a')['href']
        print("\x1b[32m" + title.text + "\x1b[0m")
        #titoli_anime.append((title.text).replace(" ","_"))
        print("TRAMA:")
        print("\x1b[37m" + trama.text +"\x1b[0m")
        anime_list.append(link)
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
    selected -=1 #la lista parte da 0
    URL = anime_list[selected]
    #titolo = titoli_anime[selected]
    if(all):
        #print("Correlati:")
        get_correlati(URL)
    else:
        season = 1
        selected_anime(URL)

if __name__ == "__main__":
    main()
