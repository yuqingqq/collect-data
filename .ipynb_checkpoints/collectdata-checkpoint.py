# import os
# import tweepy as tw
# import pandas as pd
#
# consumer_key= 'G5yZd45N9hkr1fvckndrxORvk'
# consumer_secret= 'X3euuvT4HoPKeFDlaK2wORNAyoEpANCetPVKeyDyhaosOqY3x0'
# access_token= '1379301855734296576-RdkH9mW6ZPTzpqrsGDrILH1XFZP4zA'
# access_token_secret= 'xOj3GVIFGNyxvLPCBAcIVVNMUhwG7lxe2OFHbMCMvhaUA'
#
# auth = tw.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token, access_token_secret)
# api = tw.API(auth, wait_on_rate_limit=True)
#
# # print(api.trends_place(1, []))
# #api.update_status("Look, I'm tweeting from #Python in my #earthanalytics class! ")
#
# search_words = "#stockmarket OR #stockprice"
# date_since = "2020-01-01"
# tweets = tw.Cursor(api.search,
#               q=search_words,
#               lang="en",
#               since=date_since).items()
# sum =0
# for tweet in tweets:
#     sum += 1
#     if tweet.retweeted:
#         print(f'author is {tweet.author.id} is retwt?{tweet.retweeted}\n ')
# print(f'extracted {sum } tweets')
# recent = api.user_timeline(include_rts =1 , user_id = 'yuqing')
# sum =0
# for tweet in recent:
#     # print(tweet.retweets)
#     sum +=1
#     if tweet.retweeted:
#         print(f'this twit id: {tweet.id}\n')
#     # print(tweet.text)
# print(f'tested {sum} tweets')
def my_criteria(data):
    crit = [10,10,2]
    if data>=crit:
        return True
    return False

def retrive_hashtags(content):
    return re.findall('#\w+', content)

def record_trend(data):
    sorted_trends = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
    trend_list = []
    for k in sorted_trends:
        print(f'tag: {k[0]} has {k[1]} more potential inf, start time:{hashtag_time[k[0]]}')
        #   if k[1]<=[0,0,0]: break
        trend_list.append([k[0], k[1][0], k[1][1], k[1][2], hashtag_time[k[0]]])
    trend_df = pd.DataFrame(trend_list, columns=['Trend', 'Retweet', 'Like', 'Reply', 'Start Time'])
    trend_df.to_csv('trend.csv', header=True)

def record_influencer(data):
    sortedinfluencers = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
    inf_df = pd.DataFrame.from_dict(sortedinfluencers,orient='index')
    inf_df.to_csv('influencer.csv',mode='a',header=False)

import snscrape.modules.twitter as sntwitter
import pandas as pd
from requests_oauthlib import OAuth1Session
import datetime
import re
import operator
import numpy as np
hashtag = '#Bitcoin OR #Ether OR #ether OR #bitcoin'
curdate = datetime.date.today()
startdate = curdate - datetime.timedelta(7)
#print(startdate)
query = hashtag + ' since:'+str(startdate)
print(f'query is {query}')
PastN = 100
# Using TwitterSearchScraper to scrape data and append tweets to list
totaltweets = sntwitter.TwitterSearchScraper(query)
hashtag_trends ={}
hashtag_time = {}
user_inf = {}

# last_N_tweets = sntwitter.TwitterSearchScraper('from:AsithosM').get_items()
# for N,tweet_user in enumerate(last_N_tweets):
#     print(f'user {tweet_user.user.username} content {tweet_user.content}')
record_round =1
for i,tweet in enumerate(totaltweets.get_items()):
    if tweet == None: continue
    if tweet.user.username in user_inf.keys():continue
    if len(hashtag_trends)>= record_round*500:
        record_trend(hashtag_trends)
        record_round += 1
    inf = [tweet.retweetCount, tweet.likeCount, tweet.replyCount]
    if inf ==[]: continue
    if len(user_inf.keys())>=record_round*100:
        record_influencer(user_inf)
    if my_criteria(inf):
        thisuser = tweet.user.username
        tag_Ipropagate ={}
        last_N_tweets = sntwitter.TwitterSearchScraper('from:'+thisuser).get_items()
        infthisuer = []
        for N,tweet_user in enumerate(last_N_tweets):
            if N>PastN:break
            got_hashtags = retrive_hashtags(content=tweet_user.content)
            # avg[0] += tweet_user.retweetCount/PastN
            # avg[1] += tweet_user.likeCount/PastN
            # avg[2] += tweet_user.replyCount/PastN
            infthisuer.append([tweet_user.retweetCount,tweet_user.likeCount,tweet_user.replyCount])
            for h in got_hashtags:
                h = h.lower()
                if h in tag_Ipropagate.keys():
                    tag_Ipropagate[h] = max(tag_Ipropagate[h], [tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                else:
                    tag_Ipropagate[h] = [tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount]
                if h in hashtag_time.keys():
                    hashtag_time[h] = min(hashtag_time[h],tweet_user.date)
                else:
                    hashtag_time[h] = tweet_user.date
        if len(infthisuer)==0: continue
        infthisuer = np.array(infthisuer, dtype=np.float32)
        avg = infthisuer.mean(0)
        for h in tag_Ipropagate.keys():
            tag_Ipropagate[h] = np.array(tag_Ipropagate[h],dtype=np.float32)
            if h in hashtag_trends.keys():
                hashtag_trends[h] += [avg[i] - tag_Ipropagate[h][i] for i in range(3)]
            else:
                hashtag_trends[h] = [avg[i] - tag_Ipropagate[h][i] for i in range(3)]
        user_inf[thisuser] = avg
        print(f'user {thisuser} avg inf : {avg}')

#test
# hashtag_trends = {'#a':0.8, '#b':19, '#c':-5}
# hashtag_time ={'#a':datetime.date.today(), '#b':datetime.date.today(),'#c':datetime.date.today()}



# Creating a dataframe from the tweets list above
# tweets_df2 = pd.DataFrame(tweets_list2, columns=['Datetime', 'Tweet Id', 'Username'])