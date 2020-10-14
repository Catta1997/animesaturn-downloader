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
[![Travis](https://img.shields.io/travis/com/Catta1997/animesaturn-downloader/master?logo=travis)](https://travis-ci.com/thebespokepixel/badges "Travis")  

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
  crawl_path = 
  download_path = 
  movie_folder = 
  all = True
  only_ITA = False
  type = -1
  ```
  lasciare il valore vuoto per la path di default oppure inserire una nuova path Es: "C:\Users\utente\anime\"
