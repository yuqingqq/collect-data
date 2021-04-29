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

from typing import List,Dict
import snscrape.modules.twitter as sntwitter
import pandas as pd
from requests_oauthlib import OAuth1Session
import datetime
import re
import operator
import numpy as np

class TrendInfo:

    def __init__(self, curdate, timedif:int, hashtag:str = '#Bitcoin OR #Ether OR #ether OR #bitcoin'):
        self._endday = curdate - datetime.timedelta(1)
        self._startday = self._endday - datetime.timedelta(timedif)
        self._hashtag = hashtag
        self._PastN = 100
        self._hashtag_trends ={}
        self._user_inf_inthepast={}
        self._user_inf ={}
        self._hashtag_time ={}
        self._hashtag_trends_now ={}
        self._hashtag_trend_pre={}
        self._propagte_group ={}
        self._tweetsinfo = []
        self._tweetsuserinfo = []
        self._testtweets = 0
        self._inftweets = 0

    def my_criteria(self,data)->bool:
        crit = [10,10,2]
        if data>=crit:
            return True
        return False

    def retrive_hashtags(self,content:str)->List[str]:
        return re.findall('#\w+', content)

    def record_trend(self):
        data = self._hashtag_trends
        hashtag_time = self._hashtag_time
        sorted_trends = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
        trend_List = []
        for k in sorted_trends:
            #print(f'tag: {k[0]} has {k[1]} more potential inf, start time:{hashtag_time[k[0]]}')
            #   if k[1]<=[0,0,0]: break
            trend_List.append([k[0], k[1][0], k[1][1], k[1][2], hashtag_time[k[0]]])
        trend_df = pd.DataFrame(trend_List, columns=['Trend', 'Retweet', 'Like', 'Reply', 'Start Time'])
        trend_df.to_csv('trend.csv', header=True)

    def record_influencer(self,data:Dict[str,List[int]]):
        sortedinfluencers = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
        influencer_List =[]
        for k in sortedinfluencers:
            influencer_List.append([k[0],k[1][0],k[1][1],k[1][2]])
        inf_df = pd.DataFrame(influencer_List,columns=['username','retweet','Like','Reply'])
        inf_df.to_csv('influencer.csv',header=True)

    def measure_estimator(self):
        estimator_div =[0]*11
        user_pastinf = self._user_inf_inthepast
        usernowinf = self._user_inf
        for k,v in user_pastinf.items():
            if k not in usernowinf.keys():
                continue
            sumpast = sum(v)
            sumnow = sum(usernowinf[k])
            if sumnow ==0 or sumpast ==0:
                print(f'user {k} has avg inf {usernowinf[k]} past inf {v}')
                continue
           # print(f'inf now is {sumnow} inf past is {sumpast}')
            div = abs(sumpast-sumnow)/sumnow
            idx = int(div//0.1)
            idx = min(10,idx)
            estimator_div[idx] += 1
        suminfer = sum(estimator_div)
        estimator_div = [1.0*x/suminfer for x in estimator_div]
        print(f'estimator div distribution {estimator_div}')
        inf_df = pd.DataFrame(estimator_div)
        inf_df.to_csv('estimator_div.csv')

    def record_tweets(self,his:bool):
        tweets_df = pd.DataFrame(self._tweetsinfo)
        headers = ['id','url','user','date','content','retweet','like','reply','place',
                                                    'coordinates','lang','media','source','quotecount','quotedtweet']
        if his == True:
            name = 'tweetsinfo_his.csv'
        else:
            name = 'tweetsinfo.csv'
        tweets_df.to_csv(name,header=headers)

    def record_user_tweets(self,his:bool):
        tweets_df = pd.DataFrame(self._tweetsuserinfo)
        headers = ['id','url','user','date','content','retweet','like','reply','place',
                                                    'coordinates','lang','media','source','quotecount','quotedtweet']
        if his == True:
            name = 'tweetsuserinfo_his.csv'
        else:
            name = 'tweetsuserinfo.csv'
        tweets_df.to_csv(name,header=headers)
    
    def measure_estimetion(self, currentinf:Dict[str,List[int]]):
        div={}
        error_List = [0] * 11
        mean_reversion =0
        total_reversion =0
        trend_follow =0
        total_follow =0
        follow_trend = []
        reversion_trend =[]
        sametrend = 0
        hash_inf_reversion = []
        hash_inf_follow =[]
        for h in self._hashtag_trend_pre.keys():
            preDict_inf = sum(self._hashtag_trend_pre[h])
            previous_inf = sum(self._hashtag_trends_now[h])
            num_infer = self._propagte_group[h]
            if previous_inf < preDict_inf and num_infer >= 5:
                total_reversion += 1
                if h in currentinf.keys():
                    sametrend += 1
                    curinf = sum(currentinf[h])
                    hash_inf_reversion.append([h,preDict_inf,previous_inf,curinf])
                    if curinf == 0:
                        continue
                    if curinf > previous_inf*0.1:
                        mean_reversion +=1
                        reversion_trend.append(h)
                        div[h] = abs(preDict_inf-curinf)/curinf
                        idx = int(div[h]// 0.1)
                        idx = min(idx, 10)
                        error_List[idx] += 1
                        #hash_inf_reversion.append([h,preDict_inf,previous_inf,curinf])
            if previous_inf>preDict_inf and num_infer >=5:
                total_follow += 1
                if h in currentinf.keys():
                    sametrend += 1
                    curinf = sum(currentinf[h])
                    hash_inf_follow.append([h,preDict_inf,previous_inf,curinf])
                    if curinf == 0:
                        continue
                    if curinf>preDict_inf:
                        trend_follow +=1
                        follow_trend.append(h)
                        div[h] = abs(preDict_inf-curinf)/curinf
                        idx = int(div[h]// 0.1)
                        idx = min(idx, 10)
                        error_List[idx] += 1
                        #hash_inf_follow.append([h,preDict_inf,previous_inf,curinf])
        sumtags = sum(error_List)
        if sumtags==0: return
        error_List = [1.0*error_List[i]/sumtags for i in range(11)]
        error_List = []
        if total_reversion>0:
            error_List.append(mean_reversion)
            error_List.append(total_reversion)
            print(f'mean reversion ratio is {mean_reversion/total_reversion}')
        if total_follow>0:
            print(f'trend following ratio is {trend_follow/total_follow}')
            error_List.append(trend_follow)
            error_List.append(total_follow)
        error_List.append(sametrend)
        print(f'error trend distribution is {error_List}')
        error_df = pd.DataFrame(error_List)
        error_df.to_csv('error_distribution.csv')
        follow_trend_df = pd.DataFrame(follow_trend)
        follow_trend_df.to_csv('follow_trend.csv')
        hash_inf_reversion_df = pd.DataFrame(hash_inf_reversion)
        hash_inf_reversion_df.to_csv('hash_inf_reversion.csv')
        hash_inf_follow_df = pd.DataFrame(hash_inf_follow)
        hash_inf_follow_df.to_csv('hash_inf_follow.csv')
        reversion_trend_df = pd.DataFrame(reversion_trend)
        reversion_trend_df.to_csv('reversion_trend.csv')
        #return sametrend

    def get_current_trends(self)->Dict[str,List[int]]:
        return self._hashtag_trends_now

    def retrieve_trends(self):
        query = self._hashtag + ' since:' + str(self._startday)+' until:'+str(self._endday)
        print(f'query is {query}')
        totaltweets = sntwitter.TwitterSearchScraper(query)
        record_round = 1
        for i, tweet in enumerate(totaltweets.get_items()):
            self._testtweets += 1
            if tweet == None: continue
            self._tweetsinfo.append([tweet.id, tweet.url,tweet.user,tweet.date,tweet.content,tweet.retweetCount,tweet.likeCount,tweet.replyCount,tweet.place,tweet.coordinates,tweet.lang,tweet.media,tweet.source,tweet.quoteCount,tweet.quotedTweet])
            if tweet.user.username in self._user_inf.keys(): continue
            if len(self._hashtag_trends) >= record_round * 50:
               break
            inf = [tweet.retweetCount, tweet.likeCount, tweet.replyCount]
            if inf == []: continue
            if self.my_criteria(inf):
                self._inftweets += 1
                thisuser = tweet.user.username
                tag_Ipropagate = {}
                last_N_tweets = sntwitter.TwitterSearchScraper('from:' + thisuser +' until:'+str(self._endday)).get_items()
                infthisuer = []
                infthisuer_inthepast = []
                for N, tweet_user in enumerate(last_N_tweets):
                    self._testtweets += 1
                    if tweet_user == None: continue
                    self._tweetsuserinfo.append([tweet_user.id, tweet_user.url,tweet_user.user,tweet_user.date,tweet_user.content,tweet_user.retweetCount,tweet_user.likeCount,tweet_user.replyCount,tweet_user.place,tweet_user.coordinates,tweet_user.lang,tweet_user.media,tweet_user.source,tweet_user.quoteCount,tweet_user.quotedTweet])
                    if N > self._PastN * 2:
                        break
                    got_hashtags = self.retrive_hashtags(content=tweet_user.content)
                    if N <= self._PastN:
                        infthisuer.append([tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                    else:
                        infthisuer_inthepast.append([tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                   # print(f'date is type of {type(tweet_user.date)}')
                    if tweet_user.date.date()<self._startday:
                        continue
                    for h in got_hashtags:
                        h = h.lower()
                        if N <= self._PastN:
                            if h in tag_Ipropagate.keys():
                                tag_Ipropagate[h] = max(tag_Ipropagate[h], [tweet_user.retweetCount, tweet_user.likeCount,
                                                                            tweet_user.replyCount])
                            else:
                                tag_Ipropagate[h] = [tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount]
                            if h in self._hashtag_time.keys():
                                self._hashtag_time[h] = min(self._hashtag_time[h], tweet_user.date)
                            else:
                                self._hashtag_time[h] = tweet_user.date
                if len(infthisuer) > 0:
                    infthisuer = np.array(infthisuer, dtype=np.float32)
                    avg = infthisuer.mean(0)
                    for h in tag_Ipropagate.keys():
                        if h in self._hashtag_trends.keys():
                            self._hashtag_trends[h] += [avg[i] - tag_Ipropagate[h][i] for i in range(3)]
                            self._hashtag_trends_now[h] += tag_Ipropagate[h]
                            self._hashtag_trend_pre[h] += avg
                            self._propagte_group[h] += 1
                        else:
                            self._hashtag_trends[h] = [avg[i] - tag_Ipropagate[h][i] for i in range(3)]
                            self._hashtag_trends_now[h] = tag_Ipropagate[h]
                            self._hashtag_trend_pre[h] = avg
                            self._propagte_group[h] = 1
                    self._user_inf[thisuser] = [avg[0], avg[1], avg[2]]
                #    print(f'user {thisuser} avg inf : {avg}')
                if len(infthisuer_inthepast) > 0:
                    infthisuer_inthepast = np.array(infthisuer_inthepast, dtype=np.float32)
                    avg = infthisuer_inthepast.mean(0)
                    self._user_inf_inthepast[thisuser] = [avg[0], avg[1], avg[2]]
                 #   print(f'user {thisuser} past avg inf : {avg}')
        #return [hashtag_trend_pre,hashtag_trends_now,propagte_group,hashtag_trends,hashtag_time,user_inf_inthepast,user_inf,inftweets,testtweets]

    # def verify_pre(preDictions,users,curdate):
    #     startdate = curdate-datetime.timedelta(7)
    #     propagation_res ={}
    #     for thisuser in users:
    #         query = 'from:' + thisuser +' since:'+str(startdate)+' until:'+str(curdate)
    #         last_N_tweets = sntwitter.TwitterSearchScraper(query).get_items()
    #         tag_propagate ={}
    #         for N, tweet_user in enumerate(last_N_tweets):
    #             if tweet_user == None: continue
    #             got_hashtags = self.retrive_hashtags(content=tweet_user.content)
    #             for h in got_hashtags:
    #                 h = h.lower()
    #                 if h not in preDictions.keys(): continue
    #                 if h in tag_propagate.keys():
    #                     tag_propagate[h] = max(tag_propagate[h], [tweet_user.retweetCount, tweet_user.likeCount,
    #                                                                 tweet_user.replyCount])
    #                 else:
    #                     tag_propagate[h] = [tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount]
    #         for h,v in tag_propagate.items():
    #             if h in propagation_res.keys():
    #                 propagation_res[h] += v
    #             else:
    #                 propagation_res[h] =v
    #     return propagation_res


curdate = datetime.datetime.today().date()
curdate -= datetime.timedelta(1);
#print(f'today is {curdate} type is {type(curdate)}')
histroy_date = curdate - datetime.timedelta(7)
#print(f'histroy date is {histroy_date} type is {type(histroy_date)}')

histroy_trends = TrendInfo(histroy_date,7)
histroy_trends.retrieve_trends()
histroy_trends.record_tweets(his=True)
histroy_trends.record_user_tweets(his=True)

#result = verify_pre(preDictions=histroy_trends[0], users=histroy_trends[2].keys(),curdate=curdate)
current_trends = TrendInfo(curdate,7)
current_trends.retrieve_trends()
current_trends.record_tweets(his=False)
current_trends.record_user_tweets(his=False)
#current_trends.record_trend()

# current_preDictor = current_trends[0]
# current_hashtrends = current_trends[3]
# current_trends_time = current_trends[4]
# current_estimator_past = current_trends[5]
# current_estimator = current_trends[6]
# current_inftweets = current_trends[7]
# current_testtweets = current_trends[8]

current_trends.measure_estimator()

#tweets_crawled = [histroy_trends, histroy_testtweets, current_inftweets,current_testtweets]
#print(f'crawl data: {tweets_crawled}')

#tweets_crawled_df = pd.DataFrame(tweets_crawled)
#tweets_crawled_df.to_csv('tweets.csv')
# users_related = [len(histroy_trends[6]), len(current_trends[6])]
# print(f'crawl users:{users_related}')
# users_related_df = pd.DataFrame(users_related)
# users_related_df.to_csv('infers.csv')
sametrend = histroy_trends.measure_estimetion(current_trends.get_current_trends())


# last_N_tweets = sntwitter.TwitterSearchScraper('from:AsithosM').get_items()
# for N,tweet_user in enumerate(last_N_tweets):
#     print(f'user {tweet_user.user.username} content {tweet_user.content}')

#test
# hashtag_trends = {'#a':0.8, '#b':19, '#c':-5}
# hashtag_time ={'#a':datetime.date.today(), '#b':datetime.date.today(),'#c':datetime.date.today()}



# Creating a dataframe from the tweets List above
# tweets_df2 = pd.DataFrame(tweets_List2, columns=['Datetime', 'Tweet Id', 'Username'])