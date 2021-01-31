from PyQt5.QtWidgets import *
from src.SMD import SMD
import os, glob
import shutil
from src.ui.pyqt.view3d import *
import subprocess
import sys
import re


def put_file_in_dict(parent, text_dict, keyword):
    def func():
        path, _ = QFileDialog.getOpenFileName(parent, 'Select File')
        if keyword in text_dict:
            text_dict[keyword].setText(path)

    return func


def generate_temp_smd_files(mdl_path):
    tmp_path = './tmp_smd_files'
    try:
        os.mkdir(tmp_path)
    except FileExistsError:
        shutil.rmtree(tmp_path)
        os.mkdir(tmp_path)

    os.system('Crowbar.exe -p "{mdl_path}" -o "%CD%/tmp_smd_files"'.format(mdl_path=mdl_path))

    # crowbar exports smds as based on the qc it generates
    # this means that pulling the appropriate .smd out is a bit more complicated than it might
    # seem: you need to read the qc and determine what the main refernece model is, as well as
    # what body groups need to be pulled

    # the code above does work (assuming Crowbar.exe is placed in the same directory as this file)
    # but more work will need to be done in terms of pulling the right data out

    r_dict = dict()

    for file in glob.glob('{tmp_path}/*.smd'.format(tmp_path=tmp_path)):
        name = re.search(r'(?:[/\\])(?P<name>[^/\\]+)(?:[.]smd)', file).groupdict()['name']
        r_dict[name] = SMD(file)

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

        self.file_paths['mesh_smd'] = QLineEdit()
        self.file_paths['phys_smd'] = QLineEdit()
        file_path_layout.addWidget(self.file_paths['mesh_smd'], 0, 1)
        file_path_layout.addWidget(self.file_paths['phys_smd'], 1, 1)

        self.btn_select_mesh_smd = QPushButton('...')
        self.btn_select_mesh_smd.clicked.connect(put_file_in_dict(self, self.file_paths, 'mesh_smd'))
        self.btn_select_phys_smd = QPushButton('...')
        self.btn_select_phys_smd.clicked.connect(put_file_in_dict(self, self.file_paths, 'phys_smd'))

        file_path_layout.addWidget(self.btn_select_mesh_smd, 0, 2)
        file_path_layout.addWidget(self.btn_select_phys_smd, 1, 2)

        self.file_path_area.setLayout(file_path_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.file_path_area)
        self.setLayout(main_layout)

    def getSMDs(self):
        r_dict = dict()
        mesh_path = self.file_paths['mesh_smd'].text()
        phys_path = self.file_paths['phys_smd'].text()

        r_dict['mesh_smd'] = SMD(mesh_path)
        r_dict['phys_smd'] = SMD(phys_path)

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

        layout = QGridLayout()
        smd_selection_tabs = QTabWidget()
        self.smd_selector = smd_selection_tabs
        smd_selection_tabs.addTab(SMDSelector(), 'Select SMD Files')
        smd_selection_tabs.addTab(MdlSelector(), 'Select Mdl File')
        layout.addWidget(smd_selection_tabs, 0, 0)
        self.process_button = QPushButton('Go')
        self.process_button.clicked.connect(self.load_smds)
        layout.addWidget(self.process_button, 1, 0)
        #self.preview_window = SMDPreviewWindow(SMDs=[SMD('./chair_office_reference.smd')])
        #layout.addWidget(self.preview_window, 0, 1)
        self.cw.setLayout(layout)

    def load_smds(self):
        smd_tab = self.smd_selector.currentWidget()
        self.instance_data = [1,1,1,128,128,128]
        smd_dict = smd_tab.getSMDs()
        smds = list()
        names = list()
        for name, smd in smd_dict.items():
            names.append(name)
            smds.append(smd)
        self.preview_window = SMDRenderWindow(SMDs=smds, SMD_names=names, instance_data=self.instance_data)

        def create_func(idx):
            def func(data):
                self.instance_data[idx] = int(data)
                self.preview_window.update()

            return func

        self.tiling_widget = QWidget()
        tiling_widget_layout = QGridLayout()
        h_slider = QSlider(QtCore.Qt.Horizontal)
        h_slider.setTickInterval(1)
        h_slider.setMinimum(1)
        h_slider.setMaximum(10)
        h_slider.setValue(1)
        h_slider.valueChanged.connect(create_func(0))
        w_slider = QSlider(QtCore.Qt.Horizontal)
        w_slider.setTickInterval(1)
        w_slider.setMinimum(1)
        w_slider.setMaximum(10)
        w_slider.setValue(1)
        w_slider.valueChanged.connect(create_func(1))
        l_slider = QSlider(QtCore.Qt.Horizontal)
        l_slider.setTickInterval(1)
        l_slider.setMinimum(1)
        l_slider.setMaximum(10)
        l_slider.setValue(1)
        l_slider.valueChanged.connect(create_func(2))
        tiling_widget_layout.addWidget(QLabel('X #'), 0, 0)
        tiling_widget_layout.addWidget(h_slider, 0,1)
        tiling_widget_layout.addWidget(QLabel('Y #'), 1, 0)
        tiling_widget_layout.addWidget(w_slider, 1,1)
        tiling_widget_layout.addWidget(QLabel('Z #'), 2, 0)
        tiling_widget_layout.addWidget(l_slider, 2,1)
        self.tiling_widget.setLayout(tiling_widget_layout)

        self.cw.layout().addWidget(self.preview_window, 0, 1)
        self.cw.layout().addWidget(self.tiling_widget, 1, 1)

    def closeEvent(self, e):
        pass


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()