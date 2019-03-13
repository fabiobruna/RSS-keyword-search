import os
import sys
import time
import datetime
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt,QTimer
from rss_search import *

class Window(QtWidgets.QWidget):
    def __init__(self):
        super(Window, self).__init__()

        self.initUI()

    def initUI(self):

        self.setStyleSheet("font: 10pt")
        self.begin = True
        self.lineLabel = QtWidgets.QLabel('Add keywords to search for (keyword#1, keyword#2, ...)')
        self.lineEdit = QtWidgets.QLineEdit()
        self.timeLabel = QtWidgets.QLabel('Search Frequency (5 min - 60min)')
        self.timeSlider = QtWidgets.QSlider(Qt.Horizontal)

        self.timeSlider.setMinimum(1)
        self.timeSlider.setMaximum(12)
        self.timeSlider.setValue(2)
        self.timeSlider.setTickInterval(1)

        self.timeSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.caps = QtWidgets.QCheckBox('Case Sensitive?')
        self.addKeywordFile = QtWidgets.QPushButton('Add Keyword File')
        self.addRssFile = QtWidgets.QPushButton('Add Rss File')
        self.startButton = QtWidgets.QPushButton('Start')
        self.outputLabel = QtWidgets.QLabel('\n Output:')
        self.output = QtWidgets.QTextBrowser(self)
        self.output.setReadOnly(True)

        horizontal_box_line = QtWidgets.QHBoxLayout()
        horizontal_box_line.addWidget(self.lineLabel)

        horizontal_box_line_2 = QtWidgets.QHBoxLayout()
        horizontal_box_line_2.addWidget(self.lineEdit)
        horizontal_box_line_2.addWidget(self.addKeywordFile)

        horizontal_box_time = QtWidgets.QHBoxLayout()
        horizontal_box_time.addWidget(self.timeLabel)

        horizontal_box_caps = QtWidgets.QHBoxLayout()
        horizontal_box_caps.addWidget(self.caps)

        horizontal_box_caps.addWidget(self.addRssFile)

        horizontal_box_output = QtWidgets.QHBoxLayout()
        horizontal_box_output.addWidget(self.outputLabel)

        vertical_box = QtWidgets.QVBoxLayout()
        vertical_box.addLayout(horizontal_box_line)
        vertical_box.addLayout(horizontal_box_line_2)
        vertical_box.addLayout(horizontal_box_time)
        vertical_box.addWidget(self.timeSlider)
        vertical_box.addLayout(horizontal_box_caps)
        vertical_box.addWidget(self.startButton)
        vertical_box.addLayout(horizontal_box_output)
        vertical_box.addWidget(self.output)

        self.setLayout(vertical_box)
        self.setWindowTitle('News Search')

        self.startButton.clicked.connect(self.start)
        self.addKeywordFile.clicked.connect(self.setFileKey)
        self.addRssFile.clicked.connect(self.setFileRss)
        self.setAutoFillBackground(True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateSearch)

        self.show()

    def start(self):
    	'''
    	INPUT: self.lineEdit.text() - Input text from lineEdit
		INPUT: self.timeSlider.value() - Time from slider in minutes (5-60)
		INPUT: FILE
        INPUT: self.caps.isChecked()
    	'''
    	print self.begin
        if(self.begin):
            self.output.setText("")
            print "start"
            self.begin = False

            self.startButton.setText('Stop')

            leVal = self.lineEdit.text()
            tsVal = self.timeSlider.value()
            isCaps = self.caps.isChecked()

            if (leVal == "" or leVal == "file added"):
                print "No keyword selected in text editor, i hope you added a file!"
            else:
                meow.set_keywords(leVal)
                print "keyword: " + leVal

            meow.case_sens = isCaps
            print "Case Sensitive? - " + str(isCaps)

            print "Slider value: " + str(tsVal)
            self.intervalTime = tsVal*5*60

            self.previousTime = 0.0
            self.timer.start(1000)

        else:
            print "Stop"
            self.timer.stop()
            self.begin = True
            self.startButton.setText('Start')

    def updateSearch(self):
            currentTime = time.time()
            timeCheck = self.checkTime(self.previousTime,currentTime) # extra check that enough time has elapsed
            if timeCheck == False:
            	# maybe implement better error handling
            	return
            self.previousTime = currentTime
            #print datetime.datetime.now()

            self.timer.setInterval(self.intervalTime*1000)
            
            meow() # searching
            titles = meow.titles
            descriptions = meow.descriptions
            links = meow.links

            # removing duplicates
            lists = [meow.titles,meow.descriptions,meow.links]
            meow.titles,meow.descriptions,meow.link = self.removeDuplicates(lists)

            output = ''
            for a,b,c in zip(meow.titles,meow.descriptions,meow.links):
                output += '<br>'.join([self.wrap(a,'b'),b,self.wrap(c,'a'),'<br>'])
            #print output

            self.output.setStyleSheet('background-color: rgb(, 255, 255);')
            self.output.setText(output + "\n <i> Search finished:  " + time.strftime('%d/%m/%Y %H:%M:%S')+"</i>")
            self.output.setOpenExternalLinks(True)

    def setFileKey(self):
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', os.getenv('HOME'))
            with open(filename[0], 'r') as f:
                file_text = f.read()
                print file_text
                meow.set_keywords(file_text)
                self.lineEdit.setText("file added")
                self.output.setText("Keyword file = " + str(filename))
        except:
            print "No file was choosen!"

    def setFileRss(self):
        try:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', os.getenv('HOME'))
            with open(filename[0], 'r') as f:
                file_text = f.read() #file xyz.no/rss, vg.no/rss, etc
                meow.set_pages(file_text)
                print "rss"
                self.output.setText("RSS file = " + str(filename))
        except:
            print "No file was choosen!"

    def wrap(self,string,tag):
        '''
        Wraps the string in the desired html tag.
        '''
        if tag.strip() == 'a':
            ret = '<a href="%s">%s</a>'%(string,string)
        else:
            ret = '<%s>%s</%s>'%(tag,string,tag)
        return ret

    def removeDuplicates(self,lists):
        '''
        Removes duplicates in lists:
        lists = list containing the lists to remove duplicates from
        '''
        if len(lists) > 0:
            remove = lambda x,y: [x[i] for i in y]
            b = set()
            a = lists[0]
            index = [i for i in range(len(a)) if a[i] not in b and not b.add(a[i])] 

            nu_lists = []
            for l in lists:
                nu_lists.append(remove(l,index))

            return nu_lists
        else:
            return 

    def checkTime(self,previousTime,currentTime):
    	'''
		Checks if enough time has elapsed since the last time self.updateSearch has been called
    	'''
    	print (currentTime-previousTime)/self.intervalTime
        if ((currentTime-previousTime)/self.intervalTime > 0.99):
        	return True
        else:
        	return False

    def checkNetwork(self):
        '''
        TODO: add error messages for network issues
        '''
    	pass

if __name__=='__main__':
	meow = rss_search()
	app = QtWidgets.QApplication(sys.argv)
	a_window = Window()
	sys.exit(app.exec_())
