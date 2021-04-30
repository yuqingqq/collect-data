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
import sys

class TrendInfo:

    def __init__(self, curdate:datetime.date, timedif:int, hashtag:str = '#Bitcoin OR #Ether OR #ether OR #bitcoin'):
        self._endday: datetime.date = curdate - datetime.timedelta(1)
        self._startday: datetime.date = self._endday - datetime.timedelta(timedif)
        self._hashtag:str = hashtag
        self._PastN:int = 100
        self._hashtag_trends:Dict[str,List[float]] = {}
        self._user_inf_inthepast : Dict[str,List[float]] ={}
        self._user_inf : Dict[str,List[float]] ={}
        self._hashtag_time: Dict[str,datetime.date] ={}
        self._hashtag_trends_now :Dict[str,List[float]]={}
        self._hashtag_trend_pre : Dict[str,List[float]]={}
        self._propagte_group :Dict[str,int]={}
        self._tweetsinfo :List[List[str]]= []
        self._tweetsuserinfo:List[List[str]] = []
        self._testtweets :int= 0
        self._inftweets :int = 0

    def my_criteria(self,inf:List[float])->bool:
        crit = [10,10,2]
        if inf>=crit:
            return True
        return False

    def retrive_hashtags(self,content:str)->List[str]:
        return re.findall('#\w+', content)

    def record_trend(self):
        data :Dict[str,float]= self._hashtag_trends
        hashtag_time:Dict[str,datetime.date] = self._hashtag_time
        sorted_trends = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
        trend_List:List[List[str]] = []
        for k in sorted_trends:
            #print(f'tag: {k[0]} has {k[1]} more potential inf, start time:{hashtag_time[k[0]]}')
            #   if k[1]<=[0,0,0]: break
            trend_List.append([k[0], k[1][0], k[1][1], k[1][2], hashtag_time[k[0]]])
        trend_df = pd.DataFrame(trend_List, columns=['Trend', 'Retweet', 'Like', 'Reply', 'Start Time'])
        trend_df.to_csv('trend.csv', header=True)

    def record_influencer(self):
        data :Dict[str,List[float]] = self._user_inf
        sortedinfluencers = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
        influencer_List:List[List[str]] =[]
        for k in sortedinfluencers:
            influencer_List.append([k[0],k[1][0],k[1][1],k[1][2]])
        inf_df = pd.DataFrame(influencer_List,columns=['username','retweet','Like','Reply'])
        name = 'influencer_'+str(self._startday)+'.csv'
        inf_df.to_csv(name,header=True)

    def measure_estimator(self):
        estimator_div =[0]*11
        user_pastinf:Dict[str,List[float]] = self._user_inf_inthepast
        usernowinf:Dict[str,List[float]] = self._user_inf
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
        tweets_df:pd.DataFrame = pd.DataFrame(self._tweetsinfo)
        headers = ['id','url','user','date','content','hashtags','retweet','like','reply','place',
                                                    'coordinates','lang','media','source','quotecount','quotedtweet']
        if his == True:
            name = 'tweetsinfo_his.csv'
        else:
            name = 'seedtag_'+str(self._startday)+'.csv'
        tweets_df.to_csv(name,header=headers)

    def record_user_tweets(self,his:bool):
        tweets_df:pd.DataFrame = pd.DataFrame(self._tweetsuserinfo)
        headers = ['id','url','user','date','content','hashtags','retweet','like','reply','place',
                                                    'coordinates','lang','media','source','quotecount','quotedtweet']
        if his == True:
            name = 'tweetsuserinfo_his.csv'
        else:
            name = 'usertweets_'+str(self._startday)+'.csv'
        tweets_df.to_csv(name,header=headers)

    def fetch_long_term_data(self,startdate:datetime.date=datetime.date(year=2021,month=1,day=1),enddate:datetime.date= datetime.date.today()):
        curday = enddate-datetime.timedelta(1)
        while curday>startdate:
            self._endday = curday
            self._startday = curday-datetime.timedelta(1)
            self.retrieve_trends()
            self.record_user_tweets(his=False)
            self.record_tweets(his=False)
            self.record_influencer()
            curday -= datetime.timedelta(1)

    def refresh(self):
        self._hashtag_trends:Dict[str,List[float]] = {}
        self._user_inf_inthepast : Dict[str,List[float]] ={}
        self._user_inf : Dict[str,List[float]] ={}
        self._hashtag_time: Dict[str,datetime.date] ={}
        self._hashtag_trends_now :Dict[str,List[float]]={}
        self._hashtag_trend_pre : Dict[str,List[float]]={}
        self._propagte_group :Dict[str,int]={}
        self._tweetsinfo :List[List[str]]= []
        self._tweetsuserinfo:List[List[str]] = []
        self._testtweets :int= 0
        self._inftweets :int = 0

    def measure_estimetion(self, currentinf:Dict[str,List[int]]):
        div:Dict[str,float]={}
        error_List:list[float] = [0] * 11
        mean_reversion:float =0
        total_reversion:float =0
        trend_follow:float =0
        total_follow:float =0
        follow_trend:List[str] = []
        reversion_trend:List[str] =[]
        sametrend:int = 0
        hash_inf_reversion:List[List[str]] = []
        hash_inf_follow:List[List[str]] =[]
        for h in self._hashtag_trend_pre.keys():
            preDict_inf:float = sum(self._hashtag_trend_pre[h])
            previous_inf:float = sum(self._hashtag_trends_now[h])
            num_infer:int = self._propagte_group[h]
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
        error_List:List[float] = []
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

    def get_current_trends(self)->Dict[str,List[float]]:
        return self._hashtag_trends_now

    def retrieve_trends(self):
        query :str = self._hashtag + ' since:' + str(self._startday)+' until:'+str(self._endday)
        print(f'query is {query}')
        totaltweets = sntwitter.TwitterSearchScraper(query)
        record_round :int= 1
        for i, tweet in enumerate(totaltweets.get_items()):
            self._testtweets += 1
            if tweet == None or tweet.date.date()<self._startday: continue
            tweet_hashtags = ""
            for h in self.retrive_hashtags(tweet.content):
                if tweet_hashtags=="":tweet_hashtags+= h
                else: tweet_hashtags = tweet_hashtags+" "+h
            self._tweetsinfo.append([tweet.id, tweet.url,tweet.user.username,tweet.date,tweet.content,tweet_hashtags,tweet.retweetCount,tweet.likeCount,tweet.replyCount,tweet.place,tweet.coordinates,tweet.lang,tweet.media,tweet.source,tweet.quoteCount,tweet.quotedTweet])
            if tweet.user.username in self._user_inf.keys(): continue
            inf :List[float]= [tweet.retweetCount, tweet.likeCount, tweet.replyCount]
            if inf == []: continue
            if self.my_criteria(inf):
                self._inftweets += 1
                thisuser:str = tweet.user.username
                tag_Ipropagate :Dict[str,float]= {}
                last_N_tweets = sntwitter.TwitterSearchScraper('from:' + thisuser +' until:'+str(self._endday)).get_items()
                infthisuer:List[List[float]] = []
                infthisuer_inthepast: List[List[float]] = []
                for N, tweet_user in enumerate(last_N_tweets):
                    self._testtweets += 1
                    if tweet_user == None: continue
                    #if N > self._PastN * 2:
                    if N > self._PastN:
                        break
                    got_hashtags = self.retrive_hashtags(content=tweet_user.content)
                    if N <= self._PastN:
                        infthisuer.append([tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                    #else:
                    #   infthisuer_inthepast.append([tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                   # print(f'date is type of {type(tweet_user.date)}')
                    if tweet_user.date.date()<self._startday:
                        continue
                    tweet_use_hashtags = ""
                    for h in got_hashtags:
                        if tweet_use_hashtags == "": tweet_use_hashtags+=h
                        else: tweet_use_hashtags = tweet_use_hashtags+" "+h
                    self._tweetsuserinfo.append([tweet_user.id, tweet_user.url,tweet_user.user.username,tweet_user.date,tweet_user.content,tweet_use_hashtags,tweet_user.retweetCount,tweet_user.likeCount,tweet_user.replyCount,tweet_user.place,tweet_user.coordinates,tweet_user.lang,tweet_user.media,tweet_user.source,tweet_user.quoteCount,tweet_user.quotedTweet])
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
                # if len(infthisuer_inthepast) > 0:
                #     infthisuer_inthepast = np.array(infthisuer_inthepast, dtype=np.float32)
                #     avg = infthisuer_inthepast.mean(0)
                #     self._user_inf_inthepast[thisuser] = [avg[0], avg[1], avg[2]]
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

if __name__ == "__main__":
    curdate = datetime.datetime.today().date()
    curdate -= datetime.timedelta(1);
    startdate = sys.argv[1]
    startdate = datetime.date(year = int(startdate[0:4]),month=int(startdate[4:6]),day = int(startdate[6:]))
    enddate = sys.argv[2]
    enddate = datetime.date(year = int(enddate[0:4]),month=int(enddate[4:6]),day = int(enddate[6:]))

    #print(f'today is {curdate} type is {type(curdate)}')
    #histroy_date = curdate - datetime.timedelta(7)
    #print(f'histroy date is {histroy_date} type is {type(histroy_date)}')
    histroy_trends = TrendInfo(curdate,1)
    histroy_trends.fetch_long_term_data(startdate,enddate)

#result = verify_pre(preDictions=histroy_trends[0], users=histroy_trends[2].keys(),curdate=curdate)
# current_trends = TrendInfo(curdate,7)
# current_trends.retrieve_trends()
# current_trends.record_tweets(his=False)
# current_trends.record_user_tweets(his=False)
#current_trends.record_trend()

# current_preDictor = current_trends[0]
# current_hashtrends = current_trends[3]
# current_trends_time = current_trends[4]
# current_estimator_past = current_trends[5]
# current_estimator = current_trends[6]
# current_inftweets = current_trends[7]
# current_testtweets = current_trends[8]

#current_trends.measure_estimator()

#tweets_crawled = [histroy_trends, histroy_testtweets, current_inftweets,current_testtweets]
#print(f'crawl data: {tweets_crawled}')

#tweets_crawled_df = pd.DataFrame(tweets_crawled)
#tweets_crawled_df.to_csv('tweets.csv')
# users_related = [len(histroy_trends[6]), len(current_trends[6])]
# print(f'crawl users:{users_related}')
# users_related_df = pd.DataFrame(users_related)
# users_related_df.to_csv('infers.csv')

#sametrend = histroy_trends.measure_estimetion(current_trends.get_current_trends())


# last_N_tweets = sntwitter.TwitterSearchScraper('from:AsithosM').get_items()
# for N,tweet_user in enumerate(last_N_tweets):
#     print(f'user {tweet_user.user.username} content {tweet_user.content}')

#test
# hashtag_trends = {'#a':0.8, '#b':19, '#c':-5}
# hashtag_time ={'#a':datetime.date.today(), '#b':datetime.date.today(),'#c':datetime.date.today()}



# Creating a dataframe from the tweets List above
# tweets_df2 = pd.DataFrame(tweets_List2, columns=['Datetime', 'Tweet Id', 'Username'])