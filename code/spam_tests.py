#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 12:17:48 2019

@author: cyril
"""



#!/usr/bin/env python
# encoding: utf-8
"""
screengrab.py

Created by Alex Snet on 2011-10-10.
Copyright (c) 2011 CodeTeam. All rights reserved.
"""
from PIL import Image

import sys
import os




class screengrab:
    def __init__(self):
        try:
            import gtk
        except ImportError:
            pass
        else:
            self.screen = self.getScreenByGtk

        try:
            import PyQt4
        except ImportError:
            pass
        else:
            self.screen = self.getScreenByQt

        try:
            import wx
        except ImportError:
            pass
        else:
            self.screen = self.getScreenByWx

        try:
            import ImageGrab
        except ImportError:
            pass
        else:
            self.screen = self.getScreenByPIL


    def getScreenByGtk(self):
        import gtk.gdk      
        w = gtk.gdk.get_default_root_window()
        sz = w.get_size()
        pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
        pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
        if pb is None:
            return False
        else:
            width,height = pb.get_width(),pb.get_height()
            return Image.fromstring("RGB",(width,height),pb.get_pixels() )

    def getScreenByQt(self):
        from PyQt4.QtGui import QPixmap, QApplication
        from PyQt4.Qt import QBuffer, QIODevice
        from io import StringIO
        import io
        app = QApplication(sys.argv)
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        QPixmap.grabWindow(QApplication.desktop().winId()).save(buffer, 'png')
        strio = io.BytesIO()
        strio.write(buffer.data())
        buffer.close()
        del app
        strio.seek(0)
        return Image.open(strio)

    def getScreenByPIL(self):
        import ImageGrab
        img = ImageGrab.grab()
        return img

    def getScreenByWx(self):
        import wx
        wx.App()  # Need to create an App instance before doing anything
        screen = wx.ScreenDC()
        size = screen.GetSize()
        bmp = wx.EmptyBitmap(size[0], size[1])
        mem = wx.MemoryDC(bmp)
        mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
        del mem  # Release bitmap
        #bmp.SaveFile('screenshot.png', wx.BITMAP_TYPE_PNG)
        myWxImage = wx.ImageFromBitmap( myBitmap )
        PilImage = Image.new( 'RGB', (myWxImage.GetWidth(), myWxImage.GetHeight()) )
        PilImage.fromstring( myWxImage.GetData() )
        return PilImage

if __name__ == '__main__':
    s = screengrab()
    screen = s.screen()
    screen.show()


"""
##See if cards are dealt
try:
#Attempt to locate fast_fold_button
fast_fold_button = pyautogui.locate('../screenshots/menu_fast_fold.png', table_img, confidence=0.8)
print('"Fast-fold" button available')
print(fast_fold_button)
if(take_actions):
print("Moving to Fast-fold")
move_to_button(fast_fold_button)

except:
print('')
try:
#Attempt to locate fold_button
fold_button = pyautogui.locate('../screenshots/menu_fold.png', table_img, confidence=0.8)
print('"Fold" button available')
print(fold_button)
if(take_actions):
print("Moving to Fold")
move_to_button(fold_button)
continue
except:
print('')
try:
#Attempt to locate check_button
check_button = pyautogui.locate('../screenshots/menu_check.png', table_img, confidence=0.8)
print('"Check" button available')
print(check_button)
if(take_actions):
print("Moving to Check")
move_to_button(check_button)
continue
except:
print('')


#print('Waiting for opponents')
try:
dealer_button = pyautogui.locate('../screenshots/dealer_button.png', table_img, confidence=0.8)
print("located dealer")
print(dealer_button)
if(take_actions):
print("Moving to Dealer button")
move_to_button(dealer_button)
continue
except:
print('')
"""





"""
try:
#Attempt to locate hero
hero_display = pyautogui.locate('../screenshots/hero_display.png', table_img, confidence=0.7)
print('"Hero display" available')
if(take_actions):
    #move_to_button(hero_display)
except:
print('')
"""



   


#img_gray = rgb2gray(np.array(list(image.getdata())))

#startButton = pyautogui.locateOnScreen('../screenshots/dealer_button.png', region=(0,0,970,810), confidence=0.6)

#img_array = np.array(img)

#img_hsv = colorsys.rgb_to_hsv(img_array[1]/255.,img_array[2]/255.,img_array[3]/255.)

#brain_cont_canny = feature.canny(img_array, sigma=1, low_threshold = 20, high_threshold = 60)


#ax.imshow(brain_cont_canny,cmap='gray')
#plt.show()

#fig, ax = plt.subplots(1, 1, figsize=(12, 12))
#img_tresh = (img_array>240)
#ax.imshow(img_tresh, cmap='gray')