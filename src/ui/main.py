from tkinter import Tk, Label, Button, filedialog, Text, INSERT, Frame, LabelFrame
import tkinter as tk
class MainLanding:
    def init_smd_selection_area(self, master):
        self.smd_selection_container = LabelFrame(master, text="Base SMD Selection")
        self.smd_selection_container.pack()
        self.file_path_area = Frame(self.smd_selection_container)
        self.file_path_area.pack(fill=tk.BOTH)


        self.lbl_mesh_smd = Label(self.file_path_area, text="Mesh SMD")
        self.lbl_mesh_smd.grid(row=0, column=0)
        self.text_inputs["mesh_smd"] = Text(self.file_path_area, height=1, width=30)
        self.text_inputs["mesh_smd"].grid(row=0, column=1)
        self.btn_select_mesh_smd = Button(self.file_path_area, text="...", command=self.select_file("mesh_smd"))
        self.btn_select_mesh_smd.grid(row=0, column=2)

        self.lbl_phys_smd = Label(self.file_path_area, text="Phys SMD")
        self.lbl_phys_smd.grid(row=1, column=0)
        self.text_inputs["phys_smd"] = Text(self.file_path_area, height=1, width=30)
        self.text_inputs["phys_smd"].grid(row=1, column=1)
        self.btn_select_phys_smd = Button(self.file_path_area, text="...", command=self.select_file("phys_smd"))
        self.btn_select_phys_smd.grid(row=1, column=2)

        self.lbl_ref_smd = Label(self.file_path_area, text="Ref SMD")
        self.lbl_ref_smd.grid(row=2, column=0)
        self.text_inputs["ref_smd"] = Text(self.file_path_area, height=1, width=30)
        self.text_inputs["ref_smd"].grid(row=2, column=1)
        self.btn_select_ref_smd = Button(self.file_path_area, text="...", command=self.select_file("ref_smd"))
        self.btn_select_ref_smd.grid(row=2, column=2)

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