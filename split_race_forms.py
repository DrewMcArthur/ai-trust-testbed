"""
    Splits race forms into individual horses and headers using PyPDF2 and pdfminer3k
"""

import os
import sys
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTLine, LTTextLine
import PyPDF2
import re

horse_num = None
race_num = None


def get_horse_num(layout, y1, y2):
    horsepat = re.compile(r'([1-9][0-9]?[a-c]?)[ A-Za-z0-9]{0,30}')
    for lt_obj in layout:
        if (isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine)) and y2 > lt_obj.bbox[1] > y1 \
                and lt_obj.bbox[3]-lt_obj.bbox[1] > 25 and horsepat.fullmatch(lt_obj.get_text().strip()):
            global horse_num
            horse_num = horsepat.fullmatch(lt_obj.get_text().strip()).group(1)
            print(horse_num)
            return
        if isinstance(lt_obj, LTTextLine) and y2 > lt_obj.bbox[1] > y1 and lt_obj.bbox[3]-lt_obj.bbox[1] > 25:
            print(lt_obj.bbox)
            print(y1)
            print(lt_obj.get_text())
        elif hasattr(lt_obj, '__iter__') and y2 > lt_obj.bbox[1] > y1:
            get_horse_num(lt_obj, y1, y2)


def get_race_num(layout, y1, y2):
    racepat = re.compile(r'.*([1-9][0-9]?) .* [1-9][0-9]*.?.?.? (Furlongs?|MILES?|YARDS) .*', re.DOTALL)
    print('getting race number')
    for lt_obj in layout:
        if isinstance(lt_obj, LTTextBox) and lt_obj.bbox[1] + 30 > y1 and racepat.match(lt_obj.get_text()):
            global race_num
            print(lt_obj.get_text())
            race_num = racepat.match(lt_obj.get_text()).group(1)
            print(race_num)
            return
        if isinstance(lt_obj, LTTextBox) and lt_obj.bbox[1] + 30 > y1:
            print(lt_obj.bbox)
            print(y1)
            print(lt_obj.get_text())
        elif hasattr(lt_obj, '__iter__') and lt_obj.bbox[1] + 15 > y1:
            get_race_num(lt_obj, y1, y2)


def find_lines(layout):
    # Gets the y coordinates of the horizontal lines in a page of a races form and adds them
    # to global variable ycoords, to be used to split the pdf.
    # Also checks if the page starts with a header.
    racepat = re.compile(r'.*([1-9][0-9]?) .* [1-9][0-9]*.?.?.? (Furlongs?|MILES?|YARDS) .*', re.DOTALL)
    for lt_obj in layout:
        if isinstance(lt_obj, LTLine) and lt_obj.bbox[1] == lt_obj.bbox[3] and \
                        lt_obj.bbox[0] < 25 and 612-lt_obj.bbox[2] < 30:
            ycoords.append(lt_obj.bbox[1])
        elif isinstance(lt_obj, LTTextBox) and racepat.match(lt_obj.get_text()):
            print('has header')
            global new_race
            new_race = True
        elif hasattr(lt_obj, '__iter__'):
            find_lines(lt_obj)


def find_endofpage(layout, index):
    # Finds the y coordinate of the last line of text on the page.
    global end_index
    for lt_obj in layout:
        if isinstance(lt_obj, LTTextBox) and lt_obj.bbox[1] < index and ('TRAINER: ' in lt_obj.get_text()):
            end_index = lt_obj.bbox[3]
            return
        elif isinstance(lt_obj, LTTextBox) and lt_obj.bbox[1] < index and ('WORKS:' in lt_obj.get_text()) \
                and 8 < lt_obj.bbox[3]-lt_obj.bbox[1] < 12:
            end_index = lt_obj.bbox[3] - 10
            return
        elif isinstance(lt_obj, LTTextBox) and lt_obj.bbox[1] < index:
            print(lt_obj.get_text())
            print(lt_obj.bbox)
        elif hasattr(lt_obj, '__iter__'):
            find_endofpage(lt_obj, index)


def split_pdf(filename):
    # Splits a race form into individual horses and headers.
    # extract the track abbreviation and date using regular expression
    prog = re.compile(r'([A-Z]+)--(\d+)-(\d+)-(\d+) ?\(?(\d*)\)?\.pdf')
    m = prog.match(filename)
    race_date = m.group(1) + m.group(4)[-2:] + m.group(2) + m.group(3) + '_'
    # open pdf for reading
    fp = open(os.path.join(folder, filename), 'rb')
    # set up the pdfminer parser to be used to extract the location of the y coordinates
    parser = PDFParser(fp)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # set up loop variables
    global end_index
    global new_race
    global race_num
    global horse_num
    page_num = 0
    end_index = None
    new_race = False
    # set up PyPDF2 reader to split the race forms
    reader = PyPDF2.PdfFileReader(fp)
    for page in doc.get_pages():
        # split each page in the race form
        print(page_num)
        # get the y coordinates
        global ycoords
        ycoords = []
        interpreter.process_page(page)
        layout = device.get_result()
        find_lines(layout)
        page = reader.getPage(page_num)
        if new_race:
            # Extract header if there is one
            new_race = False
            race_num = None
            writer = PyPDF2.PdfFileWriter()
            page.mediaBox.upperRight = (page.mediaBox[2], ycoords.pop(0))
            page.mediaBox.lowerLeft = (page.mediaBox[0], ycoords.pop(0))
            print(page.mediaBox)
            get_race_num(layout, page.mediaBox[1], page.mediaBox[3])
            out_file = race_date + race_num + '_header.pdf'
            out_file = os.path.join(new_folder, out_file)
            writer.addPage(page)
            with open(out_file, 'wb') as outfp:
                writer.write(outfp)
        while len(ycoords) > 1:
            # get each horse from the page
            writer = PyPDF2.PdfFileWriter()
            top = ycoords.pop(0)
            page.mediaBox.upperRight = (page.mediaBox[2], top)
            page.mediaBox.lowerLeft = (page.mediaBox[0], ycoords[0])
            horse_num = None
            get_horse_num(layout, page.mediaBox[1], page.mediaBox[3])
            writer.addPage(page)
            out_file = os.path.join(new_folder, race_date + race_num + '_' + horse_num + '.pdf')
            with open(out_file, 'wb') as outfp:
                writer.write(outfp)
        # get the last horse of the page
        top = ycoords.pop(0)
        find_endofpage(layout, top)
        writer = PyPDF2.PdfFileWriter()
        page.mediaBox.upperRight = (page.mediaBox[2], top)
        page.mediaBox.lowerLeft = (page.mediaBox[0], end_index - 10)
        get_horse_num(layout, page.mediaBox[1], page.mediaBox[3])
        writer.addPage(page)
        out_file = os.path.join(new_folder, race_date + race_num + '_' + horse_num + '.pdf')
        with open(out_file, 'wb') as outfp:
            writer.write(outfp)
        page_num += 1


ycoords = []
new_race = False
end_index = None
folder = 'test_forms'
if len(sys.argv) > 1:
    folder = sys.argv[1]
else:
    pass
new_folder = 'split'
if not os.path.exists(new_folder):
    os.makedirs(new_folder)
# split each race form in folder
for filename in [f for f in os.listdir(folder) if f.endswith(".pdf") and os.path.isfile(os.path.join(folder, f))]:
    print(filename)
    split_pdf(filename)
