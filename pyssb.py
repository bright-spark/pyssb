#!/usr/bin/env python


import json
import os
import pickle
from   pprint import pprint
from   PyQt5 import QtCore
from   PyQt5 import QtGui
from   PyQt5 import QtNetwork
from   PyQt5 import QtWebKitWidgets
from   PyQt5 import QtWidgets
import sys


class SearchWidget(QtWidgets.QLineEdit):
  def __init__(self, wb):
    super(SearchWidget, self).__init__()

    self.wb = wb 
    self.move(100, 100)
    self.hideSearch = QtWidgets.QShortcut("Esc", self, activated = lambda: self.toggleSearch())
    self.hideSearch2 = QtWidgets.QShortcut("Ctrl+F", self, activated = lambda: self.toggleSearch())
    self.returnPressed.connect(self.search)


  def focusOutEvent(self, event):
    self.hide()


  def search(self):
    self.wb.findText(self.text(), QtWebKitWidgets.QWebPage.FindWrapsAroundDocument)


  def toggleSearch(self):
    if self.isVisible():
      self.hide()
      self.wb.setFocus()
    else:
      self.move(self.wb.x(), self.wb.y()+self.wb.size().height()-self.size().height())
      self.show()
      self.setFocus()


class SSBWindow(QtWebKitWidgets.QWebView):
  def __init__(self, ssb_config):
    super(SSBWindow, self).__init__()

    # Load Settings
    self.config = ssb_config
    self.settings = QtCore.QSettings("pyssb", self.config['name'])

    # Window Position
    self.setWindowTitle(self.config['title'])
    try:
      self.restoreGeometry(self.settings.value("geometry"))
    except:
      # Reasonable Defaults
      self.resize(900, 600)
      self.move(100, 100)

    ### Extra Browser Functionality
    self.search = SearchWidget(self)
    self.showSearch = QtWidgets.QShortcut("Ctrl+F", self, activated = lambda: self.search.toggleSearch())

    self.quit = QtWidgets.QShortcut("Ctrl+Q", self, activated = self.close)
    self.zoomIn = QtWidgets.QShortcut("Ctrl++", self, activated = lambda: self.setZoomFactor(self.zoomFactor()+.2))
    self.zoomIn2 = QtWidgets.QShortcut("Ctrl+=", self, activated = lambda: self.setZoomFactor(self.zoomFactor()+.2))
    self.zoomIn = QtWidgets.QShortcut("Ctrl+-", self, activated = lambda: self.setZoomFactor(self.zoomFactor()-.2))
    self.zoomOne = QtWidgets.QShortcut("Ctrl+0", self, activated = lambda: self.setZoomFactor(1))
    ###

    # Icon
    if not self.settings.value("icon"):
      print('geticon')
      '''
      if no icon then 
        try to get base url
        pull favicon.ico (alternatively, set callback when finished loading to read favicon.ico
      save icon into base64
      '''

      self.setWindowIcon(QtGui.QIcon('favicon.ico'))


    # Cookie Jar
    self.cookiejar = QtNetwork.QNetworkCookieJar(self)
    self.page().networkAccessManager().setCookieJar(self.cookiejar)

    # Load Cookies
    try:
      raw_cookies = pickle.loads(self.settings.value("cookies"))
      cookies = []
      for r in raw_cookies:
        c = QtNetwork.QNetworkCookie.parseCookies(r)
        cookies.append(c[0])
      self.cookiejar.setAllCookies(cookies)
    except:
      pass

    # Load Page
    self.load(QtCore.QUrl(self.config['url']))


  def closeEvent(self, event):
    # Save Window Position
    self.settings.setValue("geometry", self.saveGeometry())

    # Save Cookies
    cookies = self.cookiejar.allCookies()
    raw_cookies = []
    for cookie in cookies:
      raw_cookies.append( cookie.toRawForm(1) )
    self.settings.setValue("cookies", pickle.dumps(raw_cookies))

    self.search.close()
    QtWidgets.QMainWindow.closeEvent(self, event)


### BEGIN CONFIG ###
ssb_config = {'name':'pyssb','title':'pyssb','url':'https://github.com/lhl/pyssb'}
### END CONFIG ###


if __name__ == "__main__":
  # Disable Logging
  def handler(msg_type, msg_log_context, msg_string):
    pass

  QtCore.qInstallMessageHandler(handler)

  app = QtWidgets.QApplication(sys.argv)
  ssb = SSBWindow(ssb_config)
  ssb.show()
  sys.exit(app.exec_())
