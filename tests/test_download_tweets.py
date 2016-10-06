import election_analyzer.manage_files as manage_files
import election_analyzer.tweet_util as tweet_util
import election_analyzer.config_manager as cm
import download_tweets.download_tweets as download_tweets
import unittest


class TestDownloadTweets(unittest.TestCase):

  def test_download_cycle(self):
    download_tweets.download_cycle(1, 1)

    trump_pos_terms = file_manager.load_tracked_terms()[u'classified'][u'trump']
    recent_trump_pos_tweets = file_manager.load_most_recent_classified_tweets('trump', 'pos')
    recent_trump_text = tweet_util.get_text(recent_trump_pos_tweets[0])
    print recent_tumpt_text
    contains_term = text_contains_at_least_one_term(recent_trump_text, trump_pos_terms)
    self.assertTrue(contains_term)

    unclassified_terms = file_manager.load_tracked_terms()[u'unclassified']
    recent_unclassified_tweets = manage_file.load_most_recent_unclassified_tweets()
    unclassified_texts = [tweet_util.get_text(tweet) for tweet in recent_unclassified_tweets]
    print unclassified_texts
    tweet_results = [text_contains_at_least_one_term(text, unclassified_terms) for text in unclassified_texts]
    print tweet_results
    all_correct = all(tweet_results)
    self.assert_true(all_correct)

  def test_download_classified_tweets_by_category(self):
    tracked_terms = file_manager.load_tracked_terms()
    pos_bernie_terms = tracked_terms[u'classified'][u'sanders'][u'pos']

    download_tweets.download_classified_tweets_by_category('sanders', 'pos', 3)
    recent_tweets = file_manager.load_most_recent_classified_tweets('sanders', 'pos')
    for tweet in recent_tweets:
      text = tweet_util.get_text(tweet)
      
      contains_bernie_term = False
      for term in pos_bernie_terms:
        if term in text:
          contains_bernie_term = True
  
      self.assertTrue(contains_bernie_term)

  def test_download_unclassified_tweets(self):
    file_manager = manage_files.FileManager('data/test_set')
    config_manager = cm.ConfigLoader('config/config.json')
    unclassified_terms = config_manager.get_parameter('unclassified_terms')

    download_tweets.download_unclassified_tweets(5)
    recent_tweets = file_manager.load_most_recent_unclassified_tweets()
    for tweet in recent_tweets:
      text = tweet_util.get_text(tweet)

      contains_candidate = False
      for term in unclassified_terms:
        if term in text:
          contains_candidate = True

      self.assertTrue(contains_candidate)

def text_contains_at_least_one_term(text, terms):
  for term in terms:
    if term in text:
      return True
  return False

if __name__ == '__main__':
  unittest.main()
