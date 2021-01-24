from tkinter import Tk, Label, Button, filedialog
class MainLanding:
    def __init__(self, master):
        self.master = master
        master.title("Source Batch Helper")

        self.label = Label(master, text="Model Batch Helper")
        self.label.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()


root = Tk()
main_landing = MainLanding(root)
root.mainloop()