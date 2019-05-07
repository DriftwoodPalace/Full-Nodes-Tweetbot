# Import our Twitter credentials from credentials.py
from credentials import *
from time import sleep
import sqlite3
import tweepy
import os
import shutil

active_nodes = """
select (
	select count(distinct node_id) 
	from connections 
	where strftime('%s','now') - start < 60*60*24*7 
    AND version IS NOT NULL
) as nodes_active_in_last_week;
"""

active_nodes_tor = """
select (
	select count(distinct node_id) 
	from connections 
	where strftime('%s','now') - start < 60*60*24*7 
    AND version IS NOT NULL AND 	
	node_id IN (
		SELECT id 
		FROM nodes
		WHERE nodes.ip LIKE '%onion%'
)) as nodes_active_in_last_week;
"""

# Access and authorize our Twitter credentials from credentials.py
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def copy():
    # Make a copy of the database
    con = sqlite3.connect('../crawler.db')
    with sqlite3.connect('server.db') as bck:
        con.backup(bck, pages=1, progress=None)
    

def execute(query, args={}):
    # Open the database
    with sqlite3.connect('server.db') as conn:
        return conn.execute(query, args)

while True:
    copy()
    node_lst = execute(active_nodes).fetchall()
    week = [i[0] for i in node_lst]
    node_lst_tor = execute(active_nodes_tor).fetchall()
    week_tor = [i[0] for i in node_lst_tor]
    tweet = "Number of reachable nodes last 7 days: " + str(week[0]) \
            + "\nOf which was tor-nodes: " + str(week_tor[0])
    api.update_status(status=tweet)
    # Sleep 24h
    sleep(60*60*24)
