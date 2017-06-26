import tkinter as tk
import time
from PIL import Image, ImageTk

def check():
    # checks for keyboard interrupts (ctrl+q)
    root.after(50, self.check)
    Window1.exit()

def combine_funcs( *funcs):
    # runs two functions at once
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func

class Window1:
    def __init__(self, master):
        self.master = master
        self.settings = tk.Frame(self.master)
        """self.button = tk.Button(self.settings, text = 'Start', command = self.new_window)"""
        self.settings.grid()
        self.s_settings()
    def s_settings(self):
        # setting title
        tk.Label(self.settings, text = 'Settings', font = (None, 15)).grid(row = 1, column = 1, columnspan = 2, pady = 10)
        # number of trials prompt
        tk.Label(self.settings, text = 'Number of Trials: ').grid(row = 2, column = 1, padx = 10, pady = 5, sticky = tk.W)
        # number of trials text box
        self.trials = tk.Entry(self.settings, width = 3)
        self.trials.grid(row = 2, column = 2, sticky = tk.W)
        # accuracy prompt
        tk.Label(self.settings, text = 'Accuracy: ').grid(row = 3, column = 1, padx = 10, pady = 5, sticky = tk.W)
        # accuracy slider
        self.accuracy = tk.Scale(self.settings, orient = tk.HORIZONTAL, resolution = 10, 
            showvalue = 0, tickinterval = 10, length = 300)
        self.accuracy.grid(row = 3, column = 2, columnspan = 2, sticky = tk.W)
        # show prompt
        tk.Label(self.settings, text = 'Show: ').grid(row = 4, column = 1, padx = 10, pady = 5,sticky = tk.W)
        tk.Label(self.settings, text = 'Note: default is one horse', font = (None, 10)).grid(row = 6, column = 1, padx = 10, pady = 5, sticky = tk.S + tk.W)
        # show check buttons
        self.showtime = tk.StringVar(self.settings)
        self.showbeyer = tk.StringVar(self.settings)
        self.showorder = tk.StringVar(self.settings)
        C1 = tk.Checkbutton(self.settings, text = "Time", variable = self.showtime, onvalue = True, offvalue = False)
        C1.grid(row = 4, column = 2, sticky = tk.W)
        C1.deselect()
        C2 = tk.Checkbutton(self.settings, text = "Beyer", variable = self.showbeyer, onvalue = True, offvalue = False)
        C2.grid(row = 5, column = 2, sticky = tk.W)
        C2.deselect()
        C3 = tk.Checkbutton(self.settings, text = "Complete Order", variable = self.showorder, onvalue = True, offvalue = False)
        C3.grid(row = 6, column = 2, sticky = tk.W)
        C3.deselect()
        # betting amount prompt
        tk.Label(self.settings, text = 'Betting Amount: ').grid(row = 7, column = 1, padx = 10, pady = 5, sticky = tk.W)
        # betting amount options
        # enabling and disenabling text box for fixed option
        def enableEntry():
            self.betting.configure(state = "normal")
            self.betting.update()
        def disableEntry():
            self.betting.configure(state = "disabled")
            self.betting.update()
        self.betting = tk.Entry(self.settings, width = 3)
        self.betting.grid(row = 8, column = 2, padx = 100, sticky = tk.W)
        self.option_betting = tk.StringVar()
        tk.Radiobutton(self.settings, variable = self.option_betting, text = 'Change', value = 'Change',
            command = disableEntry).grid(row = 7, column = 2, sticky = tk.W)
        tk.Radiobutton(self.settings, variable = self.option_betting, text = 'Fixed', value = 'Fixed', 
            command = enableEntry).grid(row = 8, column = 2, sticky = tk.W)
        # purse size prompt
        tk.Label(self.settings, text = 'Purse Size: ').grid(row = 9, column = 1, padx = 10, pady = 5, sticky = tk.W)
        # purse size entry
        tk.Label(self.settings, text = '$').grid(row = 9, column = 2, sticky = tk.W)
        self.purse = tk.Entry(self.settings, width = 5)
        self.purse.grid(row = 9, column = 2, sticky = tk.W, padx = 15)
        # number of horses prompt
        tk.Label(self.settings, text = 'Number of Horses: ').grid(row = 8, column = 1, padx = 10, pady = 5, sticky = tk.W)
        # number of horses entry
        self.horses = tk.Entry(self.settings, width = 3)
        self.horses.grid(row = 10, column = 2, sticky = tk.W)
        # time limit per race prompt
        tk.Label(self.settings, text = 'Time Limit per Race: ').grid(row = 11, column = 1, padx = 10, pady = 5, sticky = tk.W)
        # time limit per race entry
        self.time = tk.Entry(self.settings, width = 3)
        self.time.grid(row = 11, column = 2, sticky = tk.W)
        tk.Label(self.settings, text = 'minutes').grid(row = 11, column = 2, padx = 30, sticky = tk.W)

        # submit button
        tk.Button(self.settings, text = 'Submit', command = self.instructions).grid(row = 13, 
            column = 1, columnspan = 2, pady = 10)

        # defaults
        self.trials.insert(0, 5)
        self.accuracy.set(50)
        self.option_betting.set('Fixed')
        self.betting.insert(0, 2)
        self.purse.insert(0, "{0:.02f}".format(25.00))
        self.horses.insert(0, 3)
        self.time.insert(0, 15)

    def countdown(self):
        # count down timer
        mins, secs = divmod(self.t, 60)
        self.timeformat = '{:02d}:{:02d}'.format(mins, secs)
        if self.t is not None:
            self.t = self.t
        if self.t <= 0:
            self.label.set("")
            self.retrieving_data()
        else:
            self.timer_label['text'] = self.timeformat
            self.t = self.t - 1
            root.after(1000, self.countdown)

    def errorcheck(self):
        elementlist = [self.trials.get(), self.accuracy.get(), self.showtime.get(), self.showbeyer.get(), self.showorder.get(), self.purse.get(), self.betting.get(), self.horses.get(), self.time.get()]
        for element in elementlist:
            if not element:
                error = tk.Tk()
                error.title("ERROR")
                error.bind('<Control-q>', quit)
                tk.Label(error, text = "Fill in all settings.").pack(padx = 10, pady = 10)
                tk.Button(error, text = "OK", command = lambda : error.destroy()).pack(padx = 10, pady = 10)
                return False
            if element == self.purse.get():
                try:
                    float(element)
                except:
                    error = tk.Tk()
                    error.title("ERROR")
                    error.bind('<Control-q>', quit)
                    tk.Label(error, text = "Please correct format for purse.").pack(padx = 10, pady = 10)
                    tk.Button(error, text = "OK", command = lambda : error.destroy()).pack(padx = 10, pady = 10)
                    return False
            elif element != self.showtime.get() or element != self.showbeyer.get() or element != self.showorder.get():
                try:
                    int(element)
                except:
                    error = tk.Tk()
                    error.title("ERROR")
                    error.bind('<Control-q>', quit)
                    tk.Label(error, text = "Please enter integers.").pack(padx = 10, pady = 10)
                    tk.Button(error, text = "OK", command = lambda : error.destroy()).pack(padx = 10, pady = 10)
                    return False

    def instructions(self):
        # screen that displays the instructions
        """SAVE DATA"""
        # checking if all entries are filled out
        if not self.errorcheck():
            # saving data from settings
            self.trials1 = int(self.trials.get())
            self.accuracy1 = int(self.accuracy.get())
            self.showtime1 = self.showtime.get()
            self.showbeyer1 = self.showbeyer.get()
            self.showorder1 = self.showorder.get()
            self.purse1 = float(self.purse.get())
            self.purse1 = round(self.purse1, 2)
            self.betting_option = self.option_betting.get()
            if not (self.betting.get()):
                self.betting1 = 0
            else:
                self.betting1 = int(self.betting.get())
            self.horses1 = int(self.horses.get())
            self.time1 = int(self.time.get())

            print("Trials: ", self.trials1, 
                "\nAccuracy: ", self.accuracy1,
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
            self.window.attributes("-fullscreen", True)
            self.instructions = tk.Frame(self.window)
            self.instructions.grid()
            self.instructions.grid_rowconfigure(0, weight = 1)
            self.instructions.grid_columnconfigure(0, weight = 1)
            # betting screen
            self.bet = tk.Frame(self.window)
            self.bet.grid()
            self.bet.grid_rowconfigure(0, weight = 1)
            self.bet.grid_columnconfigure(0, weight = 1)
            # instructions label
            tk.Label(self.instructions, text = 'Welcome!\n Please decide the winner.'
                "\n You will have %s minutes per race. \nThere are %s races." 
                "\n Press start when you are ready."
                % (self.time1, self.trials1), font = (None, 50)).grid(row = 1, column = 1, padx = 500, pady = (300, 100))
            tk.Button(self.instructions, text = 'Start', font = (None, 25), command = combine_funcs(self.countdown, self.betting_screen)).grid(row = 1, column = 1, sticky = tk.S)
            # timer
            self.t = self.time1 * 60
            self.timer_label = tk.Label(self.bet, text = "", font = (None, 25), width = 10)
            self.timer_label.grid(row = 0, column = 5, padx = 10, pady = 10, sticky = tk.N + tk.E)
            self.next_race = False

    def retrieving_data(self):
        self.bet.destroy()
        self.next_race = True
        self.retrieve = tk.Tk()
        self.retrieve.title("Retrieving Data")
        self.retrieve.bind('<Control-q>', quit)
        tk.Label(self.retrieve, text = "Retrieving Data...", font = (None, 50)).pack(padx = 10, pady = 10)
        self.retrieve.after(2000, lambda: self.results())
        self.retrieve.mainloop()
        print(self.timeformat)

    def betting_screen(self):
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
        if self.next_race == True:
            # betting screen
            self.bet = tk.Frame(self.window)
            self.bet.grid()
            self.bet.grid_rowconfigure(0, weight = 1)
            self.bet.grid_columnconfigure(0, weight = 1)
            # timer
            self.t = self.time1 * 60
            self.timer_label = tk.Label(self.bet, text = "", font = (None, 25), width = 10)
            self.timer_label.grid(row = 0, column = 5, padx = 10, pady = 10, sticky = tk.N + tk.E)
        self.scrolledcanvas()
        tk.Button(self.bet, text = 'Submit', command = self.retrieving_data).grid(row = 0, column = 5, padx = 10, pady= 10, sticky = tk.S)

    def scrolledcanvas(self):
        self.canv = tk.Canvas(self.bet, relief = 'sunken')
        self.canv.config(width = 1500, height = 1125)
        self.canv.config(highlightthickness = 0)

        sbarV = tk.Scrollbar(self.bet, orient = 'vertical', command = self.canv.yview)
        sbarV.grid(row = 0, column = 5, rowspan = 5, sticky = tk.N + tk.S + tk.W)
        self.canv.config(yscrollcommand = sbarV.set)

        self.canv.grid(row = 0, column = 0, rowspan = 5, columnspan = 5, sticky = tk.N + tk.S + tk.W + tk.E)
        self.im = Image.open("file1.jpg")
        self.im = self.im.resize((1500, 4000), Image.ANTIALIAS)
        width, height = self.im.size
        self.canv.config(scrollregion = (0, 0, width, height))
        self.im2 = ImageTk.PhotoImage(self.im)
        self.imgtag = self.canv.create_image(0, 0, anchor = "nw", image = self.im2)

    def results(self):
        self.retrieve.destroy()
        self.result = tk.Frame(self.window)
        self.result.grid()
        self.result.grid_rowconfigure(0, weight = 1)
        self.result.grid_columnconfigure(0, weight = 1)
        tk.Label(self.result, text = 'Results', font = (None, 35)).grid(row = 1, column = 1, columnspan = 2, pady= (400, 10))
        tk.Label(self.result, text = 'Actual result: ', font = (None, 25)).grid(row = 2, column = 0, padx = (700, 10), pady= 10)
        tk.Label(self.result, text = 'System\'s choice: ', font = (None, 25)).grid(row = 3, column = 0, padx = (700, 10), pady= 10)
        tk.Label(self.result, text = 'Your choice: ', font = (None, 25)).grid(row = 4, column = 0, padx = (700, 10), pady= 10)
        tk.Label(self.result, text = 'Updated Wallet: ', font = (None, 25)).grid(row = 5, column = 0, padx = (700, 10), pady= 10)
        if self.trials1 == 1:
            tk.Button(self.result, text = 'Exit', font = (None, 20), command = self.exit).grid(row = 6, column = 1, padx = 10, pady = 10)
        else:
            tk.Button(self.result, text = 'Next Race', font = (None, 20), command = self.races).grid(row = 6, column = 1, padx = 10, pady = 10)

    def races(self):
        if self.trials1 > 0:
            self.betting_screen()
            self.countdown()
            combine_funcs(self.countdown, self.betting_screen)
            self.trials1 -= 1

    def exit(self):
        self.result.destroy()
        self.exit = tk.Frame(self.window)
        self.exit.grid()
        self.exit.grid_rowconfigure(0, weight = 1)
        self.exit.grid_columnconfigure(0, weight = 1)
        tk.Label(self.exit, text = 'Thank you!', font = (None, 50)).grid(row = 0, column = 1, padx = (800, 20), pady = (400,20))
        tk.Button(self.exit, text = 'Save', font = (None, 30)).grid(row = 1, column = 1, padx = 10, pady = 10)
        tk.Button(self.exit, text = 'Exit', font = (None, 30), command = self.window.destroy()).grid(row = 1, column = 2, padx = 10, pady = 10)

root = tk.Tk()
root.title("Horse Racing")
root.geometry("500x400")
root.bind('<Control-q>', quit)
app = Window1(root)
root.mainloop()
