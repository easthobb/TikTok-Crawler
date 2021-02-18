import requests
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
import time, random
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://t.tiktok.com/api/recommend/item_list/?aid=1988&app_name=tiktok_web&device_platform=web&referer=&root_referer=&user_agent=Mozilla%2F5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F88.0.4324.150+Safari%2F537.36&cookie_enabled=true&screen_width=2560&screen_height=1440&browser_language=ko-KR&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F88.0.4324.150+Safari%2F537.36&browser_online=true&ac=4g&timezone_name=Asia%2FSeoul&priority_region=&verifyFp=verify_kl8znk7j_UCx7rIre_7LBx_4qud_BioE_XdjXw1dexl2R&appId=1180&region=KR&appType=t&isAndroid=false&isMobile=false&isIOS=false&OS=windows&did=6923212441551719681&count=30&itemID=1'
res = requests.get(url)

driver = webdriver.Chrome(ChromeDriverManager().install())
caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
driver.get('https://www.tiktok.com/')

ret_list = []
def parse_tik(page_source:str):
    res_list = []
    html = BeautifulSoup(page_source, 'html.parser')
    for x in html.select('span.lazyload-wrapper'):
        content = x.select('div.feed-item-content')
        if not content:
            continue
        content = content[0]
        video_id = content.select('a.item-video-card-wrapper')[0]['href']
        unique_id = content.select('h3.author-uniqueId')[0].text
        nickname = content.select('h4.author-nickname')[0].text
        caption = content.select('div.tt-video-meta-caption')
        hashtags=[]
        if not caption:
            caption_text = ""
        else:
            caption = caption[0]
            if not caption.select('a'):
                pass
            else:
                hashtags = [a.text for a in caption.select('a')]
            caption_text = caption.text
        music = content.select('div.tt-video-music')[0].text
        rect_params = {k['title']: k.text for k in content.select('div.pc-action-bar strong')}
        info_params = {
            'uid': unique_id,
            'nickname': nickname,
            'video_id': video_id,
            'caption': caption_text,
            'hashtags': hashtags,
            'music': music
        }
        info_params.update(rect_params)
        res_list.append(info_params)
    return res_list

is_next = True

while is_next:
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    except:
        is_next = False
    time.sleep(random.uniform(3, 5))
    res = parse_tik(driver.page_source)
    if len(res) > 100:
        is_next = False

ret_list = []
for x in res:
    tag = ",".join(x['hashtags'])
    x.update({'tags': tag})
    ret_list.append(x)


for x in ret_list:
    del x['hashtags']

df = pd.DataFrame.from_records(ret_list)

df.to_excel('tiktok_main.xlsx', index=False)
# len(list(set(recomend_urls)))

# from bs4 import BeautifulSoup
# html = BeautifulSoup(driver.page_source, 'html.parser')

# ret_list = []
# for x in html.select('span.lazyload-wrapper'):
#     content = x.select('div.feed-item-content')
#     if not content:
#         continue
#     content = content[0]
#     unique_id = content.select('h3.author-uniqueId')[0].text
#     nickname = content.select('h4.author-nickname')[0].text
#     caption = content.select('div.tt-video-meta-caption')
#     hashtags = []
#     if not caption:
#         caption_text = ""
#     else:
#         caption = caption[0]
#         if not caption.select('a'):
#             pass
#         else:
#             hashtags = [a.text for a in caption.select('a')]
#         caption_text = caption.text
#     music = content.select('div.tt-video-music')[0].text
#     rect_params = {k['title']: k.text for k in content.select('div.pc-action-bar strong')}
#     info_params = {
#         'uid': unique_id,
#         'nickname': nickname,
#         'caption': caption_text,
#         'hashtags': hashtags,
#         'music': music
#     }
#     info_params.update(rect_params)
#     ret_list.append(info_params)

# len(ret_list)