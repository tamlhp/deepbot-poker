#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 12:17:48 2019

@author: cyril
"""



#!/usr/bin/env python
# encoding: utf-8



import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


text = pytesseract.image_to_string(Image.open("../data/table-flop.png"), lang='eng',
                        config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')



"""
###CV2 PYTESSERACT OCR
import cv2
import pytesseract
from PIL import Image



path = '../data/table-flop.png'

image = cv2.imread(path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


 
scale_percent = 100 # percent of original size
width = int(image.shape[1] * scale_percent / 100)
height = int(image.shape[0] * scale_percent / 100)
dim = (width, height) 

gray = cv2.resize(gray, dim, interpolation = cv2.INTER_AREA) 

temp = "2"
# If user enter 1, Process Threshold or if user enters 2, then process medianBlur. Else, do nothing.
if temp == "1":
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
elif temp == "2":
    gray = cv2.medianBlur(gray, 3)


filename = "{}.png".format("temp")
cv2.imwrite(filename, gray)

text = pytesseract.image_to_string(Image.open(filename))
print(text)
"""


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

"""

    #cards =['2','3','4','5','6','7','8','9','J','Q','K','A']
    #for card in cards:
    #card_2 = Card(id_='card_2', image_path= 'card_2',detection_confidence=0.65)
    #card_2.locate(table_img)
    #card_3 = Card(id_='card_3', image_path= 'card_3',detection_confidence=0.65)
    #card_3.locate(table_img)
    #card_4 = Card(id_='card_4', image_path= 'card_4.png',detection_confidence=0.9)
    #card_4.locate(table_img)
    #card_5 = Card(id_='card_5', image_path= 'card_5.png',detection_confidence=0.9)
    #card_5.locate(table_img)
    #card_spade = Card(id_='card_spade', image_path= 'card_spade.png',detection_confidence=0.9)
    #card_spade.locate_all(table_img)
    #print(card_spade.isHeroCard(table))
    #card_diamond = Card(id_='card_diamond', image_path= 'card_diamond.png',detection_confidence=0.9)
    #card_diamond.locate(table_img)
    #print(card_spade.isHeroCard())
    #card_heart = Card(id_='card_heart', image_path= 'card_heart.png',detection_confidence=0.9)
    #card_heart.locate(table_img)
    #card_club = Card(id_='card_club', image_path= 'card_club.png',detection_confidence=0.9)
    #card_club.locate(table_img)
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

"""

def move_to_button(button_):    
    #print('Handling movement');
    #define the beta distribution parameters, from where the randomness of the agent is drawn
    beta_=random.uniform(0.1,5);
    alpha_smart=random.uniform(beta_,5);
    alpha_balanced=random.uniform(0.1,5);
    
    #define aimed location (with randomness)
    aimed_button = button_
    x_aimed = aimed_button.left+beta.rvs(alpha_balanced,beta_, size=1)[0]*aimed_button.width
    y_aimed = aimed_button.top+beta.rvs(alpha_balanced,beta_, size=1)[0]*aimed_button.height
    #define time to move (between 0.1 and 2 seconds)
    time_to_move = 0.1+2.4*beta.rvs(alpha_smart,beta_, size=1)[0]
    #define the easing function
    easing_function_select = beta.rvs(alpha_balanced,beta_, size=1)[0]*5
    if(easing_function_select<=1):
        #easing_function = pyautogui.easeInBounce;
        easing_function = pyautogui.easeInQuad;
    elif(easing_function_select<=2):
        easing_function = pyautogui.easeInQuad;
    elif(easing_function_select<=3):
        easing_function = pyautogui.easeInOutQuad;
    elif(easing_function_select<=4):
        easing_function = pyautogui.easeOutQuad;
    elif(easing_function_select<=5):
        #easing_function = pyautogui.easeInElastic;   
        easing_function = pyautogui.easeOutQuad;
    pyautogui.moveTo(x_aimed, y_aimed, time_to_move, easing_function)  
    #take short break before clicking
    #time.sleep(int(random.choice('011'))*0.8*beta.rvs(alpha_balanced,beta_, size=1)[0])
    #time.sleep(int(time_to_move))
    #pyautogui.click()
    print('Succesfuly handled movement');
    return
"""


"""
class HeroCards():
    def __init__(self, card1, card2):
        self.card1 = card1
        self.card2 = card2
        
        self.cards = [{'value':card1.value, 'color':card1.color}, {'value':card2.value,'color':card2.color}]
        print("## Hero has: "+self.cards[0]["value"]+ " of "+self.cards[0]["color"]+ " ##")
        print("## And: "+self.cards[1]["value"]+ " of "+ self.cards[1]["color"] + " ##")
              
              
"""