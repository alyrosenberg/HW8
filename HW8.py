# Import statements
import unittest
import sqlite3
import requests
import json
import re
import tweepy
import twitter_info # still need this in the same directory, filled out
import pprint

consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
pp = pprint.PrettyPrinter(indent=4)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

# And we've provided the setup for your cache. But we haven't written any functions for you, so you have to be sure that any function that gets data from the internet relies on caching.
CACHE_FNAME = "twitter_cache.json"
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

## [PART 1]

# Here, define a function called get_tweets that searches for all tweets referring to or by "umsi"
# Your function must cache data it retrieves and rely on a cache file!

#api.user_timeline(screen_name = 'umsi')

def get_tweets(keyword="umsi"):
    if keyword in CACHE_DICTION:
        return CACHE_DICTION[keyword]
    else:
        public_tweets = api.search(q=keyword) #look if theres an option for case insensitive
        textandtime = []
        for i in range(0, len(textandtime)-1):
            firstfive[textandtime[i]] = textandtime[i + 1]
        CACHE_DICTION[keyword] = public_tweets
        writefile = open(CACHE_FNAME,"w")
        writefile.write(json.dumps(CACHE_DICTION))
        writefile.close()
    return public_tweets

# def get_tweets2(keyword = "umsi"):
#     if keyword in CACHE_DICTION:
#         return CACHE_DICTION[keyword]
#     else:
#         umsitweets = api.user_timeline(screen_name = 'umsi')
#         CACHE_DICTION[keyword] = public_tweets
#         writefile = open(CACHE_FNAME,"w")
#         writefile.write(json.dumps(CACHE_DICTION))
#         writefile.close()
#     return umsitweets

## [PART 2]
# Create a database: tweets.sqlite,
# And then load all of those tweets you got from Twitter into a database table called Tweets, with the following columns in each row:
## tweet_id - containing the unique id that belongs to each tweet
## author - containing the screen name of the user who posted the tweet (note that even for RT'd tweets, it will be the person whose timeline it is)
## time_posted - containing the date/time value that represents when the tweet was posted (note that this should be a TIMESTAMP column data type!)
## tweet_text - containing the text that goes with that tweet
## retweets - containing the number that represents how many times the tweet has been retweeted

# Below we have provided interim outline suggestions for what to do, sequentially, in comments.

# 1 - Make a connection to a new database tweets.sqlite, and create a variable to hold the database cursor.
conn = sqlite3.connect('twitter.sqlite')
cur = conn.cursor()
# 2 - Write code to drop the Tweets table if it exists, and create the table (so you can run the program over and over), with the correct (4) column names and appropriate types for each.
# HINT: Remember that the time_posted column should be the TIMESTAMP data type!
cur.execute('DROP TABLE IF EXISTS umsi')
cur.execute('CREATE TABLE umsi (tweet_id TEXT, author TEXT, time_posted TIMESTAMP, tweet_text TEXT, retweets INTEGER)')

# 3 - Invoke the function you defined above to get a list that represents a bunch of tweets from the UMSI timeline. Save those tweets in a variable called umsi_tweets.
umsi_tweets = get_tweets()['statuses'] #this statuses thing might be wrong

# 4 - Use a for loop, the cursor you defined above to execute INSERT statements, that insert the data from each of the tweets in umsi_tweets into the correct columns in each row of the Tweets database table.
for tweet in umsi_tweets:
    cur.execute('INSERT INTO umsi (tweet_id, author, time_posted, tweet_text, retweets) VALUES (?, ?, ?, ?, ?)',                     
            (tweet['id'], tweet["user"]["name"], tweet['created_at'], tweet['text'], tweet['retweet_count']))
    conn.commit()

#  5- Use the database connection to commit the changes to the database

# You can check out whether it worked in the SQLite browser! (And with the tests.)

## [PART 3] - SQL statements
# Select all of the tweets (the full rows/tuples of information) from umsi_tweets and display the date and message of each tweet in the form:
    # Mon Oct 09 16:02:03 +0000 2017 - #MondayMotivation https://t.co/vLbZpH390b
    #
    # Mon Oct 09 15:45:45 +0000 2017 - RT @MikeRothCom: Beautiful morning at @UMich - It’s easy to forget to
    # take in the view while running from place to place @umichDLHS  @umich…
# Include the blank line between each tweet.
cur.execute("select time_posted || ' - ' || tweet_text || '\n'  from umsi")
for row in cur:
    print (row[0])

# Select the author of all of the tweets (the full rows/tuples of information) that have been retweeted MORE
# than 2 times, and fetch them into the variable more_than_2_rts.
# Print the results
more_than_2_rts = []
cur.execute("select distinct author from umsi where retweets >2")
for row in cur:
    more_than_2_rts.append(row[0])
print (more_than_2_rts)


cur.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
