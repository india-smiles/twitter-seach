
#NEXT WE WILL SET UP THE LIBRARIES WE NEED, AND DEFINE ANY FUNCTIONS WE WILL USE IN PROGRAMME.

import sqlite3
from textblob import TextBlob, Word
import time
from datetime import datetime, timedelta
import dateutil.parser as parser
from nltk import punkt
import zlib
import re
import string

#I SHOULD UPDATE THIS FUNCTION TO REMOVE URLS RATHER THAN LEFT STRIP. AND ALSO ADD A FUNCTION TO REMOVE @MENTIONS.
def urlstrip (s):
    if re.search('http',s):
        return s[:s.find('http')]
    else:
        return s


#LIBRARY SET-UP IS COMPLETE.
#NEXT WE WILL CREATE OUR NOW INDEX DATABASE.


conn = sqlite3.connect('twitter_search_index_4.sqlite')
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS Tweets ''')
cur.execute('''DROP TABLE IF EXISTS "Tweet Phrases" ''')
cur.execute('''DROP TABLE IF EXISTS Phrases ''')
cur.execute('''DROP TABLE IF EXISTS Words ''')
cur.execute('''DROP TABLE IF EXISTS "Tweet Words" ''')
cur.execute('''DROP TABLE IF EXISTS "Search Terms" ''')
cur.execute('''DROP TABLE IF EXISTS Glossary ''')

cur.execute('''CREATE TABLE IF NOT EXISTS Tweets
    (
    "ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "Text"	BLOB NOT NULL,
	"Posted_At"	INTEGER NOT NULL,
	"Retweets"	INTEGER,
    "Tweet_URL" BLOB,
	"Sentiment"	INTEGER,
	"Search_ID"	INTEGER NOT NULL
    )''')
cur.execute('''CREATE TABLE IF NOT EXISTS Words
    (
    "ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Text"	TEXT NOT NULL UNIQUE
    )''')
cur.execute('''CREATE TABLE IF NOT EXISTS "Tweet Words"
    (
    "Tweet_ID"	INTEGER NOT NULL,
	"Word_ID"	INTEGER NOT NULL,
	"Count"	INTEGER,
    UNIQUE(tweet_id, word_id)
    )''')
cur.execute('''CREATE TABLE IF NOT EXISTS "Search Terms"
    (
    "ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Text"	TEXT UNIQUE
    )''')
cur.execute('''CREATE TABLE IF NOT EXISTS "Glossary"
    (
    "ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Text"	TEXT NOT NULL UNIQUE,
	"Word_ID"	INTEGER
    )''')

print("Created the index database " "as" " twitter_search_index_2.sqlite")

#OUR INDEX DATABASE IS NOW CREATED.
#NEXT WE WILL CONNECT TO OUR ORIGINAL TWEET DATABASE


conn_1 = sqlite3.connect('file:tweet_search.sqlite?mode=ro', uri=True)
cur_1 = conn_1.cursor()

cur_1.execute('''SELECT COUNT(*) FROM Tweets''')
tweets_total=cur_1.fetchone()[0]

print("Loaded all",tweets_total,"tweets")


#WE HAVE CONNECTED TO THE ORIGINAL TWEET DATABASE
#NEXT WE WILL PARSE THE DATE USING TEXTBLOB AND DATEUTIL, TO GET OUR NEW VARIABLES



cur_1.execute('''SELECT text, created_at, search_term, tweet_url, retweet_count FROM Tweets''')

tweets=dict()
search_terms=dict()
words=dict()


count=0

for message_row in cur_1:
#WE ARE LOOPING THROUGH EACH TWEET
#THE ORDER IN WHICH WE UPDATE THE TABLES IS UPDATED BY THE DEPENDENCIES IN THE DATA STRUCTURE
#WE NEED TO KNOW THE SEARCH ID TO POPULATE 'TWEETS'
#AND THEN WE NEED TO KNOW THE TWEET ID TO POPULATE THE 'TWEET WORDS' TABLE FOR EACH WORD
#AND THEN WE NEED TO KNOW THE WORD ID TO POPULATE THE 'GLOSSARY' TABLE FOR EACH DEFINITION
#SO OUR ORDER OF POPULATION IS (1) SEARCH (2) TWEETS (3) WORDS (4) TWEET WORDS (5) GLOSSARY


#THE 'TWEET' AND 'SEARCH' TABLES ARE UPDATED IN THE TWEET LOOP
    text=message_row[0]
    textblobbed = TextBlob(text.lower())

    search_term=message_row[2].lower()
    tweet_url=message_row[3]
    retweet_count=message_row[4]
    posted_at= parser.parse(message_row[1]).isoformat()
    sentiment=round(round((textblobbed.sentiment.polarity),2)*100)

    tweet_id=tweets.get(text, None)
    search_id=search_terms.get(search_term, None)

    if search_id is None :
        cur.execute('INSERT OR IGNORE INTO "Search Terms" (text) VALUES ( ? )', ( search_term, ) )
        conn.commit()
        cur.execute('SELECT id FROM "Search Terms" WHERE text=? LIMIT 1', ( search_term, ))
        try:
            row = cur.fetchone()
            search_id = row[0]
            search_terms[search_term] = search_id
            print("Search ID:", search_id)
        except:
            print('Could not retrieve search id',search)
            break

    #print(text, len(text),posted_at,sentiment,search_id)
    if tweet_id is None :
        cur.execute('INSERT OR IGNORE INTO "Tweets" (text, posted_at, sentiment, search_id, tweet_url, retweets) VALUES ( ?, datetime(?), ?, ?, ?, ?)', (zlib.compress(text.encode()), posted_at,sentiment,int(search_id), zlib.compress(tweet_url.encode()), retweet_count ))
        conn.commit()
        cur.execute('SELECT id FROM "Tweets" WHERE text=? LIMIT 1', (zlib.compress(text.encode()), ))
        try:
            row = cur.fetchone()
            tweet_id = row[0]
            tweets[text] = tweet_id
            print("Tweet_ID:",tweet_id)
        except:
            print('Could not retrieve tweet id',text)
            break

#THE 'WORDS' AND 'TWEET WORDS' TABLES ARE UPDATED IN THE WORD LOOP FOR EACH TWEET
    word_count_dict=textblobbed.word_counts #Sets word_count later used for Tweet Words table
    cleaned_text=urlstrip(text.lower()) #Removes trailing urls
    word_list=re.findall('([a-z]+)',cleaned_text) #Creates word list

    for word in word_list:
        if len(word)<3: continue #Ignore single letters or 2 letters words
        word=Word(word).singularize()
        word_id=words.get(word, None)
        if word_id is None:
            cur.execute('INSERT OR IGNORE INTO Words (text) VALUES ( ? )', ( word, ) )
            conn.commit()
            cur.execute('SELECT id FROM Words WHERE text=? LIMIT 1', ( word, ))
            try:
                row = cur.fetchone()
                word_id = row[0]
                words[word] = word_id
            except:
                print('Could not retrieve word id',word)
                break

            cur.execute('INSERT OR IGNORE INTO "Tweet Words" (tweet_id, word_id, count) VALUES ( ?, ?, ? )', ( int(tweet_id), int(word_id), int(word_count_dict[word]) ) )
            conn.commit()

#THE 'GLOSSARY' TABLE IS UPDATED IN THE DEFINITION LOOP FOR EACH WORD
        glossary=Word(word).definitions
        if len(glossary)==0: continue
        for definition in glossary:
            cur.execute('INSERT OR IGNORE INTO "Glossary" (text, word_id) VALUES ( ?, ? )', (definition, word_id ) )
            conn.commit()

#NOW ALL THE TABLES HAVE BEEN UPDATED FOR THE TWEET
    count = count + 1
    print("Processing complete upto tweet", count)


cur.close()
cur_1.close()
