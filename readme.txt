Algorithm in Report-social trend.pdf

fetch_data.py:
Input: startdate, enddate, hashtag
Output: 
	influencer.csv-> influencer's historical influence [username, retweet, like ,reply]
	trend.csv -> popular trends during the user defined period sorted by influence [trendname, retweet, like, reply, starttime]
 	usertweets.csv -> record influencer's tweets [id, url, user, date, content, hashtags, retweet, like, reply, place, coordinates, lang, media, source, quotecount, quotedtweet]
	seedtag.csv -> record tweets satisfying the user defined criterial (e.g., retweets >=10) [id, url, user, date, content, hashtags, retweet, like, reply, place, coordinates, lang, media, source, quotecount, quotedtweet]