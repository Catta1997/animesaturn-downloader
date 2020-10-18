# animesaturn-downloader
![GitHub Pipenv locked Python version (branch)](https://img.shields.io/github/pipenv/locked/python-version/Catta1997/animesaturn-downloader/master?logo=python&logoColor=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/requests/master?color=yellow) 
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/beautifulsoup4/master?color=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/psutil/master?color=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/tqdm/master?color=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/wget/master?color=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/configparser/master?color=yellow)

![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/Catta1997/animesaturn-downloader/master?logo=codefactor) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/be1ac1ec55dc48678fbcaf15f8e69e3a)](https://app.codacy.com/gh/Catta1997/animesaturn-downloader?utm_source=github.com&utm_medium=referral&utm_content=Catta1997/animesaturn-downloader&utm_campaign=Badge_Grade) 
![Travis (.com) branch](https://img.shields.io/travis/com/Catta1997/animesaturn-downloader/master?logo=travis)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)   

### Installazione
  - Installate i requisiti contenuti in "requirment.txt"
### Installazione con virtualenv
- Creare virtualenv con `python3 -m virtualenv venv`
- Entrare in virtualenv con `source venv/bin/activate`
- Aggiornare pip con `pip install -U pip`
- Installare le dipendenze con `pip install -r requirements.txt`
- Avviare  il programma con `python start.py`
### Config
  - editare il file config.ini
  ```
[DEFAULT]
# watchdir .crawljob
crawl_path =
# path di salvataggio standalone e dei file scaricati con JDownloader
download_path =
# path in cui vengono salvati i film (solo se scaricato con JDownloader)
movie_path =
# scarica tutte le stagioni di un anime
all = True
# negli anime doppiati (es SAO) scarica solo gli episodi in italiano
only_ITA = False
# 0 = crawljob, 1 = standalone, -1  = chiedi
type = -1
# limite di episodi scaricabili contemporaneamente, Defaule -1 (scarica tutti)
limit = 1
  ```
  lasciare il valore vuoto per la path di default oppure inserire una nuova path Es: "C:\Users\utente\anime\"
