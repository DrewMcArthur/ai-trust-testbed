import yaml, csv
from ai.learn import read_data, read_output, split_data
from ai.compare import ColWiseEncoder
from sklearn.preprocessing import OneHotEncoder, SelectKBest

config = yaml.safe_load(open("./config.yml"))

data = read_data(config['final_data_filename'])
targets = read_output("LABELS." + config['final_data_filename'], data)

print("Read data.")

cwe = ColWiseEncoder()
ohe = OneHotEncoder(categorical_features=cat_feats, 
                    handle_unknown='ignore')
skb = SelectKBest(k=1750)

print("Created Objects.")

training = cwe.fit_transform(data)
training = ohe.fit_transform(training)
training = skb.fit_transform(training)

print("Tranformed Data.")

f = open("training.csv", 'w')
w = csv.writer(f, dialect='unix')
for row in training:
    w.writerow(row)

print("Wrote data to file.")
