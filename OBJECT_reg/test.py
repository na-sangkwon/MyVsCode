import sys
print(sys.executable)
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QLineEdit, QHBoxLayout, QGridLayout, QMessageBox
from PyQt5.QtCore import QSettings, Qt, QEvent, pyqtSignal
import obang, obs, hanbang, naver, zigbang, register, deunggi
import object_data, threading
import pyautogui 
import time

from PyQt5.QtWidgets import QMessageBox
from naver import NaverThread 

class MyApp(QWidget):
  # # 시그널 정의
  # show_confirmation_signal = pyqtSignal()
  
  def __init__(self):
    super().__init__()
    self.queryData = {}
    self.initUI() #인터페이스를 초기화
    self.user = { #딕셔너리를 생성하여 사용자 ID와 PW를 저장
      'id':self.idInput.text(),
      'pw':self.pwInput.text()
    }

  def obangThread(self):
    objectNumbers = self.objectInput.text()
    print(f"objectNumbers: {objectNumbers}")
    objectNumber = objectNumbers.split(',')

    # objectNumber 배열의 길이 확인
    최대등록가능개수 = "30"
    if len(objectNumber) > int(최대등록가능개수):
        pyautogui.alert(f"등록요청 매물개수: {len(objectNumber)}개\n\n최대 {최대등록가능개수}개의 매물만 일괄등록 가능합니다.")
        return  # 함수 종료
    threads = []
    for object_code in objectNumber:
      # print(f"object_code: {object_code}")
      if len(objectNumber) != 1 : #일괄등록
        thread_o = threading.Thread(target=self.onObang, args=(object_code,'Y'))  # 필요한 인자를 args 튜플로 전달
        thread_o.daemon = True
        threads.append(thread_o)
        thread_o.start()
        time.sleep(10)
      else: #단일등록
        self.onObjectClick()
        thread_o = threading.Thread(target=self.onObang) #새로운 스레드 객체를 생성
        thread_o.daemon = True
        threads.append(thread_o)
        thread_o.start()
    
    if len(objectNumber) != 1 :    
      # 모든 스레드의 완료를 기다립니다.
      for t in threads:
          t.join()
      pyautogui.alert("모든 매물 등록이 완료되었습니다.")  # 모든 스레드 완료 후 메시지 표시

  def obsThread(self):
    thread_n = threading.Thread(target=self.onObs)
    thread_n.daemon = True
    thread_n.start()

   # naver.py에서 NaverThread 가져오기
  def naverThread(self):
    # thread_n = threading.Thread(target=self.onNaver)
    # thread_n.daemon = True
    # thread_n.start()


    self.onObjectClick()
    print("네이버 매물등록을 시작합니다.")

    # NaverThread 생성
    self.thread = NaverThread(self.queryData, self.user)
    self.thread.ask_confirmation.connect(self.show_confirmation)
    self.thread.finished.connect(self.on_naver_finished)
    self.thread.start()
  def show_confirmation(self, message):
      # 메인 스레드에서 확인 메시지 띄우기
      response = QMessageBox.question(
          self,
          "확인",
          message,
          QMessageBox.Yes | QMessageBox.No
      )
      # 사용자 응답을 스레드로 전달
      self.thread.send_response(response == QMessageBox.Yes)

  def on_naver_finished(self, success):
      # 스레드 작업 완료 후 처리
      if success:
          QMessageBox.information(self, "완료", "네이버 매물 등록이 완료되었습니다.")
      else:
          QMessageBox.warning(self, "중단", "네이버 매물 등록이 중단되었습니다.")


  def hanbangThread(self):
    thread_n = threading.Thread(target=self.onHanbang)
    thread_n.daemon = True
    thread_n.start()

  def zigbangThread(self):
    thread_n = threading.Thread(target=self.onZigbang)
    thread_n.daemon = True
    thread_n.start()

  def BuildingRegisterThread(self):
    thread_n = threading.Thread(target=self.onBuildingRegister)
    thread_n.daemon = True
    thread_n.start()

  def RegistrationCertThread(self):
    thread_n = threading.Thread(target=self.onRegistrationCert)
    thread_n.daemon = True
    thread_n.start()

  def initUI(self):
    
    settings = QSettings('NSGMacro', 'nsg') # 'NSGMacro' 앱의 설정 파일을 로드
    userId = settings.value('userId')
    userPw = settings.value('userPw')

    self.objectLabel = QLabel('새홈 번호: ')
    self.objectInput = QLineEdit(self)
    self.objectInput.setText('508005') # 10172 543937
    # self.objectInput.setText('670983,343799,248831') # 10172 543937
    self.objectInput.textChanged.connect(self.update_button_state) #self.objectInput의 textChanged 시그널을 self.update_button_state 슬롯에 연결
    self.objectInput.selectAll() #모든 텍스트를 선택
    self.objectInput.mousePressEvent = self.focusObjInput #self.objectInput 위젯의 mousePressEvent 이벤트를 재정의하여 클릭 시 모든 텍스트를 선택하도록 설정

    self.objectInput.setFocus()  # objectInput 위젯에 초기 포커스 설정

    self.objectBtn = QPushButton('불러오기',self)
    self.objectBtn.clicked.connect(self.onObjectClick) #self.objectBtn 위젯의 clicked 시그널을 self.onObjectClick 슬롯에 연결합니다.

    self.idLabel = QLabel('프로중개인ID: ')
    self.idInput = QLineEdit(self)
    self.idInput.setText(userId) #self.idInput 위젯의 초기 텍스트를 userId로 설정
    self.idInput.textChanged.connect(self.updateId) #self.idInput 위젯의 textChanged 시그널을 self.updateId 슬롯에 연결

    self.pwLabel = QLabel('PW: ')
    self.pwInput = QLineEdit(self)
    self.pwInput.setEchoMode(QLineEdit.Password) # 패스워드 입력 시 별표 표시
    self.pwInput.setText(userPw)
    self.pwInput.textChanged.connect(self.updatePw)

    self.startBtn = QPushButton('오방', self)
    self.startBtn.clicked.connect(self.obangThread) #self.startBtn 위젯의 clicked 시그널을 self.startThread 슬롯에 연결

    self.obsBtn = QPushButton('오부사', self)  # '오부사' 버튼 생성
    self.obsBtn.clicked.connect(self.obsThread)

    self.hanbangBtn = QPushButton('한방', self)  # '한방' 버튼 생성
    self.hanbangBtn.clicked.connect(self.hanbangThread)

    self.naverBtn = QPushButton('네이버', self)  # '네이버' 버튼 생성
    self.naverBtn.clicked.connect(self.naverThread)

    self.zigbangBtn = QPushButton('직방', self)  # '직방' 버튼 생성
    self.zigbangBtn.clicked.connect(self.zigbangThread)

    self.BuildingRegisterBtn = QPushButton('건축물대장', self)  # '건축물대장' 버튼 생성
    self.BuildingRegisterBtn.clicked.connect(self.BuildingRegisterThread)

    self.RegistrationCertBtn = QPushButton('등기부등본', self)  # '등기부등본' 버튼 생성
    self.RegistrationCertBtn.clicked.connect(self.RegistrationCertThread)
    
    self.msgLabel = QLabel('제목 15글자 이상, 제목과 연관지어서 상세설명 60자 이상 작성 할 것!!')

    self.statusLabel = QLabel('상태:',self)  # QLabel을 생성하여 상태 표시 메시지를 표시할 위젯으로 사용합니다.
    # self.statusBar().addWidget(self.statusLabel)  # QMainWindow의 상태 표시줄에 QLabel을 배치합니다.

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
    hbox3.addWidget(self.obsBtn)
    hbox3.addWidget(self.hanbangBtn)  # '한방등록' 버튼
    hbox3.addWidget(self.naverBtn)
    hbox3.addWidget(self.zigbangBtn)
    hbox3.addStretch(1)
    
    hbox4 = QHBoxLayout()
    # hbox4.addWidget(self.msgLabel)
    hbox4.addWidget(self.statusLabel)
    hbox4.addStretch(1)
    
    hbox5 = QHBoxLayout()
    # hbox5.addWidget(self.msgLabel)
    hbox5.addWidget(self.BuildingRegisterBtn)
    hbox5.addWidget(self.RegistrationCertBtn)
    hbox5.addStretch(1)
    

    vbox = QVBoxLayout()
    vbox.addStretch(1) #상단공백
    vbox.addLayout(userBox)
    vbox.addLayout(hbox)
    vbox.addLayout(hbox3)
    vbox.addStretch(1) #하단공백
    vbox.addWidget(self.msgLabel)
    vbox.addStretch(1) #하단공백
    vbox.addLayout(hbox4)
    vbox.addStretch(1) #하단공백
    vbox.addLayout(hbox5)
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


    # # 버튼들을 그리드 형태로 배치
    # gridLayout = QGridLayout()
    # gridLayout.addWidget(self.startBtn, 0, 0)  # 첫 번째 줄, 첫 번째 열
    # gridLayout.addWidget(self.obsBtn, 0, 1)  # 첫 번째 줄, 두 번째 열
    # gridLayout.addWidget(self.hanbangBtn, 1, 0)  # 두 번째 줄, 첫 번째 열
    # gridLayout.addWidget(self.naverBtn, 1, 1)  # 두 번째 줄, 두 번째 열
    # gridLayout.addWidget(self.zigbangBtn, 1, 2)  # 두 번째 줄, 세 번째 열

    # vbox.addLayout(gridLayout)  # 그리드 레이아웃을 vbox에 추가

  def focusObjInput(self, event): # objectInput 위젯에 대한 포커스 이벤트를 처리(마우스 버튼이 눌릴 때 objectInput 위젯이 선택되고, 모든 텍스트가 선택되도록 설정)
    if event.type() == QEvent.MouseButtonPress:
        if event.button() == Qt.LeftButton:
            self.objectInput.selectAll()
  
  def onObjectClick(self): # "불러오기" 버튼 클릭 시 수행되는 동작을 정의
    getData = object_data.getData(self.objectInput.text(), self.idInput.text(), self.pwInput.text()) # objectInput에 입력된 텍스트에 대한 데이터를 가져옵니다.
    if getData:
      self.resultLabel.setText(getData['folderPath']) #getData에서 folderPath 값을 가져와 resultLabel에 텍스트로 표시
      self.queryData = getData #queryData에 getData 값을 저장
        

  def onObang(self, objectNumber = '', group='N'):
      print(f"onObang({objectNumber})")
      self.group = group
      if objectNumber != '':
        getData = object_data.getData(objectNumber, self.idInput.text(), self.pwInput.text())
        if getData:
            self.queryData = getData
      # print("getData:", getData)
      if self.queryData:
        obang.macro(data=self.queryData, user=self.user, group=self.group)  # 매물 등록 처리   
      
  def onObs(self): #"오부사" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick()
    print("오부사 매물등록을 시작합니다.")
    obs.macro(data = self.queryData, user = self.user)
  
  def onHanbang(self): #"한방" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick()
    print("한방 매물등록을 시작합니다.")
    hanbang.macro(data = self.queryData, user = self.user)
  
  def onNaver(self): #"네이버" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick()
    print("네이버 매물등록을 시작합니다.")
    naver.macro(data = self.queryData, user = self.user)
  
  def onZigbang(self): #"직방" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick()
    print("직방 매물등록을 시작합니다.")
    zigbang.macro(data = self.queryData, user = self.user)
  
  def onBuildingRegister(self): #"건축물대장" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick()
    print("건축물대장발급을 시작합니다.")
    register.macro(data = self.queryData, user = self.user)
    # BuildingRegister.macro(data = self.queryData, user = self.user)
  
  def RegistrationCertThread(self): #"직방" 버튼 클릭 시 수행되는 동작을 정의
    self.onObjectClick()
    print("등기부발급을 시작합니다.")
    deunggi.macro(data = self.queryData, user = self.user)
    # RegistrationCert.macro(data = self.queryData, user = self.user)

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