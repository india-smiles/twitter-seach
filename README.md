# twitter-seach
An application to use Twitter's Search API to search for popular tweets for any keyword, then analyse results.


# Goal of this programme:
The ultimate goal of the programme is to have an application within Twitter, which takes an input of search query and #tweets and produces automatic visualisations of results in a webpage, including public mood (from semantic analysis of tweets) and a glossary of key terminology for that topic.


# About the programme:
This programme uses SQLite and TextBlob https://textblob.readthedocs.io/en/dev, pulling tweets from the Twitter Search API. https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets


## Pre-reqs to run the programme:
- You must update hidden_public.py with your own private keys from your 'Twitter for Developers' account

- You mut have TextBlob (with supporting NLTK files) imported, as well as RegEx, SQlite3, Datetime, Zlib and string

- You must be using Python3


## How to run the programme:
1. Run tw_search_spider_21may_final.py. This programme will ask you to input the query term you want to search, and how many tweets to look for (this is rate limited by Twitter). It will then pull these tweets and put the results in the database tweet_search.sqlite.

2. Run tw_search_index_21may_final.py. This programme will index all the data in tweet_search.sqlite, using TextBlob to get the dictionary definitions of words. The results are put in the database twitter_search_index_4.sqlite.

3. Run tw_basic_13july_final.py. This programme wil ask you to input the search term you want to learn more about, then print out the total number of tweets, a couple of tweets and the details of the most popular tweet. The outputs are printed in the console.


### The current output of the index is:
- Tweet: Text, Posted_At, Retweets, URL (_often inaccurate_), Sentiment (Scale from Negative = -100 to Positive = +100; found using Textblob)

- Search Terms

- Words _All words used in tweet, attempting to remove urls_

- Glossary _Dictionary definition of all known words found using TextBlob_

and there's a linking table Tweet Words to match the many-to-many relationship of Tweet/Words.


### What is missing from the programme:
*Visualisations (TBD)

*Twitter application set-up guide


# Would love any comments! Good luck :+1:

