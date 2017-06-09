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

# allow/disallow printing.  errors must turn on printing
def allowPrinting():
    sys.stdout = sys.__stdout__   
def blockPrinting(VERBOSE):
    if not VERBOSE:
        sys.stdout = open(os.devnull, 'w')

def fixDate(d):
    """ given a date d, return the same date in YYMMDD format. """
    if d == "":
        return ""
    if "/" not in d or not d:
        return d
    r = d[-2:]
    d = d[:5]
    r += d[:2]
    r += d[-2:]

    return r

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
        if col in row.keys() and row[col] != "":
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
    path = folder + f
    print("         ", f)

    # lists of entries to write to file
    races = []
    horses = []

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, dialect='unix')
        raceIDInfo = {}
        # iterate through the data in the file we're reading,
        for row in reader:
            row['R_RCDate'] = fixDate(row['R_RCDate'])
            # and write that data to the race file
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
        if not rowEmpty(race, raceHeaders):
            for k in raceHeaders:
                allowPrinting()
                print(k,":          ",race[k])
                blockPrinting(VERBOSEMODE)
            RACEWRITER.writerow(race)
    for horse in horses:
        HORSEWRITER.writerow(horse)

def writeLabelInfo(f, folder, LABELWRITER):
    """ Scrapes data from file f in folder, and writes the data to 
        a labels file, using the object LABELWRITER """

    # list of dictionaries, each dict is a data entry to be written to LABELS
    labeldata = []

    # parse track and date from filename
    m = re.match("([a-zA-Z]{2,3})([0-9]{6})_([0-9]{1,2}).*", f)
    track = m.group(1)
    date = m.group(2)
    race = m.group(3)

    print('writing from',folder + f, 'to labelwriter')
    print("         ", f)
    raceIDInfo = {"R_RCTrack": track, "R_RCDate": date, "R_RCRace": race}
    print("dealing with this race: ")
    print(raceIDInfo)

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
                allowPrinting()
                print("Error! reading entries from two label files and ")
                print("       the horse names don't match! You screwed up!")
                print("Race: " + str(raceIDInfo))
                print("time's horse: " + t['Horse'])
                print("beyer's horse: " + entry['Horse'])
                blockPrinting(VERBOSEMODE)
            entry.update({"L_Time": t["Fin"]})

            # add entry to list and update rank
            labeldata.append(entry)
            rank += 1

    [print(x) for x in labeldata]
    labeldata.sort(key=lambda x: (x["R_RCRace"], x["B_Horse"]))

    # write the entries in labeldata to file
    for entry in labeldata:
        LABELWRITER.writerow(entry)

def writePreRaceMulFile(f, folder, RACEWRITER, HORSEWRITER):
    """ given a file (*.cr.csv), gather data from it and 4 other related files
        (*.{pgh,ch,cs,ct}.csv) and write the data to {RACES, HORSES}.data.csv
    """

    # list of dictionary entries to be added to RACES and HORSES
    entries = {}

    def getKey(e):
        """ returns a unique identifier for the entry """
        keys = ['RCTrack','RCDate','RCRace','Horse']
        r = ""
        for key in keys:
            if key in e:
                r += e[key]
        r = r.replace("/", "")
        r = r.replace("'", "")
        r = r.replace(" ", "")
        return r

    # parse track and date from filename
    m = re.match("([a-zA-Z]{2,3})(.?)([0-9]{6}).*", f)
    track = m.group(1)
    separator = m.group(2)
    date = m.group(3)

    # get base filename
    base = track + separator + date  # BEL170605 or Rp_170427

    # check if single file exists, in which case we can skip these files
    if os.path.isfile(folder + base + ".sf.csv"):
        print("Found single file for this data, skipping", f)
        return None

    # create 2d list of relevant information
    # i.e., filename, column header prefix, number of columns to skip
    # last boolean is for ct, which contains multiple rows of trainer info per 
    # horse entry.  
    filelist = [["ch", "H_", False],
                ["cr", "R_", False],
                ["pgh", "B_", False],
                ["cs", "S_", False],
                ["ct", "T_", True]
               ]

    for info in filelist:
        # open the file
        r = csv.DictReader(open(folder + base + "." + info[0] +".csv"), 
                           dialect='unix')
        lastHorse = ""              # name of the last horse dealt with
        count = 0                   # count of the number of entries so far
        samecount = 1               # which trainer we're on

        for row in r:
            if 'Horse' not in row.keys() or getKey(row) not in entries.keys():
                entries[getKey(row)] = {}
            entry = entries[getKey(row)]

            # if the current horse is the same as the last, then 
            if info[2] and row['Horse'] == lastHorse:
                samecount += 1
            # but when we get to a new horse, increment count & reset samecount
            else:
                samecount = 1

            row['RCDate'] = fixDate(row['RCDate'])

            for k, v in row.items():
                if info[2]:
                    entry[info[1] + k + "_" + str(samecount)] = v
                else:
                    entry[info[1] + k] = v

            if info[0] == "cr":
                print("row that was read from", info[0], ": ")
                print(row)
                print("info to be added to entry: ")
                print(entry)

            if 'Horse' in row.keys():
                entries.update({getKey(row): entry})
            else:
                # if this needs to occur for all horses
                for key in entries.keys():
                    if getKey(row) in key:
                        h = key.replace(getKey(row), '')
                        entries[getKey(row) + h] = entry

            if info[2]:
                lastHorse = row['Horse']

    # write the entries to file
    for key, entry in entries.items():
        print()
        print()
        print("entry to be written: ")
        print(key)
        print(entry)
        print("if this looks right, take out the quit() on line 258")
        if not rowEmpty(entry, horseHeaders):
            HORSEWRITER.writerow(entry)
        if not rowEmpty(entry, raceHeaders):
            RACEWRITER.writerow(entry)
        #quit()

def create_middle_files():
    """ iterate through files in DATA directory and create 
        {RACES, HORSES, LABELS}.data.csv """
    # open the files for writing
    HORSEFILE = open(HORSEFILENAME, 'w')
    RACEFILE = open(RACEFILENAME, 'w')
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
    if os.stat(LABELFILENAME).st_size == 0:
        LABELWRITER.writeheader()

    # iterate through files in data directory
    print(DATA)
    for place in os.listdir(DATA):
        if os.path.isdir(DATA + place):
            print(" ", place)
            for date in os.listdir(DATA + place):
                # note: DATA includes a trailing "/" but most dirs don't.
                folder = DATA + place + "/" + date + "/"
                if os.path.isdir(folder):
                    print("     ",date)
                    for f in os.listdir(folder):
                        # if file is single file export of race info
                        if f.endswith('sf.csv'):
                            writePreRaceInfo(f, folder, RACEWRITER, HORSEWRITER)
                        # if the file contains labels for races
                        # elif f.endswith('lb.csv') or f.endswith('lt.csv'):
                        # only looking for one of two label files, to avoid dups
                        # the other filename is generated in the function below.
                        elif f.endswith('lt.csv'):
                            writeLabelInfo(f, folder, LABELWRITER)

                        # deals with files exported as multiple files
                        elif f.endswith('cr.csv'):
                            if "--skip-multi" not in sys.argv:
                                writePreRaceMulFile(f, folder, RACEWRITER, 
                                                               HORSEWRITER)
                        # notification for verbosity
                        else:
                            print("Skipping file - unnecessary type:", f)

def sort_middle_files():
    """ sorts the middle files by trackname, date, race number, and horse name. 
    """
    races = []
    horses = []
    labels = []

    import time

    # open the middle files and create csv reader objects
    with open(RACEFILENAME) as RACEFILE,\
         open(HORSEFILENAME) as HORSEFILE,\
         open(LABELFILENAME) as LABELFILE:
        rReader = csv.DictReader(RACEFILE, dialect='unix')
        hReader = csv.DictReader(HORSEFILE, dialect='unix')
        lReader = csv.DictReader(LABELFILE, dialect='unix')

        # obtain sorted lists of the data
        t0 = time.time()
        races = sorted(rReader, key=lambda row:(row['R_RCTrack'], 
                                                row['R_RCDate'], 
                                                row['R_RCRace']))
        t1 = time.time()
        print("Finished sorting races, that took", str(t1 - t0), "seconds.")
        horses = sorted(hReader, key=lambda row:(row['R_RCTrack'], 
                                                 row['R_RCDate'], 
                                                 row['R_RCRace'],
                                                 row['B_Horse']))
        t2 = time.time()
        print("Finished sorting horses, that took", str(t2 - t1), "seconds.")
        labels = sorted(lReader, key=lambda row:(row['R_RCTrack'], 
                                                 row['R_RCDate'], 
                                                 row['R_RCRace'],
                                                 row['B_Horse']))
        t3 = time.time()
        print("Finished sorting labels, that took", str(t3 - t2), "seconds.")

    with open(RACEFILENAME, 'w') as RACEFILE,\
         open(HORSEFILENAME, 'w') as HORSEFILE,\
         open(LABELFILENAME, 'w') as LABELFILE:

        # create csv writer objects
        RACEWRITER = csv.DictWriter(RACEFILE, fieldnames=raceHeaders, 
                                    extrasaction='ignore', dialect='unix')
        HORSEWRITER = csv.DictWriter(HORSEFILE, fieldnames=horseHeaders, 
                                     extrasaction='ignore', dialect='unix')
        LABELWRITER = csv.DictWriter(LABELFILE, fieldnames=labelHeaders, 
                                     extrasaction='ignore', dialect='unix')

        # rewrite the files
        [w.writeheader() for w in [RACEWRITER, HORSEWRITER, LABELWRITER]]
        [RACEWRITER.writerow(race) for race in races]
        [HORSEWRITER.writerow(horse) for horse in horses]
        [LABELWRITER.writerow(label) for label in labels]

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
                blockPrinting(VERBOSEMODE)

            else:
                # error checking to make sure the labels and horse line up
                # checks horse name and race number, two most likely to differ
                try: 
                    if (label['R_RCRace'] != horse['R_RCRace'] or
                        label['B_Horse'] != horse['B_Horse']):
                        p=lambda x: str(x['R_RCTrack']) + \
                                    str(x['R_RCDate']) + str(x['R_RCRace'])
                        allowPrinting()
                        print("Error! label and race mismatch:")
                        print(" Race:   " + p(race))
                        print("Label:   " + p(label))
                        print("Horse:   " + p(horse))
                        print()
                        blockPrinting(VERBOSEMODE)
                except KeyError:
                    allowPrinting()
                    print("label")
                    print(label)
                    print("horse")
                    print(horse)
                    blockPrinting(VERBOSEMODE)
                    quit()
        
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

    # future mode for verbosity toggling
    VERBOSEMODE = True

    # set verbosity settings
    if "-v" not in sys.argv:
        VERBOSEMODE = False
        blockPrinting(VERBOSEMODE)

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
    if "-g" not in sys.argv:
        create_middle_files()
        sort_middle_files()
    if "-m" not in sys.argv:
        generate_data(1)
