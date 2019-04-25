# Twitter bot

Twitterbot that tweet's information about Bitcoin full nodes once a week.

Loosely following this tutorial https://www.digitalocean.com/community/tutorials/how-to-create-a-twitterbot-with-python-3-and-the-tweepy-library

Using this crawler https://github.com/justinmoon/crawler and producing a crawler.db containing information about Bitcoin full nodes.

## Setup

* Clone and run the crawler to create the database (it needs to run for a week to get the correct result)
* Cd to the crawler `cd crawler` and start it in the background with `nohup python3 crawler.py &` 
* Get your twitter developer credentials at https://developer.twitter.com/
* Clone this project to the same folder as the crawler (so the path is ../crawler/full-nodes-tweetbot/) `git clone https://github.com/DriftwoodPalace/Full-Nodes-Tweetbot.git`
* Cd to the folder `cd  Full-Nodes-Tweetbot` 
* Create an virtual environment if you like and install the requirements `pip3 install -r requirements.txt`
* Change `credentials_example.py`to `credentials.py` and add your Twitter credentials.
* Run the twitterbot in the background `nohup python3 twitterbot_textfile.py &`
