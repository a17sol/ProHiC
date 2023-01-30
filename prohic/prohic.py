import math
from os.path import basename
from random import uniform
import sys

import cooler
import numpy as np
from pgcolorbar.colorlegend import ColorLegendItem
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QSize
import pyqtgraph as pg

try:
	from .colormaps import colormaps # launch with terminal command
except:
	from colormaps import colormaps # launch directly

class BrowserWindow(pg.GraphicsLayoutWidget):

	shiftChanged = pyqtSignal(float)
	sizeChanged = pyqtSignal(int)

	def __init__(self):

		super().__init__()

		buttonLayout=pg.GraphicsLayout(border=pg.getConfigOption('foreground'))
		buttonLayout.setMaximumWidth(225)
		buttons=[]
		buttons.extend((Button('Open map (O)', self.open, enabled=True),
			Button('Close map (Q)', self.close),
			Button('Resolution (R)', self.resolution),
			Button('Color palette (C)', self.colormap, enabled=True),
			Button('Observed/expected (E)', self.oe),
			Button('Logarithmic color (L)', self.log),
			Button('Tilt map (T)', self.tilt),
			Button('Open track (B)', self.bed, enabled=True),
			Button('Shift left (←)', self.left),
			Button('Shift right (→)', self.right)))
		for i in (1,2,4,5,6,8,9):
			self.sizeChanged.connect(buttons[i].act)
		for i in buttons:
			buttonLayout.addItem(i)
			buttonLayout.nextRow()

		self.luah=Board()
		self.luah.update(closed=True)
		buttonLayout.addItem(self.luah)

		self.addItem(buttonLayout, row=0, col=0)

		self.mainLayout=pg.GraphicsLayout()
		self.addItem(self.mainLayout, row=0, col=1)

		self.image = MyImageItem()
		self.image.setAutoDownsample(False) # No downsampling when zoomed out

		self.mapViewBox = MyViewBox()
		self.mapViewBox.addItem(self.image)

		self.plot = pg.PlotItem(viewBox=self.mapViewBox)
		self.plot.disableAutoRange()
		self.plot.invertY(True)
		self.plot.setAspectLocked()
		self.plot.showAxes((None,True,True,None))
		self.plot.getAxis('right').setStyle(showValues=False, tickLength=0)
		self.plot.getAxis('bottom').setStyle(showValues=False, tickLength=0)
		self.plot.getAxis('top').setStyle(showValues=True)
		self.plot.getAxis('top').setLabel(units='bp')
		self.plot.getAxis('left').setLabel(units='bp')
		self.plot.getAxis('left').setWidth(70)
		self.plot.setContentsMargins(-5, 0, 0, 0)

		self.mapColorBar = ColorLegendItem(imageItem=self.image, showHistogram=True)
		self.mapColorBar.resetRangeMouseButtons = [QtCore.Qt.RightButton]
		self.mapColorBar.axisItem.setWidth(50)
		self.mapColorBar.mainLayout.setContentsMargins(15, 0, 0, 0)
		self.mapColorBar.setLut(makeLUT('magma'))

		self.mainLayout.addItem(self.plot)
		self.mainLayout.addItem(self.mapColorBar)

		self.setWindowTitle('ProHiC')
		
		self.tracksOpened=0
		self.shiftEdge=5000
		self.HiC=hicInterface()

		self.showMaximized()

	def keyPressEvent(self, event): #Keyboard control

		if event.key()==79: #O
			self.open()

		elif event.key()==81: #Q
			self.close()

		elif event.key()==82: #R
			self.resolution()
			
		elif event.key()==67: #C
			self.colormap()

		elif event.key()==69: #E
			self.oe()

		elif event.key()==76: #L
			self.log()

		elif event.key()==16777236: #->
			self.right()

		elif event.key()==16777234: #<-
			self.left()

		elif event.key()==84: #T
			self.tilt()

		elif event.key()==66: #B
			self.bed()

	#User control functions:
	def open(self):
		firstTime=True if self.HiC.name=='' else False
		fname, suc = opendialog('Open HiC map')
		if suc:
			if self.HiC.open(file=fname):
				self.image.setImage(self.HiC.product())
				self.image.setScale(self.HiC.res)
				self.luah.update(closed=False, bname=self.HiC.bname, sizebp=self.HiC.sizebp, res=self.HiC.res, log=self.HiC.log, oe=self.HiC.oe, shift=int(self.HiC.shift*self.HiC.sizebp/100))
				self.sizeChanged.emit(self.HiC.sizebp)

				if self.tracksOpened==0 and firstTime: 
					self.plot.autoRange()
				elif self.tracksOpened!=0 and firstTime:
					diapX,diapY=self.mapViewBox.state['viewRange']
					self.mapViewBox.setYRange(max=(diapX[0]+diapX[1])/2+(diapY[1]-diapY[0])/2, 
						min=(diapX[0]+diapX[1])/2-(diapY[1]-diapY[0])/2, padding=0)
				
				self.mapColorBar.autoScaleFromImage()

	def close(self):
		if self.HiC.name!='':
			self.shiftChanged.emit(-self.HiC.sizebp/100*self.HiC.shift)
		self.HiC.close()
		self.plot.disableAutoRange()
		self.image.clear()
		#self.image.setScale(1)
		self.luah.update(closed=True)
		self.sizeChanged.emit(self.HiC.sizebp)

	def resolution(self):
		if self.HiC.name!='':
			res, suc = selectdialog(self.HiC.resolutions, 'Set resolution')
			if suc:
				self.HiC.open(file=self.HiC.name, resolution=int(res))
				self.image.setImage(self.HiC.product())
				self.image.setScale(self.HiC.res)
				self.luah.update(res=self.HiC.res, sizebp=self.HiC.sizebp)

	def colormap(self):
		cm, suc = selectdialog(colormaps, 'Set colormap')
		if suc:
			self.mapColorBar.setLut(makeLUT(cm))
			self.luah.update(colormap=cm)

	def oe(self):
		if self.HiC.name!='':
			self.HiC.toggleOE()
			self.image.setImage(self.HiC.product())
			self.luah.update(oe=self.HiC.oe)
			self.mapColorBar.autoScaleFromImage()

	def log(self):
		if self.HiC.name!='':
			self.HiC.toggleLOG()
			self.image.setImage(self.HiC.product())
			self.luah.update(log=self.HiC.log)
			self.mapColorBar.autoScaleFromImage()

	def right(self):
		if self.HiC.name!='':
			self.HiC.changeShift(1)
			self.image.setImage(self.HiC.product())
			self.luah.update(shift=int(self.HiC.shift*self.HiC.sizebp/100))
			self.shiftChanged.emit(self.HiC.sizebp/100)

	def left(self):
		if self.HiC.name!='':
			self.HiC.changeShift(-1)
			self.image.setImage(self.HiC.product())
			self.luah.update(shift=int(self.HiC.shift*self.HiC.sizebp/100))
			self.shiftChanged.emit(-self.HiC.sizebp/100)

	def tilt(self):
		if self.HiC.name!='':
			self.plot.disableAutoRange()
			diapX,diapY=self.mapViewBox.state['viewRange']
			if self.image.tilt() == True:
				self.mapViewBox.setYRange(diapY[0]-diapY[1], 0, padding=0)
			else:
				self.mapViewBox.setYRange(max=(diapX[0]+diapX[1])/2+(diapY[1]-diapY[0])/2, 
					min=(diapX[0]+diapX[1])/2-(diapY[1]-diapY[0])/2, padding=0)

	def bed(self):
		fname, suc = opendialog('Open track')
		if suc:
			self.importTrack(fname)
	#End of user control functions

	def importTrack(self, fname): #Parse given file and draw the data

		with pg.BusyCursor():

			if fname[-4:]==".bed":
				
				starts,ends,names = np.genfromtxt(
					fname=fname, 
					delimiter="\t", 
					dtype=None, 
					usecols=(1,2,3), 
					unpack=True, 
					encoding=None, 
					comments='track')
				
				track=Track(curve=False, name=basename(fname).split('.')[0])
				sh=self.HiC.shift*self.HiC.sizebp/100

				for i in range(len(starts)): #Draw lines
					a=Region(
						x=[starts[i]+sh, ends[i]+sh], 
						nameOfReg=names[i], mapsize=self.HiC.sizebp,
						direction='0')
					track.addItem(a)
					self.shiftChanged.connect(a.mov)
					self.sizeChanged.connect(a.siz)

				self.addTrack(track)

			elif fname[-4:] in (".gff", "gff2", 'gff3'):
				
				featureType,starts,ends,strand,featureName = np.genfromtxt(
					fname=fname, 
					delimiter="\t", 
					dtype=None, 
					usecols=(2,3,4,6,8), 
					unpack=True, 
					encoding=None, 
					comments='#')

				names=[featureType[i]+'\n'+featureName[i] for i in range(len(featureType))]
				
				toPop=[]
				for i in range(len(starts)-1):
					if starts[i]==starts[i+1]:
						toPop.append(i+1)
						names[i]+='\n\n'+names[i+1]
				starts=np.delete(starts, toPop)
				ends=np.delete(ends, toPop)
				names=np.delete(names, toPop)

				track=Track(curve=False, name=basename(fname).split('.')[0])
				sh=self.HiC.shift*self.HiC.sizebp/100

				for i in range(len(starts)):
					a=Region(
						x=[starts[i]+sh, ends[i]+sh], 
						nameOfReg=names[i], 
						mapsize=self.HiC.sizebp,
						direction=strand[i])
					track.addItem(a)
					self.shiftChanged.connect(a.mov)
					self.sizeChanged.connect(a.siz)

				self.addTrack(track)

			elif fname[-9:]==".bedgraph":
				starts,ends,values = np.genfromtxt(
					fname=fname, 
					delimiter="\t", 
					dtype=None, 
					usecols=(1,2,3), 
					unpack=True, 
					encoding=None, 
					comments='track')
				
				track=Track(curve=True, name=basename(fname).split('.')[0])

				starts=[i+self.HiC.shift*self.HiC.sizebp/100 for i in starts]
				ends=[i+self.HiC.shift*self.HiC.sizebp/100 for i in ends]
				xset=[(starts[i]+ends[i])/2 for i in range(len(starts))]
				yset=values
				dataList=[(xset[i],yset[i]) for i in range(len(xset))]
				curveData=np.array(dataList, dtype=[('x', 'f'), ('y', 'f')])

				a=Curve(curveData=curveData, 
					pen='#DDD', 
					mapsize=self.HiC.sizebp)
				track.addItem(a)
				self.shiftChanged.connect(a.mov)
				self.sizeChanged.connect(a.siz)

				self.addTrack(track)

	def addTrack(self, track): #Add Track and Close button
		
		self.tracksOpened+=1
		self.mainLayout.nextRow()

		if self.tracksOpened==1 and self.HiC.name=='':
			self.plot.disableAutoRange()
			pad=-0.05 if track.curve else -0.33
			track.getViewBox().autoRange(axis='x', padding=pad)
			diapX,diapY=track.getViewBox().state['viewRange']
			self.plot.setXRange(max=diapX[1], min=diapX[0], padding=0)
		
		self.mainLayout.addItem(track)
		
		track.setXLink(self.plot)

		btn=CloseButton(linkedTrack=track, height=100 if track.curve else 50, 
			parentLayout=self.mainLayout, parentWindow=self)
		self.mainLayout.addItem(btn, col=1)


class hicInterface(): #Convinient envelope for cooler, also processing data and metadata

	def __init__(self):

		self.clr=None
		self.rawdata=np.zeros((2,2))
		self.prepdata=np.zeros((2,2))
		self.name=''
		self.bname=''
		self.res=5000
		self.log=True
		self.oe=False
		self.shift=0
		self.size=0
		self.sizebp=0
		self.resolutions=[] #available resolutions in other coolers

	def open(self, file, resolution=None):
		if resolution==None: resolution=self.res
		if file[-6:]==".mcool":
			resolutions=[i.split('/')[-1] for i in cooler.fileops.list_coolers(file)]
			if str(resolution) not in resolutions:
				diffResList=list(enumerate([abs(int(i)-resolution) for i in resolutions]))
				resolution=int(resolutions[min(diffResList, key=lambda i : i[1])[0]])
			self.clr=cooler.Cooler(file+'::resolutions/'+str(resolution))
			self.rawdata=self.clr.matrix(balance=True)[:, :]
			self.name=file
			self.res=resolution
			self.resolutions=resolutions

		elif file[-5:]==".cool":
			self.clr=cooler.Cooler(file)
			self.rawdata=self.clr.matrix(balance=True)[:, :]
			self.name=file
			self.res=int(self.clr.binsize)
			self.resolutions=[str(self.clr.binsize)]

		elif file[-3:]==".np": #numpy savetxt files
			self.rawdata=np.loadtxt(file)
			self.name=file
			self.res=1
			self.resolutions=[]

		else:
			return False

		self.bname=basename(self.name)
		self.size=self.rawdata.shape[0]		
		self.sizebp=self.size*self.res
		self.process()
		return True

	def close(self):
		self.__init__()

	def process(self):
		self.prepdata=self.rawdata
		if self.oe:
			self.prepdata=OE(self.prepdata)
		if self.log:
			self.prepdata=LOG(self.prepdata)
		self.prepdata=NORM(self.prepdata)

	def product(self):
		step=self.rawdata.shape[0]/100
		findata=np.roll(self.prepdata, int(self.shift*step), axis=0)
		findata=np.roll(findata, int(self.shift*step), axis=1)
		return findata

	def toggleOE(self):
		self.oe=not self.oe
		self.process()

	def toggleLOG(self):
		self.log=not self.log
		self.process()

	def changeShift(self, arg):
		self.shift+=arg
		if self.shift>=100:
			self.shift=0
		if self.shift<=-100:
			self.shift=0

	#def summary(self):
	#	return self.bname, self.sizebp, self.res, self.log, self.oe, int(self.shift*self.sizebp/100)


class Track(pg.PlotItem): #Track for showing features
	
	def __init__(self, name, curve=False):
		if curve:
			super().__init__(axisItems={'left':MyYAxis()}, viewBox=MyViewBox())
		else:
			super().__init__(viewBox=MyViewBox())
		height=100 if curve else 50
		#track.getAxis('bottom').setScale(int(window.selectedRes))
		self.setMaximumHeight(height)
		self.showAxes(True, showValues=False)
		self.getAxis('bottom').setStyle(showValues=False, tickLength=0)
		self.getAxis('top').setStyle(showValues=False, tickLength=0)
		self.getAxis('right').setStyle(showValues=False, tickLength=0)
		self.getAxis('left').setWidth(65)
		self.curve=curve
		title=pg.LabelItem(text=name, parent=self)
		title.anchor(itemPos=(0,0), parentPos=(0,0), offset=(66,0))
		if curve==False:
			self.getAxis('left').setStyle(showValues=False, tickLength=0)
			self.disableAutoRange()
			self.setYRange(-2,2)
			self.setMouseEnabled(x=True,y=False)
		else:
			self.getAxis('left').setStyle(showValues=True)
			self.enableAutoRange(y=True, x=False)
			
			self.buttonsHidden=True
			self.setMouseEnabled(x=True,y=False)


regionColors=pg.colormap.get('CET-R4')
class Region(pg.PlotCurveItem): #Genes and regions on tracks

	def __init__(self, x, mapsize, direction='0', nameOfReg=''):

		if '+' in direction:
			pen=pg.mkPen(regionColors.map(uniform(0.78,1)), width=12*dpr)
			y=[1,1]
		elif '-' in direction:
			pen=pg.mkPen(regionColors.map(uniform(0.1,0.35)), width=12*dpr)
			y=[-1,-1]
		else:
			pen=pg.mkPen(regionColors.map(uniform(0.375,0.60)), width=12*dpr)
			y=[0,0]
		
		super().__init__(x=np.array(x)%mapsize if mapsize!=0 else x, 
			y=y, pen=pen, clickable=True, skipFiniteCheck=True)

		if self.xData[0]>self.xData[1]:
			self.setPen(None)
		
		self.nameOfReg=nameOfReg
		#self.direction=direction
		self.setClickable(True, width=15*dpr)
		self.sigClicked.connect(self.lineClicked)
		self.mapsize=mapsize
		self.pen=pen
		self.setCursor(Qt.PointingHandCursor)

	def mov(self, arg):
		self.setData(x=(self.xData+arg)%self.mapsize, y=self.yData)
		if self.xData[0]>self.xData[1]:
			self.setPen(None)
		else:
			self.setPen(self.pen)

	def siz(self, arg):
		self.mapsize=arg

	def lineClicked(self):
		msg = QtWidgets.QMessageBox()
		msg.setText(self.nameOfReg.replace(';','\n'))
		#msg.setInformativeText(str(self.xData))
		msg.setWindowTitle("Feature info")
		msg.exec_()


class Curve(pg.PlotCurveItem): #bedgraph curves on tracks
#Переписываем curveData под array
	def __init__(self, curveData, pen, mapsize):
		self.mapsize=mapsize
		self.pen=pen
		self.curveData=curveData
		self.rearrange(self.curveData)
		self.log=False

		super().__init__(x=self.curveData['x'], y=self.curveData['y'], pen=pen, skipFiniteCheck=True)
		
	def rearrange(self, inpList):
		if self.mapsize!=0:
			inpList['x']%=self.mapsize
		inpList.sort(order='x')

	def toggleLOG(self):
		if self.log==False:
			self.mi=np.nanmin(self.curveData['y'])
			self.curveData['y']=LOG(self.curveData['y'])
		else:
			self.curveData['y']=self.mi+10**self.curveData['y']
		self.setData(x=self.curveData['x'], y=self.curveData['y'])
		self.log=not self.log

	def mov(self, arg):
		self.curveData['x']+=arg
		self.rearrange(self.curveData)
		self.setData(x=self.curveData['x'], y=self.curveData['y'])

	def siz(self, arg):
		self.mapsize=arg

class Button(pg.LabelItem): #Control button (clickable label calling a function)

	def __init__(self, name, func, enabled=False):
		super().__init__(text=name)
		self.name=name
		self.func=func
		self.enabled=enabled
		if self.enabled:
			self.act(1)
		else:
			self.act(0)
		self.setPreferredHeight(50)
		self.setMaximumHeight(50)
		
	def hoverEvent(self, ev):
		if not self.enabled: return
		if ev.isExit():
			self.opts['color']=pg.getConfigOption('foreground')
			self.setText(self.name)
		elif ev.isEnter():
			if ev.pos()!=ev.lastPos():
				self.opts['color']='#DDD'
				self.setText(self.name)
		else:
			self.opts['color']='#DDD'
			self.setText(self.name)

	def mousePressEvent(self, ev):
		if not self.enabled: return
		self.opts['color']='#777'
		self.setText(self.name)

	def mouseReleaseEvent(self, ev):
		if not self.enabled: return
		self.func()

	def act(self, arg):
		if arg==0:
			self.enabled=False
			self.setCursor(Qt.ArrowCursor)
			self.opts['color']='#555'
			self.setText(self.name)
		else:
			self.enabled=True
			self.setCursor(Qt.PointingHandCursor)
			self.opts['color']=pg.getConfigOption('foreground')
			self.setText(self.name)


class CloseButton(pg.LabelItem): #Clickable label, closing one track
	
	def __init__(self, linkedTrack, height, parentLayout, parentWindow):
		super().__init__(text="Close")
		self.linkedTrack=linkedTrack
		self.setMaximumHeight(height)
		self.parentL=parentLayout
		self.parentW=parentWindow
		self.setCursor(Qt.PointingHandCursor)

	def hoverEvent(self, ev):
		if ev.isEnter():
			self.opts['color']='#DDD'
			self.setText('Close')
		elif ev.isExit():
			self.opts['color']=pg.getConfigOption('foreground')
			self.setText('Close')

	def mousePressEvent(self, ev):
		self.opts['color']='#777'
		self.setText('Close')

	def mouseReleaseEvent(self, ev):
		with pg.BusyCursor():
			self.parentL.removeItem(self.linkedTrack)
			for i in self.linkedTrack.getViewBox().allChildren()[1:]:
				self.parentW.sizeChanged.disconnect(i.siz)
				self.parentW.shiftChanged.disconnect(i.mov)	
				del i		
			del self.linkedTrack
			self.parentL.removeItem(self)
			self.parentW.tracksOpened-=1


class Board(pg.LabelItem): #Label with map info

	def __init__(self, text=''):
		super().__init__(text=text)
		self.data={'bname':'', 'sizebp':0, 'res':0, 'log':True, 'oe':False, 
			'shift':0, 'colormap':'magma', 'closed':True}

	def update(self, **kwargs):
		for i in kwargs.keys():
			for j in self.data.keys():
				if i==j:
					self.data[j]=kwargs[i]
		if self.data['closed']:
			self.setText('<p style="font-family: '+monoFont+'">No map is opened</p>', color=makeLUT(self.data['colormap'])[128])
		else:
			if 'bname' in kwargs.keys():
				if len(self.data['bname'])>18:
					self.data['bname']=self.data['bname'][0:15]+'...'
			if 'sizebp' in kwargs.keys():
				sizebp=''
				for i in range(1,len(str(self.data['sizebp']))+1):
					sizebp=(str(self.data['sizebp'])[-i]+"'" if (i-1)%3==0 and i!=1 else str(self.data['sizebp'])[-i]) + sizebp
				self.data['sizebp']=sizebp
			if 'res' in kwargs.keys():
				if str(self.data['res'])[-3:]=='000':
					self.data['res']=str(self.data['res'])[0:-3]+'k' 
			
			self.setText('<p style="font-family: '+monoFont+'">{bname}<br>Size {sizebp} bp<br>Resolution {res} bp<br>LOG={log}<br>OE={oe}<br>Shift={shift}<br>Colormap: {colormap}</p>'.format(**self.data), color=makeLUT(self.data['colormap'])[128])


class MyImageItem(pg.ImageItem): #allows to scale and rotate easily

	def __init__(self):
		super().__init__()
		self.baseScale=1
		self.tilted=False

	def setScale(self, coeff):
		self.baseScale=coeff
		tr = QtGui.QTransform()
		k=self.baseScale*(0.7071 if self.tilted else 1) 
		tr.scale(k,k)
		tr.rotate(-45 if self.tilted else 0)
		self.setTransform(tr)

	def tilt(self):
		self.tilted=not self.tilted
		self.setScale(self.baseScale)
		return self.tilted


class MyViewBox(pg.ViewBox): #fixes zooming&moving plots with locked aspect, adds independent autorange for 2 axes 

	def __init__(self):
		super().__init__()

	def _resetTarget(self):
		self.state['targetRange'] = [self.state['viewRange'][0][:], self.state['viewRange'][1][:]]

	def scaleBy(self, s=None, center=None, x=None, y=None):

		if s is not None:
			x, y = s[0], s[1]

		affect = [x is not None, y is not None]
		if not any(affect):
			return

		scale = pg.Point([1.0 if x is None else x, 1.0 if y is None else y])

		if self.state['aspectLocked'] is not False:
			scale[0] = scale[1] if x is None else scale[0]
			scale[1] = scale[0] if y is None else scale[1]

		vr = self.targetRect()
		if center is None:
			center = pg.Point(vr.center())
		else:
			center = pg.Point(center)

		tl = center + (vr.topLeft()-center) * scale
		br = center + (vr.bottomRight()-center) * scale

		if not affect[0]:
			self.setYRange(tl.y(), br.y(), padding=0)
		elif not affect[1]:
			self.setXRange(tl.x(), br.x(), padding=0)
		else:
			self.setRange(QtCore.QRectF(tl, br), padding=0)

	def autoRange(self, padding=None, axis='xy'):
		bounds = self.childrenBoundingRect()
		if bounds is not None:
			if 'x' in axis:
				self.setXRange(bounds.left(), bounds.right(), padding=padding)
			if 'y' in axis:
				self.setYRange(bounds.bottom(), bounds.top(), padding=padding)


class MyYAxis(pg.AxisItem): #Axis toggling log mode on click
	def __init__(self):
		super().__init__('left')
		self.setCursor(Qt.PointingHandCursor)
		self.log=False

	def mouseClickEvent(self, event): #Toggle log mode
		for i in self.linkedView().allChildren():
				if isinstance(i, Curve):
					i.toggleLOG()
		if self.log==False:
			self.setLogMode(y=True)
		else:
			self.setLogMode(y=False)
		self.log=not self.log


def opendialog(title):
	return QtWidgets.QFileDialog.getOpenFileName(None, title, '')


def selectdialog(options, title):
	return QtWidgets.QInputDialog.getItem(None, title, None, options, False)


def makeLUT(name): #...and return certain LUT in proper format
	redCurveList=colormaps[name]['red']
	greenCurvelist=colormaps[name]['green']
	blueCurvelist=colormaps[name]['blue']
	colors=[(redCurveList[i], greenCurvelist[i], blueCurvelist[i]) for i in range(256)]
	colorArray = np.array([np.array(color) for color in colors])
	lookUpTab = colorArray.astype(np.uint8)
	return lookUpTab


def OE(data): #Compute observed/expected
	a=data
	a=np.array([np.roll(a[i], -i) for i in range(a.shape[0])])
	a=np.nansum(a, axis=0)
	a=np.row_stack([a]*a.shape[0])
	a=np.array([np.roll(a[i], i) for i in range(a.shape[0])])
	#return(data/np.nansum(data)-a/np.nansum(a)) #Place for experiments
	return(data/a)


def NORM(data):

	mi=(np.nanmin(data))
	ma=(np.nanmax(data))
	if ma!=mi:
		return (data-mi)/(ma-mi)
	else:
		return np.zeros(data.shape)

def LOG(data):
	
	mi=np.nanmin(data)
	ma=np.nanmax(data)
	rang = ma-mi
	shifted=data-mi+rang/10000
	if ma!=mi:
		return np.log10(shifted)
	else:
		return np.zeros(data.shape)


def main():

	if len(sys.argv) > 1: # "prohic shortcut" command makes a desktop shortcut
		if sys.argv[1] == 'shortcut':
			print("Making desktop shortcut...")
			from pyshortcuts import make_shortcut
			make_shortcut(__file__, name='ProHiC', startmenu=False)
			print("Desktop shortcut made successfully")
			if sys.platform=='linux':
				print("You should allow launching in its right-button menu")
			sys.exit()

	global monoFont
	global dpr
	
	np.seterr(invalid='ignore')
	pg.setConfigOption('foreground', '#AAA') #make fg color lighter

	app = QtWidgets.QApplication(sys.argv) #GUI control object
	font=app.font()
	font.setPointSize(font.pointSize()+1)
	app.setFont(font)

	#Not the best idea, but will work on most OS
	if sys.platform=='win32':
		monoFont='Consolas'
	elif sys.platform=='darwin':
		monoFont='Monaco'
	elif sys.platform=='linux':
		monoFont='Ubuntu Mono'

	window = BrowserWindow() #Make main window
	dpr=window.devicePixelRatio() #Global var to scale interface correctly
	sys.exit(app.exec_()) #Main cycle

main() # if started directly as "python prohic.py" or similarly
