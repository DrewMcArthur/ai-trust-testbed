import yaml, csv
from ai.learn import read_data, read_output, split_data, ColWiseEncoder
from sklearn.preprocessing import OneHotEncoder, Imputer
from sklearn.feature_selection import SelectKBest

config = yaml.safe_load(open("./config.yml"))

data = read_data(config['final_data_filename'])
targets = read_output("LABELS." + config['final_data_filename'], data)

print("Read data.")

cat_feats = [eval(x) for x in config['data_is_categorical'][:-1].split(', ')]

cwe = ColWiseEncoder(cat_feats)
imp = Imputer(strategy='most_frequent')
ohe = OneHotEncoder(categorical_features=cat_feats, 
                    handle_unknown='ignore')
skb = SelectKBest(k=1750)

print("Created Objects.")

training = cwe.fit_transform(data)
training = imp.fit_transform(training)
training = ohe.fit_transform(training)
training = skb.fit_transform(training)

print("Tranformed Data.")

f = open("training.csv", 'w')
w = csv.writer(f, dialect='unix')
for row in training:
    w.writerow(row)

print("Wrote data to file.")
