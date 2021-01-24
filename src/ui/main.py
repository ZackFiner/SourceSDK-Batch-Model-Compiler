from tkinter import Tk, Label, Button, filedialog, Text, INSERT, Frame, LabelFrame
import tkinter as tk
class MainLanding:
    def init_smd_selection_area(self, master):
        self.smd_selection_container = LabelFrame(master, text="Base SMD Selection")
        self.smd_selection_container.pack(fill=tk.BOTH)
        row1 = Frame(self.smd_selection_container)
        row1.pack(fill=tk.X)
        row2 = Frame(self.smd_selection_container)
        row2.pack(fill=tk.X)
        row3 = Frame(self.smd_selection_container)
        row3.pack(fill=tk.X)

        self.lbl_mesh_smd = Label(row1, text="Mesh SMD")
        self.lbl_mesh_smd.pack(fill=tk.X, side=tk.LEFT)
        self.text_inputs["mesh_smd"] = Text(row1, height=1, width=30)
        self.text_inputs["mesh_smd"].pack(side=tk.LEFT, fill=tk.X)
        self.btn_select_mesh_smd = Button(row1, text="...", command=self.select_file("mesh_smd"))
        self.btn_select_mesh_smd.pack(side=tk.LEFT, fill=tk.X)

        self.lbl_phys_smd = Label(row2, text="Phys SMD")
        self.lbl_phys_smd.pack(fill=tk.X, side=tk.LEFT)
        self.text_inputs["phys_smd"] = Text(row2, height=1, width=30)
        self.text_inputs["phys_smd"].pack(side=tk.LEFT, fill=tk.X)
        self.btn_select_phys_smd = Button(row2, text="...", command=self.select_file("phys_smd"))
        self.btn_select_phys_smd.pack(side=tk.LEFT, fill=tk.X)

        self.lbl_ref_smd = Label(row3, text="Ref SMD")
        self.lbl_ref_smd.pack(fill=tk.X, side=tk.LEFT)
        self.text_inputs["ref_smd"] = Text(row3, height=1, width=30)
        self.text_inputs["ref_smd"].pack(fill=tk.X, side=tk.LEFT)
        self.btn_select_ref_smd = Button(row3, text="...", command=self.select_file("ref_smd"))
        self.btn_select_ref_smd.pack(side=tk.LEFT, fill=tk.X)

    def __init__(self, master):
        self.master = master
        master.title("Source Batch Helper")
        self.data_table = dict()
        self.text_inputs = dict()

        self.init_smd_selection_area(master)

        self.label = Label(master, text="Model Batch Helper")
        self.label.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()


    def select_file(self, text_input_key):
        def func():
            result = filedialog.askopenfilename()
            if text_input_key in self.text_inputs:
                self.text_inputs[text_input_key].delete("1.0", "end")  # clear the specific file object
                self.text_inputs[text_input_key].insert(INSERT, result)
        return func


root = Tk()
main_landing = MainLanding(root)
root.mainloop()