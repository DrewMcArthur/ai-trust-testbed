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
    [print() for _ in range(10)]
    print("fixing date: ", d)
    if d == "":
        return ""
    if "/" not in d or not d or d[:2] == "17":
        return d
    r = d[-2:]
    d = d[:5]
    r += d[:2]
    r += d[-2:]

    print("Fixed date: ", r)
    [print() for _ in range(10)]
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
    skip = ['from_filetype', 'from_filename', 
            'R_RCTrack', 'R_RCDate', 'R_RCRace']
    for col in headers:
        if col in row.keys() and col not in skip and row[col] != "":
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
            row['from_filename'] = f
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
        race['from_filetype'] = 'sf'
        if not rowEmpty(race, raceHeaders):
            for k in raceHeaders:
                #allowPrinting()
                print(k,":          ",race[k])
                #blockPrinting(VERBOSEMODE)
            RACEWRITER.writerow(race)
    for horse in horses:
        horse['from_filetype'] = 'sf'
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

    #print('writing from',folder + f, 'to labelwriter')
    print("         ", f)
    raceIDInfo = {"R_RCTrack": track, "R_RCDate": date, "R_RCRace": race}
    #print("dealing with this race: ")
    #print(raceIDInfo)

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
                          "L_BSF": b["Chart"],
                          "from_filename": f
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

    #[print(x) for x in labeldata]
    labeldata.sort(key=lambda x: (x["B_Horse"]))

    # write the entries in labeldata to file
    for entry in labeldata:
        #entry['from_filetype'] = 'lb/lt'
        if len(entry['B_Horse']) < 30:
            LABELWRITER.writerow(entry)

def writePreRaceMulFile(f, folder, RACEWRITER, HORSEWRITER):
    """ given a file (*.cr.csv), gather data from it and 4 other related files
        (*.{pgh,ch,cs,ct}.csv) and write the data to {RACES, HORSES}.data.csv
    """
    allowPrinting()

    # list of dictionary entries to be added to RACES and HORSES
    entries = {}

    def getKey(e, keys=['RCTrack','RCDate','RCRace','Horse']):
        """ returns a unique identifier for the entry """
        if 'RCDate' in e:
            e['RCDate'] = fixDate(e['RCDate'])
        r = ""
        for key in keys:
            if key in e:
                r += e[key].upper()
        r = r.replace("/", "")
        r = r.replace("'", "")
        r = r.replace(" ", "")
        r = r.replace(".00", "")
        if r == "":
            return getKey(e, ["R_RCTrack", "R_RCDate", "R_RCRace", "B_Horse"])
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
                entry = {}
            else:
                entry = entries[getKey(row)]

            # if the current horse is the same as the last, then 
            if info[2] and row['Horse'] == lastHorse:
                samecount += 1
            # but when we get to a new horse, increment count & reset samecount
            else:
                samecount = 1

            row['RCDate'] = fixDate(row['RCDate'])
            entry['from_filename'] = f

            for k, v in row.items():
                if info[2]:
                    entry[info[1] + k + "_" + str(samecount)] = v
                else:
                    entry[info[1] + k] = v

            print("row that was read from", info[0], ": ")
            print(row)
            print("info to be added to entry: ")
            print(entry)
            print()
            print()
            print()

            # do we put this in entries for one horse, or for multiple horses?
            if 'Horse' in row.keys():
                entries.update({getKey(row): entry})
                print("entry so far: ")
                print("we've read up to the filetype", info[0])
                print(entries[getKey(row)])
            else:
                # if this needs to occur for all horses
                for key in entries.keys():
                    if getKey(row) in key:
                        h = key.replace(getKey(row), '')
                        entries.update({getKey(row) + h: entry})
                        print("entry so far: ")
                        print("we've read up to the filetype", info[0])
                        print(entries[getKey(row) + h])
            

            # keep track of the horse names, for trainer file 
            # with multiple rows per horse
            if info[2]:
                lastHorse = row['Horse']

    # write the entries to file
    for key, entry in entries.items():
        if key != getKey(entry):
            print()
            print()
            print("row key, vs entry key")
            print(key, "vs", getKey(entry))
            print("entry to be written: ")
            print(entry)
            print("if this looks right, take out the quit() on line 258")
        entry['from_filetype'] = 'mul'
        if not rowEmpty(entry, horseHeaders):
            HORSEWRITER.writerow(entry)
        if not rowEmpty(entry, raceHeaders):
            RACEWRITER.writerow(entry)
    quit()

def create_labels():
    """ iterate through files in DATA directory and create 
        {RACES, HORSES, LABELS}.data.csv """
    # open the files for writing
    LABELFILE = open(LABELFILENAME, 'w')

    # create an object which writes data to files as a csv, using column headers
    # from config.yml and ignoring extra data
    #RACEWRITER = csv.DictWriter(RACEFILE, fieldnames=raceHeaders, 
    #                               extrasaction='ignore', dialect='unix')
    #HORSEWRITER = csv.DictWriter(HORSEFILE, fieldnames=horseHeaders, 
    #                               extrasaction='ignore', dialect='unix')
    LABELWRITER = csv.DictWriter(LABELFILE, fieldnames=labelHeaders, 
                                   extrasaction='ignore', dialect='unix')


    # if ENDFILE is empty, then write the header columns to the file.
    #if os.stat(RACEFILENAME).st_size == 0:
    #    RACEWRITER.writeheader()
    #if os.stat(HORSEFILENAME).st_size == 0:
    #    HORSEWRITER.writeheader()
    if os.stat(LABELFILENAME).st_size == 0:
        LABELWRITER.writeheader()

    # iterate through files in data directory
    print(DATA)
    for place in os.listdir(DATA):
        if os.path.isdir(DATA + '/' + place):
            print(" ", place)
            for date in os.listdir(DATA + '/' + place):
                # note: DATA includes a trailing "/" but most dirs don't.
                folder = DATA + '/' + place + "/" + date + "/"
                if os.path.isdir(folder):
                    print("     ",date)
                    for f in os.listdir(folder):
                        # if the file contains labels for races
                        # elif f.endswith('lb.csv') or f.endswith('lt.csv'):
                        # only looking for one of two label files, to avoid dups
                        # the other filename is generated in the function below.
                        if f.endswith('lt.csv'):
                            writeLabelInfo(f, folder, LABELWRITER)

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

            # if we don't know what race this horse was in, then skip this data.
            if horseRaceID == "  ":
                continue

            # ensure we have info on the correct race, and
            # when we move on to a new race, get that updated info
            if raceID != horseRaceID:
                # read the next race info from racefile
                race = getNextRow(rReader)
                # update raceid
                raceID = horseRaceID


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
                                    str(x['R_RCDate']) + \
                                    str(x['R_RCRace']) + " " + \
                                    str(x['B_Horse'])
                        allowPrinting()
                        print("Error! label and race mismatch:")
                        print(" Race:   " + p(race))
                        print("Label:   " + p(label))
                        print("Horse:   " + p(horse))
                        print()
                        blockPrinting(VERBOSEMODE)
                except KeyError:
                    allowPrinting()
                    print('key error, dang')
                    print("race")
                    print(race)
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

def get_data_fn(label):
    track = label['R_RCTrack']
    date = label['R_RCDate']
    race = label['R_RCRace']
    horsename = label['B_Horse']
    separator = "" if len(track) == 3 else "_"
    return DATA+"/"+track+"/"+date+"/"+track+separator+date+"_SF.CSV"

def get_race_info(row):
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

def get_input_data(INPUTFN, LABELFN):

    #debugging purposes, delete later
    missingfiles = []

    with open(LABELFN) as LABELFILE, open(INPUTFN, 'w') as INPUTFILE:
        labelReader = csv.DictReader(LABELFILE, dialect='unix')
        inputWriter = csv.DictWriter(INPUTFILE, fieldnames=inputHeaders, 
                                     extrasaction='ignore', dialect='unix')

        inputWriter.writeheader()

        # the current datafilename we're scraping, and the object itself
        currfn = ""
        datafile = None

        # used for copying race info to rows missing this data
        raceInfo = {}

        # iterate through each label
        for label in labelReader:
            # if we aren't looking at the right file, fix that
            if currfn != get_data_fn(label):
                currfn = get_data_fn(label)
                if os.path.isfile(currfn):
                    datafile = csv.DictReader(open(currfn), dialect='unix')
                else:
                    print("Error! sf file not found for this data. I'll keep track of how many of these there are.")
                    missingfiles.append(currfn)

            # iterate through the data, and
            for row in datafile:
                # first, we add race info to each row where its missing
                if row["R_RCTrack"] == "":
                    row.update(raceInfo)
                else:
                    raceInfo = get_race_info(row)
                
                # when we reach the right entry, we write it to file
                if (label['B_Horse'] == row['B_Horse'] and 
                    label['R_RCRace'] == row['R_RCRace']):
                    # write this row to inputWriter
                    inputWriter.writerow(row)

    print("Here's the",len(missingfiles),"files we couldn't find for the labels:")
    for f in missingfiles:
        print(f)
        tocheck = f[:-5]
        


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
    #RACEFILENAME = "RACES." + ENDFILENAME
    #HORSEFILENAME = "HORSES." + ENDFILENAME
    LABELFILENAME = "LABELS." + ENDFILENAME

    # get a list of label headers for various files
    labelHeaders = config['label_data_col_headers'].split(', ')
    labelHeaders[-1] = labelHeaders[-1][:-1]
    inputHeaders = config['input_data_col_headers'].split(', ')
    inputHeaders[-1] = inputHeaders[-1][:-1]

    # generate the headers for data.csv as a combination of the middle files'
    headers = labelHeaders#combineList(labelHeaders, raceHeaders, horseHeaders)

    # okay, go!
    #create_labels()
    get_input_data(ENDFILENAME, LABELFILENAME)
