""" Drew McArthur
    6/28/17
    First attempt at using a neural net to compare two horses and 
        choose the one that will finish first
"""

from learn import split_data
from itertools import permutations
from collections import OrderedDict
import yaml, os, csv 

def get_raceID(horse):
    """ returns a string ID for the race the horse is in. """
    if isinstance(horse, dict):
        return horse['R_RCTrack'] + horse['R_RCDate'] + "_" + horse['R_RCRace']
    else:
        return horse[1] + horse[2] + "_" + horse[3]

def read_data(filename):
    """ read data from the filename, splitting horses into races """
    with open(filename) as dataFile:
        datareader = csv.reader(dataFile, dialect='unix')
        races = {}
        headers = next(datareader)
        for row in datareader:
            row = OrderedDict(zip(headers, row))
            ID = get_raceID(row)
            if ID in races:
                races[ID].append(row)
            else:
                races.update({ID:[row]})

        # dictionary where key=raceID (e.g. "PRX170603_4"), 
        #                value=list of horses in race
        return races

def get_comparison(horses):
    """ returns a comparison of horseA and B, 
        boolean value == (horseA['position'] < horseB['position'])
        i.e. true if horseA finished before horseB                  """
    horseA, horseB = horses
    return 1 if horseA['L_Position'] < horseB['L_Position'] else 0

def get_label(horse):
    """ returns the horse's finishing position in its race. """
    return horse['L_Position']

def read_output(filename, races):
    """ adds the position of each horse to the data in races """
    # read labels.data.csv
    with open(filename) as lFile:
        labelreader = csv.DictReader(lFile, dialect='unix')
        r = []
        # iterate through the file and keep track of times
        for row in labelreader:
            ID = get_raceID(row)
            if ID in races:
                for horse in races[ID]:
                    if horse['ID'] == row['ID']:
                        horse.update({"L_Position": row['L_Position']})
        return races

def generate_pairs(race):
    """ given a race (list of horses (dictionaries)), return a list,
        where each element in the list is a list compiled of all the data for
        two of the horses.  (not a dictionary, since the AI needs lists)
    """
    return list(permutations(race, 2))

def remove_raceInfo(l):
    """ given a list representing a horse, remove the list items 
        that give information on the race.  This is necessary since 
        the race info is already provided in the other horse. 
        this preserves ID, however """
    ID = l[0]
    name = l[4]
    newlist = l[30:]
    return [ID] + [name] + newlist

def format_pair(pair):
    """ given a tuple of two horses (dictionaries), return a single list
        containing all the information. """
    # split the tuple and remove labels.
    A, B = pair
    A.pop('L_Position', None)
    B.pop('L_Position', None)

    # get the values in each dictionary, then sort them by the original order
    keys, ret = zip(*A.items())
    keys, items = zip(*B.items())

    items = remove_raceInfo(list(items))

    # combine the lists and return them
    ret = list(ret) + items
    return ret

def isint(x):
    """ returns true if x is probably an int hidden in a string """
    try:
        int(x)
        return True
    except:
        return False

def format_data(horse):
    for i in range(len(horse)):
        if horse[i] == '':
            horse[i] = None
        elif isint(horse[i]):
            horse[i] = int(horse[i])
    return horse

def get_model(Xs, Ys):
    """ given the input and output data, return a trained AI model
        that classifies winners of horse races. 
        each row consists of information on two horses
    """
    # create necessary sklearn objects
    nn = MLPClassifier()

    # construct a pipe from previous objects
    model = make_pipeline()

    # train the model
    model.fit(Xs, Ys)

    return model

def test_model(model, x_test, y_test):
    """ given a model and test values, predict the Ys and print out a report
        of accuracy.
    """
    # get accuracy and predictions
    y_pred = model.predict(x_test)
    deltas = [abs(p-l) for p, l in zip(y_pred, y_test)]

    print("results for classifying winners")
    print(sum(deltas)/len(deltas))
    print(explained_variance_score(y_test, y_pred))
    print(r2_score(y_test, y_pred))

def main():
    # read the data and labels from file
    config = yaml.safe_load(open("./config.yml"))
    races = read_data(config['final_data_filename'])
    races = read_output("LABELS." + config['final_data_filename'], races)

    print("Read data from file.")

    # races now equals a dictionary, where each item is a race, 
    #       with key equal to the race's ID (given by get_raceID).  
    # a race is a list of horses that participated in that race
    # a horse is a dictionary containing all related information

    data = []
    labels = []
    i = 0
    for ID, race in races.items():
        pairs = generate_pairs(race)
        newlabels = [get_comparison(pair) for pair in pairs]
        data += [format_pair(pair) for pair in pairs]
        labels += newlabels
        print("Parsed {0:.2f}% of races.".format(i / (len(races)/100)), 
              end='\r')
        i += 1

    data = [format_data(d) for d in data]

    nuns = [0 for _ in range(len(data[0]))]
    for datum in data:
        for i in range(len(datum)):
            if datum[i] == None:
                nuns[i] += 1
    print(nuns)
    quit()

    # split the data
    training, test = split_data(data, labels, .9)
    x_train, y_train = training
    x_test, y_test = test

    # train the model
    model = get_model(x_train, y_train)

    # test the model
    test_model(model, x_test, y_test)

if __name__ == "__main__":
    main()
