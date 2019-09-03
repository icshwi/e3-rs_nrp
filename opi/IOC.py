#from org.csstudio.opibuilder.scriptUtil import PVUtil
#!/opt/conda/bin/python
#-*- coding:utf-8 -*-
import os
import re
import sys
import time
import math
import warnings
import threading

import numpy as np
import PyQt5

from epics import caget, caput, cainfo, camonitor

import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
warnings.filterwarnings('ignore')
##----------------End import-----------------##

# Class that incapsulate the matplotlib for use in PyQt
"""======================================= bwCanvas"""
class PSensorCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        #Creates the figure object
        self.pars={'width':width,'height':height,'dpi':dpi, 
                   'left': 0.15, 'right': 0.95, 'bottom': 0.12, 'top': 0.9}
        self.figure = Figure(figsize=(self.pars['width'],    # create a figure
                                      self.pars['height']), 
                                      dpi=self.pars['dpi'])
        self.axes = self.figure.subplots() # Adds plot region
        self.figure.subplotpars.left=self.pars['left']
        self.figure.subplotpars.right=self.pars['right']
        self.figure.subplotpars.bottom=self.pars['bottom']
        self.figure.subplotpars.top=self.pars['top']
        #Initializes the default FigureCanvas superclass
        super().__init__(self.figure)
        self.setParent(parent)
        self.form=parent

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()
        self.axes.set_visible(False) 

    def plot(self,array,Time_length,Points,TriggerLevel,OffsetTime):
        # plots only on the case of the valid measurement
        if array is not None:
            self.figure.clear()
            self.axes=self.figure.subplots() #return Axes object
            int_Points = int(Points)
            interval = Time_length/int_Points
            #interval = float('%.3f' % x)
            #print(interval)
            offset = OffsetTime * 1000
            time_array = interval * np.arange(int_Points) + offset * np.ones((int_Points),dtype=np.int16)
            trigger_array = TriggerLevel * np.ones((int_Points),dtype=np.int16)
            self.axes.plot(time_array,array,'b-')
            self.axes.plot(time_array,trigger_array,'r-',linewidth=3)
            self.axes.text(np.max(time_array)*0.75,TriggerLevel+2,'Trigger Level',color='red')
            font1 = {'family':'sans-serif','weight':'normal','color':'black','size':10}
            self.axes.set_title('Trace Waveform',fontsize=12,fontweight='bold',color='black')
            self.axes.set_xlabel('Time [ms]',fontdict=font1)
            self.axes.set_ylabel('Power [dBm]',fontdict=font1)
            self.axes.set_ylim((-80,20))
            self.axes.autoscale(enable='True',axis='x',tight=None)
            self.axes.grid(True)
            self.figure.tight_layout()
            self.draw()

    def erase(self):
        self.figure.clear()
        self.draw()

class TraceMeasure(object): # trace measurement data
    #CONSTRUCTOR
    def __init__(self):
        super().__init__()
        self._array = {}
        self._points = None
        self._time = None
        self._triggerlevel = None
        self._offsetTime = None

    @property
    def TraceArray(self):
        return self._array
    @property
    def TracePoints(self):
        return self._points
    @property
    def TraceTime(self):
        return self._time
    @property
    def TriggerLevel(self):
        return self._triggerlevel
    @property
    def TraceOffsetTime(self):
        return self._offsetTime

class Trace(QtCore.QThread):
    """ timer for the IOC measurement"""
    ##--------Signal Definition--------##
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal('PyQt_PyObject')
    ##--------CONSTRUCTOR--------##    
    def __init__(self,interval): # t--interval call the hFunction
        QtCore.QThread.__init__(self)
        self.interval = interval
        self.evented = threading.Event()  # 引入事件进行定时器的设置
        self.trace_points = None
        self.trace_time = None
        self.trace_value = {} 
        self.trace_triggerlevel = None
        self.trace_offsettime = None     
    #Execute
    def run(self):
        self.started.emit()
        while not self.evented.is_set():
            self.evented.wait(self.interval)
            #self.trace_points = caget('SRFLab-010:RFS-PM-01:Trace_points.VAL', as_string=False)
            self.trace_time = caget('SRFLab-010:RFS-PM-01:Trace_time.VAL', as_string=False)
            self.trace_value = caget('SRFLab-010:RFS-PM-01:Value_trace.VAL', as_string=False)
            self.trace_triggerlevel = caget('SRFLab-010:RFS-PM-01:Trace_level_callback_DBM.VAL', as_string=False)
            self.trace_offsettime = caget('SRFLab-010:RFS-PM-01:Trace_offset_time_callback.VAL',as_string=False)
            self.trace_points = len(self.trace_value)
            psen = TraceMeasure()
            psen._array = self.trace_value
            psen._points = self.trace_points
            psen._time = self.trace_time
            psen._triggerlevel = self.trace_triggerlevel
            psen._offsetTime = self.trace_offsettime
            self.finished.emit(psen)
    #STOP
    def cancel(self):
        self.evented.set()

class PyTraceWidget(QtWidgets.QWidget):
    """ Trace """
    def __init__(self,parent):
        super().__init__()
        self.thrun=None         # thread
        self.result=None        # measurement result
        self.set=None           # Timer interval
        self.parent=parent
        self.__controls()
        self.__layout()

    def __controls(self):
        #Quit Button
        self.btnQuit = QtWidgets.QPushButton('Quit', self)
        self.btnQuit.setToolTip('Quit from PyTrack')
        self.btnQuit.clicked.connect(self.parent.close)
        #Label stupida
        self.lblinfo = QtWidgets.QLabel(' ',self)
        self.lblinfo.setToolTip('http://esss.se')
        self.lblinfo.setPixmap(QtGui.QPixmap('ESS_Logo.png'))
        #Take a measurement
        self.btnStart = QtWidgets.QPushButton('Start',self)
        self.btnStart.clicked.connect(self.Start)
        self.btnStop = QtWidgets.QPushButton('Stop',self)
        self.btnStop.clicked.connect(self.Stop)
        #Label for Messages
        self.lblMessages=QtWidgets.QLabel('Press button to start',self)
        self.lblAuthors=QtWidgets.QLabel('MuYuan 2019\nSRF Section\nLinac Group\nAcceleration Division')
        self.lblAuthors.setAlignment(QtCore.Qt.AlignCenter)
        self.lblAuthors.setFont(QtGui.QFont('',10))
        #puts a canvas object here
        self.PSensorPlot=PSensorCanvas(self, width=5, height=3.5, dpi=144)
        self.PSensorPlot.setToolTip('IOC Measurement')
        #time message
        self.lblTimeMessages=QtWidgets.QLabel(time.strftime("%d-%m-%Y %H:%M:%S",time.localtime(time.time())),self)
        #other controls
        self.lblOperator=QtWidgets.QLabel('Operator',self)
        self.txtOperator=QtWidgets.QLineEdit(self)
        self.txtOperator.setText('SRF Team')
        self.txtOperator.setFixedWidth(100)
        self.lblLocation=QtWidgets.QLabel('Location',self)
        self.txtLocation=QtWidgets.QLineEdit(self)
        self.txtLocation.setText('SRF Laboratory')
        self.lblComments=QtWidgets.QLabel('Comments',self)
        self.txtComments=QtWidgets.QLineEdit(self)
        self.txtComments.setText('IOC waveform measurement')
        self.txtComments.setFixedWidth(300)
        self.lblScanInterval=QtWidgets.QLabel('Interval:',self)
        self.txtScanInterval=QtWidgets.QLineEdit(self)
        self.txtScanInterval.setText('1')
        self.txtScanInterval.setFixedWidth(40)
        self.lblUnit=QtWidgets.QLabel('s',self)
        self.btnInterval=QtWidgets.QPushButton('Apply',self)
        self.btnInterval.setEnabled(True)
        self.btnInterval.clicked.connect(self.setInterval)

    def __layout(self):
        # first line
        self.hboxfirst=QtWidgets.QHBoxLayout()
        self.hboxfirst.addWidget(self.lblMessages)
        self.hboxfirst.addStretch(1)
        self.hboxfirst.addStretch(1)
        self.hboxfirst.addWidget(self.lblinfo)
        self.hboxfirst.addWidget(self.lblAuthors)
        self.hboxfirst.addStretch(1)

        # second line
        self.hboxsecond=QtWidgets.QHBoxLayout()
        self.hboxsecond.addStretch(1)
        self.hboxsecond.addWidget(self.lblOperator)
        self.hboxsecond.addWidget(self.txtOperator)
        self.hboxsecond.addStretch(1)
        self.hboxsecond.addWidget(self.lblLocation)
        self.hboxsecond.addWidget(self.txtLocation)
        self.hboxsecond.addStretch(1)
        self.hboxsecond.addWidget(self.lblComments)
        self.hboxsecond.addWidget(self.txtComments)
        self.hboxsecond.addStretch(1)

        # third line
        self.hboxthird=QtWidgets.QHBoxLayout()
        self.hboxthird.addStretch(1)
        self.hboxthird.addWidget(self.btnStart)
        self.hboxthird.addStretch(1)
        self.hboxthird.addWidget(self.btnStop)
        self.hboxthird.addStretch(1)
        self.hboxthird.addWidget(self.lblScanInterval) # Interval
        self.hboxthird.addWidget(self.txtScanInterval) #
        self.hboxthird.addWidget(self.lblUnit)         #
        self.hboxthird.addWidget(self.btnInterval)
        self.hboxthird.addStretch(1)

        # down
        self.hboxdo=QtWidgets.QHBoxLayout()
        self.hboxdo.addWidget(self.lblTimeMessages)
        self.hboxdo.addStretch(1)
        self.hboxdo.addStretch(1)
        self.hboxdo.addWidget(self.btnQuit)
        
        # vertical layout
        self.vbox=QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hboxfirst)
        self.vbox.addLayout(self.hboxsecond)
        self.vbox.addLayout(self.hboxthird)
        self.vbox.addWidget(self.PSensorPlot)
        self.vbox.addLayout(self.hboxdo)
        #3 Apply Layout. This is how the window area looks
        self.setLayout(self.vbox)

    def setInterval(self):
        self.set = int(self.txtScanInterval.text())  # time interval
       
##----------- IOC Waveform Measurement -----------##
    def Start(self):
    ##---------- Strating the Measurement ----------##
        self.thrun=Trace(self.set)
        self.thrun.started.connect(self.tracestart)
        self.thrun.finished.connect(self.function)   
        self.thrun.start()
    
    def tracestart(self):
        self.lblMessages.setText('Start Measurement')
        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(True)
        self.btnInterval.setEnabled(False)
        self.txtScanInterval.setEnabled(False)
    
    def function(self,measure):
        self.result = measure
        Array = self.result.TraceArray
        Points= self.result.TracePoints
        Time =  self.result.TraceTime
        TriggerLevel = self.result.TriggerLevel
        OffsetTime = self.result.TraceOffsetTime
        self.PSensorPlot.plot(Array,Time,Points,TriggerLevel,OffsetTime)
  
    ## close the HDF file  
    def Stop(self):
        self.btnInterval.setEnabled(True)
        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)
        self.txtScanInterval.setEnabled(True)
        self.thrun.cancel()

    

class PyTrackMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        #It contains just the vtWidget. No neet to define a layout, as it is defined there
        self.PyTrace_widget=PyTraceWidget(self)
        self.setCentralWidget(self.PyTrace_widget)
        #Initializes the bells and whistles of a container app
        self.initializeGUI()
    def initializeGUI(self):
        #Tooltips
        QtWidgets.QToolTip.setFont(QtGui.QFont('SansSerif', 14))
        self.setToolTip('IOC Measurement')
        #Toolbar
        self.addToolBar(NavigationToolbar(self.PyTrace_widget.PSensorPlot,self))
        #Menu
        mnuExit=QtWidgets.QAction('&End Program',self)
        mnuExit.setStatusTip('Exit PyTrace')
        mnuExit.triggered.connect(self.close)
        menu=self.menuBar()
        mnufile=menu.addMenu('P&yTrace')
        mnufile.addAction(mnuExit)
        # Resize main window
        self.resize(1100,1000)  # 1000, 850
        #self.center()
        self.setWindowTitle('PyTrace@ESS')
        self.show()       
    """ Menu"""
    def toggleSBView(self,state):
        if state:
            self.statusBar().show()
        else:
            self.statusBar().hide()
    """ Context menu"""            
    def contextMenuEvent(self, event):     
           cmenu = QtWidgets.QMenu(self)
           quitAct = cmenu.addAction("Quit")
           # to map the coordinates so that 
           action = cmenu.exec_(self.mapToGlobal(event.pos()))
           if action == quitAct:
               self.close()
    """ Traps the close Event"""
    def closeEvent(self,event):
        reply = QtWidgets.QMessageBox.question(self,'Hej!','Are you sure to quit?',
                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


""" MAIN APPLICATION ENTRY"""
if __name__ == '__main__':
    qapp = QtWidgets.QApplication(sys.argv)
    w=PyTrackMainWindow()
    w.show()
    qapp.exec_()

