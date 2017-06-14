import tkinter as tk
import time
from threading import Thread

def check():
    # checks for keyboard interrupts
    root.after(50, self.check)

class Window1:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        """self.button = tk.Button(self.frame, text = 'Start', command = self.new_window)
        self.button.pack()"""
        self.frame.grid()
        self.frame.grid_rowconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight = 1)
        self.settings()
    def settings(self):
        # setting title
        tk.Label(self.frame, text = 'Settings').grid(row = 1, column = 1, columnspan = 2, pady = 5)
        tk.Label(self.frame, text = '  ').grid(row = 1, column = 0)
        tk.Label(self.frame, text = '  ').grid(row = 1, column = 4, sticky = tk.E)
        # number of trails prompt
        tk.Label(self.frame, text = 'Number of Trails: ').grid(row = 2, column = 1, sticky = tk.W)
        # number of trails text box
        self.trails = tk.Entry(self.frame, width = 3)
        self.trails.grid(row = 2, column = 2, sticky = tk.W)
        # accuracy prompt
        tk.Label(self.frame, text = 'Accuracy: ').grid(row = 3, column = 1, sticky = tk.W)
        # accuracy slider
        self.accuracy = tk.Scale(self.frame, orient = tk.HORIZONTAL, resolution = 10, 
            showvalue = 0, tickinterval = 10, length = 300)
        self.accuracy.grid(row = 3, column = 2, columnspan = 2, sticky = tk.W)
        # label prompt
        tk.Label(self.frame, text = 'Label: ').grid(row = 4, column = 1, sticky = tk.W)
        # label drop down menu
        self.label = tk.StringVar(self.frame)
        option = tk.OptionMenu(self.frame, self.label, "Time", "Beyer", "Rank")
        option.grid(row = 4, column = 2, sticky = tk.W)
        # betting amount prompt
        tk.Label(self.frame, text = 'Betting Amount: ').grid(row = 5, column = 1, sticky = tk.W)
        # betting amount options
        def enableEntry():
            self.betting.configure(state = "normal")
            self.betting.update()
        def disableEntry():
            self.betting.configure(state = "disabled")
            self.betting.update()
        self.betting = tk.Entry(self.frame, width = 3, state = 'disabled')
        self.betting.grid(row = 6, column = 2, padx = 100, sticky = tk.W)
        self.option_betting = tk.StringVar()
        tk.Radiobutton(self.frame, variable = self.option_betting, text = 'Change', value = 'Change',
            command = disableEntry).grid(row = 5, column = 2, sticky = tk.W)
        tk.Radiobutton(self.frame, variable = self.option_betting, text = 'Fixed', value = 'Fixed', 
            command = enableEntry).grid(row = 6, column = 2, sticky = tk.W)
        # purse size prompt
        tk.Label(self.frame, text = 'Purse Size: ').grid(row = 7, column = 1, sticky = tk.W)
        # purse size entry
        tk.Label(self.frame, text = '$').grid(row = 7, column = 2, sticky = tk.W)
        self.purse = tk.Entry(self.frame, width = 3)
        self.purse.grid(row = 7, column = 2, sticky = tk.W, padx = 15)
        # number of horses prompt
        tk.Label(self.frame, text = 'Number of Horses: ').grid(row = 8, column = 1, sticky = tk.W)
        # number of horses entry
        self.horses = tk.Entry(self.frame, width = 3)
        self.horses.grid(row = 8, column = 2, sticky = tk.W)
        # time limit per race prompt
        tk.Label(self.frame, text = 'Time Limit per Race: ').grid(row = 9, column = 1, sticky = tk.W)
        # time limit per race entry
        self.time = tk.Entry(self.frame, width = 3)
        self.time.grid(row = 9, column = 2, sticky = tk.W)
        tk.Label(self.frame, text = 'minutes').grid(row = 9, column = 2, padx = 30, sticky = tk.W)

        # submit button
        tk.Button(self.frame, text = 'Submit', command = self.instructions).grid(row = 11, 
            column = 1, columnspan = 2, pady = 10)

        # defaults
        self.trails.insert(0, 5)
        self.accuracy.set(50)
        self.label.set("Time")
        self.option_betting.set('Change')
        self.purse.insert(0, 25)
        self.horses.insert(0, 3)
        self.time.insert(0, 15)

    def countdown(self):
        mins, secs = divmod(self.time, 60)
        self.timeformat = '{:02d}:{:02d}'.format(mins, secs)
        if self.time is not None:
            self.time = self.time
        if self.time <= 0:
            self.label.configure(text="")
            self.frame.destroy()
        else:
            self.timer_label.configure(text=self.timeformat)
            self.time = self.time - 1
            root.after(1000, self.countdown)
        self.betting_screen()

    def instructions(self):
        """SAVE DATA"""
        """CHECK IF EVERYTHING IS FILLED OUT"""
        self.trails = int(self.trails.get())
        self. accuracy = int(self.accuracy.get())
        self.label = self.label.get()
        self.purse = int(self.purse.get())
        if not (self.betting.get()):
            self.betting = 0
        else:
            self.betting = int(self.betting.get())
        self.horses = int(self.horses.get())
        self.time = int(self.time.get())
        print("Trails: ", self.trails, 
            "\nAccuracy: ", self.accuracy,
            "\nLabel: ", self.label,
            "\nBetting Amount: ", self.betting,
            "\nPurse: ", self.purse,
            "\nNumber of Horses: ", self.horses,
            "\nTime Limit per Race: ", self.time)

        # clearing screen and making a instructions screen
        self.frame.destroy()
        self.instructions = tk.Frame(self.master)
        self.instructions.grid()
        self.instructions.grid_rowconfigure(0, weight = 1)
        self.instructions.grid_columnconfigure(0, weight = 1)
        # betting screen
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.frame.grid_rowconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight = 1)
        # instructions label
        tk.Label(self.instructions, text = 'Welcome!\n Please decide the winner.'
            ' \n Press start when you are already.').grid(row = 1, column = 1, padx = 10, pady = 10)
        tk.Button(self.instructions, text = 'Start', command = self.countdown).grid(row = 2, column = 1)
        # timer
        self.t = self.time
        self.time = self.time * 60
        self.timer_label = tk.Label(self.frame, text = "", width = 10)
        self.timer_label.grid(row = 0, column = 2, sticky = tk.E)

    def betting_screen(self):
        # clear instructions screen
        self.instructions.destroy()
        tk.Entry (self.frame).grid(row = 1, column = 0)
        tk.Button(self.frame, text = 'Submit', command = self.frame.destroy).grid(row = 2, column = 1)
        print(self.timeformat)

    def new_window(self):
        self.newWindow = tk.Toplevel()
        self.app = Window2(self.newWindow)

class Window2:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.quitButton = tk.Button(self.frame, text = 'Quit', command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
    def close_windows(self):
        self.master.destroy()

root = tk.Tk()
root.title("House Racing")
root.geometry("500x300")
app = Window1(root)
root.bind('<Control-c>', quit)
root.mainloop()