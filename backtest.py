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


def record_trend(data, hashtag_time):
    sorted_trends = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
    trend_list = []
    for k in sorted_trends:
        #print(f'tag: {k[0]} has {k[1]} more potential inf, start time:{hashtag_time[k[0]]}')
        #   if k[1]<=[0,0,0]: break
        trend_list.append([k[0], k[1][0], k[1][1], k[1][2], hashtag_time[k[0]]])
    trend_df = pd.DataFrame(trend_list, columns=['Trend', 'Retweet', 'Like', 'Reply', 'Start Time'])
    trend_df.to_csv('trend.csv', header=True)

def record_influencer(data):
    sortedinfluencers = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
    influencer_list =[]
    for k in sortedinfluencers:
        influencer_list.append([k[0],k[1][0],k[1][1],k[1][2]])
    inf_df = pd.DataFrame(influencer_list,columns=['username','retweet','Like','Reply'])
    inf_df.to_csv('influencer.csv',header=True)

def measure_estimator(user_pastinf, usernowinf):
    estimator_div =[0]*11
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

def measure_estimetion(predict,curval,newresult):
    div={}
    error_list = [0] * 11
    mean_reversion =0
    total_rev =0
    trend_follow =0
    total_follow =0
    for h in newresult.keys():
        if h in predict.keys():
            sumpre = sum(predict[h])
            sumnew = sum(newresult[h])
            sumnow = sum(curval[h])
            if sumnew ==0:
                #print(f'{h} has inf {newresult[h]}')
                continue
            print(f'hashtag {h} pre inf {sumpre} new inf {sumnew}')
            if sumpre>sumnow:
                total_rev += 1
                if sumnew>sumnow:
                    mean_reversion +=1
            if sumnow>1.1*sumpre:
                total_follow += 1
                if sumnew>sumnow:
                    trend_follow +=1
            div[h] = abs(sumpre-sumnew)/sumnew
            idx = int(div[h]// 0.1)
            idx = min(idx, 10)
            error_list[idx] += 1
    sumtags = sum(error_list)
    if sumtags==0: return
    print(f'mean reversion ratio is {mean_reversion/total_rev}')
    print(f'trend following ratio is {trend_follow/total_follow}')
    error_list = [1.0*error_list[i]/sumtags for i in range(11)]
    print(f'error trend distribution is {error_list}')
    error_list.append(mean_reversion/total_rev)
    error_list.append(trend_follow/total_follow)
    error_df = pd.DataFrame(error_list)
    error_df.to_csv('error_distribution.csv')

def retrieve_trends(curdate):
    startdate = curdate - datetime.timedelta(7)
    hashtag = '#Bitcoin OR #Ether OR #ether OR #bitcoin'
    query = hashtag + ' since:' + str(startdate)+' until:'+str(curdate)
    print(f'query is {query}')
    totaltweets = sntwitter.TwitterSearchScraper(query)
    PastN = 100
    hashtag_trends ={}
    user_inf_inthepast={}
    user_inf ={}
    hashtag_time ={}
    hashtag_trends_now ={}
    hashtag_trend_pre={}
    record_round = 1
    for i, tweet in enumerate(totaltweets.get_items()):
        if tweet == None: continue
        if tweet.user.username in user_inf.keys(): continue
        if len(hashtag_trends) >= record_round * 1000:
            record_trend(hashtag_trends,hashtag_time)
            # record_influencer(user_inf)
            # measure_estimetion(hashtag_trends_predict, hashtag_trends_now)
            measure_estimator(user_pastinf=user_inf_inthepast, usernowinf=user_inf)
            record_round += 1
        inf = [tweet.retweetCount, tweet.likeCount, tweet.replyCount]
        if inf == []: continue
        if my_criteria(inf):
            thisuser = tweet.user.username
            tag_Ipropagate = {}
            last_N_tweets = sntwitter.TwitterSearchScraper('from:' + thisuser +' until:'+str(curdate)).get_items()
            infthisuer = []
            infthisuer_inthepast = []
            for N, tweet_user in enumerate(last_N_tweets):
                if tweet_user == None: continue
                if N > PastN * 2:
                    break
                got_hashtags = retrive_hashtags(content=tweet_user.content)
                if N <= PastN:
                    infthisuer.append([tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                else:
                    infthisuer_inthepast.append([tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                for h in got_hashtags:
                    h = h.lower()
                    if N <= PastN:
                        if h in tag_Ipropagate.keys():
                            tag_Ipropagate[h] = max(tag_Ipropagate[h], [tweet_user.retweetCount, tweet_user.likeCount,
                                                                        tweet_user.replyCount])
                        else:
                            tag_Ipropagate[h] = [tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount]
                        if h in hashtag_time.keys():
                            hashtag_time[h] = min(hashtag_time[h], tweet_user.date)
                        else:
                            hashtag_time[h] = tweet_user.date
            if len(infthisuer) > 0:
                infthisuer = np.array(infthisuer, dtype=np.float32)
                avg = infthisuer.mean(0)
                for h in tag_Ipropagate.keys():
                    if h in hashtag_trends.keys():
                        hashtag_trends[h] += [avg[i] - tag_Ipropagate[h][i] for i in range(3)]
                        hashtag_trends_now[h] += tag_Ipropagate[h]
                        hashtag_trend_pre[h] += avg
                    else:
                        hashtag_trends[h] = [avg[i] - tag_Ipropagate[h][i] for i in range(3)]
                        hashtag_trends_now[h] = tag_Ipropagate[h]
                        hashtag_trend_pre[h] = avg
                user_inf[thisuser] = [avg[0], avg[1], avg[2]]
                print(f'user {thisuser} avg inf : {avg}')
            if len(infthisuer_inthepast) > 0:
                infthisuer_inthepast = np.array(infthisuer_inthepast, dtype=np.float32)
                avg = infthisuer_inthepast.mean(0)
                user_inf_inthepast[thisuser] = [avg[0], avg[1], avg[2]]
                print(f'user {thisuser} past avg inf : {avg}')
    return [hashtag_trend_pre,hashtag_trends_now,user_inf]

def verify_pre(predictions,users,curdate):
    startdate = curdate-datetime.timedelta(7)
    propagation_res ={}
    for thisuser in users:
        query = 'from:' + thisuser +' since:'+str(startdate)+' until:'+str(curdate)
        last_N_tweets = sntwitter.TwitterSearchScraper(query).get_items()
        tag_propagate ={}
        for N, tweet_user in enumerate(last_N_tweets):
            if tweet_user == None: continue
            got_hashtags = retrive_hashtags(content=tweet_user.content)
            for h in got_hashtags:
                h = h.lower()
                if h not in predictions.keys(): continue
                if h in tag_propagate.keys():
                    tag_propagate[h] = max(tag_propagate[h], [tweet_user.retweetCount, tweet_user.likeCount,
                                                                tweet_user.replyCount])
                else:
                    tag_propagate[h] = [tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount]
        for h,v in tag_propagate.items():
            if h in propagation_res.keys():
                propagation_res[h] += v
            else:
                propagation_res[h] =v
    return propagation_res


import snscrape.modules.twitter as sntwitter
import pandas as pd
from requests_oauthlib import OAuth1Session
import datetime
import re
import operator
import numpy as np
curdate = datetime.date.today()
histroy_date = curdate - datetime.timedelta(7)
histroy_trends = retrieve_trends(histroy_date)

result = verify_pre(predictions=histroy_trends[0], users=histroy_trends[2].keys(),curdate=curdate)
#current_trends = retrieve_trends(curdate)
measure_estimetion(predict=histroy_trends[0],curval=histroy_trends[1],newresult=result)

# last_N_tweets = sntwitter.TwitterSearchScraper('from:AsithosM').get_items()
# for N,tweet_user in enumerate(last_N_tweets):
#     print(f'user {tweet_user.user.username} content {tweet_user.content}')




#test
# hashtag_trends = {'#a':0.8, '#b':19, '#c':-5}
# hashtag_time ={'#a':datetime.date.today(), '#b':datetime.date.today(),'#c':datetime.date.today()}



# Creating a dataframe from the tweets list above
# tweets_df2 = pd.DataFrame(tweets_list2, columns=['Datetime', 'Tweet Id', 'Username'])