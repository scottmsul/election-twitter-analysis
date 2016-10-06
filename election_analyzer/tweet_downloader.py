import os
import util
from stream_tweets import stream_duration

# don't stream for more than 10 minutes at a time to save memory
MAX_STREAM_DURATION = 60*10

class TweetDownloader:

  def __init__(self, config_file, save_directory):
    self.__initialize_config_file(config_file)
    self.__initialize_save_directory(save_directory)

  def __initialize_config_file(self, config_file):
    config_fullpath = os.path.realpath(config_file)
    config_data = util.load_json_data(config_fullpath)
    self.config_data = config_data

  def __initialize_save_directory(self, save_directory):
    self.save_directory = save_directory

  def download_tweets(self):
    name = self.config_data[u'name']
    collection_name = "%s.tweets" % name
    tweet_manager = util.TweetManager(collection_name)
    tweet_manager.clear()

    duration = self.config_data[u'duration']
    tags = self.config_data[u'tags']
    account_keys = self.config_data[u'account_keys']
    while duration > 0:
      if duration > MAX_STREAM_DURATION:
        curr_duration = MAX_STREAM_DURATION
      else:
        curr_duration = duration
      tweets = stream_duration(curr_duration, tags, account_keys)
      tweet_manager.save_tweets(tweets)
      duration -= curr_duration
