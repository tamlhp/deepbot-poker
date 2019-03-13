#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 14:57:03 2019

@author: cyril
"""
import random
import pyautogui
from scipy.stats import beta
import time
from extra_functions import getRandDistrParams


class ScreenItem:
    def __init__(self, id_, image_path, detection_confidence):
        self.id = id_
        self.image_path = image_path
        self.detection_confidence = detection_confidence
        self.box = None
        self.is_available = False
        self.center_pos = None
        self.search_margin = 1/4
        self.hasKnownLocation = False


            
    def search(self, table_img):
        try:
            #Attempt to locate button
            self.box = pyautogui.locate('../data/images/'+self.image_path, table_img, confidence=self.detection_confidence)
            if(self.box!=None):
                self.is_available=True
                self.compCenterPosition()
                self.hasKnownLocation = True
                print('[ScreenItem] : "'+ self.id +'" spotted and available')
        except:
            #print('ScreenItem : "'+ self.id +'" is NOT available')
            pass
        
    def compCenterPosition(self):
        if (not self.is_available):
            #print('ScreenItem : "'+ self.id +'" is NOT available')
            pass
        else:
             self.center_pos= [self.box.left+self.box.width/2,self.box.top+self.box.height/2]
        return
    
    def printPosition(self):    
        if (not self.is_available):
            #print('ScreenItem : "'+ self.id +'" is NOT available')
            pass
        else:
            print(self.id+' defined by position : \n [left:'+str(self.box.left)+', top:'+str(self.box.top)
                +'] \n [width: '+str(self.box.width)+', height: '+str(self.box.height)
                +'] \n [center_x: '+str(self.center_pos[0])+', center_y: '+str(self.center_pos[1])+']')
        return
         
         
    def moveTo(self, click=False, location='random', easing_function='deterministic', move_time='random', click_time='random'):
        if (self.is_available):                      
            #print('Handling movement');
            #define the beta distribution parameters, from where the randomness of the agent is drawn
            if(location=='random' or easing_function=='random' or move_time=='random' or click_time =='random'):
                beta_, alpha_smart, alpha_balanced = getRandDistrParams();
            

            aimed_box = self.box         
            
            #define the location to go
            if(location=='deterministic'):
                x_aimed = aimed_box.left
                y_aimed = aimed_box.top
            elif(location=='random'):
                x_aimed = aimed_box.left+(0.1+0.8)*beta.rvs(alpha_smart,beta_, size=1)[0]*aimed_box.width
                if(self.id=='Bet_sizer'):
                    y_aimed = aimed_box.top+aimed_box.height/2
                else:
                    y_aimed = aimed_box.top+(0.1+0.8)*beta.rvs(alpha_smart,beta_, size=1)[0]*aimed_box.height
       
            #define the easing function (movement motion)
            if(easing_function=='deterministic'):
                easing_function = pyautogui.easeInOutQuad
            elif(easing_function=='random'):
                #define the easing function
                easing_function_select = beta.rvs(alpha_smart,beta_, size=1)[0]*5
                if(easing_function_select<=1):
                    easing_function = pyautogui.easeInBounce;
                    #easing_function = pyautogui.easeInQuad;
                elif(easing_function_select<=2):
                    easing_function = pyautogui.easeInQuad;
                elif(easing_function_select<=3):
                    easing_function = pyautogui.easeInOutQuad;
                elif(easing_function_select<=4):
                    easing_function = pyautogui.easeOutQuad;
                elif(easing_function_select<=5):
                    easing_function = pyautogui.easeInElastic;   
                    #easing_function = pyautogui.easeOutQuad;
                
            #define time to move (between 0.1 and 2 seconds)
            if(move_time=='deterministic'):
                time_to_move = 0.6
            elif(move_time=='random'):
                time_to_move = 0.4+1.1*beta.rvs(alpha_smart,beta_, size=1)[0]


            pyautogui.moveTo(x_aimed, y_aimed, time_to_move, easing_function)
        
            
            if(click):
                #take short break before clicking
                if(click_time=='random'):
                    time.sleep(int(random.choice('011'))*0.5*beta.rvs(alpha_smart,beta_, size=1)[0])
                pyautogui.click()
            print('Succesfuly handled movement');
            return

        else:
            print("[Warning] Tried to move to '" +self.id+"', but it is unavailable")
            return



class Table(ScreenItem):
    def __init__(self, id_, image_path, detection_confidence, table_size=6):
        ScreenItem.__init__(self,id_,image_path,detection_confidence)
        
        #self.center = self.getTableCenter
    
   # def getTableCenter(self):
   

        