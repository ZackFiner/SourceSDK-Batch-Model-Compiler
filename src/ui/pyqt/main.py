from PyQt5.QtWidgets import *
from src.SMD import SMD
import os
import shutil
import subprocess
import sys


def put_file_in_dict(parent, text_dict, keyword):
    def func():
        path, _ = QFileDialog.getOpenFileName(parent, 'Select File')
        if keyword in text_dict:
            text_dict[keyword].setText(path)

    return func

import re
def generate_temp_smd_files(mdl_path):
    tmp_path = './tmp_smd_files'
    try:
        os.mkdir(tmp_path)
    except FileExistsError:
        shutil.rmtree(tmp_path)
        os.mkdir(tmp_path)

    os.system('Crowbar.exe -p "{mdl_path}" -o "%CD%/tmp_smd_files"'.format(mdl_path=mdl_path))
    name = re.search(r'(?:[/\\])(?P<name>[^/\\]+)(?:[.]mdl)', mdl_path).groupdict()['name']

    # crowbar exports smds as based on the qc it generates
    # this means that pulling the appropriate .smd out is a bit more complicated than it might
    # seem: you need to read the qc and determine what the main refernece model is, as well as
    # what body groups need to be pulled

    # the code above does work (assuming Crowbar.exe is placed in the same directory as this file)
    # but more work will need to be done in terms of pulling the right data out

    r_dict = dict()

    r_dict["mesh_smd"] = SMD("{tmp_path}/{name}_reference.smd".format(tmp_path=tmp_path, name=name))
    r_dict["phys_smd"] = SMD("{tmp_path}/{name}_physics.smd".format(tmp_path=tmp_path, name=name))
    r_dict["ref_smd"] = SMD("{tmp_path}/{name}_reference.smd".format(tmp_path=tmp_path, name=name))

    # now cleanup our file system
    shutil.rmtree(tmp_path)

    return r_dict


class SMDFileSelector:
    def getSMDs(self) -> dict:
        pass


class SMDSelector(QWidget, SMDFileSelector):
    def __init__(self, *args, **kwargs):
        # pop any custom arguments up here
        # self.some_internal = kwargs.pop('some_internal')
        super(SMDSelector, self).__init__(*args, **kwargs)
        self.file_paths = dict()
        self.file_path_area = QWidget()
        file_path_layout = QGridLayout()
        file_path_layout.addWidget(QLabel('Mesh SMD'), 0, 0)
        file_path_layout.addWidget(QLabel('Phys SMD'), 1, 0)
        file_path_layout.addWidget(QLabel('Ref SMD'), 2, 0)

        self.file_paths['mesh_smd'] = QLineEdit()
        self.file_paths['phys_smd'] = QLineEdit()
        self.file_paths['ref_smd'] = QLineEdit()
        file_path_layout.addWidget(self.file_paths['mesh_smd'], 0, 1)
        file_path_layout.addWidget(self.file_paths['phys_smd'], 1, 1)
        file_path_layout.addWidget(self.file_paths['ref_smd'], 2, 1)

        self.btn_select_mesh_smd = QPushButton('...')
        self.btn_select_mesh_smd.clicked.connect(put_file_in_dict(self, self.file_paths, 'mesh_smd'))
        self.btn_select_phys_smd = QPushButton('...')
        self.btn_select_phys_smd.clicked.connect(put_file_in_dict(self, self.file_paths, 'phys_smd'))
        self.btn_select_ref_smd = QPushButton('...')
        self.btn_select_ref_smd.clicked.connect(put_file_in_dict(self, self.file_paths, 'ref_smd'))
        file_path_layout.addWidget(self.btn_select_mesh_smd, 0, 2)
        file_path_layout.addWidget(self.btn_select_phys_smd, 1, 2)
        file_path_layout.addWidget(self.btn_select_ref_smd, 2, 2)

        self.file_path_area.setLayout(file_path_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.file_path_area)
        self.setLayout(main_layout)

    def getSMDs(self):
        r_dict = dict()
        mesh_path = self.file_paths['mesh_smd'].text()
        phys_path = self.file_paths['phys_smd'].text()
        ref_path = self.file_paths['ref_smd'].text()

        r_dict['mesh'] = SMD(mesh_path)
        r_dict['phys'] = SMD(phys_path)
        r_dict['ref'] = SMD(ref_path)

        return r_dict


class MdlSelector(QWidget):
    def __init__(self, *args, **kwargs):
        super(MdlSelector, self).__init__(*args, **kwargs)
        self.file_paths = dict()
        self.file_path_area = QWidget()
        file_path_layout = QGridLayout()

        file_path_layout.addWidget(QLabel('Model MDL'), 0, 0)

        self.file_paths['model_mdl'] = QLineEdit()
        file_path_layout.addWidget(self.file_paths['model_mdl'], 0, 1)

        self.btn_select_mdl = QPushButton('...')
        self.btn_select_mdl.clicked.connect(put_file_in_dict(self, self.file_paths, 'model_mdl'))
        file_path_layout.addWidget(self.btn_select_mdl, 0, 2)

        self.file_path_area.setLayout(file_path_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.file_path_area)
        self.setLayout(main_layout)

    def getSMDs(self):
        selected_mdl_path = self.file_paths['model_mdl'].text()
        r_dict = generate_temp_smd_files(selected_mdl_path)
        return r_dict



class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.cw = QWidget(self)
        layout = QGridLayout()
        self.setCentralWidget(self.cw)
        self.index = 0

        self.btn = QPushButton("...")
        self.btn.clicked.connect(self.do_something)

        layout = QGridLayout()
        smd_selection_tabs = QTabWidget()
        self.smd_selector = smd_selection_tabs
        smd_selection_tabs.addTab(SMDSelector(), 'Select SMD Files')
        smd_selection_tabs.addTab(MdlSelector(), 'Select Mdl File')
        layout.addWidget(smd_selection_tabs, 0, 0)
        self.process_button = QPushButton('Go')
        self.process_button.clicked.connect(self.do_something)
        layout.addWidget(self.process_button, 1, 0)

        self.cw.setLayout(layout)

    def do_something(self):
        #smd_tab = self.smd_selector.currentWidget()
        #smd_dict = smd_tab.getSMDs()
        #print(smd_dict['mesh_smd'].getsmdstring())
        print("pressed")

    def closeEvent(self, e):
        pass

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()