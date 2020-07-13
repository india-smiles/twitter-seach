import sqlite3
import time
import zlib
import string

conn = sqlite3.connect('twitter_search_index_4.sqlite')
cur = conn.cursor()


cur.execute('SELECT id, text FROM "Search Terms"')
search_terms = dict()
for message_row in cur :
    search_terms[message_row[1]] = message_row[0]

print("The search terms are:")
for search_term in list(search_terms.keys()):
    print (search_term)

print()
search=input ("Which search term do you want to visualise in a word cloud?  ")
if search in list(search_terms.keys()):
    chosen_search_term = search
    chosen_search_id = search_terms.get(search)

    cur.execute('''SELECT text AS word,word_count FROM
    (SELECT word_id, sum(count) as word_count FROM "Tweet Words" GROUP BY word_id ORDER BY word_count DESC LIMIT 100)A
    JOIN (SELECT Text, ID FROM Words)B ON A.word_id=B.ID
    WHERE A.word_id IN (SELECT word_id FROM "Tweet Words" WHERE tweet_id IN (SELECT ID FROM Tweets WHERE search_id = %d))
    ''' % chosen_search_id)
    words = dict()
    for message_row in cur:
        words[message_row[0]] = message_row[1]


    x = sorted(words, key=words.get, reverse=True)
    # print(x)
    highest = None
    lowest = None
    for k in x[:1000]:
        if highest is None or highest < words[k]:
            highest = words[k]
        if lowest is None or lowest > words[k]:
            lowest = words[k]
    print('Range of counts:', highest, lowest)


    # Spread the font sizes across 20-100 based on the count
    bigsize = 80
    smallsize = 20

    fhand = open('tw_word.js', 'w')
    fhand.write("tw_word = [")
    first = True
    for k in x[:100]:
        if not first:
            fhand.write(",\n")
        first = False
        size = words[k]
        size = (size - lowest) / float(highest - lowest)
        size = int((size * bigsize) + smallsize)
        fhand.write("{text: '" + k + "', size: " + str(size) + "}")
    fhand.write("\n];\n")
    fhand.close()

    print("Output written to tw_word.js")
    print("Open tw_word.htm in a browser to see the vizualization")
