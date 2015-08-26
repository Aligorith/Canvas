#!/usr/bin/env python

"""
Simple PyQt application to display a plain-coloured backdrop, 
complete with slight gradients applied for a nicer appearance.
Main use case is for taking fancy screenshots of WIP GUI's
free from additional distractions (i.e. other windows and 
desktop icons or personal wallpapers for instance).

Author: Joshua Leung (gmail -> aligorith)
Date: August 2013
"""

import sys

from math import *

import PyQt4
from PyQt4 import QtCore as qcore
from PyQt4 import QtGui as qgui

######################################################
# Color sets

# Blue Color-Set
COLOR_BLUE  = qgui.QColor(86, 158, 199)

# Dark Grey Color-Set
COLOR_DGRAY = qgui.QColor(80, 80, 80)

# Light Grey (Near White)
COLOR_LGRAY = qgui.QColor(220, 220, 220)

######################################################
# Main Window

# Main Window - Empty except for a canvas
class GradientWindow(qgui.QWidget):
	# ctor
	# < color: ([QColor]) list of colors that can be displayed
	def __init__(self, colors):
		qgui.QWidget.__init__(self)
		
		# window settings
		#self.setWindowState(qcore.Qt.WindowMaximized)
		self.setWindowState(qcore.Qt.WindowMaximized)
		self.setWindowTitle("Canvas")
		
		# display settings
		self.colors = colors           # ([QColor]) list of colors to toggle between
		self.current_color = 0         # (int) index of color within buffer
		
		self.grad_strength = 0.7       # (float - [0,1]) width factor for gradient falloff
		self.center_offset = -0.25     # (float) offset factor for center of gradient - negative default for upwards
		
		# bind events
		self.bind_events()
		
	# -----------------------------------------
	
	# setup custom shortcuts
	def bind_events(self):
		keymap = {
			'q'			: self.quit,
			'z'			: self.toggleColors,
		}
		self.bind_keymap(keymap)
		
	def bind_keymap(self, keymap):
		for key, cmd in keymap.items():
			shortcut = qgui.QShortcut(qgui.QKeySequence(key), self)
			shortcut.activated.connect(cmd)
	
	# -----------------------------------------
	
	# Entrypoint for custom drawing
	def paintEvent(self, evt):
		p = qgui.QPainter()
		
		p.begin(self)
		self.draw_background(p)
		p.end()
		
	# Draw gradient backdrop
	# < p: (QPainter)
	def draw_background(self, p):
		# compute viewpoint dimensions ........
		w = self.width() - 1
		h = self.height() - 1
		
		# diagonal length - make all measurements propotional to this
		d = sqrt(w**2 + h**2)
		
		# midpoint of view
		midpoint = qcore.QPointF(self.rect().center())
		
		# grab current color ..................
		col = self.colors[self.current_color]
		
		# setup gradient ......................
		
		# center for gradient is offset slightly from the middle of view (slightly higher)
		center = midpoint + qcore.QPointF(0.0, self.center_offset * d)
		radius = self.grad_strength * d
		
		gr = qgui.QRadialGradient(center, radius)
		
		# 0 = midpoint = base color
		gr.setColorAt(0.0, col)
		
		# 1 = edge = darkened color
		darkCol = col.darker().darker().darker() # XXX: check on exactly best way to do this... 
		gr.setColorAt(1.0, darkCol)
		
		# draw gradient .......................
		p.fillRect(self.rect(), gr)
		
	# -----------------------------------------
	
	# Quit application
	def quit(self):
		# XXX...
		self.deleteLater()
	
	# Toggle between colors
	def toggleColors(self):
		self.current_color = (self.current_color + 1) % len(self.colors)
		self.repaint()

######################################################

def main():
	app = qgui.QApplication(sys.argv)
	
	# TODO: show a config dialog to allow choosing which color-scheme to use?
	
	win = GradientWindow([COLOR_BLUE, COLOR_DGRAY])
	win.show()
	
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	main()
