"""
 *  Drew McArthur, Geo Engel, Risa Ulinski, Judy Zhou
 *  6/1/17
 *  a script to produce a single datafile from the race and horse information 
    located in the raw data folder (defined in config) for use with an AI
 *  note: use python3
"""

import yaml, os, csv
config = yaml.safe_load(open("config.yml"))

# right way to access config vars
# config['raw_data_path']

# get root folder, as well as pathname and file objects for the final product.
DATA = config['raw_data_path']
ENDFILENAME = config['final_data_filename']
ENDFILE = open(ENDFILENAME, 'w')
#ENDFILEWRITER = csv.DictWriter(ENDFILE, config['data_col_headers'])

# iterate through files in data directory
for d in os.listdir(DATA):
    for f in os.listdir(DATA + d):
        if f.endswith('.csv'):
            path = DATA + "/" + d + "/" + f
            with open(path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    print(row)
                    quit()
