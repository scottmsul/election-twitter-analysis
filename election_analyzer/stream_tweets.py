import json
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
# import election_analyzer.util as util
import util

# time to wait before setting up a new stream (in seconds)
# discovered this through a little trial-and-error
MIN_TIME_BETWEEN_STREAMS = 10.0

# def stream(config_data):
def stream_duration(duration, tags, account_keys):
  timer = Timer()

  stored_tweets = []
  listener = get_listener(duration, tags, stored_tweets)
  auth = get_auth(account_keys)
  s = Stream(auth, listener)
  s.filter(track=tags)

  timer.wait_if_necessary()
  return stored_tweets

# can update later to include quantity listener
def get_listener(duration, tags, stored_tweets):
  listener = TimeListener(duration, tags, stored_tweets)
  return listener

def get_auth(account_keys):
  access_token = account_keys['access_token']
  access_token_secret = account_keys['access_token_secret']
  consumer_key = account_keys['consumer_key']
  consumer_secret = account_keys['consumer_secret']

  auth = OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  return auth

class QuantityListener(StreamListener):

  def __init__(self, num_tweets, data, tags):
    self.tags = tags
    self.data = data
    self.num_tweets = num_tweets
    self.tweet_count = 0

  def on_data(self, tweet_text):
    tweet = json.loads(tweet_text)
    if u'text' not in tweet:
      print "tweet does not contain 'text' attribute, skipping..."
      return
    if util.contains_tag(self.tags, tweet):
      self.data.append(tweet)
      self.tweet_count += 1
      print "downloading tweet %i of %i" % (self.tweet_count, self.num_tweets)
    else:
      text = util.get_text(tweet)
      print "tweet \"%s\" did not contain proper tag, skipping..." % text

    if self.tweet_count == self.num_tweets:
      return False

  def on_error(self, status):
    if status == 420:
      print "420 error"
      raise IOError
      return False

class TimeListener(StreamListener):

  def __init__(self, duration, tags, data):
    self.tags = tags
    self.data = data
    self.start = time.time()
    self.duration = duration

  def on_data(self, tweet_text):
    tweet = json.loads(tweet_text)
    if u'text' not in tweet:
      print "tweet does not contain 'text' attribute, skipping..."
      return
    if util.contains_tag(self.tags, tweet):
      self.data.append(tweet)

    if time.time() - self.start > self.duration:
      return False

  def on_error(self, status):
    if status == 420:
      print "420 error"
      return False

class Timer:

  def __init__(self):
    self.start_time = time.time()

  def wait_if_necessary(self):
    start_time = self.start_time
    end_time = time.time()
    diff = end_time - start_time
    if diff < MIN_TIME_BETWEEN_STREAMS:
      sleep_time = MIN_TIME_BETWEEN_STREAMS - diff
      time.sleep(sleep_time)
