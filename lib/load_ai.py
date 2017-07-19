""" Drew McArthur, 6/23/17
    load_ai.py

    contains methods used to generate an ordered list of horses in a race
        based on their predicted finishing.  
    call get_positions with the required arguments, and let the code do the rest
    need to slim data down using headers in config.yml

    TODO: format data correctly, similar to compile_data.py
            more efficient version of format data, 
            add more keys to keep in format data
"""

import joblib, csv, os
from ai.compare import ColWiseEncoder, format_pair
from lib.compile_data import get_race_info

class Horse:
    def __init__(self, horse, nn):
        self.horse = horse
        self.nn = nn
    def __lt__(self, other):
        return aWins(self.nn, self.horse, other.horse)

def remove_raceInfo(d):
    """ removes the columns relating race info from d """
    ID = d[0]
    name = d[4]
    newlist = d[30:]
    return [ID] + [name] + newlist

def remove_columns(d):
    """ removes a bunch of columns from the list """

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

    newdata = []
    for i in range(len(d)):
        if i not in todelete:
            newdata.append(d[i])
    return newdata

def makepair(a, b):
    """ given two horses, return them formatted for use with the nn """
    a.pop('L_Position', None)
    b.pop('L_Position', None)

    kA, ret = zip(*a.items())
    kB, items = zip(*b.items())

    items = remove_raceInfo(list(items))

    data = list(ret) + items

    return remove_columns(data)

def aWins(nn, horseA, horseB):
    """ returns true if the first horse would win, or false otherwise. """
    d = format_pair(horseA, horseB)
    return nn.predict([d]) == 1

def format_data(row):
    """ formats a row (dictionary) of data to our standards. """
    # list of desired keys
    keys = ['R_RCTrack', 'R_RCDate', 'B_Horse', 'L_Rank', 'L_Time', 'L_BSF', 
            'R_RCRace', 'B_MLOdds', 'B_ProgNum', 'P_Rank', 'P_Time', 'P_BSF']
    toRemove = []
    # remove all keys not in the list above
    for key, item in row.items():
        if key not in keys:
            toRemove.append(key)
    for key in toRemove:
        row.pop(key)
    return row

def load_horsedata(filename, n_race):
    """ given the path to a file containing horse data, and a specific race 
        read the file and return data on horses in the race. """
    with open(filename) as f:
        reader = csv.DictReader(f, dialect='unix')
        raceInfo = {}
        horses = []
        for horse in reader:
            # ensure that each row has all the information on the race
            if horse['R_RCRace'] == "":
                horse.update(raceInfo)
            else:
                raceInfo = get_race_info(horse)

            # if this horse is in the race we want, add it to the list
            if horse['R_RCRace'] == n_race:
                horses.append(horse)

            # once we get all of the horses, return the list
            if str(len(horses)) == horse['R_Starters']:
                return horses

def similar(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()
    
def add_labels(horses, labelpath):
    """ given a list of horses, and a base path to the two labels files, 
        return the list with labels for each horse added to the dictionary.
    """
    with open(labelpath + "_LT.CSV") as tLabel, \
         open(labelpath + "_LB.CSV") as bLabel:
        tReader = csv.DictReader(tLabel, dialect='unix')
        bReader = csv.DictReader(bLabel, dialect='unix')
        rank = 1
        for row in bReader:
            trow = next(tReader)
            for horse in horses:
                if similar(horse['B_Horse'], row['Horse']) > .4:
                    horse.update({"L_Rank": rank, 
                                  "L_Time": trow['Fin'],
                                  "L_BSF": row['Chart']
                                })
            rank += 1
    return horses

def get_list_data(horses):
    """ given a list of dictionaries, 
        return the same data, but formatted as lists """
    return [[i for k, i in horse.items()] for horse in horses]

def get_ai():
    """ returns the ai object used to predict horse's ranks """
    return (joblib.load("ai/models/ai_beyer_linear.pickle"), 
            joblib.load("ai/models/ai_time_linear.pickle"))

def formatTime(t):
    huns = (int(t) % 1000)
    secs = int(t) // 1000
    mins = int(secs) // 60
    secs = secs % 60

    return "{}:{}.{}".format(mins, secs, huns)

def nnrank(horses):
    """ adds P_Rank to each horse, which is its rank as predicted 
        by the bracket-style neural net. """
    Horses = []
    nn = joblib.load("ai/models/classifier.pickle")
    for horse in horses:
        Horses.append(Horse(horse, nn))
    
    Horses.sort()

    rank = 1
    for h in Horses:
        h.horse.update({'P_Rank':rank})
        rank += 1

    return [h.horse for h in Horses]

def get_positions(track, date, n_race):
    """ given identifying info on a race, (Track, Date, Number)
        return a list of horses in the predicted order of their finishing. """

    if isinstance(n_race, int):
        n_race = str(n_race)

    # separator, since filenames can be PRX170603.csv or WO_170603.csv
    sep = "" if len(track) == 3 else "_"

    # get pathnames
    datapath = "data/" + track + "/" + date + "/" + \
                    track + sep + date + "_SF.CSV"
    labelpath = "data/" + track + "/" + date + "/" + \
                    track + sep + date + "_" + n_race 

    # get the data on horses in the race
    horses = load_horsedata(datapath, n_race)

    # format it as a 2D list, (horses is a list of dictionaries)
    data = get_list_data(horses)

    # add a P_Rank value to each horse, which is 
    # its rank predicted by a classifying nn
    if os.path.isfile('ai/models/classifier.pickle'):
        horses = nnrank(horses)

    # load the ai and generate predicted heuristics of their performance
    beyer_ai, time_ai = get_ai()
    beyers = beyer_ai.predict(data)
    times = time_ai.predict(data)

    # add actual labels to horses
    horses = add_labels(horses, labelpath)


    toremove = []
    # update each horse with its heuristic, then sort to produce an ordered list
    for beyer, time, horse in zip(beyers, times, horses):
        if "L_Rank" not in horse:
            toremove.append(horse)
        else:
            horse.update({"P_BSF": beyer, "P_Time": formatTime(time)})

    for horse in toremove:
        horses.remove(horse)

    #horses.sort(key=lambda horse: horse['L_BSF'], reverse=True)
    horses.sort(key=lambda horse: horse['P_Time'])
    #horses.sort(key=lambda horse: horse['P_Rank'])

    return [format_data(horse) for horse in horses]

def main():
    """ Testing functions """
    horses = get_positions("PRX", "170528", 2)
    keys = ['B_Horse', 'L_Rank', 'L_Time', 'L_BSF', 'P_Rank', 'P_Time', 'P_BSF']
    for h in horses:
        for k in keys:
            if k not in h:
                h.update({k: '-'})
    print("               Actual                 Predicted")
    print("Name           Rank  Time      BSF    Rank       Time        BSF")
    [print("{:15}   {}  {:8}  {:3}    {}        {:8}    {:3.2f}"\
            .format(horse['B_Horse'], horse['L_Rank'], horse['L_Time'], 
                    horse['L_BSF'], horse['P_Rank'], horse['P_Time'], 
                    horse['P_BSF']))
        for horse in sorted(horses, key=lambda h: h['L_Rank'])]

if __name__ == "__main__":
    main()
