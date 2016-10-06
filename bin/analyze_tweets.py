#!/usr/bin/python
import argparse

parser = argparse.ArgumentParser(description = 'Download tweets.')
parser.add_argument('-c', '--config_file', help = 'Config file. Defaults to ./config.json')
args = parser.parse_args()

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

from election_analyzer.election_analyzer import ElectionAnalyzer
election_analyzer = ElectionAnalyzer(config_file)
election_analyzer.analyze_election_tweets()
