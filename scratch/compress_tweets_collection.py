# add election_analyzer to python path
import os
import sys
file_dir = os.path.realpath(__file__)
bin_dir = os.path.split(file_dir)[0]
project_dir = os.path.split(bin_dir)[0]
sys.path.append(project_dir)

import election_analyzer.util as util
import pymongo

def compress_tweets_collection(collection_name):
  client = pymongo.MongoClient()
  db = client.election
  co = db[collection_name]
  keys = [
      'contributors',
      'truncated',
      'is_quote_status',
      'in_reply_to_status_id',
      'id',
      'favorite_count',
      'source',
      'retweeted',
      'coordinates',
      'timestamp_ms',
      'entities',
      'in_reply_to_screen_name',
      'in_reply_to_user_id',
      'retweet_count',
      'id_str',
      'favorited',
      'retweeted_status',
      'geo',
      'in_reply_to_user_id_str',
      'possibly_sensitive',
      'lang',
      'created_at',
      'filter_level',
      'in_reply_to_status_id_str',
      'place',
      'extended_entities',
      'supported_candidate',
      'opposed_candidate',
      'quoted_status_id_str',
      'quoted_status_id',
      'quoted_status',
      'user.default_profile_image',
      'user.id_str',
      'user.utc_offset',
      'user.statuses_count',
      'user.description',
      'user.friends_count',
      'user.profile_link_color',
      'user.profile_image_url',
      'user.notifications',
      'user.profile_background_image_url_https',
      'user.profile_background_color',
      'user.profile_banner_url',
      'user.profile_background_image_url',
      'user.screen_name',
      'user.lang',
      'user.profile_background_tile',
      'user.favourites_count',
      'user.name',
      'user.url',
      'user.created_at',
      'user.contributors_enabled',
      'user.time_zone',
      'user.profile_sidebar_border_color',
      'user.default_profile',
      'user.following',
      'user.listed_count',
      'user.verified',
      'user.follow_request_sent',
      'user.profile_use_background_image',
      'user.profile_image_url_https',
      'user.profile_sidebar_fill_color',
      'user.profile_text_color',
      'user.followers_count',
      'user.protected',
      'user.is_translator',
      'user.geo_enabled',
  ]
  for key in keys:
    print key
    co.update({}, {'$unset': {key: 1}}, multi=True)
