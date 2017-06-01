"""
 *  Drew McArthur, Geo Engel, Risa Ulinski, Judy Zhou
 *  6/1/17
 *  a script to produce a single datafile from the race and horse information 
    located in the raw data folder (defined in config) for use with an AI
 *  note: use python3
"""

import yaml
config = yaml.safe_load(open("config.yml"))

# right way to access config vars
# config['raw_data_path']
