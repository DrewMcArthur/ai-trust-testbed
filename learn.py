""" 
 *  Drew McArthur
 *  6/14/17
 *  testing out sklearn on horse racing data
"""

from sklearn.svm import SVR
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction import FeatureHasher
from sklearn.feature_selection import RFECV
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
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
                r.append(int(row['L_BSF']))
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

    print("Loading Data ... ", end='\r')
    data = read_data(config['final_data_filename'])
    targets = read_output("LABELS." + config['final_data_filename'], data)
    print("Loading Data ......... Loaded!")

    print("Hashing Features ... ", end='\r')
    fh = FeatureHasher(input_type='string')
    data = fh.fit_transform(data, targets)
    print("Hashing Features ... Hashed!")

    print("Pruning Features ... ", end='\r')
    estimator = SVR(kernel="linear")
    selector = RFECV(estimator)
    selector.fit_transform(data, targets)
    print("Pruning Features ... Pruned!")

    print("Data is of shape:", data.shape)
    quit()

    recursive_feature_pruner

    kBest = SelectKBest()

    tSVD = TruncatedSVD(n_components=50)
    pca = PCA(n_components=50)

    pipe = Pipeline([("kb", kBest),
                     ("svd", tSVD),
                     ("clf", clf)
                    ])
    pipe.fit_transform(data, targets)
    prediction = pipe.predict(data)
    pipe.score(data, targets)
