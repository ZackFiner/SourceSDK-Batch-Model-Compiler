from tkinter import Tk, Label, Button, filedialog, Text, INSERT, Frame, LabelFrame, OptionMenu
import tkinter as tk


def select_file_callback(text_dict, text_input_key):
    def func():
        result = filedialog.askopenfilename()
        if text_input_key in text_dict:
            text_dict[text_input_key].delete("1.0", "end")  # clear the specific file object
            text_dict[text_input_key].insert(INSERT, result)
    return func


class MDLSelectionMenu:
    def __init__(self, master):
        self.master = master
        self.container_Frame = Frame(self.master)
        self.file_path_area = Frame(self.container_Frame)
        self.file_path_area.pack(fill=tk.BOTH)

        self.lbl_model_mdl = Label(self.file_path_area, text="Model File")
        self.lbl_model_mdl.grid(row=0, column=0)

        self.text_inputs["model_mdl"] = Text(self.file_path_area, height=1, width=30)
        self.text_inputs["model_mdl"].grid(row=0, column=1)

        self.btn_select_model_mdl = Button(self.file_path_area, text="...", command=select_file_callback(self.text_inputs, "model_mdl"))
        self.btn_select_model_mdl.grid(row=0, column=2)

    def get_frame(self):
        return self.container_Frame


class SMDSelectionMenu:
    def __init__(self, master):
        self.text_inputs = dict()
        self.master = master
        self.container_frame = Frame(self.master)
        self.file_path_area = Frame(self.container_frame)
        self.file_path_area.pack(fill=tk.BOTH)

        self.lbl_mesh_smd = Label(self.file_path_area, text="Mesh SMD")
        self.lbl_mesh_smd.grid(row=0, column=0)
        self.text_inputs["mesh_smd"] = Text(self.file_path_area, height=1, width=30)
        self.text_inputs["mesh_smd"].grid(row=0, column=1)
        self.btn_select_mesh_smd = Button(self.file_path_area, text="...", command=select_file_callback(self.text_inputs, "mesh_smd"))
        self.btn_select_mesh_smd.grid(row=0, column=2)

        self.lbl_phys_smd = Label(self.file_path_area, text="Phys SMD")
        self.lbl_phys_smd.grid(row=1, column=0)
        self.text_inputs["phys_smd"] = Text(self.file_path_area, height=1, width=30)
        self.text_inputs["phys_smd"].grid(row=1, column=1)
        self.btn_select_phys_smd = Button(self.file_path_area, text="...", command=select_file_callback(self.text_inputs, "phys_smd"))
        self.btn_select_phys_smd.grid(row=1, column=2)

        self.lbl_ref_smd = Label(self.file_path_area, text="Ref SMD")
        self.lbl_ref_smd.grid(row=2, column=0)
        self.text_inputs["ref_smd"] = Text(self.file_path_area, height=1, width=30)
        self.text_inputs["ref_smd"].grid(row=2, column=1)
        self.btn_select_ref_smd = Button(self.file_path_area, text="...", command=select_file_callback(self.text_inputs, "ref_smd"))
        self.btn_select_ref_smd.grid(row=2, column=2)

    def get_frame(self):
        return self.container_frame


class SelectFramePanel:
    def __init__(self, master, frame_dict):
        self.master = master
        self.frame_dict = frame_dict
        self.selected = list(frame_dict)[0]

        self.container_frame = Frame(self.master)

    def select_frame(self, *args):
        pass



class MainLanding:
    def __init__(self, master):
        self.master = master
        master.title("Source Batch Helper")
        self.data_table = dict()
        self.text_inputs = dict()
        self.smd_selection_container = LabelFrame(master, text="Base Model Selection")
        self.smd_selection_container.pack()
        self.file_selection_area = SMDSelectionMenu(self.smd_selection_container)

        self.label = Label(master, text="Model Batch Helper")
        self.label.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()


root = Tk()
main_landing = MainLanding(root)
root.mainloop()