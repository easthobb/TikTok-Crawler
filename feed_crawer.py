import requests
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import sqlalchemy
from sqlalchemy import create_engine


class TikTokFeedCrawler(object):

    def __init__(self):
        
        self.tiktok_url = 'https://www.tiktok.com/'
        self.feed_url = 'https://t.tiktok.com/api/recommend/item_list/?aid=1988&app_name=tiktok_web&device_platform=web&referer=&root_referer=&user_agent=Mozilla%2F5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F88.0.4324.150+Safari%2F537.36&cookie_enabled=true&screen_width=2560&screen_height=1440&browser_language=ko-KR&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F88.0.4324.150+Safari%2F537.36&browser_online=true&ac=4g&timezone_name=Asia%2FSeoul&priority_region=&verifyFp=verify_kl8znk7j_UCx7rIre_7LBx_4qud_BioE_XdjXw1dexl2R&appId=1180&region=KR&appType=t&isAndroid=false&isMobile=false&isIOS=false&OS=windows&did=6923212441551719681&count=30&itemID=1'
        self.max_feed_count = 100

    def parse_tik(self, page_source: str):

        res_list = []
        html = BeautifulSoup(page_source, 'html.parser')

        for x in html.select('span.lazyload-wrapper'):
            content = x.select('div.feed-item-content')
            if not content:
                continue
            content = content[0]
            video_id = str(content.select(
                'a.item-video-card-wrapper')[0]['href']).split('/')[-1]
            channel_user_id = content.select('h3.author-uniqueId')[0].text
            channel_nickname = content.select('h4.author-nickname')[0].text
            caption = content.select('div.tt-video-meta-caption')
            video_url = content.select('a.item-video-card-wrapper')[0]['href']
            hashtags = []
            if not caption:
                caption_text = ""
            else:
                caption = caption[0]
                if not caption.select('a'):
                    pass
                else:
                    hashtags = [a.text for a in caption.select('a')]
                caption_text = caption.text

            video_hashtag = ','.join(hashtags)  # 해시태그 결합 구분자 ,
            music = content.select('div.tt-video-music')[0].text
            reaction_params = {k['title']: k.text for k in content.select(
                'div.pc-action-bar strong')}
            print('rect:', reaction_params)
            units = {"K": 1000, "M": 1000000, "B": 1000000000}  # 정수형 변환 및 칼럼이름 변경
            coverted_reaction = {}
            for key, value in reaction_params.items():
                print(key, value)
                try:
                    coverted_reaction[key] = int(value)
                except ValueError:
                    unit = value[-1]
                    new_value = float(value[:-1])
                    coverted_reaction[key] = int(new_value*units[unit])

            info_params = {
                'feed_crawl_date': datetime.date.today().isoformat(),
                'video_id': video_id,
                'channel_user_id': channel_user_id,
                'channel_nickname': channel_nickname,
                'video_description': caption_text,
                'video_hashtag': video_hashtag,
                'video_music': music,
                'video_url': video_url,
                'digg_count': coverted_reaction['like'],
                'share_count': coverted_reaction['share'],
                'comment_count': coverted_reaction['comment']
            }
            res_list.append(info_params)

        return res_list

    def crawl_feed_info(self):

        url = self.feed_url
        res = requests.get(url)
        driver = webdriver.Chrome(ChromeDriverManager().install())
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        driver.get(self.tiktok_url)

        is_next = True
        while is_next:
            try:
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
            except:
                is_next = False
            time.sleep(random.uniform(3, 5))
            res = self.parse_tik(driver.page_source)
            if len(res) > self.max_feed_count:
                is_next = False

        feed_info = pd.DataFrame.from_records(res)
        return feed_info

    def insert_db_feed_info(self,feed_info:pd.DataFrame):

        engine = create_engine(self.db_connection_info)

        feed_info.to_sql(name='feed_info_daily',
                        con=engine,
                        schema='public',
                        if_exists='append',
                        index=False,
                        dtype={
                            'feed_crawl_date': sqlalchemy.Date,
                            'video_id': sqlalchemy.types.VARCHAR(50),
                            'channel_user_id': sqlalchemy.types.VARCHAR(50),
                            'channel_nickname': sqlalchemy.types.VARCHAR(50),
                            'video_description': sqlalchemy.types.Text,
                            'video_hashtag': sqlalchemy.types.Text,
                            'video_music': sqlalchemy.types.VARCHAR(300),
                            'video_url': sqlalchemy.types.Text,
                            'digg_count': sqlalchemy.types.INTEGER(),
                            'share_count': sqlalchemy.types.INTEGER(),
                            'comment_count': sqlalchemy.types.INTEGER()
                        })
        engine.dispose()
    
    def start(self):
        try:
            feed_info = self.crawl_feed_info()
            self.insert_db_feed_info(feed_info)
        except Exception as e :
            print(e)
            print("CAN NOT CRAWL FEED INFO")

        print('done')

if __name__ == '__main__':

    crawler = TikTokFeedCrawler()
    crawler.start()
    print('done')
