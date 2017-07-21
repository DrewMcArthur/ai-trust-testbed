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
from sklearn.base import TransformerMixin
from joblib import Parallel, delayed, dump, load
from itertools import product
import bisect
import yaml, csv, random, time, sys
import numpy as np

class ColWiseEncoder(TransformerMixin):
    def __init__(self, cat_feats):
        self.mask = cat_feats

    def fit(self, Xs, Ys=None):
        # convert the list of dicts to a list of lists
        listXs = [[item for key, item in row.items()] for row in Xs]
        # convert 2d list to 2d numpy array
        nArray = np.array(listXs)
        # create a list of labelencoders, one for each column
        self.mapper= []
        # for each column, fit a labelencoder to that column
        for i in range(len(Xs[0])):
            if self.mask[i]:
                self.mapper.append(LabelEncoder())
                col = nArray[:,i]
                self.mapper[i].fit(col)
                le_classes = self.mapper[i].classes_.tolist()
                bisect.insort_left(le_classes, 'other')
                self.mapper[i].classes_ = le_classes
            else:
                self.mapper.append(False)

    def transform(self, Xs, Ys=None):
        # convert the list of dicts to a list of lists
        listXs = [[item for key, item in row.items()] for row in Xs]
        nArray = np.array(listXs)
        for i in range(len(Xs[0])):
            if self.mask[i]:
                col = nArray[:,i]
                col = list(map(lambda s: 'other' if s not in self.mapper[i].classes_
                                                 else s, col.tolist()))

                # transform the columns
                nArray[:,i] = self.mapper[i].transform(col)
        nArray = list(map(lambda x: "NaN" if x == '' else x, nArray))
        return nArray
        
    def fit_transform(self, Xs, Ys=None):
        """ applies labelencoder to each column, if the column is determined
            to be continuous variables """
        # convert the list of dicts to a list of lists
        listXs = [[item for key, item in row.items()] for row in Xs]
        # convert 2d list to 2d numpy array
        nArray = np.array(listXs)
        # create a list of labelencoders, one for each column
        self.mapper= []
        # get first row, which is all headers
        headers = nArray[0]

        # for each column, fit and transform using its respective labelencoder
        for i in range(len(headers)):
            col = nArray[:,i]
            if self.mask[i]:
                self.mapper.append(LabelEncoder())
                self.mapper[i].fit(col)

                le_classes = self.mapper[i].classes_.tolist()
                bisect.insort_left(le_classes, 'other')
                self.mapper[i].classes_ = le_classes
                
                nArray[:,i] = self.mapper[i].transform(col)
            else:
                self.mapper.append(False)

        nArray = list(map(lambda x: "NaN" if x == '' else x, nArray))
        return nArray

def read_data(filename):
    """ returns an array of the data """
    with open(filename) as dataFile:
        datareader = csv.DictReader(dataFile, dialect='unix')
        r = []
        for row in datareader:
            r.append(row)
        r.sort(key=lambda x:x['ID'])
        return r

def get_label(horse):
    """ returns the time and beyer figure for the given horse. """
    # time
    #return float(horse['L_Time'])
    # Beyer Figure
    return int(horse['L_BSF'])

def read_output(filename, data):
    """ returns an array of outputs """

    IDs = [d['ID'] for d in data]

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

def test_n_features(Xs, Ys, c, e):
    beg = time.time()

    training, test = split_data(Xs, Ys, .90)
    x_train, y_train = training
    x_test, y_test = test

    print("x Split data.")

    # TODO: get array of indices that represents the categorical columns
    #       this would go second, after feature hashing
    cat_feats = [eval(x) for x in config['data_is_categorical'][:-1].split(', ')]

    enc = OneHotEncoder(cat_feats)
    fh = FeatureHasher(input_type='string')
    cwe = ColWiseEncoder(cat_feats)
    kBest = SelectKBest(k=1750)
    estimator = SVR(kernel="linear", C=c, epsilon=e)

    print("x Created sklearn objects.")

    pipe = make_pipeline(cwe, enc, kBest, estimator)

    print("x Created pipeline.")

    pipe.fit(x_train, y_train)

    print("x Trained model.")

    #dump(pipe, 'ai_time_linear.pickle')

    print("x Dumped model to file.")

    y_pred = pipe.predict(x_test)

    deltas = [abs(p-l) for p, l in zip(y_pred, y_test)]

    end = time.time()

    # open output.csv and append a row to it consisting of 
    # the number of features, the avg. error, 
    # the explained variance, and r^2

    print("Writing data for C=", c, "e=",e)
    print('time')
    print(end-beg)
    print('avg delta')
    print(sum(deltas)/len(deltas))
    print('variance score')
    print(explained_variance_score(y_test, y_pred))
    print('r squared')
    print(r2_score(y_test, y_pred))
    print()
    print()
    #print('prediction - actual = deltas')
    #[print(p,"-",a,"=",d) for p,a,d in zip(y_pred, y_test, deltas)]
    
if __name__ == "__main__":
    config = yaml.safe_load(open("./config.yml"))

    data = read_data(config['final_data_filename'])
    targets = read_output("LABELS." + config['final_data_filename'], data)

    print("x read data and labels.")

    print("c={}, e={}".format(sys.argv[1], sys.argv[2]))
    #Ns = range(1700, 1810, 10)
    #Cs = [1.0, 10.0, 100.0, 1000.0]
    #Es = [.1, .01, .001, .0001]
    #args = list(product(Cs, Es))
    test_n_features(data, targets, sys.argv[1], sys.argv[2])
    #Parallel(n_jobs=8)(delayed(test_n_features)(data, targets, c, e) 
                                                #for c, e in args)
    #test_n_features(1750, data, targets)
