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

import joblib, csv
from lib.compile_data import get_race_info

def format_data(row):
    """ formats a row (dictionary) of data to our standards. """
    # list of desired keys
    keys = ['R_RCTrack', 'R_RCDate', 'B_Horse', 'L_Time', 'L_BSF', 'R_RCRace', 'B_MLOdds', 'B_ProgNum']
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

def get_list_data(horses):
    """ given a list of dictionaries, 
        return the same data, but formatted as lists """
    return [[i for k, i in horse.items()] for horse in horses]

def get_ai():
    """ returns the ai object used to predict horse's ranks """
    return (joblib.load("lib/ai_beyer.pickle"), 
            joblib.load("lib/ai_time.pickle"))

def get_positions(track, date, n_race):
    """ given identifying info on a race, (Track, Date, Number)
        return a list of horses in the predicted order of their finishing. """

    if isinstance(n_race, int):
        n_race = str(n_race)

    # separator, since filenames can be PRX170603.csv or WO_170603.csv
    sep = "" if len(track) == 3 else "_"
    # get pathname
    path = "data/" + track + "/" + date + "/" + track + sep + date + "_SF.CSV"

    # get the data on horses in the race
    horses = load_horsedata(path, n_race)

    # format it as a 2D list, (horses is a list of dictionaries)
    data = get_list_data(horses)

    # load the ai and generate predicted heuristics of their performance
    beyer_ai, time_ai = get_ai()
    beyers = beyer_ai.predict(data)
    times = time_ai.predict(data)

    # update each horse with its heuristic, then sort to produce an ordered list
    for beyer, time, horse in zip(beyers, times, horses):
        horse.update({"L_BSF": beyer, "L_Time": time})
    #horses.sort(key=lambda horse: horse['L_BSF'], reverse=True)
    horses.sort(key=lambda horse: horse['L_Time'])

    return [format_data(horse) for horse in horses]

def main():
    """ Testing functions """
    horses = get_positions("PRX", "170508", 2)
    [print(horse['B_Horse'],horse['L_Time'], horse['L_BSF']) for horse in horses]

if __name__ == "__main__":
    main()
