A python project dedicated to analyzing the election. Who will win? Let's find out.

Purpose of each script/order to run them in:

0) source initialize.sh
This script temporarily adds ./bin/ to the path

1) bin/download_tweets.py
This script downloads tweets from twitter's streaming API. Check the config file in runs/test_run for some options.

2) bin/upload_state_data.py
This script uploads data from './data/democratic_primary_results.csv' to 'state_data' in mongodb. Contains past primary results.

3) bin/analyze_tweets.py
This script analyzes downloaded tweets by state and uploads the results to 'state_data' in mongodb.


