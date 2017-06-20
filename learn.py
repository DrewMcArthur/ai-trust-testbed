""" 
 *  Drew McArthur
 *  6/14/17
 *  testing out sklearn on horse racing data
"""

from sklearn import metrics
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
        r.sort(key=lambda x:x[0])
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
                r.append((row['ID'], int(row['L_BSF'])))
        r.sort(key=lambda x:x[0])
        return [x[1] for x in r]

def split_data(d, l, r):
    """ d=data, l=labels, r=ratio
        returns a tuple, of two lists, x and y where x is r% of d, 
        randomly chosen """
    len_test = round(len(d) * (1 - r))
    test = []
    testlabels = []
    for _ in range(len_test):
        i = random.randrange(len(d))
        test.append(d.pop(i))
        testlabels.append(l.pop(i))
    return ((d,l), (test,testlabels))

if __name__ == "__main__":
    config = yaml.safe_load(open("./config.yml"))

    #print("Loading Data ... ", end='\r')
    data = read_data(config['final_data_filename'])
    targets = read_output("LABELS." + config['final_data_filename'], data)
    #print("Loading Data ...................... Loaded!")

    
    for n in range(10,1500):
        #print("Splitting training data ... ", end='\r')
        training, test = split_data(data, targets, .95)
        tData, tLabels = training
        testData, testLabels = test
        #print("Splitting training data ........... Split!")

        #print("Hashing Features ... ", end='\r')
        fh = FeatureHasher(input_type='string')
        tData = fh.fit_transform(tData, tLabels)
        testData = fh.transform(testData)
        #print("Hashing Features .................. Hashed!")

        #print("Continuizing Discrete Variables ... ", end='\r')
        # TODO: get array of indices that represents which columns are categorical
        #cat_feats = []
        #enc = OneHotEncoder(categorical_features=cat_feats)
        #tData = enc.fit_transform(tData)
        #testData = enc.transform(testData)
        #print("Continuizing Discrete Variables ... Continuized!")

        #print("Pruning Features ... ", end='\r')
        kBest = SelectKBest(k=n)
        tData = kBest.fit_transform(tData, tLabels)
        testData = kBest.transform(testData)
        #print("Pruning Features .................. Pruned!")

        #print("Dimensions of data:")
        #print("    data: [{}]".format(data.shape))
        #print(" targets: [{}]".format(len(targets)))

        # TODO split training data with labels, 
        # fit estimator on training, then predict on test data
        #print("Fitting Data ... ", end='\r')
        estimator = SVR(kernel="linear", epsilon=0.05)
        estimator.fit(tData, tLabels)
        #print("Fitting Data ...................... Fit!")

        #print("Predicting Outcomes ... ", end='\r')
        preds = estimator.predict(testData)
        #print("Predicting Outcomes ............... Predicted!")

        deltas = [abs(p-l) for p, l in zip(preds, testLabels)]
        #for p, l in zip(preds, testLabels):
            # input, output = data # (test, testlabels) from split_data
            # write to file the outputs
            #print("Guess: {:.2f},   Actual: {},  delta: {:.2f}.".format(p,l,p-l))
            #deltas.append(abs(p-l))

        print()
        print("With {} features selected: ".format(n))
        print("     average delta:", sum(deltas)/len(deltas))
        print("explained variance:",metrics.explained_variance_score(testLabels, preds))
        print("        mean error:",metrics.mean_absolute_error(testLabels, preds))
        print("      mean^2 error:",metrics.mean_squared_error(testLabels, preds))
        print("      median error:",metrics.median_absolute_error(testLabels, preds))
        print("               r^2:",metrics.r2_score(testLabels, preds))
        print()

    quit()

    selector = RFECV(estimator)
    data = selector.fit_transform(data, targets)

    tSVD = TruncatedSVD(n_components=50)
    pca = PCA(n_components=50)

    pipe = Pipeline([("kb", kBest),
                     ("svd", tSVD),
                     ("clf", clf)
                    ])
    data = pipe.fit_transform(data, targets)
