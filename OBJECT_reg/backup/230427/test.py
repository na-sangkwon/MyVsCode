import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QLineEdit, QHBoxLayout, QGridLayout
from PyQt5.QtCore import QSettings, Qt, QEvent
import macro
import object_data, threading


class MyApp(QWidget):

  def __init__(self):
    super().__init__()
    self.queryData = {}
    self.initUI()
    self.user = {
      'id':self.idInput.text(),
      'pw':self.pwInput.text()
    }

  def startThread(self):
    thread = threading.Thread(target=self.onStart)
    thread.daemon = True
    thread.start()

  # def oneShotThread(self):
    # self.onObjectClick()
    # macro.macro(data=self.queryData, user=self.user)

  def initUI(self):
    
    settings = QSettings('NSGMacro', 'nsg')
    userId = settings.value('userId')
    userPw = settings.value('userPw')

    self.objectLabel = QLabel('새홈 번호: ')
    self.objectInput = QLineEdit(self)
    self.objectInput.textChanged.connect(self.update_button_state)
    self.objectInput.selectAll()
    self.objectInput.mousePressEvent = self.focusObjInput

    self.objectBtn = QPushButton('불러오기',self)
    self.objectBtn.clicked.connect(self.onObjectClick)

    self.idLabel = QLabel('ID: ')
    self.idInput = QLineEdit(self)
    self.idInput.setText(userId)
    self.idInput.textChanged.connect(self.updateId)

    self.pwLabel = QLabel('PW: ')
    self.pwInput = QLineEdit(self)
    self.pwInput.setText(userPw)
    self.pwInput.textChanged.connect(self.updatePw)


    self.startBtn = QPushButton('오방등록', self)
    self.startBtn.clicked.connect(self.startThread)

    self.oneShotBtn = QPushButton('한방등록', self)  # '한방등록' 버튼 생성
    # self.oneShotBtn.clicked.connect(self.oneShotThread)  # 클릭 이벤트에 해당하는 함수 정의


    # 'ENTER' key로 시작하기 버튼 클릭하기
    self.objectInput.returnPressed.connect(self.startBtn.click)

    userBox = QHBoxLayout()
    userBox.addWidget(self.idLabel)
    userBox.addWidget(self.idInput)
    userBox.addWidget(self.pwLabel)
    userBox.addWidget(self.pwInput)

    hbox = QHBoxLayout()
    hbox.addStretch(1)
    hbox.addWidget(self.objectLabel)
    hbox.addWidget(self.objectInput)
    hbox.addWidget(self.objectBtn)
    hbox.addStretch(1)

    hbox3 = QHBoxLayout()
    hbox3.addStretch(1)
    hbox3.addWidget(self.startBtn)
    hbox3.addWidget(self.oneShotBtn)  # '한방등록' 버튼 추가
    hbox3.addStretch(1)
    

    vbox = QVBoxLayout()
    vbox.addStretch(1)
    vbox.addLayout(userBox)
    vbox.addLayout(hbox)
    vbox.addLayout(hbox3)
    vbox.addStretch(1)
    self.setLayout(vbox)

    self.setWindowTitle('macro')
    self.setGeometry(300, 300, 700, 50)
    self.show()

    self.resultLabel = QLabel(self)
    vbox.addWidget(self.resultLabel)

    # set tab order
    self.setTabOrder(self.idInput, self.pwInput)
    self.setTabOrder(self.pwInput, self.objectInput)
    self.setTabOrder(self.objectInput, self.objectBtn)
    self.setTabOrder(self.objectBtn, self.startBtn)

  def focusObjInput(self, event):
    if event.type() == QEvent.MouseButtonPress:
        if event.button() == Qt.LeftButton:
            self.objectInput.selectAll()
  
  def onObjectClick(self):
    getData = object_data.getData(self.objectInput.text())
    self.resultLabel.setText(getData['folderPath'])
    self.queryData = getData
  
  def onStart(self):
    self.onObjectClick()
    macro.macro(data = self.queryData, user = self.user)

  def closeEvent(self, event):
    self.save_value()
    event.accept()

  def save_value(self):
    settings = QSettings('NSGMacro', 'nsg')
    settings.setValue('userId', self.idInput.text())
    settings.setValue('userPw', self.pwInput.text())
  
  def update_button_state(self):
    if self.objectInput.text() == "":
      self.startBtn.setEnabled(False)
    else:
      self.startBtn.setEnabled(True)

  def updateId(self, text):
    self.user['id'] = text

  def updatePw(self, text):
    self.user['pw'] = text

  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Return and self.objectInput.hasFocus():
      self.startBtn.click()

  def focusInEvent(self, event):
    if event.reason() == Qt.TabFocusReason:
      self.objectInput.selectAll()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  ex = MyApp()
  ex.show()
  sys.exit(app.exec_())