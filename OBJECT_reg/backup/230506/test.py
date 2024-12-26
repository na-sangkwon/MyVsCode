import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QLineEdit, QHBoxLayout, QGridLayout
from PyQt5.QtCore import QSettings, Qt, QEvent
import obang, hanbang, naver
import object_data, threading


class MyApp(QWidget):

  def __init__(self):
    super().__init__()
    self.queryData = {}
    self.initUI() #인터페이스를 초기화
    self.user = { #딕셔너리를 생성하여 사용자 ID와 PW를 저장
      'id':self.idInput.text(),
      'pw':self.pwInput.text()
    }

  def obangThread(self):
    thread_o = threading.Thread(target=self.onObang) #새로운 스레드 객체를 생성
    thread_o.daemon = True #메인 스레드가 종료될 때 자동으로 스레드를 종료
    thread_o.start()

  def naverThread(self):
    thread_n = threading.Thread(target=self.onNaver)
    thread_n.daemon = True
    thread_n.start()

  def hanbangThread(self):
    thread_n = threading.Thread(target=self.onHanbang)
    thread_n.daemon = True
    thread_n.start()

  def initUI(self):
    
    settings = QSettings('NSGMacro', 'nsg') # 'NSGMacro' 앱의 설정 파일을 로드
    userId = settings.value('userId')
    userPw = settings.value('userPw')

    self.objectLabel = QLabel('새홈 번호: ')
    self.objectInput = QLineEdit(self)
    self.objectInput.setText('') # 799920 916563 357984 374005
    self.objectInput.textChanged.connect(self.update_button_state) #self.objectInput의 textChanged 시그널을 self.update_button_state 슬롯에 연결
    self.objectInput.selectAll() #모든 텍스트를 선택
    self.objectInput.mousePressEvent = self.focusObjInput #self.objectInput 위젯의 mousePressEvent 이벤트를 재정의하여 클릭 시 모든 텍스트를 선택하도록 설정

    self.objectInput.setFocus()  # objectInput 위젯에 초기 포커스 설정

    self.objectBtn = QPushButton('불러오기',self)
    self.objectBtn.clicked.connect(self.onObjectClick) #self.objectBtn 위젯의 clicked 시그널을 self.onObjectClick 슬롯에 연결합니다.

    self.idLabel = QLabel('ID: ')
    self.idInput = QLineEdit(self)
    self.idInput.setText(userId) #self.idInput 위젯의 초기 텍스트를 userId로 설정
    self.idInput.textChanged.connect(self.updateId) #self.idInput 위젯의 textChanged 시그널을 self.updateId 슬롯에 연결

    self.pwLabel = QLabel('PW: ')
    self.pwInput = QLineEdit(self)
    self.pwInput.setText(userPw)
    self.pwInput.textChanged.connect(self.updatePw)


    self.startBtn = QPushButton('오방', self)
    self.startBtn.clicked.connect(self.obangThread) #self.startBtn 위젯의 clicked 시그널을 self.startThread 슬롯에 연결

    self.hanbangBtn = QPushButton('한방', self)  # '한방' 버튼 생성
    self.hanbangBtn.clicked.connect(self.hanbangThread)

    self.naverBtn = QPushButton('네이버', self)  # '네이버' 버튼 생성
    self.naverBtn.clicked.connect(self.naverThread)


    # 'ENTER' key로 시작하기 버튼 클릭하기
    self.objectInput.returnPressed.connect(self.startBtn.click) #self.objectInput 위젯의 returnPressed 시그널을 self.startBtn 위젯의 click 슬롯에 연결

    #ID와 비밀번호 입력에 대한 레이아웃
    userBox = QHBoxLayout()
    userBox.addWidget(self.idLabel)
    userBox.addWidget(self.idInput)
    userBox.addWidget(self.pwLabel)
    userBox.addWidget(self.pwInput)

    #새홈 번호 입력에 대한 레이아웃
    hbox = QHBoxLayout()
    hbox.addStretch(1) #외쪽공백
    hbox.addWidget(self.objectLabel)
    hbox.addWidget(self.objectInput)
    hbox.addWidget(self.objectBtn)
    hbox.addStretch(1) #오른쪽공백

    #오방등록버튼,한방등록버튼에 대한 레이아웃
    hbox3 = QHBoxLayout()
    hbox3.addStretch(1)
    hbox3.addWidget(self.startBtn)
    hbox3.addWidget(self.hanbangBtn)  # '한방등록' 버튼
    hbox3.addWidget(self.naverBtn)
    hbox3.addStretch(1)
    

    vbox = QVBoxLayout()
    vbox.addStretch(1) #상단공백
    vbox.addLayout(userBox)
    vbox.addLayout(hbox)
    vbox.addLayout(hbox3)
    vbox.addStretch(1) #하단공백
    self.setLayout(vbox) #전체 레이아웃을 설정

    #MyApp 위젯의 창 설정과 초기 표시를 관리
    self.setWindowTitle('매물등록관리') #창 제목설정
    self.setGeometry(300, 300, 700, 50) #창의 위치와 크기를 설정(첫 번째 인자는 창의 x좌표, 두 번째 인자는 창의 y좌표, 세 번째 인자는 창의 너비, 네 번째 인자는 창의 높이)
    self.show() #창을 화면에 표시

    self.resultLabel = QLabel(self)
    vbox.addWidget(self.resultLabel) #self.resultLabel을 vbox 레이아웃에 추가

    #위젯들 간의 탭 순서를 설정
    self.setTabOrder(self.idInput, self.pwInput)
    self.setTabOrder(self.pwInput, self.objectInput)
    self.setTabOrder(self.objectInput, self.objectBtn)
    self.setTabOrder(self.objectBtn, self.startBtn)

  def focusObjInput(self, event): # objectInput 위젯에 대한 포커스 이벤트를 처리(마우스 버튼이 눌릴 때 objectInput 위젯이 선택되고, 모든 텍스트가 선택되도록 설정)
    if event.type() == QEvent.MouseButtonPress:
        if event.button() == Qt.LeftButton:
            self.objectInput.selectAll()
  
  def onObjectClick(self): # "불러오기" 버튼 클릭 시 수행되는 동작을 정의
    getData = object_data.getData(self.objectInput.text()) # objectInput에 입력된 텍스트에 대한 데이터를 가져옵니다.
    self.resultLabel.setText(getData['folderPath']) #getData에서 folderPath 값을 가져와 resultLabel에 텍스트로 표시
    self.queryData = getData #queryData에 getData 값을 저장
  
  # def onNaverClick(self): 
  #   print("네이버등록을 시작합니다.")
  #   getData = object_data.getData(self.objectInput.text())
  #   self.resultLabel.setText(getData['folderPath'])
  #   self.queryData = getData
  
  def onObang(self): #"오방" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick() #데이터를 가져오고 queryData를 업데이트
    obang.macro(data = self.queryData, user = self.user) #obang.macro 함수를 호출하여 queryData와 user 정보를 전달하여 작업을 실행
  
  def onHanbang(self): #"한방" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick()
    print("한방 매물등록을 시작합니다.")
    hanbang.macro(data = self.queryData, user = self.user)
  
  def onNaver(self): #"네이버" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick()
    print("네이버 매물등록을 시작합니다.")
    naver.macro(data = self.queryData, user = self.user)

  def closeEvent(self, event): #창을 닫을 때 수행되는 동작을 정의
    self.save_value() #사용자 설정을 저장
    event.accept() #이벤트를 수락하고 창을 닫습니다.

  def save_value(self): #사용자 설정을 저장하는 동작을 정의
    settings = QSettings('NSGMacro', 'nsg') # 'NSGMacro' 앱의 설정 파일을 업데이트
    settings.setValue('userId', self.idInput.text())
    settings.setValue('userPw', self.pwInput.text())
  
  def update_button_state(self): #버튼 상태를 업데이트하는 동작을 정의
    if self.objectInput.text() == "": #objectInput에 텍스트가 비어있으면
      self.startBtn.setEnabled(False) #startBtn을 비활성화
    else:
      self.startBtn.setEnabled(True) #startBtn을 활성화

  def updateId(self, text):
    self.user['id'] = text #text 매개변수로 전달된 텍스트 값을 사용하여 self.user 딕셔너리의 'id' 키에 해당하는 값을 업데이트

  def updatePw(self, text):
    self.user['pw'] = text

  def keyPressEvent(self, event): #키 이벤트를 처리하는 동작을 정의
    if event.key() == Qt.Key_Return and self.objectInput.hasFocus():
      self.startBtn.click()

  def focusInEvent(self, event): #위젯에 포커스가 들어올 때 발생하는 이벤트를 처리하는 동작을 정의
    if event.reason() == Qt.TabFocusReason: #위젯에 탭 키로 이동하여 포커스를 가져올 때, 기존의 텍스트가 선택된 상태로 입력을 시작할 수 있습니다.
      self.objectInput.selectAll()

if __name__ == '__main__': #이 스크립트 파일이 직접 실행되었는지 확인, 모듈로 임포트될 때는 실행되지 않습니다.
  app = QApplication(sys.argv) #QApplication을 생성하여 app 변수에 저장
  ex = MyApp() #MyApp 위젯을 생성하여 ex 변수에 저장
  ex.show() # MyApp 위젯을 화면에 표시
  sys.exit(app.exec_()) #app.exec_()를 호출하여 이벤트 루프를 실행하고 애플리케이션을 정상적으로 종료