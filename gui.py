import os
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QVBoxLayout, QWidget, QMessageBox, \
    QFileDialog, QProgressBar, QSizePolicy, QHBoxLayout, QSpacerItem
from PyQt5.QtCore import QThread, pyqtSignal
import serial.tools.list_ports


class UploadThread(QThread):
    finished = pyqtSignal()

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        subprocess.run(self.cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.finished.emit()


def showMessageBox(title, message, icon=QMessageBox.Information):
    msgBox = QMessageBox()
    msgBox.setIcon(icon)
    msgBox.setWindowTitle(title)
    msgBox.setText(message)
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.refreshButton = None
        self.chooseButton = None
        self.hex_path = None
        self.uploadButton = None
        self.combo = None
        self.progressBar = None
        self.initUI()

    def initUI(self):
        os.system('title UF')  # Definir o título do console do Windows
        layout = QVBoxLayout()
        self.setWindowTitle("UF")  # Definir o título da janela
        self.setFixedSize(300, 200)

        # Adiciona espaçadores para centralizar os widgets verticalmente
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.combo = QComboBox()
        self.combo.addItems([port.device for port in serial.tools.list_ports.comports()])
        layout.addWidget(self.combo)

        self.refreshButton = QPushButton("Refresh COM")
        self.refreshButton.clicked.connect(self.refreshPorts)
        layout.addWidget(self.refreshButton)

        self.chooseButton = QPushButton("File")
        self.chooseButton.clicked.connect(self.chooseFile)
        layout.addWidget(self.chooseButton)

        self.uploadButton = QPushButton("Upload")
        self.uploadButton.clicked.connect(self.uploadFirmware)
        self.uploadButton.setEnabled(False)
        layout.addWidget(self.uploadButton)

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0)
        self.progressBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Ajustar política de tamanho
        progressBarLayout = QHBoxLayout()
        progressBarLayout.addWidget(self.progressBar)  # Adiciona a barra de progresso ao layout sem espaçadores
        progressBarContainer = QWidget()
        progressBarContainer.setLayout(progressBarLayout)
        layout.addWidget(progressBarContainer)
        self.progressBar.hide()

        # Adiciona outro espaçador para manter os widgets centralizados
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def chooseFile(self):
        self.hex_path, _ = QFileDialog.getOpenFileName(self, "Choose the file", "", "Hex Files (*.hex)")
        self.uploadButton.setEnabled(bool(self.hex_path))

    def refreshPorts(self):
        self.combo.clear()
        self.combo.addItems([port.device for port in serial.tools.list_ports.comports()])

    def uploadFirmware(self):
        port = self.combo.currentText()
        avrdude_path = "./avrdude.exe"
        conf_path = "./avrdude.conf"

        if not self.hex_path:
            return

        cmd = [avrdude_path, "-C", conf_path, "-v", "-patmega32u4", "-cavr109", "-P", port, "-b57600", "-D",
               "-Uflash:w:{}:i".format(self.hex_path)]
        self.hideButtons()  # Ocultar botões
        self.progressBar.show()
        self.thread = UploadThread(cmd)
        self.thread.finished.connect(self.onUploadFinished)
        self.thread.start()

    def onUploadFinished(self):
        self.progressBar.hide()  # Ocultar a barra de progresso
        self.showButtons()
        showMessageBox("Success", "Firmware loaded successfully!")
        self.uploadButton.setEnabled(False)
        self.hex_path = None

    def hideButtons(self):
        self.refreshButton.hide()
        self.chooseButton.hide()
        self.uploadButton.hide()
        self.combo.hide()

    def showButtons(self):
        self.refreshButton.show()
        self.chooseButton.show()
        self.uploadButton.show()
        self.combo.show()


app = QApplication(sys.argv)
ex = MainWindow()
ex.show()
sys.exit(app.exec())
