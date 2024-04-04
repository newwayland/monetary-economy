# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 17:10:32 2023

@author: andre
"""
import numpy as np

def floor_with_precision(value, precision):
    return np.true_divide(np.floor(value * 10**precision), 10**precision)

def ceil_with_precision(value, precision):
    return np.true_divide(np.ceil(value * 10**precision), 10**precision)