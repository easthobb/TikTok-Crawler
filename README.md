# TikTok-Crawler

This repository implements Tiktok's channel and challenge crawler(channel_crawler.py) and recommended feed crawler(feed_crawler.py). The composition of this repo includes code to insert and load data into the attached Postgre DB. It analyzes requests that web elements from inside TikTok without using API and sends queries to TikTok servers to crawl. In case of channel information when crawling, it is executed by inserting the id of the channel user as the input factor.

본 레포지토리에서는 틱톡의 채널정보/일간인기 해시태그 정보(channel_crawler.py), 추천 피드정보(feed_crawler.py)를 구현했다. 본 레포의 구성은 첨부된 Postgresql table에 데이터를 삽입하고 적재하는 코드까지 포함된다. API를 사용하지 않고 틱톡 내부에서 웹 요소를 끌어오는 요청을 분석해 쿼리를 틱톡 서버로 보내 크롤링한다. 크롤링시 채널 정보같은 경우 채널 user의 id를 입력 인자로 넣어주면 실행된다. 

You can see dev log here!
[https://www.notion.so/hobbeskim/TikTok-Crawler-cf374f0f14674f97b3edd278c953ec99]

## Have To Prepare
- Postgresql server
- selenum(only for feed_crawler.py) 

## Requirements 
- channel_crawler.py 
    - TikTok Account(a.k.a channel) following, follower
    - channel's video list
    - videos(upload at the channel) reactions
    - tiktok hot hashtag(a.k.a challenge)
    - all this requirements are stored in DB daily or once

- feed_crawler.py
    - daily recommended feed
    - feed posts reactions
 
 ## Schema and SQL queries
![schema](https://user-images.githubusercontent.com/57410044/108812814-1e40d480-75f3-11eb-8cdf-102613edd54d.png)
 ## Execution
    pip install -r requirements.txt

    ### set db_connection_info

    ### CLI

    python channel_crawler.py
    ### enter
    > channel_id

    python feed_crawler.py
![run channel](https://user-images.githubusercontent.com/57410044/108812718-fc475200-75f2-11eb-9ce7-e23d0c5fd2f5.png)
![run feed](https://user-images.githubusercontent.com/57410044/108812685-ea65af00-75f2-11eb-8577-c1e800e2f739.png)
![result channel](https://user-images.githubusercontent.com/57410044/108812899-416b8400-75f3-11eb-8ca2-40c620c9941c.png)
![result feed](https://user-images.githubusercontent.com/57410044/108812958-6233d980-75f3-11eb-842f-2bc03c4e6f63.png)

    
