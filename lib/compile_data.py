"""
 *  Drew McArthur, Geo Engel, Risa Ulinski, Judy Zhou
 *  6/6/17
 *  a script to produce a single datafile from the race and horse information 
    located in the raw data folder (defined in config) for use with an AI
 *  this is done by first writing the data to a few files for organization, 
    categorizing information for the races, horses, and labels,
    to then be used to compile the final datafile.
 *  note: use python3
 *  TODO: read LB files not just lb files
"""

# yaml: for loading config file
#  sys: for args access and toggling of printing
#   os: for dealing with files in the os
#  csv: for reading and writing csv files
#   re: for regex parsing of filenames
import yaml, sys, os, csv, re

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
    beyerpath = folder + track + date + "_" + race + "_LB.CSV"
    timepath = folder + track + date + "_" + race + "_LT.CSV"

    if not os.path.isfile(beyerpath) or not os.path.isfile(timepath):
        if VVFLAG: 
            print("File Not Found: ", beyerpath)
        return

    # open files for reading and create respective csv.DictReader objects
    with open(timepath, newline='') as timefile,\
         open(beyerpath, newline='') as beyerfile:
        beyerreader = csv.DictReader(beyerfile, dialect='unix')
        timereader = csv.DictReader(timefile, dialect='unix')

        # add the data in the beyer label file to the list, 
        # and simultaneously add ID and rank info for the race to the row
        rank = 1
        for b in beyerreader:
            # TODO figure out why this shit isn't working
            if ord(b['Horse'][0]) > 127:
                print("AHH THE dreaded QUESTION MARK")
                t = next(timereader)
                continue

            # add race ID and horse's rank to entry
            entry = raceIDInfo.copy()
            entry.update({"L_Position": rank, 
                          "B_Horse": b["Horse"],          
                          "L_BSF": b["Chart"]
                         })

            entry = fixLabelName(entry)

            # read one line from timereader and add time to entry
            try:
                t = next(timereader)
            except StopIteration:
                t = None
                entry = None

            if entry is None:
                print("Timefile ended early. ", timepath)
            elif (t['Horse'] != b['Horse'] or not entry['B_Horse']):
                print("Error! reading entries from two label files and ")
                print("       the horse names don't match! You screwed up!")
                print("Race: " + str(raceIDInfo))
                print("beyer's horse: " + b['Horse'])
                print("time's horse: " + t['Horse'])
                entry = None
            else:
                entry.update({"L_Time": t["Fin"]})
                entry = formatData(entry)

            # add entry to list and update rank
            if entry is not None:
                labeldata.append(entry)
                rank += 1

    # write the entries in labeldata to file
    for entry in labeldata:
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
                        if f.endswith('LT.CSV'):
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

def fixDate(row):
    """ given a date d, return the same date in YYMMDD format. """
    if row is None:
        return row

    d = row['R_RCDate']

    # if there are no slashes, we assume the date is already formatted.
    if "/" in d:
        m = re.match("([0-9]*)/([0-9]*)/([0-9]*)", d)
        MM = m.group(1)
        DD = m.group(2)
        YYYY = m.group(3)

        r = YYYY[-2:] + MM + DD

        row['R_RCDate'] = r
    return row

def fixOdds(row):
    """ given the odds in the format "A-B", return a float equal to A/B. """

    if 'B_MLOdds' not in row:
        return row
    if not isinstance(row['B_MLOdds'], str) or row['B_MLOdds'] == "":
        return row

    o = row['B_MLOdds']
    a, b = [float(f) for f in o.split('-')]
    row['B_MLOdds'] = a / b

    return row

def fixTime(row):
    """ given a row, fix the time in the row """
    if row is None:
        return row

    t = row['L_Time']

    if t == '' or t is None:
        if VVFLAG:
            print("Bad Time: ", row)
        return None
    elif ":" in t:
        m = re.match("([0-9]*):([0-9]*).([0-9]*)", t)
        mins = int(m.group(1)) if m.group(1) != "" else 0
        secs = int(m.group(2))
        ms = int(m.group(3)) * 10

        secs += mins * 60
        ms += secs * 1000

        row['L_Time'] = ms
    # if t != 0 or None, but there are no colons, it's a single number 
    #   representing minutes. so, we multiply by 60000 min/ms
    elif t:
        row['L_Time'] = int(t) * 60000
    return row

def fixLabelName(row):
    """ remove non-unicode and extra characters from names that were converted
        incorrectly from pdf """
    if row is None:
        return row

    if isinstance(row, str):
        row = {'B_Horse': row}

    n = row['B_Horse']
    if len(n) > 30:
        if VVFLAG:
            print("Bad Name: ", row)
        return None
    if '-' in n:
        n = n[:n.index("-")]
    if '?' in n:
        n = n.replace('?', '')
    for c in n:
        if ord(c) > 127:
            n = n.replace(c, "")
    row['B_Horse'] = n
    return row

def checkBSF(row):
    """ returns None if a label is bad (i.e. 0 or None or "") """
    if row is None or 'L_BSF' not in row:
        return row

    # double check rowfor missing data before writing
    if (row['L_BSF'] == "-" or
        row['L_BSF'] == "-0" or
        row['L_BSF'] == "" or
        row['L_BSF'] == None ):
        if VVFLAG: 
            print("Bad Beyer Figure: ", row)
        return None

    return row

def formatData(row):
    """ function which returns a row that is formatted nicely for the AI"""
    row = fixDate(row)
    if "L_Time" in row:
        row = fixTime(row)
        row = fixLabelName(row)
        row = checkBSF(row)
    else:
        row = fixOdds(row)
    return row

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
                    horse = formatData(horse)
                    if horse is not None:
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
                    closestRow[0].update({"ID":label["ID"]})
                    horse = formatData(closestRow[0])
                    if horse is not None:
                        inputWriter.writerow(horse)

            numPlaces += 1
            print("Fetched data for {0:.2f}% of labels."
                        .format(numPlaces / (NDATA/100)), end="\r")
        # print newline after last update with carriage return
        print()

if __name__ == "__main__":
    # right way to access config vars
    # config['raw_data_path']

    if "lib" not in os.listdir("."):
        print("This script must run from the main directory, try again.")
        quit()

    config = yaml.safe_load(open("config.yml"))

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

    if "--skip-labels" not in sys.argv:
        create_labels()

    print("Scraping",DATA,"for training data ...")

    get_input_data(ENDFILENAME, LABELFILENAME)
