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

import yaml, os, csv, re
config = yaml.safe_load(open("config.yml"))

# right way to access config vars
# config['raw_data_path']

# get root folder, as well as pathname and file objects for the final product.
DATA = config['raw_data_path']

# create filenames
ENDFILENAME = config['final_data_filename']
RACEFILENAME = "RACES." + ENDFILENAME
HORSEFILENAME = "HORSES." + ENDFILENAME
LABELFILENAME = "LABELS." + ENDFILENAME

def combineList(a, b):
    c = a[:]
    for x in b:
        if x not in c:
            c.append(x)
    return c

# get a list of headers for various files
raceHeaders = config['race_data_col_headers'].split(', ')
raceHeaders[-1] = raceHeaders[-1][:-1]
horseHeaders = config['horse_data_col_headers'].split(', ')
horseHeaders[-1] = horseHeaders[-1][:-1]
labelHeaders = config['label_data_col_headers'].split(', ')
labelHeaders[-1] = labelHeaders[-1][:-1]
headers = combineList(raceHeaders, horseHeaders)

def rowEmpty(row, headers):
    """ given a row (dictionary of headers:vals), and a list of headers, 
        check if the row contains any data in the columns specified. """
    for col in headers:
        if row[col] != '':
            return False
    return True

def writePreRaceInfo(f, folder, RACEWRITER, HORSEWRITER):
    # then open the file with a csv reader
    path = folder + "/" + f
    print("         ", f)
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, dialect='unix')
        raceIDInfo = {}
        # iterate through the data in the file we're reading,
        for row in reader:
            # and write that data to its respective files
            if not rowEmpty(row, raceHeaders):
                RACEWRITER.writerow(row)

            if row["R_RCTrack"] != "":
                raceIDInfo["R_RCTrack"] = row["R_RCTrack"]
                raceIDInfo["R_RCDate"] = row["R_RCDate"]
                raceIDInfo["R_RCRace"] = row["R_RCRace"]
            else:
                row["R_RCTrack"] = raceIDInfo["R_RCTrack"]
                row["R_RCDate"] = raceIDInfo["R_RCDate"]
                row["R_RCRace"] = raceIDInfo["R_RCRace"]

            if not rowEmpty(row, horseHeaders):
                HORSEWRITER.writerow(row)

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
        for row in beyerreader:
            row.update(raceIDInfo))
            row.update({"rank": rank})
            labeldata.append(row)
            rank += 1

        # add data from the timereader to the dictionaries in that list
        for row in timereader:
            for entry in labeldata:
                if row['Horse'] == entry['Horse']
                    entry.update(row)

        print("is this label data right???")
        print(labeldata)

        # TODO: write to LABELS.data.csv
        #       create LABELWRITER and correct file to pass to this function
        quit()

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
    # ENDWRITER = csv.DictWriter(ENDFILE, fieldnames=headers, 
    #                               extrasaction='ignore', dialect='unix')
    RACEWRITER = csv.DictWriter(RACEFILE, fieldnames=raceHeaders, 
                                   extrasaction='ignore', dialect='unix')
    HORSEWRITER = csv.DictWriter(HORSEFILE, fieldnames=horseHeaders, 
                                   extrasaction='ignore', dialect='unix')
    LABELWRITER = csv.DictWriter(LABELFILE, fieldnames=labelHeaders, 
                                   extrasaction='ignore', dialect='unix')


    # if ENDFILE is empty, then write the header columns to the file.
    #if os.stat(ENDFILENAME).st_size == 0:
    #    ENDWRITER.writeheader()
    if os.stat(RACEFILENAME).st_size == 0:
        RACEWRITER.writeheader()
    if os.stat(HORSEFILENAME).st_size == 0:
        HORSEWRITER.writeheader()

    # iterate through files in data directory
    print(DATA)
    for d in os.listdir(DATA):
        if os.path.isdir(DATA + d):
            print(" ",d)
            for subd in os.listdir(DATA + d):
                # note: DATA includes a trailing "/" but most dirs don't.
                folder = DATA + d + "/" + subd
                if os.path.isdir(folder):
                    print("     ",subd)
                    for f in os.listdir(folder):
                        # if file is single file export of race info
                        if f.endswith('sf.csv') :
                            writePreRaceInfo(f, folder, RACEWRITER, HORSEWRITER)
                        # if the file contains labels for races
                        # elif f.endswith('lb.csv') or f.endswith('lt.csv'):
                        # only looking for one of the label files, to avoid dups
                        # the other filename is generated in the function below.
                        elif f.endswith('lt.csv'):
                            writeLabelInfo(f, folder, LABELWRITER)

def generate_data(n_horse):
    raceID = ""
    race = {}

    with open(RACEFILENAME) as RACEFILE,\
         open(HORSEFILENAME) as HORSEFILE,\
         open(ENDFILENAME, 'w') as ENDFILE:
        hReader = csv.DictReader(HORSEFILE, dialect='unix')
        rReader = csv.DictReader(RACEFILE, dialect='unix')
        writer = csv.DictWriter(ENDFILE, fieldnames=headers, 
                                     extrasaction='ignore', dialect='unix')
        for horse in hReader:
            horseRaceID = horse["R_RCTrack"] + " " + horse["R_RCDate"] + " " + \
                          horse["R_RCRace"]
            # when we move on to a new race, get that updated info
            if raceID != horseRaceID:
                # read the next race info from racefile
                race = next(rReader)
                # update raceid
                raceID = horseRaceID
                print("Merging information for race:", raceID)
        
            # combine information from each file
            fullRow = horse.copy()
            fullRow.update(race)

            # write race and horse info to file
            writer.writerow(fullRow)

create_middle_files()
generate_data(1)
