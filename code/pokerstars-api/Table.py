#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# created 4th of April

from ScreenItem import ScreenItem
from Box import Box
import constants

class Table(ScreenItem):
    def __init__(self, id_, image_file, detection_confidence):
        ScreenItem.__init__(self,id_,image_file,detection_confidence)


    def childUpdateState(self, table_img = None):
        if(self.never_spotted and self.is_available):
            self.compCenterPosition()
            self.relevant_box = Box(int(self.box.left-constants.RESEARCH_MARGIN*self.box.width),int(self.box.top-constants.RESEARCH_MARGIN*self.box.height),(1+2*constants.RESEARCH_MARGIN)*self.box.width,(1+2*constants.RESEARCH_MARGIN)*self.box.height)
        return
