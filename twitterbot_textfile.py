# Import our Twitter credentials from credentials.py
from credentials import *
from time import sleep
import sqlite3
import tweepy
import os
import shutil

select_nodes = """
SELECT visits_missed, count(*) AS num_members
FROM nodes
WHERE id in (select node_id from connections)
GROUP BY visits_missed
ORDER BY visits_missed
"""

select_nodes_tor = """
SELECT visits_missed, count(*) AS num_members
FROM nodes
WHERE 
	id IN (
		SELECT id 
		FROM nodes
		WHERE nodes.ip LIKE '%onion%'
	)
GROUP BY visits_missed
ORDER BY visits_missed
"""

# Access and authorize our Twitter credentials from credentials.py
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def execute(query, args={}):
    # Make a copy of the database
    try:
        shutil.copy('../crawler.db', 'server.db')
        # HACK to make sure the copying finishes
        sleep(60)
    except IOError as e:
        print("Unable to copy file. %s" % e)
    except:
        print("Unexpected error:", sys.exc_info())
    # Open the database
    with sqlite3.connect('server.db') as conn:
        return conn.execute(query, args)

def node_count(node_dict):
    # Count all nodes visited last week
    i = 0
    num_nodes = 0
    check_last = node_dict[-1]
    while i < 8:
        if check_last[0] >= i:
            select_item = node_dict[i]
            num_nodes += select_item[1]
        i += 1
    return num_nodes

def run():
    return node_count(execute(select_nodes).fetchall())

def run_tor():
    return node_count(execute(select_nodes_tor).fetchall())

while True:
    tweet = "Total number of reachable nodes past week: " + str(run()) + \
        "\nOf which was tor-nodes: " + str(run_tor())
    api.update_status(status=tweet)
    # Sleep 1h
    sleep(60*60)
