def get_raceInfo(horse):
    """ given a dictionary representing a horse, 
        return a sub-dictionary containing info only relevant to the race. """
    r = {}
    keys = ["R_RCTrack", "R_RCDate", "R_RCRace", "R_Starters", "R_TrackName", 
            "R_RaceState", "R_Division", "R_RaceBred", "R_StateBred", 
            "R_RaceSex", "R_RaceAge", "R_Class", "R_Purse", "R_HiClaim", 
            "R_LoClaim", "R_Distance", "R_Inner", "R_Surface", "R_RaceType", 
            "R_GradedRace", "R_GradedRaceDesc", "R_SimTrack", "R_SimRace", 
            "R_TrackRecord", "R_DayOfWeek", "R_PostTime", "R_LongClass", 
            "R_TrkAbbrev", "R_DistUnit", "R_TimeUnit", "R_Conditions"
           ]    
    # for each key listed above, add it and it's value in horse
    [r.update({key: horse[key]}) for key in keys]
    return r
    
def load_horsedata(filename, n_race):
    """ given the path to a file containing horse data, and a specific race 
        read the file and return data on horses in the race. """
    with open(filename) as f:
        reader = csv.DictReader(f, dialect='unix')
        raceInfo = {}
        for horse in reader:
            # if this horse is in the race we want, add it to the list
            if horse['R_RCRace'] == n_race:
                # ensure that each row has all the information on the race
                if getRaceInfo(horse) == {}:
                    horse.update(raceInfo)
                else:
                    raceInfo = getRaceInfo(horse)

                horses.append(horse)

            # once we get all of the horses, return the list
            if len(horses) == horse['R_Starters']:
                return horses

def get_list_data(horses):
    """ given a list of dictionaries, 
        return the same data, but formatted as lists """
    return [i for k, i in horse.items()] for horse in horses]

def get_ai():
    """ returns the ai object used to predict horse's ranks """
    return joblib.load("ai.pickle")

def get_positions(track, date, n_race):
    """ given identifying info on a race, (Track, Date, Number)
        return a list of horses in the predicted order of their finishing. """

    # separator, since filenames can be PRX170603.csv or WO_170603.csv
    sep = "" if len(track) == 3 else "_"
    # get pathname
    path = "data/" + track + "/" + date + "/" + track + sep + date + ".csv"

    # get the data on horses in the race
    horses = load_horsedata(path, n_race)
    # format it as a 2D list, (horses is a list of dictionaries)
    data = get_list_data(horses)

    # load the ai and generate predicted heuristics of their performance
    ai = get_ai()
    Ys = ai.predict(data)

    # update each horse with its heuristic, then sort to produce an ordered list
    for y, horse in zip(Ys, horses):
        horse.update({"heuristic": y})
    horses.sort(key=lambda horse: horse['heuristic'], reverse=True)

    return horses
