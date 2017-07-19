""" This script will iterate through the columns of data we have, 
    and determine if each column contains continuous or discrete data.
    the output of the script will be a list of boolean values.
    each value in the list refers to a column of the data, 
    true if discrete, false if continuous
"""

import numpy as np
import csv

def isDicrete(l):
    for item in l:
        try:
            float(item)
        except ValueError:
            return False
    return True

def main():
    datafile = open('data.csv')
    datareader = csv.reader(datafile, dialect='unix')

    headers = next(datareader)
    data = []
    for row in reader:
        data.append(row)

    data = np.array(data)

    mask = []
    for c in range(len(headers)):
        col = data[:,c]
        mask.append(isDiscrete(col))

    print(mask)

if __name__ == "__main__":
    main()
