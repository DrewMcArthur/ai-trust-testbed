""" Drew McArthur
    6/28/17
    First attempt at using a neural net to compare two horses and 
        choose the one that will finish first
"""

from learn import split_data
from itertools import permutations
from collections import OrderedDict
from joblib import dump, load
from sklearn.metrics import accuracy_score, explained_variance_score, r2_score
from sklearn.preprocessing import (LabelEncoder, OneHotEncoder, Imputer, MinMaxScaler) 
from sklearn.feature_extraction import FeatureHasher
from sklearn.feature_selection import SelectKBest
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.base import TransformerMixin
import yaml, os, csv, pickle, bisect
import numpy as np

class ColWiseEncoder(TransformerMixin):
    def __init__(self):
        pass

    def isContinuous(self, col):
        """ return true if the column represents continuous data """
        for _ in range(50):
            try:
                float(random.choice(col))
            except:
                return False
        return True

    def fit(self, Xs, Ys=None):
        # convert the list of dicts to a list of lists
        listXs = [[item for key, item in row.items()] for row in Xs]
        # convert 2d list to 2d numpy array
        nArray = np.array(listXs)
        # create a list of labelencoders, one for each column
        self.mapper= []
        # for each column, fit a labelencoder to that column
        for i in range(len(Xs[0])):
            self.mapper.append(LabelEncoder())
            col = nArray[:,i]
            self.mapper[i].fit(col)
            le_classes = self.mapper[i].classes_.tolist()
            bisect.insort_left(le_classes, 'other')
            self.mapper[i].classes_ = le_classes

    def transform(self, Xs, Ys=None):
        # convert the list of dicts to a list of lists
        listXs = [[item for key, item in row.items()] for row in Xs]
        nArray = np.array(listXs)
        for i in range(len(Xs[0])):
            col = nArray[:,i]
            col = map(lambda s: 'other' if s not in self.mapper[i].classes_ 
                                            else s, col.tolist())
            le_classes = self.mapper[i].classes_.tolist()
            bisect.insort_left(le_classes, 'other')
            self.mapper[i].classes_ = le_classes
            nArray[:,i] = self.mapper[i].transform(col)
        return nArray
        
    def fit_transform(self, Xs, Ys=None):
        """ applies labelencoder to each column, if the column is determined
            to be continuous variables """
        # convert the list of dicts to a list of lists
        listXs = [[item for key, item in row.items()] for row in Xs]
        # convert 2d list to 2d numpy array
        nArray = np.array(listXs)
        # create a list of labelencoders, one for each column
        self.mapper= []
        # get first row, which is all headers
        headers = nArray[0]

        # for each column, fit and transform using its respective labelencoder
        for i in range(len(headers)):
            col = nArray[:,i]
            if self.isContinuous(col):
                self.mapper.append(False)
            else:
                self.mapper.append(LabelEncoder())
                nArray[:,i] = self.mapper[i].fit_transform(col)

        return nArray

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
    if 'L_Position' not in horseA:
        return -1
    if 'L_Position' not in horseB:
        return -1
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
    [l.pop(k, None) for k in ["R_RCTrack","R_RCDate","R_RCRace","R_Starters",
                        "R_TrackName","R_RaceState","R_Division","R_RaceBred",
                        "R_StateBred","R_RaceSex","R_RaceAge","R_Class",
                        "R_Purse","R_HiClaim","R_LoClaim","R_Distance",
                        "R_Inner","R_Surface","R_RaceType","R_GradedRace",
                        "R_GradedRaceDesc","R_SimTrack","R_TrackRecord",
                        "R_DayOfWeek","R_PostTime","R_LongClass","R_TrkAbbrev",
                        "R_DistUnit","R_TimeUnit"]]
    return l

def format_pair(pair):
    """ given a tuple of two horses (dictionaries), return a single list
        containing all the information. """
    # split the tuple and remove labels.
    A, B = pair
    A.pop('L_Position', None)
    B.pop('L_Position', None)

    # remove duplicate information from the beginning of the list
    B = remove_raceInfo(B)

    # merge dictionaries
    final = OrderedDict()
    for key, item in A.items():
        final.update({"A_" + key: item})
    for key, item in B.items():
        final.update({"B_" + key: item})

    # return the merged dict
    return final

def isint(x):
    """ returns true if x is probably an int hidden in a string """
    try:
        int(x)
        return True
    except:
        return False

def format_data(horse):
    for key, item in horse.items():
        if item == '':
            horse.update({key: None})
        elif isint(item):
            horse.update({key: int(item)})
    return horse

def get_model(Xs, Ys):
    """ given the input and output data, return a trained AI model
        that classifies winners of horse races. 
        each row consists of information on two horses
    """

    # create necessary sklearn objects
    cwe = ColWiseEncoder()
    fh = FeatureHasher()
    enc = OneHotEncoder()
    imp = Imputer(missing_values='', strategy='mean', axis=0)
    scaler = MinMaxScaler()
    nn = MLPClassifier()
    kBest = SelectKBest(k=3500)

    # construct a pipe from previous objects
    model = make_pipeline(cwe, enc, kBest, nn)
    
    # train the model
    model.fit(Xs, Ys)

    return model

def test_model(model, x_test, y_test):
    """ given a model and test values, predict the Ys and print out a report
        of accuracy.
    """
    f = open("nn.pickle", 'w')
    pickle.dump(model, f)

    # get accuracy and predictions
    y_pred = model.predict(x_test)

    print("results for classifying winners")
    print("accuracy: ", accuracy_score(y_test, y_pred))
    print("variance: ", explained_variance_score(y_test, y_pred))
    print("r square: ", r2_score(y_test, y_pred))

def write_compiled(headers, data, labels):
    """ given a dictionary and a list, write each to file.
        dictionary -> csv, list to file in rows. """
    f = open("compiled_labels.txt", 'w')
    for l in labels:
        f.write(str(l) + "\n")
    w = csv.DictWriter(open("compiled_data.csv", 'w'), dialect='unix', 
                       fieldnames=headers, extrasaction='ignore')
    w.writeheader()
    for d in data:
        w.writerow(d)

def load_compiled():
    """ read formatted data from file.  UNTESTED"""
    f = open("compiled_labels.txt")
    labels = []
    for line in f:
        labels.append(int(line))

    data = []
    r = csv.DictReader(open("compiled_data.csv"), dialect='unix')
    for row in r:
        data.append(row)

    return (data, labels)

def generate_datadump(toFile=False):
    """ loads data from file, formats it, and if toFile is set to true, 
        dumps the data itself to file.  The data is then returned. """
    print("  Generating data...")
    # read the data and labels from file
    config = yaml.safe_load(open("./config.yml"))
    races = read_data("nn" + config['final_data_filename'])
    races = read_output("LABELS." + config['final_data_filename'], races)

    print("x Read data from file.")

    # races now equals a dictionary, where each item is a race, 
    #       with key equal to the race's ID (given by get_raceID).  
    # a race is a list of horses that participated in that race
    # a horse is a dictionary containing all related information

    data = []
    labels = []
    print("length of pairs, labels, and data twice. what are the differences?")
    totalpairs = 0
    for ID, race in races.items():
        pairs = generate_pairs(race)
        totalpairs += len(pairs)
        for pair in pairs:
            labels.append(get_comparison(pair))
        for pair in pairs:
            data.append(format_pair(pair))

    print(len(data))
    data = [format_data(d) for d in data]
    print(len(data))
    
    print("x Formatted Data.")

    # columns indices that will be removed, based on relevance to output
    todelete = [0, 1, 2, 3, 4, 6, 7, 13, 26, 28, 29, 34, 38, 
                1053, 2288, 173, 174, 175, 176, 177, 1408, 1409, 1410, 1411, 1412, 512, 1747, 1143, 2378, 602, 1837, 1233, 2468, 692, 1927, 782, 2017, 872, 2107, 962, 
                2197, 1052, 2287, 1142, 2377, 244, 1479, 51, 1286, 1232, 2467, 334, 1569, 424, 1659, 514, 1749, 604, 1839, 694, 1929, 784, 2019, 288, 1523, 468, 1703, 
                198, 1433, 378, 1613, 558, 1793, 874, 2109, 10, 964, 2199, 648, 1883, 738, 1973, 828, 2063, 1054, 2289, 918, 2153, 152, 1387, 1144, 2379, 1008, 2243, 
                1098, 2333, 178, 179, 180, 181, 182, 1413, 1414, 1415, 1416, 1417, 1234, 2469, 1188, 2423, 261, 1496, 352, 353, 354, 355, 356, 357, 1587, 1588, 1589, 
                1590, 1591, 1592, 351, 1586, 531, 1766, 441, 1676, 621, 1856, 711, 1946, 442, 443, 444, 445, 446, 447, 1677, 1678, 1679, 1680, 1681, 1682, 22, 801, 
                2036, 532, 533, 534, 535, 536, 537, 1767, 1768, 1769, 1770, 1771, 1772, 622, 623, 624, 625, 626, 627, 1857, 1858, 1859, 1860, 1861, 1862, 712, 713, 714, 
                715, 716, 717, 1947, 1948, 1949, 1950, 1951, 1952, 891, 2126, 802, 803, 804, 805, 806, 807, 2037, 2038, 2039, 2040, 2041, 2042, 981, 2216, 892, 893, 894, 
                895, 896, 897, 2127, 2128, 2129, 2130, 2131, 2132, 1071, 2306, 1161, 2396, 982, 983, 984, 985, 986, 987, 2217, 2218, 2219, 2220, 2221, 2222, 1072, 1073, 
                1074, 1075, 1076, 1077, 2307, 2308, 2309, 2310, 2311, 2312, 1251, 2486, 240, 251, 255, 1475, 1486, 1490, 1162, 1163, 1164, 1165, 1166, 1167, 2397, 2398, 
                2399, 2400, 2401, 2402, 420, 431, 435, 1655, 1666, 1670, 330, 341, 345, 1565, 1576, 1580, 369, 1604, 57, 1292, 459, 1694, 1252, 1253, 1254, 1255, 1256, 1257, 
                2487, 2488, 2489, 2490, 2491, 2492, 600, 611, 615, 1835, 1846, 1850, 525, 1760, 510, 521, 1745, 1756, 549, 1784, 279, 1514, 690, 701, 705, 1925, 1936, 1940, 
                870, 881, 885, 2105, 2116, 2120, 780, 791, 795, 2015, 2026, 2030, 639, 1874, 960, 971, 975, 2195, 2206, 2210, 729, 1964, 1050, 1061, 1065, 2285, 2296, 
                2300, 1230, 1241, 1245, 2465, 2476, 2480, 909, 2144, 819, 2054, 1155, 2390, 1140, 1151, 2375, 2386, 103, 1338, 1179, 2414, 1089, 2324, 189, 1424, 247, 1482, 
                337, 1572, 517, 1752, 427, 1662, 787, 2022, 607, 1842, 697, 1932, 18, 1057, 2292, 877, 2112, 967, 2202, 1237, 2472, 1147, 2382, 680, 771, 1915, 2006, 861, 
                2096, 591, 1826, 590, 1825, 501, 1736, 35, 1270, 951, 2186, 770, 2005, 681, 1916, 500, 1735, 860, 2095, 1041, 2276, 411, 1646, 950, 2185, 1040, 2275, 1130, 
                2365, 1131, 2366, 321, 1556, 1220, 2455, 1221, 2456, 410, 1645, 320, 1555, 728, 1963, 755, 1990, 638, 1873, 818, 2053, 687, 1922, 777, 2012, 845, 2080, 665, 
                1900, 867, 2102, 908, 2143, 548, 1783, 231, 1466, 597, 1832, 935, 2170, 575, 1810, 998, 2233, 1088, 2323, 1025, 2260, 1178, 2413, 458, 1693, 957, 2192, 1047, 
                2282, 1115, 2350, 612, 1847, 507, 1742, 1205, 2440, 1137, 2372, 485, 1720, 702, 1937, 792, 2027, 522, 1757, 1227, 2462, 1152, 2387, 1242, 2477, 1062, 2297, 
                972, 2207, 417, 1652, 882, 2117, 368, 1603, 230, 1465, 432, 1667, 395, 1630, 342, 1577, 327, 1562, 278, 1513, 305, 1540, 610, 1845, 520, 1755, 430, 1665, 
                700, 1935, 790, 2025, 1060, 2295, 970, 2205, 1150, 2385, 250, 1485, 252, 1487, 1240, 2475, 340, 1575, 880, 2115, 237, 1472, 188, 1423, 215, 1450, 128, 129, 
                1363, 1364, 8, 9, 20, 23, 29, 55, 143, 147, 168, 183, 262, 263, 264, 265, 266, 267, 273, 363, 453, 543, 633, 723, 813, 903, 993, 995, 999, 1003, 1007, 1083, 
                1173, 1290, 1378, 1382, 1403, 1418, 1497, 1498, 1499, 1500, 1501, 1502, 1508, 1598, 1688, 1778, 1868, 1958, 2048, 2138, 2228, 2230, 2234, 2238, 2242, 2318, 2408]

#   a = np.array(data)
#   np.delete(a, todelete)

#   data = a.tolist()
    keys = list(data[0].keys())
    headers = []
    for i in range(len(keys)):
        if i not in todelete:
            headers.append(keys[i])
        
    print(len(data))

    print("x Deleted extraneous columns.")

    if toFile:
        write_compiled(headers, data, labels)
        #dump((data, labels), 'classifier_data.pickle')
    return (data, labels)

def main():
    print("  Beginning nn script.")

    # load the data from file if it exists, or re-generate it. 
    if not os.path.isfile('compiled_data.csv') or os.stat('compiled_data.csv').st_size < 10:
        generate_datadump(True)
    data, labels = load_compiled()

    print("x Loaded data. ")

    # split the data
    splitData = split_data(data, labels, .9)
    training, test = splitData
    x_train, y_train = training
    x_test, y_test = test

    print("x Split the data.")

    # train the model
    model = get_model(x_train, y_train)
    print("x Trained the model.")

    # test the model
    test_model(model, x_test, y_test)
    print("x Tested the model.")

if __name__ == "__main__":
    main()
