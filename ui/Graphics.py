import tkinter as tk
import time
import re
import random
import os
from PIL import Image, ImageTk
from lib.load_ai import get_positions
import pickle

def check():
    # checks every 50 milliseconds for keyboard interrupts (ctrl+q)
    # quits if ctrl+q is pressed
    root.after(50, self.check)

class MainWindow:
    
    def __init__(self, master):
        # setting up first window (settings)
        self.master = master
        self.settings = tk.Frame(self.master)
        self.settings.grid()
        self.s_settings()

    class Settings:
        def save(self, filename):
            pickle.dump({i: getattr(self,i) for i in self.__dict__ if not callable(getattr(self, i)) and not i.startswith('__')},\
                        open(os.path.join(self.path,filename + '_s.p'), 'wb'))

        def load(self, filename):
            temp = pickle.load(open(os.path.join(self.path,filename+'_s.p'), 'rb'))
            print(temp)
            for i in temp.keys():
                setattr(self, i, temp[i]) 

    def load_settings(self, event):
        if os.path.isfile(os.path.join(self.Settings.path, self.defaultmenu.get() + '_s.p')):
            self.Settings.load(self.Settings,self.defaultmenu.get())
            self.set_all_defaults()

    def set_all_defaults(self):
        # trials entry box
        self.trials.delete(0, 'end')
        self.trials.insert(0, self.Settings.trials)

        # accuracy slider
        self.accuracy.set(self.Settings.accuracy)

        # use accuracy of classifer
        if not self.Settings.checkaccuracy:
            self.CA.deselect()
        else:
            self.CA.select()

        # show time
        if not self.Settings.showtime:
            self.C1.deselect()
        else:
            self.C1.select()

        # show beyer
        if not self.Settings.showbeyer:
            self.C2.deselect()
        else:
            self.C2.select()

        # show order of horses
        if not self.Settings.showorder:
            self.C3.deselect()
        else:
            self.C3.select()

        # betting options
        self.option_betting.set(self.Settings.betting_option)
        
        # fixed bet entry box
        self.betting.delete(0, 'end')
        self.betting.insert(0, self.Settings.betting_amount)

        # purse size
        self.purse.delete(0, 'end')
        self.purse.insert(0, "{0:.02f}".format(self.Settings.purse))

        # number of horses
        self.horses.delete(0, 'end')
        self.horses.insert(0, self.Settings.num_of_horses)

        # time per race
        self.time.delete(0, 'end')
        self.time.insert(0, self.Settings.time_limit)
    def s_settings(self):
        # setting title
        self.Settings.path = os.path.join('ui','settings')

        self.Settings.load(self.Settings,'default')
        tk.Label(self.settings, text='Settings', font=(None, 15)).grid( 
            row=0, column=1, columnspan=2, pady=10)

        # drop-down of default settings
        tk.Label(self.settings, text="Select settings: ").grid(row=1, column=1,
                 padx=10, pady=5, sticky=tk.W)
        defaults = [f.replace('_s.p', '') for f in os.listdir(self.Settings.path)]

        self.defaultmenu = tk.StringVar(self.settings)
        self.defaultmenu.set(defaults[0])
        self.default_select = tk.OptionMenu(self.settings, self.defaultmenu, 
                                          *defaults, command=self.load_settings)
        self.default_select.grid(row=1, column=2, sticky = tk.W)

        # number of trials prompt
        tk.Label(self.settings, text='Number of trials: ').grid(row=2,
            column=1, padx=10, pady=5, sticky=tk.W)

        # number of trials text box
        self.trials = tk.Entry(self.settings, width=3)
        self.trials.grid(row=2, column=2, sticky=tk.W)

        # disabling and enabling accuracy bar
        def toggleslider():
            if self.activate == True:
                self.accuracy.config(state='disabled')
                
                #grey out the bar
                self.accuracy.config(foreground='gainsboro')
                self.activate = False
            else:
                self.accuracy.config(state='normal')
                
                #make the bar normal colored
                self.accuracy.config(foreground='black')
                self.activate = True

        # accuracy prompt
        tk.Label(self.settings, text='Accuracy: ').grid(row=3, column=1, 
            padx=10, pady=5, sticky=tk.W)

        # accuracy slider
        self.accuracy = tk.Scale(self.settings, orient=tk.HORIZONTAL, 
            resolution=10, showvalue=0, tickinterval=10, length=300)
        self.accuracy.grid(row = 3, column = 2, columnspan = 2, sticky = tk.W)
        self.activate = True
        self.checkaccuracy = tk.StringVar(self.settings)

        # check button for using accuracy of classifer
        # if checked, accuracy bar is disabled
        self.CA = tk.Checkbutton(self.settings, 
                                 text="Use accuracy of classifer.", 
                                 variable=self.checkaccuracy, onvalue=True, 
                                 offvalue=False, command=toggleslider)
        self.CA.grid(row=4, column=2, columnspan=2, sticky=tk.W)

        # what data to show prompt
        tk.Label(self.settings, text='Show: ')\
                .grid(row=5, column=1, padx=10, pady=5,sticky=tk.W)
        tk.Label(self.settings, text='Note: default is one horse', 
                 font=(None, 10))\
                .grid(row=7, column=1, padx=10, pady=5, sticky=tk.S + tk.W)

        # show check buttons - time, beyer, and show order
        self.showtime = tk.StringVar(self.settings)
        self.showbeyer = tk.StringVar(self.settings)
        self.showorder = tk.StringVar(self.settings)
        
        #create the time button
        self.C1 = tk.Checkbutton(self.settings, text='Time', 
                                 variable=self.showtime, onvalue=True, 
                                 offvalue=False)
        self.C1.grid(row=5, column=2, sticky=tk.W)

        #create the Beyer figure button
        self.C2 = tk.Checkbutton(self.settings, text='Beyer', 
                                 variable=self.showbeyer, onvalue=True, 
                                 offvalue=False)
        self.C2.grid(row=6, column=2, sticky=tk.W)
        
        #create the order button
        self.C3 = tk.Checkbutton(self.settings, text="Complete Order",
                                 variable=self.showorder, onvalue=True, 
                                 offvalue=False)
        self.C3.grid(row=7, column=2, sticky=tk.W)

        # betting amount prompt
        tk.Label(self.settings, text='Betting Amount: ')\
                .grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)
   
        # betting amount options
        # enabling and disenabling text box for fixed option
        def enableEntry():
            self.betting.configure(state='normal')
            self.betting.update()
        def disableEntry():
            self.betting.configure(state='disabled')
            self.betting.update()

        self.betting = tk.Entry(self.settings, width=3)
        self.betting.grid(row=9, column=2, padx=100, sticky=tk.W)
        self.option_betting=tk.StringVar()
        
        # change betting option
        tk.Radiobutton(self.settings, variable=self.option_betting, 
                       text='Change', value='Change', command=disableEntry)\
                      .grid(row=8, column=2, sticky=tk.W)
        
        # fixed dollar amount betting option
        tk.Radiobutton(self.settings, variable=self.option_betting,
                       text='Fixed', value='Fixed', command=enableEntry)\
                      .grid(row=9, column=2, sticky=tk.W)

        # purse size prompt
        tk.Label(self.settings, text='Initial Purse Size: ')\
                .grid(row=10, column=1, padx=10, pady=5, sticky=tk.W)

        # purse size entry box
        tk.Label(self.settings, text='$')\
                .grid(row=10, column=2, sticky=tk.W)
        self.purse=tk.Entry(self.settings, width=5)
        self.purse.grid(row=10, column=2, sticky=tk.W, padx=15)

        # number of horses prompt
        tk.Label(self.settings, text='Number of Horses: ').grid(row=11, 
            column=1, padx=10, pady=5, sticky=tk.W)

        # number of horses entry box
        self.horses = tk.Entry(self.settings, width=3)
        self.horses.grid(row=11, column=2, sticky=tk.W)

        # time limit per race prompt
        tk.Label(self.settings, text='Time Limit per Race: ').grid(row=12,
            column=1, padx=10, pady=5, sticky=tk.W)

        # time limit per race entry box
        self.time = tk.Entry(self.settings, width=3)
        self.time.grid(row=12, column=2, sticky=tk.W)
        tk.Label(self.settings, text='minutes').grid(row=12, column=2, 
            padx=30, sticky=tk.W)

        # submit button
        tk.Button(self.settings, text='Submit', command=self.instructions).grid \
                 (row=14, column=1, columnspan=2, pady=10)

        # set all of the defaults

                # trials entry box
        self.trials.insert(0, self.Settings.trials)

        # accuracy slider
        self.accuracy.set(self.Settings.accuracy)

        # use accuracy of classifer
        if not self.Settings.checkaccuracy:
            self.CA.deselect()
        else:
            self.CA.select()

        # show time
        if not self.Settings.showtime:
            self.C1.deselect()
        else:
            self.C1.select()

        # show beyer
        if not self.Settings.showbeyer:
            self.C2.deselect()
        else:
            self.C2.select()

        # show order of horses
        if not self.Settings.showorder:
            self.C3.deselect()
        else:
            self.C3.select()

        # betting options
        self.option_betting.set(self.Settings.betting_option)
        
        # fixed bet entry box
        self.betting.insert(0, self.Settings.betting_amount)

        # purse size
        self.purse.insert(0, "{0:.02f}".format(self.Settings.purse))

        # number of horses
        self.horses.insert(0, self.Settings.num_of_horses)

        # time per race
        self.time.insert(0, self.Settings.time_limit)

    def errorcheck(self):
        # checks to make sure the settings were correct
        
        elementlist = [self.trials.get(), self.accuracy.get(), 
        self.checkaccuracy.get(), self.showtime.get(), self.showbeyer.get(), 
        self.showorder.get(), self.purse.get(), self.betting.get(), 
        self.horses.get(), self.time.get()]

        for element in elementlist:
            
            # check if any element is empty
            if not element:

                #display the error essage
                error = tk.Tk()
                error.title('ERROR')
                error.bind('<Control-q>', quit)
                tk.Label(error, text = "Fill in all settings.", 
                    font = (None, 20)).pack(padx = 10, pady = 10)
                tk.Button(error, text='OK', command=lambda : 
                    error.destroy()).pack(padx=10, pady=10)
                return False
           
            # check if purse is a float number
            elif element == self.purse.get():
                try:
                    float(element)
                except:
                    
                    #display the error message
                    error = tk.Tk()
                    error.title('ERROR')
                    error.bind('<Control-q>', quit)
                    tk.Label(error, text="Please correct format for purse.", 
                        font = (None, 20)).pack(padx = 10, pady = 10)
                    tk.Button(error, text='OK', command=lambda : 
                        error.destroy()).pack(padx=10, pady=10)
                    return False

            # check if other elements are integers (not letters)
            elif element != self.showtime.get() or element != \
            self.showbeyer.get() or element != self.showorder.get():
                try:
                    int(element)
                except:

                    #display the error message
                    error = tk.Tk()
                    error.title('ERROR')
                    error.bind('<Control-q>', quit)
                    tk.Label(error, text="Please enter integers.", 
                        font = (None, 20)).pack(padx = 10, pady = 10)
                    tk.Button(error, text='OK', command=lambda : 
                        error.destroy()).pack(padx = 10, pady = 10)
                    return False
            else:
                return True
    def instructions(self):
        # screen that displays the instructions
        # checking if all entries are filled out
        if self.errorcheck():

            # saving data from settings
            self.Settings.trials = int(self.trials.get())
            self.Settings.accuracy = int(self.accuracy.get())
            self.Settings.checkaccuracy = int(self.checkaccuracy.get())
            self.Settings.showtime = int(self.showtime.get())
            self.Settings.showbeyer = int(self.showbeyer.get())
            self.Settings.showorder = int(self.showorder.get())
            self.Settings.purse = float(self.purse.get())
            self.Settings.purse = round(self.Settings.purse, 2)
            self.Settings.betting_option = self.option_betting.get()
            self.Settings.betting_amount = int(self.betting.get())
            self.Settings.num_of_horses = int(self.horses.get())
            self.Settings.time_limit = int(self.time.get())

            self.Settings.save(self.Settings,'test')

            # checking values
            print("Trials: ", self.Settings.trials, 
                "\nAccuracy: ", self.Settings.accuracy,
                "\nCheck Accuracy: ", self.Settings.checkaccuracy,
                "\nTime: ", self.Settings.showtime,
                "\nBeyer: ", self.Settings.showbeyer,
                "\nOrder: ", self.Settings.showorder,
                "\nBetting Style: ", self.Settings.betting_option,
                "\nBetting Amount: ", self.Settings.betting_amount,
                "\nPurse: ", self.Settings.purse,
                "\nNumber of Horses: ", self.Settings.num_of_horses,
                "\nTime Limit per Race: ", self.Settings.time_limit)

            # clearing screen and making a new instructions window
            self.settings.destroy()
            root.destroy()
            self.window = tk.Tk()
            self.window.title('Horse Racing')
            self.window.bind('<Control-q>', quit)

            # find size of screen
            self.screen_width = int(self.window.winfo_screenwidth())
            self.screen_height = int(self.window.winfo_screenheight())

            # fit to screen
            self.window.geometry("{}x{}".format(self.screen_width, 
                                                self.screen_height))

            print(self.screen_width, self.screen_height)
            print(self.Settings.__dict__)
            # get screen dimensions
            self.screen_width = int(self.window.winfo_screenwidth())
            self.screen_height = int(self.window.winfo_screenheight())- 100

            # configure instructions frame
            self.instructions = tk.Frame(self.window)
            self.instructions.grid()
            for i in range(3):
                self.instructions.grid_rowconfigure(
                                        i, minsize=int(self.screen_height/3))
                self.instructions.grid_columnconfigure(
                                        i, minsize=int(self.screen_width/3))

            # instructions label
            welcomeTextChange = "Welcome!\nAs a reminder, you can choose your bets." + \
                          "\nYour task is to pick, as best you can, the " + \
                          "winner of the race.\nYou will have up to {} " + \
                          "minutes to look at all the data and make your " + \
                          "choice.\nPress start when you are ready."

            welcomeTextFixed = "Welcome!\nAs a reminder, your bets are fixed at " + \
                          "${:.2f}.\nYour task is to pick, as best you can, the " + \
                          "winner of the race.\nYou will have up to {} " + \
                          "minutes to look at all the data and make your " + \
                          "choice.\nPress start when you are ready."

            if self.Settings.betting_option == "Fixed":
                tk.Label(self.instructions, text=welcomeTextFixed\
                         .format(self.Settings.betting_amount, 
                         self.Settings.time_limit),\
                         font=(None, int(self.screen_height*.02)))\
                        .grid(row=1, column=1)
            else:
                tk.Label(self.instructions, text=welcomeTextChange\
                         .format(self.Settings.betting_amount, 
                         self.Settings.time_limit),\
                         font=(None, int(self.screen_height*.02)))\
                        .grid(row=1, column=1)

            tk.Button(self.instructions, text='Start', 
                      font=(None, int(self.screen_width*.01)),
                      command=self.betting_screen)\
                     .grid(row=1, column=1, sticky=tk.S)

    def generateforms(self):
        # creates forms with random horses
        # folder where forms are found
        folder = "data/split_jpgs"
        # randomly generate race forms
        pattern = re.compile(r'([A-Z]+)(\d+)_(\d+)_(\d*|header)?\.jpg')

        #race = random.choice(os.listdir(folder))
        race = "ARP170618_1_1.jpg"
        m = pattern.match(race)

        # get filepaths and make sure they exist before continuing
        sep = "_" if len(m.group(1)) < 3 else ""
        p = "data/" + m.group(1) + "/" + m.group(2) + "/" + m.group(1) + sep + \
            m.group(2) + "_SF.CSV"
        ltp = "data/" + m.group(1) + "/" + m.group(2) + "/" + \
              m.group(1) + sep + m.group(2) + "_" + m.group(3) + "_LT.CSV"
        lbp = "data/" + m.group(1) + "/" + m.group(2) + "/" + \
              m.group(1) + sep + m.group(2) + "_" + m.group(3) + "_LB.CSV"

        print("Looking for:",p)
        print("           :",ltp)
        print("           :",lbp)
        print("           :",folder+"/ARP170618_3_header.jpg")

        # find a race, and ensure that the files necessary exist
        while not (os.path.isfile(p) and os.path.isfile(ltp) 
                   and os.path.isfile(lbp)):
            # get new race
            print("File doesn't exist! Trying again...")
            race = random.choice(os.listdir(folder))
            m = pattern.match(race)

            # get filepaths, and make sure they exist before continuing
            sep = "_" if len(m.group(1)) < 3 else ""
            p = "data/" + m.group(1) + "/" + m.group(2) + "/" + m.group(1) + \
                sep + m.group(2) + "_SF.CSV"
            ltp = "data/" + m.group(1) + "/" + m.group(2) + "/" + \
                  m.group(1) + sep + m.group(2) + "_" + m.group(3) + "_LT.CSV"
            lbp = "data/" + m.group(1) + "/" + m.group(2) + "/" + \
                  m.group(1) + sep + m.group(2) + "_" + m.group(3) + "_LB.CSV"

        beginning = time.time()

        # pick random horses and make a form
        convert_string = "convert -append " + os.path.join(folder, m.group(1) + \
            m.group(2) + '_' + m.group(3) + "_header.jpg ")
            
        # generate a list of possible filenames
        filenames = [f for f in os.listdir(folder) 
                        if f.endswith(".jpg") and \
                           f.startswith(m.group(1)+m.group(2)+'_'+m.group(3)) \
                           and not f.endswith("_header.jpg")]

        # shuffle the list
        random.shuffle(filenames)
        nums = []
        # 
        for filename in sorted(filenames[:self.Settings.num_of_horses]):
            convert_string += os.path.join(folder, filename) + " "
            m = pattern.match(filename)
            nums += m.group(4)

        convert_string += "test.jpg"
        # TODO: why does this convert the jpgs while running? 
        #       conversion should be done beforehand for limited cases
        os.system(convert_string)

        # find horses in csv files
        self.superhorses = get_positions(m.group(1), m.group(2), m.group(3))
        self.horses_racing = []
        self.horses_odds = ""
        for horse in self.superhorses:
            if (horse['B_ProgNum'] in nums):
                self.horses_racing.append(horse)
        
        # find predicted winning horse
        self.horses_racing.sort(key=lambda x:x['L_Time'])
        self.horse_pwin = self.horses_racing[0]['B_Horse']

        # find actual winning horse
        self.horses_racing.sort(key=lambda x:x['L_Rank'])
        self.horse_win = self.horses_racing[0]['B_Horse']

        # find odds for horses
        self.horses_racing.sort(key=lambda x:x['B_ProgNum'])
        for horse in self.horses_racing:
            self.horses_odds += (horse['B_Horse'] + " : " + 
                                 horse['B_MLOdds'] + "\n ")
        end = time.time()

    def scrolledcanvas(self):
        # generate forms
        self.generateforms()

        # create a canvas for the form
        self.canv = tk.Canvas(self.bet, relief='sunken')
        self.canv.config(width=1500, height=1125)
        self.canv.config(highlightthickness=0)

        # create a scroll bar to view the form
        sbarV = tk.Scrollbar(self.bet, orient='vertical', 
                             command=self.canv.yview)
        sbarV.grid(row=0, column=0, rowspan=10, sticky=tk.N + tk.S + tk.E)
        self.canv.config(yscrollcommand=sbarV.set)

        # load the form onto the canvas and resize it to fit the screen
        self.canv.grid(row=0, column=0, rowspan=10, 
                       sticky=tk.N + tk.S + tk.W + tk.E)
        self.im = Image.open("test.jpg")
        self.im = self.im.resize((1500, 
                                  int((1500/self.im.width)*self.im.height)),
                                 Image.ANTIALIAS)
        width, height = self.im.size
        self.canv.config(scrollregion=(0, 0, width, height))
        self.im2 = ImageTk.PhotoImage(self.im)
        self.imgtag = self.canv.create_image(0, 0, anchor='nw', image=self.im2)

    def countdown(self):
        # countdown timer
        self.t -= 1
        mins, secs = divmod(self.t, 60)
        self.timer_label['text'] = '{:02d}:{:02d}'.format(mins, secs)
        self.bet.after(1000, self.countdown)
        if self.t == -1:
            self.retrieving_data()

    def betting_screen(self):
        # check if result and instructions screen has been destroyed
        # destroy them if they are created to show new race
        if hasattr(self, 'result'):
            self.result.destroy()

        # clear instructions screen
        if hasattr(self, 'instructions'):
            self.instructions.destroy()

        # betting screen
        self.bet = tk.Frame(self.window)
        self.bet.grid()
        self.bet.grid_columnconfigure(0, minsize=1500)
        self.bet.grid_columnconfigure(1, minsize=self.screen_width-1500)

        # set up for countdown timer
        self.t = self.Settings.time_limit * 60
        self.timer_label = tk.Label(self.bet, textvariable="", 
                                    font=(None, 25), justify='right')
        self.timer_label.grid(row=0, column=1, padx=15, pady=10, 
                              sticky=tk.N + tk.E)
        self.countdown()

        # show forms
        self.scrolledcanvas()

        # drop down menu of horses
        self.horse_names = []
        for horse in self.horses_racing:
            self.horse_names.append(horse['B_Horse'])

        self.horsemenu = tk.StringVar(self.bet)
        self.horsemenu.set("Select horse")
        self.horse_select = tk.OptionMenu(self.bet, self.horsemenu, 
                                          *self.horse_names)
        self.horse_select.config(font=(None, 20))

        # show race information on side
        tk.Label(self.bet, text="Purse Total: ${:.2f}".format(self.Settings.purse),\
                 font=(None,20))\
                .grid(row=1, column=1, padx=10, pady=10, sticky= tk.W)
        if self.Settings.betting_option == 'Fixed':
            tk.Label(self.bet, text="Betting Amount: ${:.2f}"\
                     .format(self.Settings.betting_amount), font=(None, 20))\
                    .grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        else:
            tk.Label(self.bet, text="Betting Amount: $", font=(None,20))\
                     .grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
            self.new_bet = tk.Spinbox(self.bet, from_=2.00, to=self.Settings.purse, \
                                      width=5, format="%.2f", font=(None, 20),\
                                      state='readonly')
            self.new_bet.grid(row=2, column=1, padx=(50,0))
        tk.Label(self.bet, text="Odds:\n {}".format(self.horses_odds),\
                 justify='left', font=(None, 20))\
                .grid(row=3, column=1, padx=10, pady=10, sticky= tk.W)
        tk.Label(self.bet, text="Aide's Suggestions: \n {}".format(self.horse_pwin),\
                 justify='left', font=(None, 20))\
                .grid(row=4, column=1, padx=10, pady=10, sticky= tk.W)
        tk.Label(self.bet, text="Horse you want to bet on:", font=(None, 20))\
                .grid(row=5, column=1, padx=10, sticky= tk.W)

        self.horse_select.grid(row=5, column=1, padx=15, pady=5, sticky=tk.W + tk.S)

        # submit button
        tk.Button(self.bet, text='Submit', 
                  command=self.retrieving_data, font=(None, 20))\
                 .grid(row=7, column=1, padx=10, pady=10)

    def retrieving_data(self):
        # check how long the user took to submit
        print(self.timer_label['text'])

        if self.Settings.betting_option == 'Change':
                self.Settings.betting_amount = float(self.new_bet.get())

        # check if a horse is selected
        if self.horsemenu.get() == "Select horse":
            error = tk.Tk()
            error.title("ERROR")
            error.bind('<Control-q>', quit)
            tk.Label(error, text="Please select a horse.", 
                     font=(None, 20))\
                    .pack(padx=10, pady=10)
            tk.Button(error, text="OK", command=lambda: error.destroy())\
                     .pack(padx=10, pady=10)
        else:
            # delete old frame
            self.bet.destroy()

            # variable to keep track if there are more races
            self.next_race = True

            # create a new window for retrieving data
            self.retrieve = tk.Tk()
            self.retrieve.title("Retrieving Data")
            self.retrieve.bind('<Control-q>', quit)

            tk.Label(self.retrieve, text="Retrieving Data...", 
                     font=(None, 50))\
                    .pack(padx=10, pady=10)

            # delete window after 2 seconds
            self.retrieve.after(2000, lambda: self.results())
            self.retrieve.mainloop()

    def update_purse(self):
        """ updates the purse """
        # take away money used to bet
        self.Settings.purse -= self.Settings.betting_amount

        # if bet on the right horse, calculate winnings
        if self.horse_win == self.horsemenu.get():
            for horse in self.superhorses:
                if horse['B_Horse'] == self.horsemenu.get():
                    odds = horse['B_MLOdds'].split('-')
            if self.Settings.betting_amount != '0':
                self.Settings.purse = (((self.Settings.betting_amount * float(odds[0])) / 
                                float(odds[1])) + self.Settings.purse)

    def results(self):
        """ displays the results of the race """
        # destroy the retrieving screen and create a new screen for results
        self.retrieve.destroy()
        self.result = tk.Frame(self.window)
        self.result.grid()
        self.result.grid_rowconfigure(0, weight=1)
        self.result.grid_columnconfigure(0, weight=1)

        # result labels
        tk.Label(self.result, text='Results', font=(None, 35))\
                .grid(row=0, column=0, padx=((self.screen_width/2.5), 10), 
                      pady=((self.screen_height/3), 10))
        tk.Label(self.result, text='Actual result: {}'.format(self.horse_win), 
                 font=(None, 25))\
                .grid(row=2, column=0, padx=((self.screen_width/2.5), 10), 
                      pady=10)
        tk.Label(self.result, text="Aide's Suggestion: {}"\
                                        .format(self.horse_pwin),
                 font=(None, 25))\
                .grid(row=3, column=0, 
                      padx=((self.screen_width/2.5), 10), pady= 10)
        tk.Label(self.result, 
                 text='Your choice: {}'.format(self.horsemenu.get()),
                 font=(None, 25))\
                .grid(row=4, column=0, 
                      padx=((self.screen_width/2.5), 10), pady=10)

        # update the users purse
        self.update_purse()
        tk.Label(self.result, text='Current Purse: ${:.2f}'.format(self.Settings.purse),
                 font=(None, 25))\
                .grid(row=5, column=0, padx=((self.screen_width/2.5), 10), 
                      pady=10)

        # check if there are more races to display 'next race' or 'exit'
        if self.Settings.trials == 1:
            tk.Button(self.result, text='Exit', 
                      font=(None, 20), command=self.exit)\
                     .grid(row=6, column=0, 
                           padx=((self.screen_width/2.5), 10), pady=10)
        else:
            tk.Button(self.result, text='Next Race', 
                      font=(None, 20), command=self.races)\
                     .grid(row=6, column=0, 
                           padx=((self.screen_width/2.5), 10), pady=10)

    def races(self):
        # if there are more races, decrement trials and load another race
        if self.Settings.trials > 0:
            self.betting_screen()
            self.Settings.trials -= 1

    def exit(self):
        # destroy result screen and make a new exit screen
        self.result.destroy()
        self.exit = tk.Frame(self.window)
        self.exit.grid()
        self.exit.grid_rowconfigure(0, weight=1)
        self.exit.grid_columnconfigure(0, weight=1)

        # instructions for what to do next
        tk.Label(self.exit, text='Thank you!\nPlease notify the researcher.',
                 font=(None, 50))\
                .grid(row=0, column=1, columnspan=2, 
                      padx=((self.screen_width/3), 100), 
                      pady=((self.screen_height/3), 10))

        # instructions for inserting ID number
        tk.Label(self.exit, text='Please enter ID number in order to save.')\
                .grid(row=2, column=1, columnspan=2, 
                      padx=((self.screen_width/3), 100))
        self.save=tk.Entry(self.exit, width=30)
        self.save.grid(row=3, column=1, columnspan=2, 
                       padx=((self.screen_width/3), 100))

        # save button
        tk.Button(self.exit, text='Save', font=(None, 15), 
                  command=self.checksave)\
                 .grid(row=4, column=1, columnspan=2, 
                       padx=((self.screen_width/3), 50), pady=10)

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
            tk.Label(error, text="Please insert ID number.", font=(None, 20))\
                    .pack(padx=10, pady=10)
            tk.Button(error, text="OK", command=lambda: error.destroy())\
                     .pack(padx=10, pady=10)

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
                tk.Label(error, text="Please insert numbers.", font=(None, 20))\
                        .pack(padx=10, pady=10)
                tk.Button(error, text="OK", command=lambda: error.destroy())\
                         .pack(padx=10, pady=10)


root = tk.Tk()

def run():
    root.title("Horse Racing")
    root.geometry("500x460")
    root.bind('<Control-q>', quit)
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    run()
