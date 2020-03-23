import os
import numpy as np

import trackpy
import pandas

from api.segment import segment
from api.analyse import analyse


def get_image_array(VirtualStack, 
    m:int, 
    c:int):
    
    c2_time_reader = VirtualStack.read(t = None, m = m, c = c)
    
    return [img.array for img in c2_time_reader]

def get_cell_tracks(VirtualStack,
    m:int,
    c:int,
    muTopx = 3,
    minsize = 10,
    minmass = 10000):

    img_list = get_image_array(VirtualStack, m, c)

    min_size = muTopx*minsize

    return trackpy.batch(img_list, min_size, minmass=minmass)

def get_spheroid_properties(VirtualStack,
    m:int,
    spheroid_channel:int,
    fluo_channel:int,
    get_fluo = False,
    muTopx = 3):

    """
    
    extracts spheroid properties from image batch.

    COMMENT: with meta data we will integrate the above
    variables implicitely.

    Returns:
     - pandas.DataFrame
    
    """

    spheroid_frame = pandas.DataFrame()

    c1_time_reader = VirtualStack.read(t = None, 
        m = m, 
        c = spheroid_channel)

    for img in c1_time_reader:
        
        t = img.meta['t']
        m = img.meta['m']

        # function to be changed to Andrey's version
        
        crop_img_BF = segment.select_well(img.array, img.array, 430, 430, muTopx)            
        sph_img = segment.find_spheroid(crop_img_BF, 430, muTopx)

        if get_fluo:

            img_Fluo = VirtualStack.get_single_image(m=m, t=t, c=fluo_channel)

            crop_img_Fluo = segment.select_well(img.array, 
                img_Fluo, 430, 430, muTopx)

            timeFrame = analyse.spheroid_properties(sph_img, crop_img_Fluo)
        
        else:
            
            timeFrame = analyse.spheroid_properties(sph_img)
        
        
        timeFrame['t'] = t
        timeFrame['m'] = m
        
        spheroid_frame = spheroid_frame.append(timeFrame)

    return spheroid_frame

