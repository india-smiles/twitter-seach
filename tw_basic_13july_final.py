import sqlite3
import zlib

conn = sqlite3.connect('twitter_search_index_4.sqlite')
cur = conn.cursor()

cur.execute('SELECT id, text, retweets, sentiment, search_id FROM Tweets')
tweets = dict()
for message_row in cur :
    tweets[message_row[0]] = (zlib.decompress(message_row[1]), message_row[2], message_row[3], message_row[4])

cur.execute('SELECT id, text FROM "Search Terms"')
search_terms = dict()
for message_row in cur :
    search_terms[message_row[0]] = message_row[1]

print("Loaded",len(tweets),"tweets, over ",len(search_terms),"search terms")
print("The search terms are:")
for search_term in list(search_terms.values()):
    print (search_term)

print()
search=input ("Which search term do you want to learn more about?  ")
#print(list(search_terms.values()))
if search in list(search_terms.values()):
    chosen_search_term = search
    search_id_terms={}
    for k,v in list(search_terms.items()):
            search_id_terms[v]=k
    search_id=search_id_terms.get(search,1)
#    print(search_id)

    search_selected={}
    for k,v in list(tweets.items()):
    #    print(k,v)
        if v[3]==search_id:
            search_selected[k]=v
    #print(search_selected)
    print()
    print("There are", len(search_selected), "tweets on the topic of", chosen_search_term)

    i=0
    print()
    print("Here are a couple of tweets:")
    for key in search_selected:
            while (i < 2):
                text = search_selected[key][0]
                print(text)
                i +=1

    print()
    print ("Below are some details on the tweet with the highest retweet count,")

    retweet_count = 0
    details = []
    for key in search_selected:
        retweets = search_selected[key][1]
        if (retweets > retweet_count):
            retweet_count = retweets
            details.append(search_selected[key])
    most_popular_tweets = details.pop()
    print ("Text:", most_popular_tweets[0])
    print ("Retweet Count:", most_popular_tweets[1])
    print ("Sentiment:", most_popular_tweets[2], "(on a scale from -100 to +100)")
    print()
