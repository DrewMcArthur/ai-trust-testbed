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

    # iterate through files in data directory, PLACE/DATE/Files
    print(DATA)
    for place in os.listdir(DATA):
        if os.path.isdir(DATA + '/' + place):
            print(" ", place)
            for date in os.listdir(DATA + '/' + place):
                folder = DATA + '/' + place + "/" + date + "/"
                if os.path.isdir(folder):
                    print("     ",date)
                    for f in os.listdir(folder):
                        # if the file contains label information, write to file
                        # only looking for one of two label files, to avoid dups
                        # the other filename is generated in the function below.
                        if f.endswith('lt.csv'):
                            writeLabelInfo(f, folder, LABELWRITER)
                        # notification for verbosity
                        #else:
                            #print("Skipping file - unnecessary type:", f)

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
    """ reads the labels file, and uses the information there to find
        input data """

    labelsmissingdata = []

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
            labelWritten = False
            # if we aren't looking at the right file, fix that
            if currfn != get_data_fn(label):
                currfn = get_data_fn(label)
                if os.path.isfile(currfn):
                    data = open(currfn)
                    datafile = csv.DictReader(data, dialect='unix')
                else:
                    print("Error! sf file not found for", currfn)
            else:
                data.seek(0)

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
                    labelWritten = True

            if not labelWritten:
                print("Error! the input info for this label was never written!")
                print(label)
                print("we thought it'd be in this file:", currfn)
                print()
                labelsmissingdata.append((currfn, label))
                row = raceInfo.copy()
                row.update({"missing":1})
                inputWriter.writerow(row)

    print("we couldn't find input info for", len(labelsmissingdata),
          "labels. :(")

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
    headers = labelHeaders

    # okay, go!
    create_labels()
    get_input_data(ENDFILENAME, LABELFILENAME)
