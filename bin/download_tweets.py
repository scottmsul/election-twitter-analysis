#!/usr/bin/python
import argparse

parser = argparse.ArgumentParser(description = 'Download tweets.')
parser.add_argument('-s', '--save-directory', help = 'Directory for saving the downloaded tweets. Defaults to ./data.')
parser.add_argument('-c', '--config-file', help = 'Path to config file. Defaults to ./config.json.')
args = parser.parse_args()

if args.save_directory:
  save_directory = args.save_directory
else:
  save_directory = './data'

if args.config_file:
  config_file = args.config_file
else:
  config_file = './config.json'

# put election_analyzer in the python path
import os
import sys
file_dir = os.path.realpath(__file__)
bin_dir = os.path.split(file_dir)[0]
project_dir = os.path.split(bin_dir)[0]
sys.path.append(project_dir)

from election_analyzer.tweet_downloader import TweetDownloader
tweet_downloader = TweetDownloader(config_file, save_directory)
tweet_downloader.download_tweets()
