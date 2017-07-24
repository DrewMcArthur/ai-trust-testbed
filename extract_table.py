"""
NOTE: needs Tabula and pdfminer installed to run
reads in pdfs from '0000 for Risa' and converts them to csvs, putting the
the ones that aren't missing data into matched_pairs
For each pdf
- renames the pdf
- extracts the location of the table in the pdf using pdfminer
- uses tabula to extract the table
- checks that tabula and pdfminer found the same list of horses
- once all pdfs have been converted, finds the ones without missing data and
    copies them to matched_pairs
"""

from tabula import read_pdf
import pandas as pd
import os.path
import sys
import shutil
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
import os
import re
import csv


incorrectfiles = 'wrong'
if not os.path.exists(incorrectfiles):
    os.makedirs(incorrectfiles)
pathname = os.path.join("C:", "Users", "rulinski", "Documents", "test")
inputfolder = '0000 for Risa'
write_flag = False
all_csvs = 'result_csvs'
all_csvs_list = [f for f in os.listdir(all_csvs) if f.endswith('.csv') and os.path.isfile(os.path.join(all_csvs, f))]

race_abbrev = {'ALB':   'Albuquerque',
              'AJX':    'Ajax',
              'ARP':    'Arapahoe',
              'AP':     'Arlington',
              'ASD':    'Assiniboia',
              'BEL':    'Belmont',
              'BTP':    'Belterra',
              'BCF':    'Brown County',
              'CMR':    'Camarero',
              'CBY':    'Canterbury',
              'CT':     'Charles Town',
              'CPW':    'Chippewa\nDowns',
              'CD':     'Churchill',
              'DEL':    'Delaware',
               'DED':    'Delta Downs',
               'UN':     'Union',
               'EMD':    'Emerald',
               'EVD':    'Evangeline',
               'FAI':    'Fair Hill',
               'FMT':    'Fair Meadows',
               'FP':     'Fairmount',
               'FL':     'Finger Lakes',
               'FON':    'Fonner Park',
               'FE':     'Fort Erie',
               'FTP':    'Fort Pierre',
               'GG':     'Golden Gate',
               'GRP':    'Grants Pass',
               'GRM':    'Great Meadow',
               'GP':     'Gulfstream',
               'HST':    'Hastings',
               'HP':     'Hazel Park',
               'IND':    'Indiana Downs',
               'JRM':    'Jerome',
               'LBT':    'Laurel Brown',
               'LRL':    'Laurel',
               'LBG':    'Lethbridge',
               'LEX':    'Lexington',
               'LS':     'Lone Star',
               'LA':     'Los Alamitos',
               'LAD':    'La. Downs',
               'MAL':    'Malvern',
               'MD':     'Marquis',
               'MC':     'Miles City',
               'MTH':    'Monmouth',
               'MNR':    'Mountaineer',
               'NP':     'Northlands',
               'OTP':    'Oak Tree\nat PLN',
               'PRX':    'Parx',
               'PEN':    'Penn National',
               'PW':     'Percy Warner',
               'PIM':    'Pimlico',
               'POD':    'Pocatello\nDowns',
               'PRM':    'Prairie Mdw',
               'PID':    'Presque\nIsle Downs',
               'RP':     'Remington',
               'RET':    'Retama Park',
               'RUI':    'Ruidoso',
               'HOU':    'Sam Houston',
               'SA':     'Santa Anita',
               'SDY':    'Sandy',
               'SON':    'Sonoita',
               'SUD':    'Sun Downs',
               'SRP':    'SunRay Park',
               'TAM':    'Tampa Bay',
               'TDN':    'Thistledown',
               'TUP':    'Turf Paradise',
               'WEB':    'Weber Downs',
               'WBR':    'Weber Downs',
               'WRD':    'Will Rogers',
               'WIL':    'Willowdale',
               'WNT':    'Winterthur',
               'WO':     'Woodbine',
               'WYO':    'Wyo Downs'}
months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER",
          "OCTOBER", "NOVEMBER", "DECEMBER"]
races = ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH",
         "ELEVENTH", "TWELFTH", "THIRTEENTH", "FOURTEENTH", "FIFTEENTH", "SIXTEENTH", "SEVENTEENTH",
         "EIGHTEENTH", "NINETEENTH", "TWENTIETH"]
timefolder = 'Time'
beyerfolder = 'Beyer Figure'
beyer_ending = '_lb.pdf'
time_ending = '_lt.pdf'
extension = '.pdf'
LENGTH = 600
WIDTH = 375


def parse_layout(layout, horseindex, horsenames, top, bottom, *args):
    # checks a pdfminer layout for a given list of words, extracts a list of the horses that raced
    # and returns a list of the words that weren't in the pdf, as well as a list of the horses
    # and the top and bottom indices of the table.
    for lt_obj in layout:
        if isinstance(lt_obj, LTTextBox) and horseindex is None and 'Horse' == lt_obj.get_text().strip():
            horseindex = lt_obj.bbox[0]
        elif isinstance(lt_obj, LTTextBox) and "OFF AT " in lt_obj.get_text():
            print(lt_obj.bbox)
            bottom = LENGTH-float(lt_obj.bbox[1])
        elif isinstance(lt_obj, LTTextBox) and 'Last Raced' in lt_obj.get_text():
            top = LENGTH-float(lt_obj.bbox[3])
        elif isinstance(lt_obj, LTTextLine) and lt_obj.get_text().strip() != 'Horse' and lt_obj.bbox[0] == horseindex:
            horsenames.append(lt_obj.get_text().strip())
        elif (isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine)) and \
                any(word in lt_obj.get_text() for word in args):
            args = [i for i in args if i not in lt_obj.get_text()]
        if hasattr(lt_obj, '__iter__'):
            parse_layout(lt_obj, horseindex, horsenames, top, bottom, *args)
    return args, horsenames, top, bottom


def rename_file(filename, path):
    # given a file and a path to a pdf downloaded from drf.com with either the time
    # or beyer figure results from a race (ex. TUP--04-30-2017 (1).pdf) extracts the
    # name, date, and number of the race, as well as the horses that ran in it, checks
    # that the former matches the filename, and renames the file.
    #  (ex. TUP170430_2_lb.pdf (beyer figure) or TUP170430_2_lt.pdf (time)).
    # returns the list of horses and the new filename as a tuple or None if the name doesn't
    # match the file contents.
    if write_flag:
        fw = open('new_pdfs.txt', "w")
    # group: 0-filename, 1-track, 2-month, 3-day, 4-year, 5-race number
    progN = re.compile(r'([A-Z]+)(\d{2})(\d{2})(\d{2})_(\d+)_(l[bt])\.pdf') # if file is already renamed
    prog = re.compile(r'([A-Z]+)--(\d+)-(\d+)-(\d+) ?\(?(\d*)\)?\.pdf')     # if file hasn't yet been renamed
    if progN.fullmatch(filename):
        m = progN.match(filename)
        num = int(m.group(5))
        date = months[int(m.group(3)) - 1] + ' ' + str(int(m.group(4)) + ',  20'+m.group(2))
        track = race_abbrev[m.group(1)]
        new_name = filename
    elif prog.fullmatch(filename):
        m = prog.match(filename)
        num = m.group(5)
        if num == '':
            num = 1
        else:
            num = int(num) + 1
        date = months[int(m.group(2)) - 1] + ' ' + str(int(m.group(3))) + ',  ' + m.group(4)
        track = race_abbrev[m.group(1)]
        new_name = m.group(1) + m.group(4)[-2:] + m.group(2) + m.group(3) + "_" + str(num)
        if timefolder in path:
            new_name += time_ending
        else:
            new_name += beyer_ending
        shutil.copy(os.path.join(path, filename), os.path.join(new_pdf_folder, new_name))
    else:
        shutil.copy(os.path.join(path, filename), os.path.join(incorrectfiles, filename))
        return None, None, None, None
    if new_name.replace('.pdf','.csv') in all_csvs_list:
        return None, None, None, None
    race = races[num - 1]
    # open file as a pdfminer layout to be parsed
    fp = open(os.path.join(path, filename), 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    unmatched = None
    horses = None
    top = None
    bottom = None
    # parse the pdf to make sure the name, date, and track match, and get a list of the horse names
    for page in doc.get_pages():
        if unmatched or horses:
            break
        interpreter.process_page(page)
        layout = device.get_result()
        unmatched, horses, top, bottom = parse_layout(layout, None, [], None, None, race, date, track)
    # copy the file to a new folder with the corrected file name if it contained the key words
    fp.close()
    if unmatched == []:
        if write_flag:
            fw.write(new_name + "\n")
        else:
            return horses, new_name, top, bottom
    else:
        shutil.copy(os.path.join(path, filename), os.path.join(incorrectfiles, filename))
        return None, None, None, None

if len(sys.argv) > 1:
    inputfolder = sys.argv[1]

new_csvs_folder = "new_csvs"
if not os.path.exists(new_csvs_folder):
    os.makedirs(new_csvs_folder)
new_pdf_folder = 'renamed_pdfs'
issues = 'issues'
header_only = 'header only'
if not os.path.exists(issues):
    os.makedirs(issues)
if not os.path.exists(new_csvs_folder):
    os.makedirs(new_csvs_folder)
if not os.path.exists(new_pdf_folder):
    os.makedirs(new_pdf_folder)
newcsvfiles = []
for dirpath, dirnames, filenames in os.walk(inputfolder):
    for filename in [f for f in filenames if f.endswith(".pdf")]:
        print(filename)
        horses, new_name, top, bottom = rename_file(filename, dirpath)
        if new_name is None or new_name.replace('.pdf','.csv') in newcsvfiles:
            continue
        if new_name.endswith("_lt.pdf"):
            col = [0, 59, 123, 227, 255, 283, 337]
        else:
            col = [0, 60, 124, 146, 170, 187, 204, 221, 255.5, 272, 289, 306, 323, 344]
        df = read_pdf(os.path.join(new_pdf_folder, new_name), guess=False, area=[top, 0, bottom, WIDTH], columns=col,
                      encoding='latin1')
        if horses is not None and 'Horse' in df:
            df = df[df['Horse'].isin(horses)]
            if horses == []:
                df.to_csv(os.path.join(header_only, new_name.replace('.pdf', '.csv')), index=False)
            elif df['Horse'].tolist() == horses:
                df.to_csv(os.path.join(all_csvs, new_name.replace('.pdf', '.csv')), index=False)
                newcsvfiles.append(new_name.replace('.pdf', '.csv'))
            else:
                shutil.copy(os.path.join(new_pdf_folder, new_name), os.path.join(issues, new_name))
        else:
            shutil.copy(os.path.join(new_pdf_folder, new_name), os.path.join(issues, new_name))

csvpath = 'result_csvs'
badcsvs = 'horsesdontmatchcsv'
goodcsvs = 'new_matched_pairs'
if not os.path.exists(goodcsvs):
    os.makedirs(goodcsvs)
if not os.path.exists(badcsvs):
    os.makedirs(badcsvs)

time = [f for f in os.listdir(csvpath) if f.endswith("_lt.csv") and f not in os.listdir('matched_pairs')]
print(time)
horseName = re.compile(r'.{0,2}?([A-Za-z 0-9\'.\-]*)')
flag = False
for tfile in time:
    bfile = tfile.replace("_lt.csv", "_lb.csv")
    if os.path.isfile(os.path.join(csvpath, bfile)):
        with open(os.path.join(csvpath, tfile)) as timecsv:
            with open(os.path.join(csvpath, bfile)) as beyercsv:
                tr = csv.DictReader(timecsv)
                br = csv.DictReader(beyercsv)
                blist = []
                tlist = []
                for row in tr:
                    if 'Fin' not in row.keys() or row['Fin'].strip() == "":
                        flag = True
                        break
                    tlist.append(horseName.match(row['Horse']).group(1))
                for row in br:
                    if 'Chart' not in row.keys() or row['Chart'].strip() == "":
                        flag = True
                        break
                    blist.append(horseName.match(row['Horse']).group(1))
                if tlist != blist:
                    flag = True
        if flag:
            shutil.copy(os.path.join(csvpath, tfile), os.path.join(badcsvs, tfile))
            shutil.copy(os.path.join(csvpath, bfile), os.path.join(badcsvs, bfile))
        else:
            shutil.copy(os.path.join(csvpath, tfile), os.path.join(goodcsvs, tfile))
            shutil.copy(os.path.join(csvpath, bfile), os.path.join(goodcsvs, bfile))
    flag = False

