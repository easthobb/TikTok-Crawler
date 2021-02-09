import requests
from bs4 import BeautifulSoup
import time
import datetime
import json
import urllib
import random
import sqlalchemy
from sqlalchemy import create_engine

DB_CONNECT_INFO = ""

class TikTokCrawler(object):

    def __init__(self,channel_id):
        pass

    def crawl_channel_info(self,channel_id):
        
        return channel_info # dict 

    def crawl_video_info(self,channel_id):
        
        return video_info_list # list of dict
    
    def crawl_hashtag_info(self):

        return hashtag_info # dict

    def upsert_db_channel_info(self,channel_info):
        pass
    
    def upsert_db_video_info(self,video_info_list):
        pass

    def upsert_db_hashtag_info(self,video_info_list):
        pass
    
    def start(self):
        pass

if __name__=="__main__":
    
    print("INPUT TIKTOK CHANNEL ID : ")
    channel_id = input()
    crawler = TikTokCrawler(channel_id)
    crawler.start()
    print("ALL DONE")
    
    
