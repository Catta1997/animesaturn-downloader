# importing the requests library
import requests
import os
import signal
import re
import time
import concurrent.futures
from tqdm import tqdm
from animesaturn import Animesaturn
def check_Path(crawl_path):
    print(crawl_path)
    if(not os.path.isdir(crawl_path)):
        os.makedirs(crawl_path)


