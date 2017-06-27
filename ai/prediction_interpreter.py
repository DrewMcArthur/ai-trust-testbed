import csv

def getHorsesInRace(reader, row):
    """ returns a list of tuples, with IDs and Horse names 
        for each horse in the given race number """
    nHorses = int(row['R_Starters'])
    horses = [(row['ID'], row['B_Horse'])]
    for _ in range(nHorses - 2):
        row = next(reader)
        horses.append((row['ID'], row['B_Horse']))
    return horses

def matchHorses(horses, labels):
    """ given a list of horses with IDs and labels, return a list of tuples 
        with the horses name and their predicted beyer figure """
    for i in range(len(horses)):
        horses[i] = (horses[i][1], labels[int(horses[i][0])])
    return horses

if __name__ == "__main__":
    labels = []
    with open("predictions170621.csv") as f:
        reader = csv.reader(f, dialect='unix')
        for row in reader:
            labels.append(row[1])
            
    with open("TEST.data.csv") as t:
        reader = csv.DictReader(t, dialect='unix')
        raceN = "0"
        lastRow = {}
        for row in reader:
            if raceN != int(row['R_RCRace']):
                if lastRow != {}:
                    print(lastRow['R_RCTrack'], lastRow['R_RCDate'], 
                          "Race #" + lastRow['R_RCRace'])
                    horses.sort(key=lambda r:float(r[1]),reverse=True)
                    [print("    ", horse) for horse in horses]
                raceN = int(row['R_RCRace'])
                horses = [(row['B_Horse'], labels[int(row['ID'])-1])]
            else:
                horses.append((row['B_Horse'], labels[int(row['ID'])-1]))

            lastRow = row
