import sys, toupcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QSignalBlocker, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QDesktopWidget, QCheckBox, QMessageBox, QMainWindow, QPushButton, QComboBox, QSlider, QGroupBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QMenu, QAction

class MainWindow(QMainWindow):  #继承窗口类
    evtCallback = pyqtSignal(int) #定义了一个名为 evtCallback 的信号

    @staticmethod #这个装饰器用于指示紧随其后的方法是一个静态方法，不需要一个类实例作为第一个参数
    def makeLayout(lbl_1, sli_1, val_1, lbl_2, sli_2, val_2):
        hlyt_1 = QHBoxLayout()  # 创建第一个水平布局 hlyt_1
        hlyt_1.addWidget(lbl_1)  # 将第一个标签 lbl_1 添加到水平布局 hlyt_1
        hlyt_1.addStretch()      # 在水平布局 hlyt_1 中添加一个弹性空间
        hlyt_1.addWidget(val_1)   # 将第一个值显示 val_1 添加到水平布局 hlyt_1
        hlyt_2 = QHBoxLayout()    # 创建第二个水平布局 hlyt_2
        hlyt_2.addWidget(lbl_2)  # 将第二个标签 lbl_2 添加到水平布局 hlyt_2
        hlyt_2.addStretch()       # 在水平布局 hlyt_2 中添加一个弹性空间
        hlyt_2.addWidget(val_2)   # 将第二个值显示 val_2 添加到水平布局 hlyt_2

        vlyt = QVBoxLayout()  # 创建一个垂直布局 vlyt
        vlyt.addLayout(hlyt_1)  # 将水平布局 hlyt_1 添加到垂直布局 vlyt
        vlyt.addWidget(sli_1)   # 将第一个滑块 sli_1 添加到垂直布局 vlyt
        vlyt.addLayout(hlyt_2)  # 将水平布局 hlyt_2 添加到垂直布局 vlyt
        vlyt.addWidget(sli_2)   # 将第二个滑块 sli_2 添加到垂直布局 vlyt
        return vlyt     # 返回构建的垂直布局

    def __init__(self):
        super().__init__()   # 调用父类（QMainWindow）的构造函数来初始化窗口
        self.setMinimumSize(1024, 768)   # 设置窗口的最小尺寸为 1024x768 像素
        self.hcam = None                # 初始化一个用于存储摄像头句柄或类似对象的变量
        self.timer = QTimer(self)       # 创建一个定时器对象
        self.imgWidth = 0              # 初始化图像宽度为 0
        self.imgHeight = 0               # 初始化图像高度为 0
        self.pData = None                   # 初始化用于存储图像数据或类似内容的变量
        self.res = 0
        self.temp = toupcam.TOUPCAM_TEMP_DEF    # 初始化一个温度相关的默认值
        self.tint = toupcam.TOUPCAM_TINT_DEF    # 初始化一个色调相关的默认值
        self.count = 0      # 初始化一个计数器变量

        gbox_res = QGroupBox("Resolution")      # 创建一个带标题“Resolution”的分组框
        self.cmb_res = QComboBox()              # 创建一个下拉菜单
        self.cmb_res.setEnabled(False)          # 初始时设置下拉菜单为禁用状态
        vlyt_res = QVBoxLayout()                # 创建一个垂直布局
        vlyt_res.addWidget(self.cmb_res)        # 将下拉菜单添加到垂直布局中
        gbox_res.setLayout(vlyt_res)            # 将垂直布局设置为分组框的布局
        self.cmb_res.currentIndexChanged.connect(self.onResolutionChanged)   # 连接下拉菜单的索引变化信号到相应的槽函数

        gbox_exp = QGroupBox("Exposure")
        self.cbox_auto = QCheckBox()
        self.cbox_auto.setEnabled(False)
        lbl_auto = QLabel("Auto exposure")
        hlyt_auto = QHBoxLayout()
        hlyt_auto.addWidget(self.cbox_auto)
        hlyt_auto.addWidget(lbl_auto)
        hlyt_auto.addStretch()

        lbl_time = QLabel("Time(us):")
        lbl_gain = QLabel("Gain(%):")
        self.lbl_expoTime = QLabel("0")
        self.lbl_expoGain = QLabel("0")
        self.slider_expoTime = QSlider(Qt.Horizontal)    # 创建一个水平滑块，用于调节曝光时间
        self.slider_expoGain = QSlider(Qt.Horizontal)    # 创建一个水平滑块，用于调节曝光增益
        self.slider_expoTime.setEnabled(False)     # 初始时设置曝光时间滑块为禁用状态
        self.slider_expoGain.setEnabled(False)      # 初始时设置曝光增益滑块为禁用状态
        #曝光垂直控件
        vlyt_exp = QVBoxLayout()
        vlyt_exp.addLayout(hlyt_auto)  # # 将含有复选框的水平布局添加到垂直布局中
        #曝光调节控件，包括时间标签，时间控制块，时间数值，增益标签，增益控制块，增益数值
        vlyt_exp.addLayout(self.makeLayout(lbl_time, self.slider_expoTime, self.lbl_expoTime, lbl_gain, self.slider_expoGain, self.lbl_expoGain))  
        gbox_exp.setLayout(vlyt_exp)

        self.cbox_auto.stateChanged.connect(self.onAutoExpo)
        self.slider_expoTime.valueChanged.connect(self.onExpoTime)
        self.slider_expoGain.valueChanged.connect(self.onExpoGain)

        gbox_wb = QGroupBox("White balance")
        self.btn_autoWB = QPushButton("White balance")
        self.btn_autoWB.setEnabled(False)
        self.btn_autoWB.clicked.connect(self.onAutoWB)
        lbl_temp = QLabel("Temperature:")
        lbl_tint = QLabel("Tint:")
        self.lbl_temp = QLabel(str(toupcam.TOUPCAM_TEMP_DEF))
        self.lbl_tint = QLabel(str(toupcam.TOUPCAM_TINT_DEF))
        self.slider_temp = QSlider(Qt.Horizontal)
        self.slider_tint = QSlider(Qt.Horizontal)
        self.slider_temp.setRange(toupcam.TOUPCAM_TEMP_MIN, toupcam.TOUPCAM_TEMP_MAX)
        self.slider_temp.setValue(toupcam.TOUPCAM_TEMP_DEF)
        self.slider_tint.setRange(toupcam.TOUPCAM_TINT_MIN, toupcam.TOUPCAM_TINT_MAX)
        self.slider_tint.setValue(toupcam.TOUPCAM_TINT_DEF)
        self.slider_temp.setEnabled(False)
        self.slider_tint.setEnabled(False)
        vlyt_wb = QVBoxLayout()
        vlyt_wb.addLayout(self.makeLayout(lbl_temp, self.slider_temp, self.lbl_temp, lbl_tint, self.slider_tint, self.lbl_tint))
        vlyt_wb.addWidget(self.btn_autoWB)
        gbox_wb.setLayout(vlyt_wb)
        self.slider_temp.valueChanged.connect(self.onWBTemp)
        self.slider_tint.valueChanged.connect(self.onWBTint)

        self.btn_open = QPushButton("Open")
        self.btn_open.clicked.connect(self.onBtnOpen)
        self.btn_snap = QPushButton("Snap")
        self.btn_snap.setEnabled(False)
        self.btn_snap.clicked.connect(self.onBtnSnap)

        vlyt_ctrl = QVBoxLayout()
        vlyt_ctrl.addWidget(gbox_res)
        vlyt_ctrl.addWidget(gbox_exp)
        vlyt_ctrl.addWidget(gbox_wb)
        vlyt_ctrl.addWidget(self.btn_open)
        vlyt_ctrl.addWidget(self.btn_snap)
        vlyt_ctrl.addStretch()
        wg_ctrl = QWidget()
        wg_ctrl.setLayout(vlyt_ctrl)

        self.lbl_frame = QLabel()
        self.lbl_video = QLabel()
        vlyt_show = QVBoxLayout()
        vlyt_show.addWidget(self.lbl_video, 1)
        vlyt_show.addWidget(self.lbl_frame)
        wg_show = QWidget()
        wg_show.setLayout(vlyt_show)

        grid_main = QGridLayout()
        grid_main.setColumnStretch(0, 1)
        grid_main.setColumnStretch(1, 4)
        grid_main.addWidget(wg_ctrl)
        grid_main.addWidget(wg_show)
        w_main = QWidget()
        w_main.setLayout(grid_main)
        self.setCentralWidget(w_main)

        self.timer.timeout.connect(self.onTimer)
        self.evtCallback.connect(self.onevtCallback)

    def onTimer(self):
        if self.hcam:
            nFrame, nTime, nTotalFrame = self.hcam.get_FrameRate()
            self.lbl_frame.setText("{}, fps = {:.1f}".format(nTotalFrame, nFrame * 1000.0 / nTime))

    def closeCamera(self):
        if self.hcam:
            self.hcam.Close()
        self.hcam = None
        self.pData = None

        self.btn_open.setText("Open")
        self.timer.stop()
        self.lbl_frame.clear()
        self.cbox_auto.setEnabled(False)
        self.slider_expoGain.setEnabled(False)
        self.slider_expoTime.setEnabled(False)
        self.btn_autoWB.setEnabled(False)
        self.slider_temp.setEnabled(False)
        self.slider_tint.setEnabled(False)
        self.btn_snap.setEnabled(False)
        self.cmb_res.setEnabled(False)
        self.cmb_res.clear()

    def closeEvent(self, event):
        self.closeCamera()

    def onResolutionChanged(self, index):
        if self.hcam: #step 1: stop camera
            self.hcam.Stop()

        self.res = index
        self.imgWidth = self.cur.model.res[index].width
        self.imgHeight = self.cur.model.res[index].height

        if self.hcam: #step 2: restart camera
            self.hcam.put_eSize(self.res)
            self.startCamera()

    def onAutoExpo(self, state):
        if self.hcam:
            self.hcam.put_AutoExpoEnable(1 if state else 0)
            self.slider_expoTime.setEnabled(not state)
            self.slider_expoGain.setEnabled(not state)

    def onExpoTime(self, value):
        if self.hcam:
            self.lbl_expoTime.setText(str(value))
            if not self.cbox_auto.isChecked():
                self.hcam.put_ExpoTime(value)

    def onExpoGain(self, value):
        if self.hcam:
            self.lbl_expoGain.setText(str(value))
            if not self.cbox_auto.isChecked():
                self.hcam.put_ExpoAGain(value)

    def onAutoWB(self):
        if self.hcam:
            self.hcam.AwbOnce()

    def wbCallback(nTemp, nTint, self):
        self.slider_temp.setValue(nTemp)
        self.slider_tint.setValue(nTint)

    def onWBTemp(self, value):
        if self.hcam:
            self.temp = value
            self.hcam.put_TempTint(self.temp, self.tint)
            self.lbl_temp.setText(str(value))

    def onWBTint(self, value):
        if self.hcam:
            self.tint = value
            self.hcam.put_TempTint(self.temp, self.tint)
            self.lbl_tint.setText(str(value))

    def startCamera(self):
        #self.pData = bytes(toupcam.TDIBWIDTHBYTES(self.imgWidth * 24) * self.imgHeight) #图像缓冲区RGB24
        self.pData = bytes(toupcam.TDIBWIDTHBYTES(self.imgWidth * 16) * self.imgHeight) #图像缓冲区RGB24
        uimin, uimax, uidef = self.hcam.get_ExpTimeRange()
        self.slider_expoTime.setRange(uimin, uimax)
        self.slider_expoTime.setValue(uidef)
        usmin, usmax, usdef = self.hcam.get_ExpoAGainRange()
        self.slider_expoGain.setRange(usmin, usmax)
        self.slider_expoGain.setValue(usdef)
        self.handleExpoEvent()
        if self.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0:
            self.handleTempTintEvent()
        try:
            self.hcam.StartPullModeWithCallback(self.eventCallBack, self)
        except toupcam.HRESULTException:
            self.closeCamera()
            QMessageBox.warning(self, "Warning", "Failed to start camera.")
        else:
            self.cmb_res.setEnabled(True)
            self.cbox_auto.setEnabled(True)
            self.btn_autoWB.setEnabled(True)
            self.slider_temp.setEnabled(self.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            self.slider_tint.setEnabled(self.cur.model.flag & toupcam.TOUPCAM_FLAG_MONO == 0)
            self.btn_open.setText("Close")
            self.btn_snap.setEnabled(True)
            bAuto = self.hcam.get_AutoExpoEnable()
            self.cbox_auto.setChecked(1 == bAuto)
            self.timer.start(1000)

    def openCamera(self):
        self.hcam = toupcam.Toupcam.Open(self.cur.id)
        if self.hcam:
            self.res = self.hcam.get_eSize()
            self.imgWidth = self.cur.model.res[self.res].width
            self.imgHeight = self.cur.model.res[self.res].height
            with QSignalBlocker(self.cmb_res):
                self.cmb_res.clear()
                for i in range(0, self.cur.model.preview):
                    self.cmb_res.addItem("{}*{}".format(self.cur.model.res[i].width, self.cur.model.res[i].height))
                self.cmb_res.setCurrentIndex(self.res)
                self.cmb_res.setEnabled(True)                     
            self.hcam.put_Option(toupcam.TOUPCAM_OPTION_BYTEORDER, 0) #Qimage use RGB byte order
            self.hcam.put_Option(toupcam.TOUPCAM_OPTION_RGB, 4)
            self.hcam.put_AutoExpoEnable(1)
            self.startCamera()

    def onBtnOpen(self):
        if self.hcam:
            self.closeCamera()
        else:
            arr = toupcam.Toupcam.EnumV2()
            if 0 == len(arr):
                QMessageBox.warning(self, "Warning", "No camera found.")
            elif 1 == len(arr):
                self.cur = arr[0]
                self.openCamera()
            else:
                menu = QMenu()
                for i in range(0, len(arr)):
                    action = QAction(arr[i].displayname, self)
                    action.setData(i)
                    menu.addAction(action)
                action = menu.exec(self.mapToGlobal(self.btn_open.pos()))
                if action:
                    self.cur = arr[action.data()]
                    self.openCamera()

    def onBtnSnap(self):
        if self.hcam:
            if 0 == self.cur.model.still:    # not support still image capture
                if self.pData is not None:
                    #image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_RGB888)
                    image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_Grayscale16)
                    self.count += 1
                    #image.save("pyqt{}.jpg".format(self.count))
                    ptr = image.constBits()
                    image_arr = np.frombuffer(ptr.asstring(2048*2048*2), dtype=np.uint16).reshape(self.height, -1)* 15
                    tiff.imwrite("output_image_T.tif",image_arr)
            else:
                menu = QMenu()
                for i in range(0, self.cur.model.still):
                    action = QAction("{}*{}".format(self.cur.model.res[i].width, self.cur.model.res[i].height), self)
                    action.setData(i)
                    menu.addAction(action)
                action = menu.exec(self.mapToGlobal(self.btn_snap.pos()))
                self.hcam.Snap(action.data())

    @staticmethod
    def eventCallBack(nEvent, self):
        '''callbacks come from toupcam.dll/so internal threads, so we use qt signal to post this event to the UI thread'''
        self.evtCallback.emit(nEvent)

    def onevtCallback(self, nEvent):
        '''this run in the UI thread'''
        if self.hcam:
            if toupcam.TOUPCAM_EVENT_IMAGE == nEvent:
                self.handleImageEvent()
            elif toupcam.TOUPCAM_EVENT_EXPOSURE == nEvent:
                self.handleExpoEvent()
            elif toupcam.TOUPCAM_EVENT_TEMPTINT == nEvent:
                self.handleTempTintEvent()
            elif toupcam.TOUPCAM_EVENT_STILLIMAGE == nEvent:
                self.handleStillImageEvent()
            elif toupcam.TOUPCAM_EVENT_ERROR == nEvent:
                self.closeCamera()
                QMessageBox.warning(self, "Warning", "Generic Error.")
            elif toupcam.TOUPCAM_EVENT_STILLIMAGE == nEvent:
                self.closeCamera()
                QMessageBox.warning(self, "Warning", "Camera disconnect.")

    def handleImageEvent(self):
        try:
            #self.hcam.PullImageV3(self.pData, 0, 24, 0, None)
            self.hcam.PullImageV3(self.pData, 0, 16, 0, None)
        except toupcam.HRESULTException:
            pass
        else:
            #image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_RGB888)
            image = QImage(self.pData, self.imgWidth, self.imgHeight, QImage.Format_Grayscale16)
            newimage = image.scaled(self.lbl_video.width(), self.lbl_video.height(), Qt.KeepAspectRatio, Qt.FastTransformation)
            self.lbl_video.setPixmap(QPixmap.fromImage(newimage))

    def handleExpoEvent(self):
        time = self.hcam.get_ExpoTime()
        gain = self.hcam.get_ExpoAGain()
        with QSignalBlocker(self.slider_expoTime):
            self.slider_expoTime.setValue(time)
        with QSignalBlocker(self.slider_expoGain):
            self.slider_expoGain.setValue(gain)
        self.lbl_expoTime.setText(str(time))
        self.lbl_expoGain.setText(str(gain))

    def handleTempTintEvent(self):
        nTemp, nTint = self.hcam.get_TempTint()
        with QSignalBlocker(self.slider_temp):
            self.slider_temp.setValue(nTemp)
        with QSignalBlocker(self.slider_tint):
            self.slider_tint.setValue(nTint)
        self.lbl_temp.setText(str(nTemp))
        self.lbl_tint.setText(str(nTint))

    def handleStillImageEvent(self):
        info = toupcam.ToupcamFrameInfoV3()
        try:
            self.hcam.PullImageV3(None, 1, 24, 0, info) # peek
        except toupcam.HRESULTException:
            pass
        else:
            if info.width > 0 and info.height > 0:
                buf = bytes(toupcam.TDIBWIDTHBYTES(info.width * 24) * info.height)
                try:
                    self.hcam.PullImageV3(buf, 1, 24, 0, info)
                except toupcam.HRESULTException:
                    pass
                else:
                    image = QImage(buf, info.width, info.height, QImage.Format_RGB888)
                    self.count += 1
                    image.save("pyqt{}.jpg".format(self.count))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())