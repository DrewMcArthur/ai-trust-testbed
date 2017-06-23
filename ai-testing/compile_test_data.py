import yaml, csv, os
from compile_data import get_race_info

if __name__ == "__main__":
    DATA = "test-data/"
    FN = "TEST.data.csv"
    NDATA = 0
    config = yaml.safe_load(open("config.yml"))
    headers = config['input_data_col_headers'].split(', ')
    headers[-1] = headers[-1][:-1]

    print(headers)

    with open(FN, 'w') as F:
        w = csv.DictWriter(F, fieldnames=headers,
                          extrasaction='ignore',dialect='unix')
        w.writeheader()

        raceInfo = {}
        for fn in os.listdir(DATA):
            if fn.endswith('.csv'):
                with open(DATA+fn) as f:
                    r = csv.DictReader(f, dialect='unix')
                    print("Reading file", fn)
                    for row in r:
                        if row['R_RCTrack'] == "":
                            row.update(raceInfo)
                        else:
                            raceInfo = get_race_info(row)
                        row.update({"ID": NDATA})
                        w.writerow(row)
                        NDATA += 1
