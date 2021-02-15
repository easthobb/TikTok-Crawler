import requests
from bs4 import BeautifulSoup
import time
import datetime
import json
# import urllib
import random
# import sqlalchemy
# from sqlalchemy import create_engine

DB_CONNECT_INFO = ""


class TikTokCrawler(object):

    def __init__(self, user_id):

        self.db_connection_info = ""
        self.channel_id = ""  # 1232124541234 정수문자열형태
        self.secret_id = ""  # MAS21das123asd 해싱형태
        self.user_id = user_id
        self.base_url = {
            'app_name': 'tiktok_web',
            'device_platform': 'web',
            'referer': 'https:%2F%2Fwww.google.com%2F',
            'root_referer': 'https:%2F%2Fwww.google.com%2F',
            'user_agent': 'Mozilla%2F5.0+(Macintosh%3B+Intel+Mac+OS+X+10_15_5)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F88.0.4324.146+Safari%2F537.36',
            'cookie_enabled': 'true',
            'screen_width': '1920',
            'screen_height': '1080',
            'browser_language':'ko-KR',
            'browser_platform': 'MacIntel',
            'browser_name': 'Mozilla',
            'browser_version':'5.0+(Macintosh%3B+Intel+Mac+OS+X+10_15_5)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F88.0.4324.146+Safari%2F537.36',
            'browser_online': 'true',
            'ac': '4g',
            'timezone_name': 'Asia%2Fseoul',
            'page_referer': 'https:%2F%2Fwww.tiktok.com%2Fsearch%3Fq%3D%25EC%25A0%259C%25EB%25A6%25AC%26lang%3Dko-KR',
            'priority_region': '', # 없음
            'verifyFp': 'verify_kkqg77dw_hai6t3Ps_dkIT_41yF_ApMY_G7euFo5nq2xH',
            'appId': '1180',
            'region': 'KR',
            'appType': 't',
            'isAndroid': 'false',
            'isMobile': 'false',
            'isIOS': 'false',
            'OS': 'mac',
            'did': '6925283638187689473',
            'count': '30',
            'cursor': '', #UNIX 시간값 - hashtag 엔 미존재
            'language': 'ko-KR',
            'secUid': '' #secret_id 로 세팅 필요 - hashtag엔 미존재
        }


    def convert_user_id_to_secret_id(self, user_id):

        url = f"https://www.tiktok.com/@{user_id}"

        res = requests.get(url)
        secuid_start_index = res.text.find('secUid')
        secret_id = res.text[int(secuid_start_index):].split('"')[2]

        return secret_id

    def crawl_channel_info(self, secret_id):
        
        now = str(time.time()).split('.')[0]
        url = 'https://t.tiktok.com/api/post/item_list/?aid=1988'
        for key,value in self.base_url.items():
            if key == 'cursor':
                url = url + '&' + key + '=' + now + '000'
            elif key == 'secUid':
                url = url + '&' + key + '=' + secret_id
            else:
                url = url + '&' + key + '=' + value

        print(url)
        res = requests.get(url)
        res = json.loads(str(res.text))
        author_info = res['itemList'][0]['author']
        author_stat = res['itemList'][0]['authorStats']
        channel_info = {
            'channel_id':author_info['id'],
            'channel_user_id':author_info['uniqueId'],
            'channel_secret_id':secret_id,
            'channel_nickname':author_info['nickname'],
            'channel_registered_date':datetime.date.today(),
            'channel_crawl_date':datetime.date.today(),
            'following_count':author_stat['followingCount'],
            'follower_count':author_stat['followerCount'],
            'heart_count':author_stat['heartCount'],
            'video_count':author_stat['videoCount'],
            'digg_count':author_stat['diggCount']
        }

        return channel_info  # dict

    def crawl_video_info(self, secret_id):
        
        video_info_list = []

        #초기 커서 설정 (현재 시점)
        now = str(time.time()).split('.')[0]
        cursor = now + '000'

        while True:
            
            url = 'https://t.tiktok.com/api/post/item_list/?aid=1988'
            print('CURRENT CURSOR : ', cursor)
            for key,value in self.base_url.items():
                if key == 'cursor':
                    url = url + '&' + key + '=' + cursor
                elif key == 'secUid':
                    url = url + '&' + key + '=' + secret_id
                else:
                    url = url + '&' + key + '=' + value
            
            time.sleep(random.randrange(1, 3) +random.random())
            res = requests.get(url) # randomized requesting
            res = json.loads(str(res.text))
            
            for item in res['itemList']:
                hash_list = []
                try:# if video does not have hashtag
                    for hashtag in item['challenges']:
                        hash_list.append(hashtag['title'])
                except:
                    hash_list.append("None")


                video_info = {
                    'video_id' : item['id'],
                    'channel_id' : item['author']['id'],
                    'video_create_date' : datetime.datetime.fromtimestamp(item['createTime']).date(),
                    'video_crawl_date' : datetime.date.today(),
                    'video_description' : item['desc'],
                    'video_hashtag': ','.join(hash_list),
                    'digg_count':item['stats']['diggCount'],
                    'share_count':item['stats']['shareCount'],
                    'comment_count':item['stats']['commentCount'],
                    'play_count':item['stats']['playCount'],
                }
                #print(video_info)
                video_info_list.append(video_info)
            print(res['hasMore'])
            if res['hasMore'] == True:
                cursor = res['cursor']
                print('NEXT CURSOR :',cursor)
            elif res['hasMore'] == False:
                break
                
        return video_info_list

    def crawl_hashtag_info(self):
        
        hashtag_info_list = []

        url = 'https://t.tiktok.com/api/discover/challenge/?aid=1988'
        for key,value in self.base_url.items():
            if key == 'cursor' or key == 'secUid':#hashtag 를 가져오는 url에서 필요없는 key,value 배제
                pass
            else:
                url = url + '&' + key + '=' + value
        url = url + '&discoverType=0&needItemList=false&keyWord=&offset=0'#hashtag에 필요한 인자들 추가
        
        res = requests.get(url)
        res = json.loads(res.text)
        
        for challenge in res['challengeInfoList']:
            hashtag_info = {
                'tag_crawl_date' : datetime.date.today(),
                'tag_id': challenge['challenge']['id'],
                'tag_title': challenge['challenge']['title'],
                'tag_description': challenge['challenge']['desc'],
                'tag_video_count': challenge['stats']['videoCount'],
                'tag_view_count': challenge['stats']['viewCount'],
            }
            hashtag_info_list.append(hashtag_info)
        return hashtag_info_list

    def upsert_db_channel_info(self, channel_info):
        pass

    def upsert_db_video_info(self, video_info_list):
        pass

    def upsert_db_hashtag_info(self, hashtag_info_list):
        for hashtag in hashtag_info_list:
            try:
                query = '''
                insert into hashtag_info_daily(tag_crawl_date, tag_id, tag_title, tag_description,tag_video_count,tag_view_count)
                values (%(tag_crawl_date)s, %(tag_id)s, %(tag_title)s, %(tag_description)s,%(tag_video_count)s,%(tag_view_count)s)
                on conflict do nothing;
                '''
                params = {

                }
        

    def start(self):

        # secret_id = self.convert_user_id_to_secret_id(self.user_id)
        # self.secret_id = secret_id
        # # for testing
        # print("CHANNEL SECRET ID : ", secret_id)
        
        # channel_info = self.crawl_channel_info(self.secret_id)
        # #for testing
        # for k,v in channel_info.items():
        #     print(k,v)
        
        # #for testing
        # video_info_list = self.crawl_video_info(self.secret_id)
        # print(video_info_list)
        
        hashtag_info_list = self.crawl_hashtag_info()
        print(hashtag_info_list)
        # hashtag_info = self.crawl_hashtag_info()

        # self.upsert_db_channel_info(channel_info)
        # self.upsert_db_video_info(video_info_list)
        # self.upsert_db_hashtag_info(hashtag_info)


if __name__ == "__main__":

    print("INPUT TIKTOK CHANNEL ID : ")
    user_id = input()
    crawler = TikTokCrawler(user_id)
    crawler.start()
    print("ALL DONE")
