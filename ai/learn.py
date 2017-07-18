""" 
 *  Drew McArthur
 *  6/14/17
 *  testing out sklearn on horse racing data
"""

from sklearn.metrics import explained_variance_score, r2_score
from sklearn.svm import SVR
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.feature_extraction import DictVectorizer, FeatureHasher
from sklearn.feature_selection import RFECV, SelectKBest, VarianceThreshold
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.pipeline import Pipeline, make_pipeline
from joblib import Parallel, delayed, dump, load
import yaml, csv, random, time

def read_data(filename):
    """ returns an array of the data """
    with open(filename) as dataFile:
        datareader = csv.reader(dataFile, dialect='unix')
        next(datareader)
        r = []
        for row in datareader:
            r.append(row)
        r.sort(key=lambda x:x[0])
        return r

def get_label(horse):
    """ returns the time and beyer figure for the given horse. """
    # Beyer Figure
    return int(round(float(horse['L_Time'])*1000))
    # time
    #return int(horse['L_BSF'])

def read_output(filename, data):
    """ returns an array of outputs """

    IDs = [d[0] for d in data]

    # read labels.data.csv
    with open(filename) as lFile:
        labelreader = csv.DictReader(lFile, dialect='unix')
        r = []
        # iterate through the file and keep track of times
        for row in labelreader:
            if row['ID'] in IDs:
                r.append((row['ID'], get_label(row)))
        r.sort(key=lambda x:x[0])
        return [x[1] for x in r]

def split_data(d, l, r):
    """ d=data, l=labels, r=ratio
        returns a tuple, of two lists, x and y where x is r% of d, 
        randomly chosen """
    assert(len(d) == len(l))
    len_test = round(len(d) * (1 - r))
    test = []
    testlabels = []
    for _ in range(len_test):
        i = random.randrange(len(d))
        test.append(d.pop(i))
        testlabels.append(l.pop(i))
    return ((d,l), (test,testlabels))

def test_n_features(n, Xs, Ys):
    beg = time.time()

    training, test = split_data(Xs, Ys, .90)
    x_train, y_train = training
    x_test, y_test = test

    print("x Split data.")

    # TODO: get array of indices that represents the categorical columns
    #       this would go second, after feature hashing
    #cat_feats = []
    #enc = OneHotEncoder(categorical_features=cat_feats)

    fh = FeatureHasher(input_type='string')
    kBest = SelectKBest(k=n)
    estimator = SVR(kernel="rbf")

    print("x Created sklearn objects.")

    pipe = make_pipeline(fh, kBest, estimator)

    print("x Created pipeline.")

    pipe.fit(x_train, y_train)

    print("x Trained model.")

    dump(pipe, 'ai.pickle')

    print("x Dumped model to file.")

    y_pred = pipe.predict(x_test)

    deltas = [abs(p-l) for p, l in zip(y_pred, y_test)]

    end = time.time()

    # open output.csv and append a row to it consisting of 
    # the number of features, the avg. error, 
    # the explained variance, and r^2

    print("Writing data for round", n)

    with open("results.csv", 'a', newline='') as oFile:
        oWriter = csv.writer(oFile, dialect='unix',
                             quoting=csv.QUOTE_MINIMAL)
        oWriter.writerow([n, end - beg,
               sum(deltas)/len(deltas),
               explained_variance_score(y_test, y_pred),
               r2_score(y_test, y_pred)])

if __name__ == "__main__":
    config = yaml.safe_load(open("./config.yml"))

    data = read_data(config['final_data_filename'])
    targets = read_output("LABELS." + config['final_data_filename'], data)

    print("x read data and labels.")

    #Ns = range(1700, 1810, 10)
    #Parallel(n_jobs=8)(delayed(test_n_features)(n, data, targets) for n in Ns)
    test_n_features(1750, data, targets)
