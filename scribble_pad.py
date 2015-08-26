#!/usr/bin/env python

"""
Simple PyQt application providing a canvas to draw in/on
using the QTabletEvent stuff to handle tablet events
"""

import sys
import os
import json

import PyQt4
from PyQt4 import QtCore as qcore
from PyQt4 import QtGui as qgui

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from backdrop import *

########################################
# Data Structures

class Point:
	# ctor
	# < co: (QPoint)
	# < pressure: (Pressure)
	def __init__(self, co, pressure):
		self.co = co
		self.pressure = pressure

class Stroke:
	def __init__(self):
		# list of Point's
		self.points = []

	# Add a point to the stroke
	# < co: (QPoint) coordinates of point
	# < pressure: (float) pressure for point
	def add(self, co, pressure=1.0):
		self.points.append(Point(co, pressure))
	
########################################
# Painting Canvas

class PaintingCanvas(GradientWindow):
	# ctor
	def __init__(self):
		super(PaintingCanvas, self).__init__([COLOR_BLUE, COLOR_DGRAY])
		
		# width of all strokes
		self.thickness = 3

		# render shadows
		self.show_shadows = True
		
		# list of strokes
		self.strokes = []
		
		# current stroke - only valid when painting
		self.curstroke = None
		
		# use crosshair cursor, for more accuracy when painting
		self.setCursor(qcore.Qt.CrossCursor)

		# update keymap
		self.bind_shortcuts()
	
	# Setup keymap
	def bind_shortcuts(self):
		keymap = {
			's'    		: self.toggle_shadows,
			
			'F1'        : self.load_canvas,
			'F2'        : self.save_canvas,
			
			'Ctrl+z'    : self.undo_stroke,
			'Del'	 	: self.clear_canvas,
		}
		self.bind_keymap(keymap)

	# Rendering ========================

	# Entrypoint for painting
	def paintEvent(self, evt):
		# We MUST do the standard drawing first (or else there's nothing to show)
		super(PaintingCanvas, self).paintEvent(evt)
		
		# Draw strokes now...
		p = qgui.QPainter()
		p.begin(self)

		p.setRenderHint(qgui.QPainter.Antialiasing)
		p.setRenderHint(qgui.QPainter.HighQualityAntialiasing)

		# draw strokes once as dark lines and with offsets
		if self.show_shadows:
			self.draw_shadows(p)
		
		# draw strokes again, this time for real
		self.draw_strokes(p)
		
		p.end()
	
	# Draw shadows for strokes
	def draw_shadows(self, p):
		col = qgui.QColor(0, 0, 0, 190) # "black"
		pen = qgui.QPen(col, self.thickness)
		pen.setCapStyle(qcore.Qt.RoundCap)
		pen.setJoinStyle(qcore.Qt.RoundJoin)

		ofs = qcore.QPoint(2, 2)
		thick = self.thickness + 2
		
		for stroke in self.strokes:
			if len(stroke.points) > 1:
				for pt1, pt2 in zip(stroke.points, stroke.points[1:]):
					# XXX: since we can't have variable thickness strokes,
					# we'll just have to make do like this
					pen.setWidthF(thick * pt1.pressure)
					
					p.setPen(pen)
					p.setBrush(qcore.Qt.NoBrush)
					
					p.drawLine(pt1.co + ofs, pt2.co + ofs)
			else:
				# just a big round dot
				p.setPen(qcore.Qt.NoPen)
				p.setBrush(col)
				
				pt = stroke.points[0]
				r  = thick * pt.pressure
				p.drawEllipse(pt.co + ofs, r, r)
					

	# Draw strokes
	def draw_strokes(self, p):
		col = qgui.QColor("#EEEEEE")
		pen = qgui.QPen(col, self.thickness)
		pen.setCapStyle(qcore.Qt.RoundCap)
		pen.setJoinStyle(qcore.Qt.RoundJoin)		
		
		for stroke in self.strokes:
			if len(stroke.points) > 1:
				for pt1, pt2 in zip(stroke.points, stroke.points[1:]):
					# XXX: since we can't have variable thickness strokes,
					# we'll just have to make do like this
					pen.setWidthF(self.thickness * pt1.pressure)
					
					p.setPen(pen)
					p.setBrush(qcore.Qt.NoBrush)
					
					p.drawLine(pt1.co, pt2.co)
			else:
				# just a big round dot
				p.setPen(qcore.Qt.NoPen)
				p.setBrush(col)
				
				pt = stroke.points[0]
				r  = self.thickness * pt.pressure
				p.drawEllipse(pt.co, r, r)

	# Drawing ============================
	dummy = """	
	# Handle tablet events
	def tabletEvent(self, evt):
		handled = False

		if self.curstroke is not None:
			# move or release? 
			if evt.type() == qcore.QEvent.TabletMove:
				# add another stroke point
				self.curstroke.add(evt.pos(), evt.pressure())
				handled = True
			else: #if evt.type() == qcore.QEvent.TabletRelease:
				# end stroke
				self.curstroke.add(evt.pos(), evt.pressure())
				self.curstroke = None
				handled = True
			#else:
			#	print "unhandled tablet event (with stroke) - %s" % (evt.type())
		elif evt.type() == qcore.QEvent.TabletPress:
			# start of new stroke
			self.curstroke = Stroke()
			self.curstroke.add(evt.pos(), evt.pressure())
			
			self.strokes.append(self.curstroke)
			handled = True

		if handled:
			evt.accept()
			self.repaint()
		else:
			# ignore mousemove that didn't go anywhere
			evt.accept()
			pass
"""
	# ------------------------------------

	# Start stroke
	def mousePressEvent(self, mevt):
		# Create new stroke, and add the current point to it
		self.curstroke = Stroke()
		try:
			pressure = mevt.pressure()
		except:
			pressure = 1.0
		self.curstroke.add(mevt.pos(), pressure)
		
		self.strokes.append(self.curstroke)
		
		self.repaint()

	# Continue stroke
	def mouseMoveEvent(self, mevt):
		if self.curstroke is None:
			mevt.ignore()
			return

		try:
			pressure = mevt.pressure()
		except:
			pressure = 1.0
		self.curstroke.add(mevt.pos(), pressure)
		self.repaint()
	
	# End stroke
	def mouseReleaseEvent(self, mevt):
		if self.curstroke is None:
			mevt.ignore()
			return
		
		try:
			pressure = mevt.pressure()
		except:
			pressure = 1.0
		self.curstroke.add(mevt.pos(), pressure)
		self.curstroke = None

		self.repaint()

	# Shortcuts ------------------------

	# Change stroke thickness
	def wheelEvent(self, evt):
		steps = evt.delta() / 120
		
		self.thickness += steps
		self.thickness = max(1, self.thickness) # clamp lower bound
		
		self.repaint()

	# Toggle shadow visibility
	def toggle_shadows(self):
		self.show_shadows ^= True
		self.repaint()

	# Canvas Management -----------------
	
	# Load canvas configuration from a file
	def load_canvas(self):
		path = qgui.QFileDialog.getOpenFileName(self, 'Open Sketch...', ".", "*.canvas")
		if not path:
			return
		
		with open(path) as f:
			#try:
				data = json.load(f)
				
				self.strokes = []
				for sdata in data['strokes']:
					stroke = Stroke()
					self.strokes.append(stroke)
					for spt in sdata:
						stroke.add(qcore.QPoint(spt[0], spt[1]), spt[2])
				
				self.thickness = data['thickness']
				self.show_shadows = data['show_shadows']
				
				self.current_color = data['bg_index']

				print "'%s' Loaded" % (path)
				self.repaint()
			#except:
			#	qgui.QMessageBox.warning(self, "File Loading Error", "%s was not a valid canvas file" % (path))
	
	# Serialise canvas to a file
	def save_canvas(self):
		path = qgui.QFileDialog.getSaveFileName(self, "Save Sketch...", ".", "*.canvas")
		if not path:
			return

		with open(path, 'w') as f:
			# serialise stroke data to a dict...
			data = {
				'strokes'      : [[[pt.co.x(), pt.co.y(), pt.pressure] for pt in stroke.points] for stroke in self.strokes],
				'thickness'    : self.thickness,
				'show_shadows' : self.show_shadows,
				'bg_index'     : self.current_color,
			}
			json.dump(data, f)

			print "Saved to %s" % (path)

	# Clear all strokes
	def clear_canvas(self):
		self.strokes = []
		self.repaint()

	# Undo - Remove the last stroke drawn
	def undo_stroke(self):
		del self.strokes[-1]
		self.repaint()

########################################

def main():
	app = qgui.QApplication(sys.argv)
	win = PaintingCanvas()
	win.show()
	sys.exit(app.exec_())

main()

