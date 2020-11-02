from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QDoubleSpinBox, QSlider, QLabel, QMessageBox, QWidget, QDialog, QApplication
import sys
class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'HELP'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        #self.initUI()
    
    def initUI(self, filename = '/Users/leon/Desktop/Capture d’écran 2020-11-02 à 15.46.46.png'):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        # Create widget
        label = QLabel(self)
        pixmap = QPixmap(filename)
        label.setPixmap(pixmap)
        self.resize(pixmap.width(),pixmap.height())
        
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.initUI('/Users/leon/Desktop/Capture d’écran 2020-10-26 à 10.17.19.png')
    sys.exit(app.exec_())
    