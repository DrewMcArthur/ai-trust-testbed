import os
import random
import re
from PIL import Image

folder = "data/split"
folder2 = "data/split_jpgs"
if not os.path.exists(folder2):
    os.makedirs(folder2)

# convert pdfs to jpgs
for filename in [f for f in os.listdir(folder) \
                if f.endswith(".pdf") and os.path.isfile(os.path.join(folder, f)) \
                   and not os.path.isfile(os.path.join(folder2, f.replace(".pdf", ".jpg")))]:
    filepath = os.path.join(folder, filename)
    print(filename)
    os.system("convert -black-threshold 100% -density 600 " + filepath + 
        " -quality 100 " + os.path.join(folder2, filename.replace(".pdf", ".jpg")))