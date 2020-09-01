# importing the requests library 
import requests,os,subprocess
import sys
import signal
from bs4 import BeautifulSoup
import re

all = False #anime correlati
list_link = list()
titolo = ""
def create_crawl():
    global list_link
    global titolo
    crwd = ""
    for link in list_link:
        crwd = crwd + '''
        {
        text= %s
        downloadFolder= /share/Plex/ANIME/School_Days/Season_1
        enabled= true
        autoStart= true
        autoConfirm= true
        }
        '''%link
    with open("%s.crawljob"%titolo, 'w') as f:
        f.write(crwd)
        f.close()
def sig_handler(_signo, _stack_frame):
    print("\n")
    sys.exit(0)
def get_correlati(URL):
    #analizzo url e cerco la sezione "correlati" e richiamo la funzione per trovare gli episodi per gonuno di essi
    new_r = requests.get(url = URL, params = {})
    pastebin_url = new_r.text 
    parsed_html = BeautifulSoup(pastebin_url,"html.parser")
    correlati = parsed_html.find_all('div', attrs={'class':'owl-item anime-card-newanime main-anime-card'})
    for dim in correlati:
        anime = dim.find('a')['href']
        print("-------")
        selected_anime(anime)
    print()
def selected_anime(URL):
    #visito la pagina, trovo il tasto per l'episodio. Sucessivamente analizzo quella  pagina e ottengo il link di streaming
    new_r = requests.get(url = URL, params = {})
    pastebin_url = new_r.text 
    parsed_html = BeautifulSoup(pastebin_url,"html.parser")
    anime_ep = parsed_html.find_all('div', attrs={'class':'btn-group episodes-button episodi-link-button'})
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
    global titolo
    titoli_anime = list()
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    anime_list  = list()
    name = input("nome:")
    URL = "https://www.animesaturn.com/animelist?search="+name
    r = requests.get(url = URL, params = {})
    pastebin_url = r.text 
    html = pastebin_url
    parsed_html = BeautifulSoup(html,"html.parser")
    animes = parsed_html.find_all('ul', attrs={'class':'list-group'})
    x = 1
    for dim in animes:
        print(x)
        print()
        title = dim.find('a',attrs={'class':'badge badge-archivio badge-light'})
        trama = dim.find('p',attrs={'class':'trama-anime-archivio text-white rounded'})
        link = dim.find('a')['href']
        print(title.text)
        titoli_anime.append((title.text).replace(" ","_"))
        print()
        print(trama.text)
        anime_list.append(link)
        print("--------")
        x+=1
    selected = int(input("ID:"))
    selected -=1 #la lista parte da 0
    URL = anime_list[selected]
    titolo = titoli_anime[selected]
    if(all):
        print("Correlati:")
        get_correlati(URL)
    else:
        selected_anime(URL)

if __name__ == "__main__":
    main()