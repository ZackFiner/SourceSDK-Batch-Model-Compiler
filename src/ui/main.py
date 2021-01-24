from tkinter import Tk, Label, Button, filedialog, Text, INSERT
class MainLanding:
    def __init__(self, master):
        self.master = master
        master.title("Source Batch Helper")
        self.data_table = dict()

        self.label = Label(master, text="Model Batch Helper")
        self.label.pack()
        self.choose_file_text = Text(master)
        self.choose_file_text.pack()
        self.choose_file = Button(master, text="Select File", command=self.select_file("filename"))
        self.choose_file.pack()
        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

    def select_file(self, key):
        def func():
            result = filedialog.askopenfilename()
            self.data_table[key] = result
            self.choose_file_text.delete("1.0", "end")  # clear the specific file object
            self.choose_file_text.insert(INSERT, result)
        return func


root = Tk()
main_landing = MainLanding(root)
root.mainloop()