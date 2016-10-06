#!/usr/bin/python

# add election_analyzer to python path
import os
import sys
file_dir = os.path.realpath(__file__)
bin_dir = os.path.split(file_dir)[0]
project_dir = os.path.split(bin_dir)[0]
sys.path.append(project_dir)

import argparse
import csv
import election_analyzer.util as util
import pymongo

parser = argparse.ArgumentParser(description = 'Download tweets.')
parser.add_argument('-c', '--config-file', help = 'Path to config file. Defaults to ./config.json.')
args = parser.parse_args()

if args.config_file:
  config_file = args.config_file
else:
  config_file = './config.json'

bin_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(os.path.split(bin_path)[0], 'data')
state_data_filename = os.path.join(data_path, 'democratic_primary_results.csv')

raw_state_data = []
with open(state_data_filename) as f:
  reader = csv.DictReader(f)
  for row in reader:
    raw_state_data.append(row)

state_data = []
for state in raw_state_data:
  curr_data = {}
  curr_data['state'] = state['State']
  curr_data['sanders_delegates'] = int(state['Sanders Delegates'])
  curr_data['clinton_delegates'] = int(state['Clinton Delegates'])
  curr_data['sanders_votes'] = int(state['Sanders Votes'])
  curr_data['clinton_votes'] = int(state['Clinton Votes'])
  curr_data['total_delegates'] = int(state['total_delegates'])
  curr_data['primary_occured'] = bool(state['primary_occured'])
  state_data.append(curr_data)
# for state in raw_state_data:
#   if state['primary_occured'] == 'TRUE':
#     curr_data = {}
#     curr_data['state'] = state['State']
#     curr_data['sanders_delegates'] = int(state['Sanders Delegates'])
#     curr_data['clinton_delegates'] = int(state['Clinton Delegates'])
#     curr_data['sanders_votes'] = int(state['Sanders Votes'])
#     curr_data['clinton_votes'] = int(state['Clinton Votes'])
#     curr_data['total_delegates'] = int(state['total_delegates'])
#     curr_data['primary_occured'] = True
#   else:
#     curr_data = {}
#     curr_data['state'] = state['State']
#     curr_data['total_delegates'] = int(state['total_delegates'])
#     curr_data['primary_occured'] = False
#   state_data.append(curr_data)

config_filename = os.path.realpath(config_file)
config_data = util.load_json_data(config_filename)
name = config_data['name']
state_collection_name = "%s.states" % name

client = pymongo.MongoClient()
db = client.election
db.drop_collection(state_collection_name)
state_collection = db[state_collection_name]
state_collection.insert_many(state_data)
