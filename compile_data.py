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

# future mode for verbosity toggling
VERBOSEMODE = True

# allow/disallow printing.  errors must turn on printing
def allowPrinting():
    sys.stdout = sys.__stdout__   
def blockPrinting():
    sys.stdout = open(os.devnull, 'w')

def getNextRow(csvreader):
    """ given a csv reader, gets the next row available, 
        returns empty dictionary/list if at EOF """
    try:
        return next(csvreader)
    except StopIteration:
        return {} if type(csvreader) == csv.DictWriter else []

def rowEmpty(row, headers):
    """ given a row (dictionary of headers:vals), and a list of headers, 
        check if the row contains any data in the columns specified. """
    for col in headers:
        if row[col] != '':
            return False
    return True

def combineList(a, *b):
    """ given a number of lists, output a the combination without duplicates.
        [1, 3, 5] + [1, 2, 3] => [1, 2, 3, 5]                               """
    c = a[:]
    for l in b:
        for x in l:
            if x not in c:
                c.append(x)
    return c

def writePreRaceInfo(f, folder, RACEWRITER, HORSEWRITER):
    """ given a *_sf.csv file, write the respective information 
        to {RACES, HORSES}.data.csv files                       """
    # open the file and create a csv reader
    path = folder + "/" + f
    print("         ", f)

    # lists of entries to write to file
    races = []
    horses = []

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, dialect='unix')
        raceIDInfo = {}
        # iterate through the data in the file we're reading,
        for row in reader:
            # and write that data to its respective files
            if not rowEmpty(row, raceHeaders):
                races.append(row)

            # if, in the file we're reading, the race information is empty,
            # then use whatever info we used last.
            if row["R_RCTrack"] == "":
                row["R_RCTrack"] = raceIDInfo["R_RCTrack"]
                row["R_RCDate"] = raceIDInfo["R_RCDate"]
                row["R_RCRace"] = raceIDInfo["R_RCRace"]

            # otherwise, update the race info we have to match what was read.
            else:
                raceIDInfo["R_RCTrack"] = row["R_RCTrack"]
                raceIDInfo["R_RCDate"] = row["R_RCDate"]
                raceIDInfo["R_RCRace"] = row["R_RCRace"]

            # note: rowEmpty checks if, given the column headers, at least
            #       one of the keys has a value in the dictionary given (row).
            if not rowEmpty(row, horseHeaders):
                horses.append(row)

    # sort the data by race number, then horse name. Track and date are ignored
    # because they should be identical for the data in one file
    races.sort(key=lambda x: (x["R_RCRace"], x["B_Horse"]))
    horses.sort(key=lambda x: (x["R_RCRace"], x["B_Horse"]))
    
    # finally, write the data to the middle files
    for race in races:
        RACEWRITER.writerow(race)
    for horse in horses:
        HORSEWRITER.writerow(horse)

def writeLabelInfo(f, folder, LABELWRITER):
    """ Scrapes data from file f in folder, and writes the data to 
        a labels file, using the object LABELWRITER """

    print('writing from',folder + "/" + f, 'to labelwriter')
    print("         ", f)

    raceIDInfo = {"R_RCTrack": track, "R_RCDate": date, "R_RCRace": race}
    print("dealing with this race: ")
    print(raceIDInfo)

    # list of dictionaries, each dict is a data entry to be written to LABELS
    labeldata = []

    # parse track and date from filename
    m = re.match("([a-zA-Z]{2,3})([0-9]{6})_([0-9]).*", f)
    track = m.group(1)
    date = m.group(2)
    race = m.group(3)

    # generate pathnames for the desired files
    beyerpath = folder + "/" + track + date + "_" + race + "_lb.csv"
    timepath = folder + "/" + track + date + "_" + race + "_lt.csv"

    # open files for reading and create respective csv.DictReader objects
    with open(beyerpath, newline='') as beyerfile, \
         open(timepath, newline='') as timefile:
        beyerreader = csv.DictReader(beyerfile, dialect='unix')
        timereader = csv.DictReader(timefile, dialect='unix')

        # add the data in the beyer label file to the list, 
        # and simultaneously add ID and rank info for the race to the row
        rank = 1
        for entry in beyerreader:
            # add race ID and horse's rank to entry
            entry.update(raceIDInfo)
            entry.update({"rank": rank})

            # read one line from timereader and add time to entry
            row = next(timereader)
            if row['Horse'] != entry['Horse']:
                allowPrinting()
                print("Error! reading entries from two label files and ")
                print("       the horse names don't match! You screwed up!")
                print("Race: " + str(raceIDInfo))
                print("time's horse: " + row['Horse'])
                print("beyer's horse: " + entry['Horse'])
                blockPrinting()
            entry.update(row)

            # add entry to list and update rank
            labeldata.append(entry)
            rank += 1

            # instead of adding to list, if it's right then just write to file 
            # LABELWRITER.writerow(entry)

        print("is this label data right???")
        print(labeldata)

        # TODO: write to LABELS.data.csv
        #       create LABELWRITER and correct file to pass to this function
        quit()

    labeldata.sort(key=lambda x: (x["R_RCRace"], x["B_Horse"]))

    # write the entries in labeldata to file
    for entry in labeldata:
        LABELWRITER.writerow(entry)

def create_middle_files():
    """ iterate through files in DATA directory and create 
        {RACES, HORSES, LABELS}.data.csv """
    # open the files for writing
    ENDFILE = open(ENDFILENAME, 'w')
    HORSEFILE = open(HORSEFILENAME, 'w')
    RACEFILE = open(RACEFILENAME, 'w+')
    LABELFILE = open(LABELFILENAME, 'w')

    # create an object which writes data to files as a csv, using column headers
    # from config.yml and ignoring extra data
    RACEWRITER = csv.DictWriter(RACEFILE, fieldnames=raceHeaders, 
                                   extrasaction='ignore', dialect='unix')
    HORSEWRITER = csv.DictWriter(HORSEFILE, fieldnames=horseHeaders, 
                                   extrasaction='ignore', dialect='unix')
    LABELWRITER = csv.DictWriter(LABELFILE, fieldnames=labelHeaders, 
                                   extrasaction='ignore', dialect='unix')


    # if ENDFILE is empty, then write the header columns to the file.
    if os.stat(RACEFILENAME).st_size == 0:
        RACEWRITER.writeheader()
    if os.stat(HORSEFILENAME).st_size == 0:
        HORSEWRITER.writeheader()

    # iterate through files in data directory
    print(DATA)
    for place in os.listdir(DATA):
        if os.path.isdir(DATA + place):
            print(" ", place)
            for date in os.listdir(DATA + place):
                # note: DATA includes a trailing "/" but most dirs don't.
                folder = DATA + place + "/" + date
                if os.path.isdir(folder):
                    print("     ",date)
                    for f in os.listdir(folder):
                        # if file is single file export of race info
                        if f.endswith('sf.csv') :
                            writePreRaceInfo(f, folder, RACEWRITER, HORSEWRITER)
                        # if the file contains labels for races
                        # elif f.endswith('lb.csv') or f.endswith('lt.csv'):
                        # only looking for one of two label files, to avoid dups
                        # the other filename is generated in the function below.
                        elif f.endswith('lt.csv'):
                            writeLabelInfo(f, folder, LABELWRITER)
                        # notification for verbosity
                        else:
                            print("Skipping file - unknown type:", f)

def generate_data(n_horse):
    """ from the preliminary {RACES, HORSES, LABELS}.data.csv files, 
        this function generates the final data file as a culmination 
        of the data from each source.       """

    # identifying info for races and labels
    raceID = ""
    race = {}
    labelID = ""
    label = {}

    # open relevant files for reading/writing
    with open(RACEFILENAME) as RACEFILE,\
         open(HORSEFILENAME) as HORSEFILE,\
         open(LABELFILENAME) as LABELFILE,\
         open(ENDFILENAME, 'w') as ENDFILE:
        # create csv reader/writer objects for the respective files
        rReader = csv.DictReader(RACEFILE, dialect='unix')
        hReader = csv.DictReader(HORSEFILE, dialect='unix')
        lReader = csv.DictReader(LABELFILE, dialect='unix')
        writer = csv.DictWriter(ENDFILE, fieldnames=headers, 
                                     extrasaction='ignore', dialect='unix')

        # read through the horse entries
        for horse in hReader:
            horseRaceID = horse["R_RCTrack"] + " " + horse["R_RCDate"] + " " + \
                          horse["R_RCRace"]
            # ensure we have info on the correct race, and
            # when we move on to a new race, get that updated info
            if raceID != horseRaceID:
                # read the next race info from racefile
                race = getNextRow(rReader)
                # update raceid
                raceID = horseRaceID
                print("Merging information for race:", raceID)

            # we also have to keep reading labels, same deal
            if labelID != horseRaceID:
                label = getNextRow(lReader)
                labelID = horseRaceID

            if not label:
                allowPrinting()
                print("ERROR: LABELS.data.csv EOF reached.")  
                print("You don't have enough labels for your data!")
                blockPrinting()

                else:
                # error checking to make sure the labels and horse line up
                # checks horse name and race number, two most likely to differ
                if (label['R_RCRace'] != horse['R_RCRace'] or
                    label['B_Horse'] != horse['B_Horse']):
                    allowPrinting()
                    print("Error! label and horse mismatch :(")
                    print(" Race:   " + str(race))
                    print("Label:   " + str(label))
                    blockPrinting()
        
            # combine information from each file into one entry
            fullRow = horse.copy()
            fullRow.update(race)
            if label:
                fullRow.update(label)

            # write race and horse info to file
            writer.writerow(fullRow)

if __name__ == "__main__":
    # get root folder and pathname and file objects for the final product.
    DATA = config['raw_data_path']

    # set verbosity settings
    if not ("-v" in sys.argv or "--verbose" in sys.argv):
        VERBOSEMODE = False
        blockPrinting()

    # create filenames
    ENDFILENAME = config['final_data_filename']
    RACEFILENAME = "RACES." + ENDFILENAME
    HORSEFILENAME = "HORSES." + ENDFILENAME
    LABELFILENAME = "LABELS." + ENDFILENAME

    # get a list of headers for various files
    raceHeaders = config['race_data_col_headers'].split(', ')
    raceHeaders[-1] = raceHeaders[-1][:-1]
    horseHeaders = config['horse_data_col_headers'].split(', ')
    horseHeaders[-1] = horseHeaders[-1][:-1]
    labelHeaders = config['label_data_col_headers'].split(', ')
    labelHeaders[-1] = labelHeaders[-1][:-1]

    # generate the headers for data.csv as a combination of the middle files'
    headers = combineList(labelHeaders, raceHeaders, horseHeaders)

    # okay, go!
    create_middle_files()
    generate_data(1)
