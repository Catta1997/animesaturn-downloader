import os
import configparser

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
config = configparser.ConfigParser()
config.read('config.ini')
debug = False
test_ID = False
titolo = ""

only_link = list()
list_link = list()
correlati_list = list()
anime = {}
all_ep = {}
season = 0
season_num = 0
file_type = -1 # 0 = normal, 1 = standalone
def init():
    global file_type
    global only_link
    global list_link
    global correlati_list
    global anime
    global all_ep
    global season
    global season_num
    global titolo
    global dir_path
    global config
    global debug
    global test_ID