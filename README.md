| :warning: WARNING          |
|:---------------------------|
| BETA BRENCH    |

# animesaturn-downloader
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/Catta1997/animesaturn-downloader)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/requests/beta?color=yellow) 
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/beautifulsoup4/beta?color=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/psutil/beta?color=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/tqdm/beta?color=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/wget/beta?color=yellow)
![GitHub Pipenv locked dependency version](https://img.shields.io/github/pipenv/locked/dependency-version/Catta1997/animesaturn-downloader/configparser/beta?color=yellow)

[![CodeFactor](https://www.codefactor.io/repository/github/catta1997/animesaturn-downloader/badge/beta)](https://www.codefactor.io/repository/github/catta1997/animesaturn-downloader/overview/beta)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/be1ac1ec55dc48678fbcaf15f8e69e3a)](https://app.codacy.com/gh/Catta1997/animesaturn-downloader?utm_source=github.com&utm_medium=referral&utm_content=Catta1997/animesaturn-downloader&utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/Catta1997/animesaturn-downloader.svg?branch=beta)](https://travis-ci.org/Catta1997/animesaturn-downloader)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)   
### Installazione
  - Installate i requisiti contenuti in "requirment.txt"
### Installazione con virtualenv
- Creare virtualenv `python3 -m virtualenv venv`
- Entrate in virtualenv con `source venv/bin/activate`
- Aggiornate pip `pip install -U pip`
- Installate le. dipendenze `pip install -r requirements.txt`
### Config
  - editare il file config.ini
  ```
  [DEFAULT]
  crawl_path = 
  download_path = 
  movie_folder = 
  all = True
  only_ITA = False
  ```
  lasciare il valore vuoto per la path di default oppure inserire una nuova path Es: "C:\Users\utente\anime\"
