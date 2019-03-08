#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 12:17:48 2019

@author: cyril
"""

import pyautogui
startButton = pyautogui.locateOnScreen('start.png')
print(startButton)




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