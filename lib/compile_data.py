"""
 *  Drew McArthur, Geo Engel, Risa Ulinski, Judy Zhou
 *  6/6/17
 *  a script to produce a single datafile from the race and horse information 
    located in the raw data folder (defined in config) for use with an AI
 *  this is done by first writing the data to a few files for organization, 
    categorizing information for the races, horses, and labels,
    to then be used to compile the final datafile.
 *  note: use python3
 *  TODO: read data from *{lt, lb}.csv files, write to LABELS.data.csv
          create LABELWRITER object and appropriate associated files
          sort data before writing to middle files
            write sorting algorithm for a list of dictionaries that sorts by
                certain keys
            this way, reading from the middle files to merge them is easier
"""

# yaml: for loading config file
#  sys: for args access and toggling of printing
#   os: for dealing with files in the os
#  csv: for reading and writing csv files
#   re: for regex parsing of filenames
import yaml, sys, os, csv, re
config = yaml.safe_load(open("config.yml"))

# right way to access config vars
# config['raw_data_path']

def writeLabelInfo(f, folder, LABELWRITER):
    """ Scrapes data from file f in folder, and writes the data to 
        a labels file, using the object LABELWRITER """

    global NDATA

    # list of dictionaries, each dict is a data entry to be written to LABELS
    labeldata = []

    # parse track and date from filename
    m = re.match("([a-zA-Z]{2,3})([0-9]{6})_([0-9]{1,2}).*", f)
    track = m.group(1)
    date = m.group(2)
    race = m.group(3)

    if VVFLAG:
        print("         ", f)

    raceIDInfo = {"R_RCTrack": track, "R_RCDate": date, "R_RCRace": race}

    # generate pathnames for the desired files
    beyerpath = folder + track + date + "_" + race + "_lb.csv"
    timepath = folder + track + date + "_" + race + "_lt.csv"

    # open files for reading and create respective csv.DictReader objects
    with open(beyerpath, newline='') as beyerfile, \
         open(timepath, newline='') as timefile:
        beyerreader = csv.DictReader(beyerfile, dialect='unix')
        timereader = csv.DictReader(timefile, dialect='unix')

        # add the data in the beyer label file to the list, 
        # and simultaneously add ID and rank info for the race to the row
        rank = 1
        for b in beyerreader:
            # add race ID and horse's rank to entry
            entry = raceIDInfo.copy()
            entry.update({"L_Position": rank, 
                          "B_Horse": b["Horse"],          
                          "L_BSF": b["Chart"]
                         })

            # read one line from timereader and add time to entry
            t = next(timereader)
            if t['Horse'] != entry['B_Horse'] or not entry['B_Horse']:
                print("Error! reading entries from two label files and ")
                print("       the horse names don't match! You screwed up!")
                print("Race: " + str(raceIDInfo))
                print("time's horse: " + t['Horse'])
                print("beyer's horse: " + entry['Horse'])

            entry.update({"L_Time": t["Fin"]})

            # add entry to list and update rank
            labeldata.append(entry)
            rank += 1

    # sort the data by horse name (track, race #, date are all identical)
    labeldata.sort(key=lambda x: (x["B_Horse"]))

    # write the entries in labeldata to file
    for entry in labeldata:
        # make sure the name isn't actually a comment on the race conditions
        if (len(entry['B_Horse']) < 30 and 
            entry['L_BSF'] != "-"):
            entry.update({"ID": NDATA})
            LABELWRITER.writerow(entry)
            NDATA += 1
            if NDATA >= MAXFLAG:
                return

def create_labels():
    """ iterate through files in DATA directory and create 
        {RACES, HORSES, LABELS}.data.csv """
    # open the files for writing
    LABELFILE = open(LABELFILENAME, 'w')

    # create an object which writes data to files as a csv, using column headers
    # from config.yml and ignoring extra data
    LABELWRITER = csv.DictWriter(LABELFILE, fieldnames=labelHeaders, 
                                   extrasaction='ignore', dialect='unix')

    # write the header columns to the file.
    LABELWRITER.writeheader()

    numPlaces = 0

    # iterate through files in data directory, PLACE/DATE/Files
    if VVFLAG:
        print(DATA)
    for place in os.listdir(DATA):
        if os.path.isdir(DATA + '/' + place):
            if VVFLAG:
                print(" ", place)
            for date in os.listdir(DATA + '/' + place):
                folder = DATA + '/' + place + "/" + date + "/"
                if os.path.isdir(folder):
                    if VVFLAG:
                        print("     ",date)
                    for f in os.listdir(folder):
                        # if the file contains label information, write to file
                        # only looking for one of two label files, to avoid dups
                        # the other filename is generated in the function below.
                        if f.endswith('lt.csv'):
                            writeLabelInfo(f, folder, LABELWRITER)
                            if NDATA >= MAXFLAG:
                                return
                        # notification for verbosity
                        elif VVFLAG:
                            print("Skipping file - unnecessary type:", f)
            numPlaces += 1
            print("Done with", numPlaces, "track folders of data.", end="\r")
    print()

def get_data_fn(label):
    """ given a label (dict), return the path to the file that would hold
        the right input data. """

    track = label['R_RCTrack']
    date = label['R_RCDate']
    race = label['R_RCRace']

    separator = "" if len(track) == 3 else "_"

    return DATA+"/"+track+"/"+date+"/"+track+separator+date+"_SF.CSV"

def get_race_info(row):
    """ returns a dictionary, given a row, of all the race-specific information.
        this is used to copy race info from the first row of a race to the next
        """
    r = {}
    keys = ["R_RCTrack", "R_RCDate", "R_RCRace","R_Starters","R_TrackName",
            "R_RaceState","R_Division","R_RaceBred","R_StateBred","R_RaceSex",
            "R_RaceAge","R_Class","R_Purse","R_HiClaim","R_LoClaim",
            "R_Distance","R_Inner","R_Surface","R_RaceType","R_GradedRace",
            "R_GradedRaceDesc","R_SimTrack","R_SimRace","R_TrackRecord",
            "R_DayOfWeek","R_PostTime","R_LongClass","R_TrkAbbrev","R_DistUnit",
            "R_TimeUnit","R_Conditions"
           ]
    for key in keys:
        r.update({key: row[key]})
    return r

def generate_racelist(reader):
    """ given a csv reader, return a list of races, where a race in the list
        consists of each row associated with that race.
        races[i] == race #(i+1) in this file. """
    races = []
    raceInfo = {}

    for row in reader:
        # first, we add race info to each row where its missing
        if row["R_RCTrack"] == "":
            row.update(raceInfo)
        # or update the info for the current row's race
        else:
            raceInfo = get_race_info(row)

        # race number for the current row
        raceN = int(row["R_RCRace"])

        # if we're at race N, but races only has info on N - 1 races, 
        if len(races) < raceN:
            # then append a new list, containing this row
            races.append([row])
        else:
            # otherwise, just add this row to the existing sublist
            races[raceN - 1].append(row)

    return races

def get_input_data(INPUTFN, LABELFN):
    """ reads the labels file, and uses the information there to find
        input data and write it to file """

    # open the relevant files and CSV objects
    with open(LABELFN) as LABELFILE, open(INPUTFN, 'w') as INPUTFILE:
        labelReader = csv.DictReader(LABELFILE, dialect='unix')
        inputWriter = csv.DictWriter(INPUTFILE, fieldnames=inputHeaders, 
                                     extrasaction='ignore', dialect='unix')

        # write the headers to data.csv
        inputWriter.writeheader()

        # the current datafilename we're scraping, and the object itself
        currfn = ""
        datafile = None

        # used for copying race info to rows missing this data
        raceInfo = {}

        numPlaces = 0

        # iterate through each label
        for label in labelReader:
            labelWritten = False

            # if we aren't looking at the right file, fix that
            if currfn != get_data_fn(label):
                currfn = get_data_fn(label)
                if os.path.isfile(currfn):
                    data = open(currfn)
                    datafile = csv.DictReader(data, dialect='unix')
                else:
                    print("Error! .SF file not found for", currfn)
                # get a list of races, where each race is a list of horses' data
                races = generate_racelist(datafile)

            # iterate through each horse in this race to find the data
            for horse in races[int(label['R_RCRace']) - 1]:
                # when we reach the right entry, we write it to file
                if label['B_Horse'] == horse['B_Horse']:
                    horse.update({"ID":label["ID"]})
                    inputWriter.writerow(horse)
                    labelWritten = True

            # if we never found the right data for the label
            if not labelWritten:
                if VVFLAG:
                    print("Error! input info for this label wasn't written!")
                    print(label)
                    print("we thought it'd be in this file:", currfn)
                    print("attempting to find the closest match...")
                    print()

                # make a list of all of the horse names in the race and how 
                # similar to the label they are
                names = []
                potNames = []
                
                # go through each row to find the ones with a matching race
                for horse in races[int(label['R_RCRace']) - 1]:
                    potNames.append(horse['B_Horse'])
                    
                    # create a ratio of the number of letters from the original name
                    # that are in the label name and put them into a list
                    lettersInCommon = 0
                    for letter in horse['B_Horse']:
                        if letter in label['B_Horse']:
                            lettersInCommon += 1
                    ratio = lettersInCommon / len(horse['B_Horse'])
                    names.append((horse, ratio))
               
                # find the row with the largest ratio of common letters
                closestRow = max(names, key=lambda x:x[1], default=0)

                # if the closest row exists and passes the threshold, 
                if closestRow != 0 and closestRow[1] > .7:
                    # write the closestRow to the file, 
                    inputWriter.writerow(closestRow[0])

            numPlaces += 1
            print("Fetched data for roughly {0:.2f}% of labels."
                        .format(numPlaces / 270), end="\r")
        # print newline after last update with carriage return
        print()

if __name__ == "__main__":
    # get root folder and pathname and file objects for the final product.
    DATA = config['raw_data_path']

    # allow levels of verbosity 
    VVFLAG = "-v" in sys.argv

    # allow -k n to choose number of rows of data to gather
    NDATA = 0
    MAXFLAG = int(config['nData'] if "-k" not in sys.argv else 
                  sys.argv[sys.argv.index("-k") + 1])

    # create filenames
    ENDFILENAME = config['final_data_filename']
    LABELFILENAME = "LABELS." + ENDFILENAME

    # get a list of label headers for various files
    labelHeaders = config['label_data_col_headers'].split(', ')
    labelHeaders[-1] = labelHeaders[-1][:-1]

    inputHeaders = config['input_data_col_headers'].split(', ')
    inputHeaders[-1] = inputHeaders[-1][:-1]

    # okay, go!
    print("Creating", LABELFILENAME, "...")

    create_labels()

    print("Scraping",DATA,"for training data ...")

    get_input_data(ENDFILENAME, LABELFILENAME)
