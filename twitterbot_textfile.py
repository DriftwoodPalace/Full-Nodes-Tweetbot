# Import our Twitter credentials from credentials.py
from credentials import *
from time import sleep
from datetime import date
import sqlite3
import tweepy
import os
import shutil
import matplotlib
import matplotlib.pyplot as plt

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

count_nodes = "SELECT nodes FROM counter" 

count_tor_nodes = "SELECT tor_nodes FROM counter" 

dates = "SELECT date FROM counter" 

# Access and authorize our Twitter credentials from credentials.py
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def copy():
    # Make a copy of the database
    con = sqlite3.connect('../crawler.db')
    with sqlite3.connect('server.db') as bck:
        con.backup(bck, pages=1, progress=None)
    

def get_values(query, args={}):
    # Open the database
    with sqlite3.connect('server.db') as conn:
        return conn.execute(query, args)

def fetch_numbers():
    with sqlite3.connect('counter.db') as conn:
        last_week = conn.execute(count_nodes).fetchall()
        last_week_tor = conn.execute(count_tor_nodes).fetchall()
    return last_week, last_week_tor

def counter():
    counter = sqlite3.connect('counter.db')
    c = counter.cursor()
    day = date.today()
    nodes = [day, node_count, '']
    tor_nodes = [day, '', tor_node_count]
    try:
        c.execute('''CREATE TABLE counter
                (date text, nodes integer, tor_nodes integer)''')
    except sqlite3.OperationalError:
        print('Database already exists')
    c.execute("INSERT INTO counter VALUES (?, ?, ?)", nodes)
    c.execute("INSERT INTO counter VALUES (?, ?, ?)", tor_nodes)
    counter.commit()
    counter.close()
    
    if len(fetch_numbers()[0]) >= 4: 
        difference = week[0] - fetch_numbers()[0][-4][0]
        difference_tor = week_tor[0] - fetch_numbers()[1][-3][0]
    else:
        difference, difference_tor = 0, 0
    if difference > 0:
        difference = "+" + str(difference)
    if difference_tor > 0:
        difference_tor = "+" + str(difference_tor)
    plotter()
    return str(difference), str(difference_tor)

def plotter():
    # Data for plotting
    with sqlite3.connect('counter.db') as conn:
        all_dates = conn.execute(dates).fetchall()
    count = 0
    date_lst = []
    tor_date_lst = []
    for num_date in all_dates:
        if count % 2 == 0:
            date_lst.append(num_date[0])
        else:
            tor_date_lst.append(num_date[0])
        count +=1
    count_lst = []
    count2 = 0
    for num in fetch_numbers()[0]:
        if count2 % 2 == 0:
            count_lst.append(num[0])
        count2 +=1  
    t = date_lst
    s = count_lst
    fig, ax = plt.subplots()
    ax.plot(t, s)
    ax.set(title='Reachable nodes (over 7 days)')
    ax.grid()
    ax.set_ylim(0, 15000)
    fig.savefig(day_png)

while True:
    copy()
    node_lst = get_values(active_nodes).fetchall()
    week = [i[0] for i in node_lst]
    node_lst_tor = get_values(active_nodes_tor).fetchall()
    week_tor = [i[0] for i in node_lst_tor]
    node_count = week[0]
    tor_node_count = week_tor[0]
    day_png = str(date.today()) + ".png"
    difference_tot = counter()
    tweet = "Number of reachable nodes last 7 days: " + str(node_count) \
            + " (" + difference_tot[0] + ")" + "\nOf which was tor-nodes: " \
                + str(tor_node_count) + " (" + difference_tot[1] + ")"
    api.update_with_media(filename=day_png, status=tweet)
    # Sleep 7 days
    sleep(60*60*24*7)
