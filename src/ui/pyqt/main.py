from PyQt5.QtWidgets import *
import sys

class SMDSelector(QWidget):
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
        self.btn_select_mesh_smd.clicked.connect(self.get_file_path_from_dialog('mesh_smd'))
        self.btn_select_phys_smd = QPushButton('...')
        self.btn_select_phys_smd.clicked.connect(self.get_file_path_from_dialog('phys_smd'))
        self.btn_select_ref_smd = QPushButton('...')
        self.btn_select_ref_smd.clicked.connect(self.get_file_path_from_dialog('ref_smd'))
        file_path_layout.addWidget(self.btn_select_mesh_smd, 0, 2)
        file_path_layout.addWidget(self.btn_select_phys_smd, 1, 2)
        file_path_layout.addWidget(self.btn_select_ref_smd, 2, 2)

        self.file_path_area.setLayout(file_path_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.file_path_area)
        self.setLayout(main_layout)

    def get_file_path_from_dialog(self, key_word):
        def func():
            path, _ = QFileDialog.getOpenFileName(self, 'Select File')
            if key_word in self.file_paths:
                self.file_paths[key_word].setText(path)
        return func


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

        layout.addWidget(SMDSelector(), 0, 0)
        self.cw.setLayout(layout)

    def do_something(self):
        self.index += 1
        print(self.index)

    def closeEvent(self, e):
        pass

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()