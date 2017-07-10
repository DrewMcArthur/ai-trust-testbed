""" This is the main program.  Running this starts the software.
    Drew McArthur, Judy Zhou, Geo Engel, and Risa Ulinski
    6/23/17                                                         """

from ui import Graphics
import os

def main():
    Graphics.run()
    os.remove('test.jpg')


if __name__ == "__main__":
    main()
