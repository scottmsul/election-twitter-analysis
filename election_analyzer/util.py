import os
import glob
import json
import datetime
import re
import pymongo
import numpy as np

#### TWEET UTILITIES ####

def extract_important_info(tweet):
  info = {}
  info[u'text'] = get_text(tweet)
  info[u'user'] = tweet[u'user']
  return info

class TweetManager:

  def __init__(self, collection_name):
    self.collection_name = collection_name
    self.client = pymongo.MongoClient()
    self.database = self.client['election']
    self.collection = self.database[collection_name]

  def clear(self):
    self.database.drop_collection(self.collection_name)

  def save_tweets(self, tweets):
    self.collection.insert_many(tweets)

  def save_tweet(self, tweet):
    self.collection.insert_one(tweet)

def contains_tag(tags, tweet):
  text = get_text(tweet)
  for tag in tags:
    if tag in text:
      return True
  return False

def get_text(tweet):
  raw_text = tweet[u'text']
  if u"\u2026" in raw_text:
    if u'retweeted_status' in tweet:
      text = tweet[u'retweeted_status'][u'text']
    else:
      text = raw_text
  else:
    text = raw_text
  text = text.lower()
  return text

states_full = [
   "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii",
   "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
   "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
   "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
   "Washington", "West Virginia", "Wisconsin", "Wyoming",
]

states_abbr = [
   "AK", "AL", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA",
   "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN",
   "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

def get_state(tweet):
  if tweet[u'user'][u'location']:
    location = tweet[u'user'][u'location'].lower()
    for i, state_abbr in enumerate(states_abbr):
      regex = ", %s$" % state_abbr.lower()
      if re.search(regex, location):
        return states_full[i]
    for i, state in enumerate(states_full):
      regex = state.lower()
      if re.search(regex, location):
        if state.lower() == 'washington':
          return
        return states_full[i]
  return None

clinton_pos = ["#hillary2016", "#imwithher", "#clintonfoundation"]
sanders_pos = ["#feelthebern", "#bernieorbust", "#stillsanders", "#bernie2016"]
trump_pos = ["#makeamericagreatagain", "#trump2016", "#maga", "#trumptrain", "#votetrump", "#votetrump2016", "#onlytrump", "#women4trump", "#americafirst"]

pos_hashtags = {
    "clinton": clinton_pos,
    "sanders": sanders_pos,
    "trump": trump_pos
}

def get_supported_candidate(tweet):
  text = get_text(tweet)
  for candidate, hashtags in pos_hashtags.iteritems():
    for pos_tag in hashtags:
      if pos_tag.lower() in text.lower():
        return candidate
  return None

clinton_neg = ["#hillary2016", "#imwithher", "#clintonfoundation"]
sanders_neg = ["#feelthebern", "#bernieorbust", "#stillsanders", "#bernie2016"]
trump_neg = ["#makeamericagreatagain", "#trump2016", "#maga", "#trumptrain", "#votetrump", "#votetrump2016", "#onlytrump", "#women4trump", "#americafirst"]

neg_hashtags = {
    "clinton": clinton_neg,
    "sanders": sanders_neg,
    "trump": trump_neg
}

def get_opposed_candidate(tweet):
  text = get_text(tweet)
  for candidate, hashtags in neg_hashtags.iteritems():
    for neg_tag in hashtags:
      if neg_tag.lower() in text.lower():
        return candidate
  return None

#### FILE/DIRECTORY UTILITIES ####

def make_empty_dir(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)
  files = glob.glob("%s/*" % directory)
  for f in files:
    os.remove(f)

def load_json_array_from_directory(directory):
  json_array = []
  files = glob.glob("%s/*.json" % directory)
  for f in files:
    curr_array = load_json_array(f)
    json_array.extend(curr_array)
  return json_array

def load_json_array(filename):
  json_array = []
  with open(filename, 'r') as f:
    for line in f:
      try:
        curr_data = json.loads(line)
        json_array.append(curr_data)
      except:
        continue
  return json_array

def load_json_data(filename):
  with open(filename, 'r') as f:
    json_data = json.load(f)
  return json_data

def save_json_array(json_array, filename):
  with open(filename, 'w') as outfile:
    for json_data in json_array:
      json.dump(json_data, outfile)
      outfile.write("\n")

def get_curr_timestamp():
  return datetime.datetime.now().strftime("%y-%m-%d_%H:%M")

#### MATH UTILITIES ####

def mean(data, uncs):
  N = len(data)
  weights = [(1./uncs[i]**2) for i in range(N)]
  return np.sum([weights[i] * data[i] for i in range(N)]) / np.sum(weights)

def std(data, uncs):
  N = len(data)
  weights = [(1./uncs[i]**2) for i in range(N)]
  return np.sqrt(
      (1. / sum(weights)) *
      (1. / (N - 1)) *
      sum([weights[i] * (data[i] - mean(data, weights)) ** 2 for i in range(N)])
      )

def weighted_geometric_mean(data, weights):
  N = len(weights)
  return np.exp(
      weighted_mean([np.log(data[i]) for i in range(N)], weights)
      )

def weighted_geometric_std(data, weights):
  N = len(weights)
  return np.exp(
      weighted_std([np.log(data[i]) for i in range(N)], weights)
      )

def weighted_geometric_std(data, weights, mean):
  return np.exp(
    np.sqrt(
      (1. / np.sum(weights) ** 2) *
      (1. / (len(weights) - 1.)) *
      np.sum([weights[i] * (np.log(data[i]) - np.log(mean)) ** 2 for i in range(len(weights))])
    )
  )
