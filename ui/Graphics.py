import tkinter as tk
import time
import re
import random
import os
from PIL import Image, ImageTk
from lib.load_ai import get_positions

def check():
    # checks every 50 milliseconds for keyboard interrupts (ctrl+q)
    # quits if ctrl+q is pressed
    root.after(50, self.check)

class Window1:
    def __init__(self, master):
        # setting up first window (settings)
        self.master = master
        self.settings = tk.Frame(self.master)
        self.settings.grid()
        self.s_settings()
    def s_settings(self):
        # setting title
        tk.Label(self.settings, text = 'Settings', font = (None, 15)).grid( \
            row = 1, column = 1, columnspan = 2, pady = 10)
        # number of trials prompt
        tk.Label(self.settings, text = 'Number of trials: ').grid(row = 2, \
            column = 1, padx = 10, pady = 5, sticky = tk.W)
        # number of trials text box
        self.trials = tk.Entry(self.settings, width = 3)
        self.trials.grid(row = 2, column = 2, sticky = tk.W)
        # disabling and enabling accuracy bar
        def toggleslider():
            if self.activate == True:
                self.accuracy.config(state = 'disabled')
                self.accuracy.config(foreground = "gainsboro")
                self.activate = False
            else:
                self.accuracy.config(state = 'normal')
                self.accuracy.config(foreground = "black")
                self.activate = True
        # accuracy prompt
        tk.Label(self.settings, text = 'Accuracy: ').grid(row = 3, column = 1, \
            padx = 10, pady = 5, sticky = tk.W)
        # accuracy slider
        self.accuracy = tk.Scale(self.settings, orient = tk.HORIZONTAL, \
            resolution = 10, showvalue = 0, tickinterval = 10, length = 300)
        self.accuracy.grid(row = 3, column = 2, columnspan = 2, sticky = tk.W)
        self.activate = True
        self.checkaccuracy = tk.StringVar(self.settings)
        # check button for using accuracy of classifer
        # if checked, accuracy bar is disabled
        self.CA = tk.Checkbutton(self.settings, text = "Use accuracy of classifer.", \
            variable = self.checkaccuracy, onvalue = True, offvalue = False, \
            command = toggleslider)
        self.CA.grid(row = 4, column = 2, columnspan = 2, sticky = tk.W)
        # show prompt
        tk.Label(self.settings, text = 'Show: ').grid(row = 5, column = 1, \
            padx = 10, pady = 5,sticky = tk.W)
        tk.Label(self.settings, text = 'Note: default is one horse', \
            font = (None, 10)).grid(row = 7, column = 1, padx = 10, pady = 5, \
            sticky = tk.S + tk.W)
        # show check buttons - time, beyer, and show order
        self.showtime = tk.StringVar(self.settings)
        self.showbeyer = tk.StringVar(self.settings)
        self.showorder = tk.StringVar(self.settings)
        self.C1 = tk.Checkbutton(self.settings, text = "Time", variable = \
            self.showtime, onvalue = True, offvalue = False)
        self.C1.grid(row = 5, column = 2, sticky = tk.W)
        self.C2 = tk.Checkbutton(self.settings, text = "Beyer", variable = \
            self.showbeyer, onvalue = True, offvalue = False)
        self.C2.grid(row = 6, column = 2, sticky = tk.W)
        self.C3 = tk.Checkbutton(self.settings, text = "Complete Order", \
            variable = self.showorder, onvalue = True, offvalue = False)
        self.C3.grid(row = 7, column = 2, sticky = tk.W)
        # betting amount prompt
        tk.Label(self.settings, text = 'Betting Amount: ').grid(row = 8, \
            column = 1, padx = 10, pady = 5, sticky = tk.W)
        # betting amount options
        # enabling and disenabling text box for fixed option
        def enableEntry():
            self.betting.configure(state = "normal")
            self.betting.update()
        def disableEntry():
            self.betting.configure(state = "disabled")
            self.betting.update()
        self.betting = tk.Entry(self.settings, width = 3)
        self.betting.grid(row = 9, column = 2, padx = 100, sticky = tk.W)
        self.option_betting = tk.StringVar()
        # change betting option
        tk.Radiobutton(self.settings, variable = self.option_betting, \
            text = 'Change', value = 'Change',
            command = disableEntry).grid(row = 8, column = 2, sticky = tk.W)
        # fixed betting option
        tk.Radiobutton(self.settings, variable = self.option_betting, \
            text = 'Fixed', value = 'Fixed', 
            command = enableEntry).grid(row = 9, column = 2, sticky = tk.W)
        # purse size prompt
        tk.Label(self.settings, text = 'Purse Size: ').grid(row = 10, \
            column = 1, padx = 10, pady = 5, sticky = tk.W)
        # purse size entry box
        tk.Label(self.settings, text = '$').grid(row = 10, column = 2, \
            sticky = tk.W)
        self.purse = tk.Entry(self.settings, width = 5)
        self.purse.grid(row = 10, column = 2, sticky = tk.W, padx = 15)
        # number of horses prompt
        tk.Label(self.settings, text = 'Number of Horses: ').grid(row = 11, \
            column = 1, padx = 10, pady = 5, sticky = tk.W)
        # number of horses entry box
        self.horses = tk.Entry(self.settings, width = 3)
        self.horses.grid(row = 11, column = 2, sticky = tk.W)
        # time limit per race prompt
        tk.Label(self.settings, text = 'Time Limit per Race: ').grid(row = 12, \
            column = 1, padx = 10, pady = 5, sticky = tk.W)
        # time limit per race entry box
        self.time = tk.Entry(self.settings, width = 3)
        self.time.grid(row = 12, column = 2, sticky = tk.W)
        tk.Label(self.settings, text = 'minutes').grid(row = 12, column = 2, \
            padx = 30, sticky = tk.W)

        # submit button
        tk.Button(self.settings, text = 'Submit', command = self.instructions).grid \
        (row = 14, column = 1, columnspan = 2, pady = 10)

        # defaults
        # trails entry box
        self.trials.insert(0, 5)
        # accuracy slider
        self.accuracy.set(50)
        # use accuracy of classifer
        self.CA.deselect()
        # show time
        self.C1.deselect()
        # show beyer
        self.C2.deselect()
        # show order of horses
        self.C3.deselect()
        # betting options
        self.option_betting.set('Fixed')
        # fixed bet entry box
        self.betting.insert(0, 2)
        # purse size
        self.purse.insert(0, "{0:.02f}".format(25.00))
        # number of horses
        self.horses.insert(0, 3)
        # time per race
        self.time.insert(0, 15)

    def errorcheck(self):
        # checks to make sure the settings were correct
        elementlist = [self.trials.get(), self.accuracy.get(), \
        self.checkaccuracy.get(), self.showtime.get(), self.showbeyer.get(), \
        self.showorder.get(), self.purse.get(), self.betting.get(), \
        self.horses.get(), self.time.get()]

        for element in elementlist:
            # check if any element is empty
            if not element:
                error = tk.Tk()
                error.title("ERROR")
                error.bind('<Control-q>', quit)
                tk.Label(error, text = "Fill in all settings.", \
                    font = (None, 20)).pack(padx = 10, pady = 10)
                tk.Button(error, text = "OK", command = lambda : \
                    error.destroy()).pack(padx = 10, pady = 10)
                return False
            # check if purse is a float number
            elif element == self.purse.get():
                try:
                    float(element)
                except:
                    error = tk.Tk()
                    error.title("ERROR")
                    error.bind('<Control-q>', quit)
                    tk.Label(error, text = "Please correct format for purse.", \
                        font = (None, 20)).pack(padx = 10, pady = 10)
                    tk.Button(error, text = "OK", command = lambda : \
                        error.destroy()).pack(padx = 10, pady = 10)
                    return False
            # check if other elements are integers (not letters)
            elif element != self.showtime.get() or element != \
            self.showbeyer.get() or element != self.showorder.get():
                try:
                    int(element)
                except:
                    error = tk.Tk()
                    error.title("ERROR")
                    error.bind('<Control-q>', quit)
                    tk.Label(error, text = "Please enter integers.", \
                        font = (None, 20)).pack(padx = 10, pady = 10)
                    tk.Button(error, text = "OK", command = lambda : \
                        error.destroy()).pack(padx = 10, pady = 10)
                    return False
            else:
                return True

    def instructions(self):
        # screen that displays the instructions
        # checking if all entries are filled out
        if self.errorcheck():
            # saving data from settings
            self.trials1 = int(self.trials.get())
            self.accuracy1 = int(self.accuracy.get())
            self.checkaccuracy1 = self.checkaccuracy.get()
            self.showtime1 = self.showtime.get()
            self.showbeyer1 = self.showbeyer.get()
            self.showorder1 = self.showorder.get()
            self.purse1 = float(self.purse.get())
            self.purse1 = round(self.purse1, 2)
            self.betting_option = self.option_betting.get()
            # set fixed betting amount to 0 if betting option is change
            if not (self.betting.get()):
                self.betting1 = 0
            else:
                self.betting1 = int(self.betting.get())
            self.horses1 = int(self.horses.get())
            self.time1 = int(self.time.get())

            # checking values
            print("Trials: ", self.trials1, 
                "\nAccuracy: ", self.accuracy1,
                "\nCheck Accuracy: ", self.checkaccuracy1,
                "\nTime: ", self.showtime1,
                "\nBeyer: ", self.showbeyer1,
                "\nOrder: ", self.showorder1,
                "\nBetting Style: ", self.betting_option,
                "\nBetting Amount: ", self.betting1,
                "\nPurse: ", self.purse1,
                "\nNumber of Horses: ", self.horses1,
                "\nTime Limit per Race: ", self.time1)

            # clearing screen and making a new instructions window
            self.settings.destroy()
            root.destroy()
            self.window = tk.Tk()
            self.window.title("Horse Racing")
            self.window.bind('<Control-q>', quit)
            # find size of screen
            self.screen_width = self.window.winfo_screenwidth()
            self.screen_height = self.window.winfo_screenheight()
            # fit to screen
            self.window.geometry("%sx%s" % (self.screen_width, self.screen_height))

            # instructions frame
            self.instructions = tk.Frame(self.window)
            self.instructions.grid()
            self.instructions.grid_rowconfigure(0, weight = 1)
            self.instructions.grid_columnconfigure(0, weight = 1)
            # instructions label
            tk.Label(self.instructions, text = 'Welcome!\n Please decide the winner.'
                "\n You will have %s minutes per race. \nThere are %s races." 
                "\n Press start when you are ready."
                % (self.time1, self.trials1), font = (None, 50)).grid(row = 1, \
                column = 1, padx = (self.screen_width/4), pady = ((self.screen_height/4), 100))
            tk.Button(self.instructions, text = 'Start', font = (None, 25), \
                command = self.betting_screen).grid(row = 1, column = 1, sticky = tk.S)

    def generateforms(self):
        # creates forms with random horses
        # folder where forms are found
        folder = "split_jpgs"
        # randomly generate race forms
        pattern = re.compile(r'([A-Z]+)(\d+)_(\d+)_(\d*|header)?\.jpg')
        #race = random.choice(os.listdir(folder))
        race = "AJX170618_3_1.jpg"
        m = pattern.match(race)

        # get filepaths and make sure they exist before continuing
        sep = "_" if len(m.group(1)) < 3 else ""
        p = "data/" + m.group(1) + "/" + m.group(2) + "/" + m.group(1) + sep + \
            m.group(2) + "_SF.CSV"
        ltp = "data/" + m.group(1) + "/" + m.group(2) + "/" + \
              m.group(1) + sep + m.group(2) + "_" + m.group(3) + "_LT.CSV"
        lbp = "data/" + m.group(1) + "/" + m.group(2) + "/" + \
              m.group(1) + sep + m.group(2) + "_" + m.group(3) + "_LB.CSV"

        # find a race
        while not (os.path.isfile(p) and os.path.isfile(ltp) and os.path.isfile(lbp)):
            print("File doesn't exist! Trying again...")
            race = random.choice(os.listdir(folder))
            m = pattern.match(race)
            # get filepaths, and make sure they exist before continuing
            sep = "_" if len(m.group(1)) < 3 else ""
            p = "data/" + m.group(1) + "/" + m.group(2) + "/" + m.group(1) + sep + \
                m.group(2) + "_SF.CSV"
            ltp = "data/" + m.group(1) + "/" + m.group(2) + "/" + \
                  m.group(1) + sep + m.group(2) + "_" + m.group(3) + "_LT.CSV"
            lbp = "data/" + m.group(1) + "/" + m.group(2) + "/" + \
                  m.group(1) + sep + m.group(2) + "_" + m.group(3) + "_LB.CSV"


        # pick random horses and make a form
        string = "convert -append " + os.path.join(folder, m.group(1) + \
            m.group(2) + '_' + m.group(3) + "_header.jpg ")
        filenames = [f for f in os.listdir(folder) if f.endswith(".jpg") and \
        f.startswith(m.group(1) + m.group(2) + '_' + m.group(3)) and not \
        f.endswith("_header.jpg")]
        random.shuffle(filenames)
        nums = []
        for filename in sorted(filenames[:self.horses1]):
            string += os.path.join(folder, filename) + " "
            m = pattern.match(filename)
            nums += m.group(4)
        string += "test.jpg"

        os.system(string)

        # find horses in csv files
        self.superhorses = get_positions(m.group(1), m.group(2), m.group(3))
        self.horses_racing = []
        self.horses_odds = ""
        for horse in self.superhorses:
            if (horse['B_ProgNum'] in nums):
                self.horses_racing.append(horse)
        
        # find predicted winning horse
        self.horses_racing.sort(key = lambda x:x['L_Time'])
        self.horse_pwin = self.horses_racing[0]['B_Horse']
        # find actual winning horse
        self.horses_racing.sort(key = lambda x:x['L_Rank'])
        self.horse_win = self.horses_racing[0]['B_Horse']
        # find odds for horses
        self.horses_racing.sort(key = lambda x:x['B_ProgNum'])
        for horse in self.horses_racing:
            self.horses_odds += horse['B_Horse'] + " : " + horse['B_MLOdds'] + "\n  "

    def scrolledcanvas(self):
        # generate forms
        self.generateforms()

        # create a canvas for the form
        self.canv = tk.Canvas(self.bet, relief = 'sunken')
        self.canv.config(width = 1500, height = 1125)
        self.canv.config(highlightthickness = 0)

        # create a scroll bar to view the form
        sbarV = tk.Scrollbar(self.bet, orient = 'vertical', command = self.canv.yview)
        sbarV.grid(row = 0, column = 5, rowspan = 5, sticky = tk.N + tk.S + tk.W)
        self.canv.config(yscrollcommand = sbarV.set)

        # load the form onto the canvas and resize it to fit the screen
        self.canv.grid(row = 0, column = 0, rowspan = 5, sticky = tk.N + tk.S + tk.W + tk.E)
        self.im = Image.open("test.jpg")
        self.im = self.im.resize((1500, int((1500/self.im.width)*self.im.height)), \
            Image.ANTIALIAS)
        width, height = self.im.size
        self.canv.config(scrollregion = (0, 0, width, height))
        self.im2 = ImageTk.PhotoImage(self.im)
        self.imgtag = self.canv.create_image(0, 0, anchor = "nw", image = self.im2)

    def countdown(self):
        # countdown timer
        self.t -= 1
        mins, secs = divmod(self.t, 60)
        self.timeformat = '{:02d}:{:02d}'.format(mins, secs)
        self.timer_label['text'] = self.timeformat
        self.bet.after(1000, self.countdown)
        if self.t == -1:
            self.retrieving_data()

    def betting_screen(self):
        # check if result and instructions screen has been destroyed
        # destroy them if they are created to show new race
        try:
            if hasattr(self, 'result'):
                self.result.destroy()
        except AttributeError:
            pass
        # clear instructions screen
        try:
            if hasattr(self, 'instructions'):
                self.instructions.destroy()
        except AttributeError:
            pass
        # betting screen
        self.bet = tk.Frame(self.window)
        self.bet.grid()
        self.bet.grid_rowconfigure(0, weight = 1)
        self.bet.grid_columnconfigure(0, weight = 1)
        # set up for countdown timer
        self.t = self.time1 * 60
        self.timer_label = tk.Label(self.bet, textvariable = "", font = (None, 25), width = 10)
        self.timer_label.grid(row = 0, column = 5, padx = 10, pady = 10, sticky = tk.N + tk.E)
        self.countdown()
        # show forms
        self.scrolledcanvas()
        # drop down menu of horses
        self.horse_names = []
        for horse in self.horses_racing:
            self.horse_names.append(horse['B_Horse'])
        self.horsemenu = tk.StringVar(self.bet)
        self.horsemenu.set("Select horse")
        self.horse_select = tk.OptionMenu(self.bet, self.horsemenu, *self.horse_names)
        self.horse_select.config(font = (None, 20))
        # show race information on side
        tk.Label(self.bet, text = 'Purse Total: $%s\n\n\nBetting Amount: '
            '$%s\n\n\nOdds:\n  %s\n\n\nSystem recommendation: \n  '
        '%s\n\n\nHorse you want to bet on: ' %(format(self.purse1, '.2f'), \
            format(self.betting1, '.2f'), self.horses_odds, self.horse_pwin), \
            font = (None, 20), justify = 'left').grid(row = 0, column = 5, \
            padx = 40, pady = 10, sticky = tk.E)
        self.horse_select.grid(row = 0, column = 5, pady = (550, 50))
        # submit button
        tk.Button(self.bet, text = 'Submit', command = self.retrieving_data, \
            font = (None, 20)).grid(row = 0, column = 5, padx = 10, pady= 10, sticky = tk.S)

    def retrieving_data(self):
        # check how long the user took to submit
        print(self.timeformat)
        # check if a horse is selected
        if self.horsemenu.get() == "Select horse":
            error = tk.Tk()
            error.title("ERROR")
            error.bind('<Control-q>', quit)
            tk.Label(error, text = "Please select a horse.", font = \
                (None, 20)).pack(padx = 10, pady = 10)
            tk.Button(error, text = "OK", command = lambda : \
                error.destroy()).pack(padx = 10, pady = 10)
        else:
            # delete old frame
            self.bet.destroy()
            # variable to keep track if there are more races
            self.next_race = True
            # create a new window for retrieving data
            self.retrieve = tk.Tk()
            self.retrieve.title("Retrieving Data")
            self.retrieve.bind('<Control-q>', quit)
            tk.Label(self.retrieve, text = "Retrieving Data...", \
                font = (None, 50)).pack(padx = 10, pady = 10)
            # delete window after 2 seconds
            self.retrieve.after(2000, lambda: self.results())
            self.retrieve.mainloop()

    def update_purse(self):
        # updates the purse
        # take away money used to bet
        self.purse1 -= self.betting1
        # if bet on the right horse, calculate winnings
        if self.horse_win == self.horsemenu.get():
            for horse in self.superhorses:
                if horse['B_Horse'] == self.horsemenu.get():
                    odds = horse['B_MLOdds'].split('-')
            if self.betting1 != '0':
                self.purse1 = ((self.betting1 * float(odds[0])) / \
                    float(odds[1])) + self.purse1

    def results(self):
        # displays the results of the race
        # destroy the retrieving screen and create a new screen for results
        self.retrieve.destroy()
        self.result = tk.Frame(self.window)
        self.result.grid()
        self.result.grid_rowconfigure(0, weight = 1)
        self.result.grid_columnconfigure(0, weight = 1)
        # result labels
        tk.Label(self.result, text = 'Results', font = (None, 35)).grid(row = 0, \
            column = 0, padx = ((self.screen_width/2.5), 10), pady = \
            ((self.screen_height/3), 10))
        tk.Label(self.result, text = 'Actual result: %s' % (self.horse_win), \
            font = (None, 25)).grid(row = 2, column = 0, padx = \
            ((self.screen_width/2.5), 10), pady= 10)
        tk.Label(self.result, text = 'System\'s choice: %s' % (self.horse_pwin), \
            font = (None, 25)).grid(row = 3, column = 0, padx = \
            ((self.screen_width/2.5), 10), pady= 10)
        tk.Label(self.result, text = 'Your choice: %s'% (self.horsemenu.get()), \
            font = (None, 25)).grid(row = 4, column = 0, padx = \
            ((self.screen_width/2.5), 10), pady= 10)
        # update the users purse
        self.update_purse()
        tk.Label(self.result, text = 'Updated Purse: $%s' % (format(self.purse1, '.2f')), \
            font = (None, 25)).grid(row = 5, column = 0, padx = \
            ((self.screen_width/2.5), 10), pady= 10)
        # check if there are more races to display 'next race' or 'exit'
        if self.trials1 == 1:
            tk.Button(self.result, text = 'Exit', font = (None, 20), command = \
                self.exit).grid(row = 6, column = 0, padx = \
                ((self.screen_width/2.5), 10), pady = 10)
        else:
            tk.Button(self.result, text = 'Next Race', font = (None, 20), command = \
                self.races).grid(row = 6, column = 0, padx = \
                ((self.screen_width/2.5), 10), pady = 10)

    def races(self):
        # if there are more races, decrement trials and load another race
        if self.trials1 > 0:
            self.betting_screen()
            self.trials1 -= 1

    def exit(self):
        # destroy result screen and make a new exit screen
        self.result.destroy()
        self.exit = tk.Frame(self.window)
        self.exit.grid()
        self.exit.grid_rowconfigure(0, weight = 1)
        self.exit.grid_columnconfigure(0, weight = 1)
        # instructions for what to do next
        tk.Label(self.exit, text = 'Thank you!\nPlease notify the researcher.', \
            font = (None, 50)).grid(row = 0, column = 1, columnspan = 2, \
            padx = ((self.screen_width/3), 100), pady = ((self.screen_height/3), 10))
        # instructions for inserting ID number
        tk.Label(self.exit, text = 'Please enter ID number in order to save.').grid\
        (row = 2, column = 1, columnspan = 2, padx = ((self.screen_width/3), 100))
        self.save = tk.Entry(self.exit, width = 30)
        self.save.grid(row = 3, column = 1, columnspan = 2, padx = ((self.screen_width/3), 100))
        # save button
        tk.Button(self.exit, text = 'Save', font = (None, 15), command = \
            self.checksave).grid(row = 4, column = 1, columnspan = 2, \
            padx = ((self.screen_width/3), 50), pady = 10)

    def checksave(self):
        # check the ID number
        # if ID number is -0, don't save
        # otherwise, save
        # check if -0 
        if self.save.get() == "-0":
            print("NO SAVE")
            self.exit.destroy()
            self.window.destroy()
        # check if no entry
        elif self.save.get() == "":
            error = tk.Tk()
            error.title("ERROR")
            error.bind('<Control-q>', quit)
            tk.Label(error, text = "Please insert ID number.", font = \
                (None, 20)).pack(padx = 10, pady = 10)
            tk.Button(error, text = "OK", command = lambda : \
                error.destroy()).pack(padx = 10, pady = 10)
        # save if pass all tests
        else:
            # check if entry is numbers
            try:
                int(self.save.get())
                print("SAVE")
                self.exit.destroy()
                self.window.destroy()
            except ValueError:
                error = tk.Tk()
                error.title("ERROR")
                error.bind('<Control-q>', quit)
                tk.Label(error, text = "Please insert numbers.", font = \
                    (None, 20)).pack(padx = 10, pady = 10)
                tk.Button(error, text = "OK", command = lambda : \
                    error.destroy()).pack(padx = 10, pady = 10)

root = tk.Tk()

def run():
    root.title("Horse Racing")
    root.geometry("500x425")
    root.bind('<Control-q>', quit)
    app = Window1(root)
    root.mainloop()

if __name__ == "__main__":
    run()
