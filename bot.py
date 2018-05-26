import tweepy
import time
import requests

from bs4 import BeautifulSoup
from calendar import timegm
from creds import *


class DauntlessStatus:
    def __init__(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.last_status = None
        self.last_check_time = time.time()

    def run(self):
        while True:
            resp = requests.get('https://status.playdauntless.com/')
            soup = BeautifulSoup(resp.text, 'lxml')
            status = list()
            for item in soup.select('ul.systems li'):
                splits = item.text.replace('\n', '').split(' ')
                if splits[0] == "Game":
                    status.append(f"{splits[0]} {splits[1]} - {splits[2]}")
                else:
                    status.append(f"{splits[0]} - {splits[1]}")
            incidents = list()
            for item in soup.select('div.incidents'):
                tm = item.select_one('span.date').text.split('/')
                tm = [f"0{x}" if len(x) == 1 else x for x in tm]
                tm = '/'.join(tm)
                utc = time.strptime(tm, "%d/%m/%Y %I:%M %p")
                epoch = timegm(utc)
                if epoch > self.last_check_time:
                    incidents.append(f"{item.select_one('span.title').text}\n"
                                     f"{item.select_one('p').text} or ''")
            self.last_check_time = time.time()
            if self.last_status == status:
                pass
            else:
                self.last_status = status
                tweet_status = '\n'.join(status)
                try:
                    self.api.update_status(status=tweet_status)
                except tweepy.error.TweepError:
                    pass

            if incidents:
                tweet_incidents = '\n'.join(incidents)
                self.api.update_status(status=tweet_incidents)

            time.sleep(60*8)


