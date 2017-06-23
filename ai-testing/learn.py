""" 
 *  Drew McArthur
 *  6/14/17
 *  testing out sklearn on horse racing data
"""
from sklearn import svm
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction import FeatureHasher
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA
import yaml, csv, random

def read_data(filename):
    """ returns an array of the data """
    with open(filename) as dataFile:
        datareader = csv.reader(dataFile, dialect='unix')
        next(datareader)
        r = []
        for row in datareader:
            r.append(row)
        return r

def read_output(filename):
    """ returns an array of outputs """
    # read labels.data.csv
    with open(filename) as lFile:
        labelreader = csv.DictReader(lFile, dialect='unix')
        r = []
        # iterate through the file and keep track of times
        for row in labelreader:
            r.append(row['L_BSF'])
        return r

def split_data(d, r):
    """ returns a tuple, of two lists, x and y where x is r% of d, 
        randomly chosen """
    len_test = round(len(d) * (1 - r))
    test = []
    for _ in range(len_test):
        i = random.randrange(len(d))
        test.append(d.pop(i))
    return (d, test)

if __name__ == "__main__":
    config = yaml.safe_load(open("./config.yml"))

    print("Loading data ... ", end='\r')
    inputs = read_data(config['final_data_filename'])
    outputs = read_output("LABELS." + config['final_data_filename'])
    print("Loading data ......... Loaded!")

    """
    print("Converting data from strings to floats ... ", end='\r')
    for col in range(len(inputs[0])):
        if isinstance(inputs[0][col], str):
            S = set([row[col] for row in inputs])
            D = dict( zip(S, range(len(S))) )
            Y = [D[row[col]] for row in inputs]
            for i in range(len(Y)):
                inputs[i][col] = Y[i]
    print("Converting data from strings to floats ... Converted!")
    print("Transforming data ... ", end='\r')
    # dictionary vectorizor method, which throws a MemoryError
    # vec = DictVectorizer()
    # inputs = vec.fit_transform(inputs).toarray()

    # feature hasher, apparently lower on memory
    fh = FeatureHasher()
    inputs = fh.fit_transform(inputs).toarray()
    print("Transforming data .... Transformed!")
    """

    print("Preprocessing data ... ", end='\r')
    lb = LabelEncoder()
    inputs = lb.fit_transform(inputs)
    print("Preprocessing data ... ", end='\r')

    print("Selecting features ... ", end='\r')
    #selector = VarianceThreshold(threshold=.16)
    #inputs = selector.fit_transform(inputs)
    print("Selecting features ... Selected!")
    print(inputs)

    print("Running PCA ... ", end='\r')
    pcaObj = PCA(n_components=50)
    inputs = pcaObj.fit_transform(inputs)
    print("Running PCA .......... PCA Complete!")

    print(inputs)
    print(inputs.toArray())
    quit()


    print("Splitting data ... ")
    data = [(inputs[i], outputs[i]) for i in range(len(inputs))]
    training, test = split_data(data, .75)

    trainX = [x[0] for x in training]
    trainY = [y[1] for y in training]
    print("                 Split!")
    print("There are {} rows in training and {} rows in test."
                .format(len(training), len(test)))

    for _ in range(10):
        print()

    [print(x) for x in trainX]
    [print(y) for y in trainY]

    print("Training regression model ... ")
    clf = svm.SVR()
    clf.fit(trainX, trainY)
    print("                 Trained!")

    nCorrect = 0.0
    nTotal = 0

    print("Testing model ... ")
    for x, y in test:
        yP = clf.predict(datum)
        if y == yP:
            nCorrect += 1.0
        nTotal += 1
    print("                 Tested!")

    print("Accuracy:", str(nCorrect/nTotal))
