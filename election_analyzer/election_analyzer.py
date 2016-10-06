import util
import os
from collections import Counter
import pprint
import pymongo
import copy
import numpy as np
import csv
import matplotlib.pyplot as pl

class ElectionAnalyzer:

  def __init__(self, config_file):
    config_data = util.load_json_data(config_file)
    name = config_data[u'name']

    client = pymongo.MongoClient()
    self.db = client.election

    self.tweet_collection_name = "%s.tweets" % name
    self.tweet_collection = self.db[self.tweet_collection_name]

    self.state_collection_name = "%s.states" % name
    self.state_collection = self.db[self.state_collection_name]

    self.users_collection_name = "%s.users" % name
    self.users_collection = self.db[self.users_collection_name]

    self.statistics = {}

  def analyze_election_tweets(self):
#     self.upload_state_data_to_tweets()
#     self.upload_candidate_data_to_tweets()
#     self.initialize_users()
#     self.calculate_user_candidate_scores()
#     self.calculate_twitter_supporters_by_state()
#     self.calculate_voter_twitter_ratios()
    self.calculate_statistics()
    self.calculate_future_primary_results()
    self.calculate_total_remaining_delegates()
    self.calculate_sigma_differences()
    self.save_data_to_csv()
    self.plot_ratios()

  def upload_state_data_to_tweets(self):
    print "analyzing states..."
    for tweet in self.tweet_collection.find():
      curr_state = util.get_state(tweet)
      if curr_state != None:
        self.tweet_collection.update({'_id': tweet[u'_id']}, {'$set': { 'state': curr_state}})

  def upload_candidate_data_to_tweets(self):
    print "analyzing supported candidates..."
    for tweet in self.tweet_collection.find():
      curr_supported_candidate = util.get_supported_candidate(tweet)
      # if curr_supported_candidate != None:
      if curr_supported_candidate != None and curr_supported_candidate != 'trump':
        self.tweet_collection.update({'_id': tweet[u'_id']}, {'$set': { 'supported_candidate': curr_supported_candidate}})

#     print "analyzing opposed candidates..."
#     for tweet in self.tweet_collection.find():
#       curr_opposed_candidate = util.get_opposed_candidate(tweet)
#       if curr_opposed_candidate != None:
#         self.tweet_collection.update({'_id': tweet[u'_id']}, {'$set': { 'opposed_candidate': curr_opposed_candidate}})

  def initialize_users(self):
    print "initializing twitter users..."
    users = self.users_collection
    for tweet in self.tweet_collection.find():
      if 'supported_candidate' in tweet:
        user_id = tweet['user']['id']
        if users.find({'user_id': user_id}).count() == 0 and 'state' in tweet:
          users.insert_one({'user_id': user_id, 'state': tweet['state']})
#         curr_user = users.find_one({'user_id': user_id})
#         if 'state' in tweet:
#           users.update({'_id': curr_user['_id']}, {'$set': { 'state': tweet['state']}})
    self.users_collection = users

  def calculate_user_candidate_scores(self):
    print "calculating supported democratic candidate..."
    total = self.users_collection.count()
    count = 0
    for user in self.users_collection.find():
      count += 1
      print "calculating candidate scores, user %i of %i" % (count, total)
      user_id = user['user_id']
      score = 0
      for tweet in self.tweet_collection.find({'user.id': user_id}):
        if 'supported_candidate' in tweet:
          if tweet['supported_candidate'] == 'clinton':
            score -= 1
          if tweet['supported_candidate'] == 'sanders':
            score += 1
#       if 'opposed_candidate' in tweet:
#         if tweet['opposed_candidate'] == 'clinton':
#           score += 1
#         if tweet['opposed_candidate'] == 'sanders':
#           score -= 1
      if score > 0:
        self.users_collection.update({'_id': user['_id']}, {'$set': { 'supported_candidate': 'sanders'}})
      if score < 0:
        self.users_collection.update({'_id': user['_id']}, {'$set': { 'supported_candidate': 'clinton'}})

  def calculate_twitter_supporters_by_state(self):
    print "calculating number of supporters in each state by candidate..."
    for state in self.state_collection.find():
      state_name = state['state']
      sanders_supporters = self.users_collection.count({'state': state_name, 'supported_candidate': 'sanders'})
      clinton_supporters = self.users_collection.count({'state': state_name, 'supported_candidate': 'clinton'})
      self.state_collection.update({'_id': state['_id']}, {'$set': { 'clinton_twitter_supporters': clinton_supporters, 'sanders_twitter_supporters': sanders_supporters}})
  
  def calculate_voter_twitter_ratios(self):
    print "calculating voter-to-twitter-supporter ratios..."
    for state in self.state_collection.find({'primary_occured': True}):
      sanders_twitter_supporters = state['sanders_twitter_supporters']
      sanders_twitter_supporters_unc = np.sqrt(sanders_twitter_supporters)
      sanders_votes = state['sanders_votes']

      clinton_twitter_supporters = state['clinton_twitter_supporters']
      clinton_twitter_supporters_unc = np.sqrt(clinton_twitter_supporters)
      clinton_votes = state['clinton_votes']

#      if sanders_twitter_supporters > 20 and clinton_twitter_supporters > 20:
      if sanders_twitter_supporters > 1 and clinton_twitter_supporters > 1:
        sanders_ratio = float(sanders_votes) / float(sanders_twitter_supporters)
        sanders_ratio_unc = (sanders_ratio / sanders_twitter_supporters) * sanders_twitter_supporters_unc
        clinton_ratio = float(clinton_votes) / float(clinton_twitter_supporters)
        clinton_ratio_unc = (clinton_ratio / clinton_twitter_supporters) * clinton_twitter_supporters_unc
        ratio_ratio = float(sanders_ratio) / float(clinton_ratio)
        ratio_ratio_unc = np.sqrt( (ratio_ratio/sanders_ratio*sanders_ratio_unc)**2 + (ratio_ratio/clinton_ratio*clinton_ratio_unc)**2)
  
        self.state_collection.update({'_id': state['_id']},
            {'$set': {
              'sanders_voter_twitter_ratio': sanders_ratio, 'sanders_voter_twitter_ratio_unc': sanders_ratio_unc,
              'clinton_voter_twitter_ratio': clinton_ratio, 'clinton_voter_twitter_ratio_unc': clinton_ratio_unc,
              'ratio_ratio': ratio_ratio, 'ratio_ratio_unc': ratio_ratio_unc}})

  def calculate_statistics(self):
    print "calculating statistics..."
    ratio_ratios = []
    ratio_ratio_uncs = []
    for state in self.state_collection.find({'ratio_ratio': {'$exists': True}}):
      ratio_ratios.append(state['ratio_ratio'])
      ratio_ratio_uncs.append(state['ratio_ratio_unc'])
      print "ratio %s: %f " % (state['state'], state['ratio_ratio'])
      print "uncrt %s: %f " % (state['state'], state['ratio_ratio_unc'])

    N = len(ratio_ratios)
    xs = ratio_ratios
    sigma_xs = ratio_ratio_uncs

    ys = [np.log(xs[i]) for i in range(N)]
    sigma_ys = [(1./xs[i]) * sigma_xs[i] for i in range(N)]

    avg_y = util.mean(ys, sigma_ys)
    sigma_avg_y = util.std(ys, sigma_ys)

    avg_x = np.exp(avg_y)
    x_unc = avg_x * sigma_avg_y

    self.statistics['average_ratio_ratio'] = avg_x
    self.statistics['average_ratio_ratio_unc'] = x_unc

    print "average: %f" % self.statistics['average_ratio_ratio']
    print "uncertainty: %f" % self.statistics['average_ratio_ratio_unc']

  def calculate_future_primary_results(self):
    print "calculating future primary results..."
    for state in self.state_collection.find({'primary_occured': False}):
      sanders_twitter_supporters = float(state['sanders_twitter_supporters'])
      clinton_twitter_supporters = float(state['clinton_twitter_supporters'])
      if sanders_twitter_supporters > 0 and clinton_twitter_supporters > 0:
        x = self.statistics['average_ratio_ratio'] * (sanders_twitter_supporters / clinton_twitter_supporters)
        delegates = float(state['total_delegates'])
        sanders_delegates = (x / (1+x)) * delegates
        clinton_delegates = (1. / (1+x)) * delegates

        sanders_delegates_sys_unc = (1. / (1+x))**2 * delegates * self.statistics['average_ratio_ratio_unc']
        sanders_delegates_stat_unc = np.sqrt(sanders_twitter_supporters)
        sanders_delegates_unc = np.sqrt(sanders_delegates_sys_unc**2 + sanders_delegates_stat_unc**2)
        clinton_delegates_sys_unc = (1. / (1+x))**2 * delegates * self.statistics['average_ratio_ratio_unc']
        clinton_delegates_stat_unc = np.sqrt(clinton_twitter_supporters)
        clinton_delegates_unc = np.sqrt(clinton_delegates_sys_unc**2 + clinton_delegates_stat_unc**2)

        self.state_collection.update({'_id': state['_id']},
          {'$set': {
            'sanders_delegates': sanders_delegates,
            'clinton_delegates': clinton_delegates,
            'sanders_delegates_unc': sanders_delegates_unc,
            'clinton_delegates_unc': clinton_delegates_unc}})
        print "state: %s, sanders delegates: %f, unc: %f" % (state['state'], sanders_delegates, sanders_delegates_unc)
        print "state: %s, clinton delegates: %f, unc: %f" % (state['state'], clinton_delegates, clinton_delegates_unc)

  def calculate_total_remaining_delegates(self):
    sanders_delegates = []
    sanders_delegates_uncs = []
    clinton_delegates = []
    clinton_delegates_uncs = []
    for state in self.state_collection.find({'sanders_delegates': {'$exists': True}, 'primary_occured': False}):
      sanders_delegates.append(state['sanders_delegates'])
      sanders_delegates_uncs.append(state['sanders_delegates_unc'])
      clinton_delegates.append(state['clinton_delegates'])
      clinton_delegates_uncs.append(state['clinton_delegates_unc'])
    total_sanders_delegates = np.sum(sanders_delegates)
    total_sanders_delegates_unc = np.sqrt(np.sum([d**2 for d in sanders_delegates_uncs]))
    total_clinton_delegates = np.sum(clinton_delegates)
    total_clinton_delegates_unc = np.sqrt(np.sum([d**2 for d in clinton_delegates_uncs]))
    print "total sanders delegates: %f, unc: %f" % (total_sanders_delegates, total_sanders_delegates_unc)
    print "total clinton delegates: %f, unc: %f" % (total_clinton_delegates, total_clinton_delegates_unc)
    self.statistics['total_sanders_delegates'] = total_sanders_delegates
    self.statistics['total_sanders_delegates_unc'] = total_sanders_delegates_unc
    self.statistics['total_clinton_delegates'] = total_clinton_delegates
    self.statistics['total_clinton_delegates_unc'] = total_clinton_delegates_unc

  def save_data_to_csv(self):
    with open('election_analysis.csv', 'w') as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow(['Data for states where primary has already occured'])
      writer.writerow(['State', 'Sanders votes', 'Clinton votes', 'Sanders twitter supporters', 'Clinton twitter supporters',
                       'Sanders vote/twitter ratio', 'Sanders ratio uncertainty', 
                       'Clinton vote/twitter ratio', 'Clinton ratio uncertainty', 
                       'Ratio of (Sanders ratio) to (Clinton ratio)', 'Ratio of ratios uncertainty'])
      for state in self.state_collection.find({'sanders_voter_twitter_ratio': {'$exists': True}, 'primary_occured': True}):
        writer.writerow([state['state'], state['sanders_votes'], state['clinton_votes'],
                       state['sanders_twitter_supporters'], state['clinton_twitter_supporters'],
                       state['sanders_voter_twitter_ratio'], state['sanders_voter_twitter_ratio_unc'],
                       state['clinton_voter_twitter_ratio'], state['clinton_voter_twitter_ratio_unc'],
                       state['ratio_ratio'], state['ratio_ratio_unc']])
      writer.writerow([])
      writer.writerow(['Data for states where primary hasn\'t occured yet'])
      writer.writerow(['State', 'Sanders twitter supporters', 'Clinton twitter supporters', 
                       'Predicted Sanders delegates', 'Predicted Sanders delegate uncertainty',
                       'Predicted Clinton delegates', 'Predicted Clinton delegate uncertainty'])
      for state in self.state_collection.find({'sanders_delegates': {'$exists': True}, 'primary_occured': False}):
        writer.writerow([state['state'], state['sanders_twitter_supporters'], state['clinton_twitter_supporters'],
                         state['sanders_delegates'], state['sanders_delegates_unc'],
                         state['clinton_delegates'], state['clinton_delegates_unc']])
      writer.writerow([])
      writer.writerow(['Statistical data'])
      writer.writerow(['Weighted average of (ratio of ratios)', 'uncertainty',
        'Total sanders delegates in mentioned states', 'uncertainty',
        'Total clinton delegates in mentioned states', 'uncertainty'])
      writer.writerow([self.statistics['average_ratio_ratio'], self.statistics['average_ratio_ratio_unc'],
          self.statistics['total_sanders_delegates'], self.statistics['total_sanders_delegates_unc'],
          self.statistics['total_clinton_delegates'], self.statistics['total_clinton_delegates_unc']])

  def plot_ratios(self):
    state_names = []
    ratio_ratios = []
    ratio_ratio_uncs = []
    for state in self.state_collection.find({'ratio_ratio': {'$exists': True}}):
      state_names.append(state['state'])
      ratio_ratios.append(state['ratio_ratio'])
      ratio_ratio_uncs.append(state['ratio_ratio_unc'])

    ax = pl.figure()
    pl.errorbar(range(len(ratio_ratios)), ratio_ratios, yerr=ratio_ratio_uncs, fmt='o')
    pl.yscale('log')
    pl.xlim([-2, 44])
    pl.ylim([-.03, 10])

    # rotates the x-axis labels by 70 degrees
    ind = np.arange(len(state_names))
    pl.xticks(ind - 0.3, state_names)
    locs, labels = pl.xticks()
    pl.setp(labels, rotation=70)

    # adds average line
    pl.axhline(self.statistics['average_ratio_ratio'])
    pl.axhline(1, linestyle='--', color='black')

    pl.title('Ratio Between (Sanders Primary Votes / Sanders Twitter Supporters) and (Clinton Primary Votes / Clinton Twitter Supporters)')

    # gives more room for the state names to appear
    pl.gcf().subplots_adjust(bottom=0.3)

    pl.show()
