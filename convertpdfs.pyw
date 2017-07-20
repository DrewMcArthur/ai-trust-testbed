import os
import random
import re
from PIL import Image

folder = "data/split"
folder2 = "data/split_jpgs"
if not os.path.exists(folder2):
    os.makedirs(folder2)

# convert pdfs to jpgs
for filename in [f for f in os.listdir(folder) if f.endswith(".pdf") and os.path.isfile(os.path.join(folder, f))]:
    filepath = os.path.join(folder, filename)
    os.system("convert -density 300 " + filepath + " -quality 100 " + os.path.join(folder2, filename.replace(".pdf", ".jpg")))
    if not filename.endswith('_header.pdf'):
        col = Image.open(os.path.join(folder2, filename.replace(".pdf", ".jpg")))
        gray = col.convert('L')
        bw = gray.point(lambda x: 0 if x<220 else 255, '1')
        bw.save(os.path.join(folder2, filename.replace(".pdf", ".jpg")))