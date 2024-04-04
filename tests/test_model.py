# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 19:09:38 2023

@author: andre
"""


import pytest
import pandas as pd
import numpy as np
from agent_based_economy.model import Model
from agent_based_economy.agents.government import Government
from agent_based_economy.agents.banks import CentralBank
from agent_based_economy.ledgers import DepositLedger, LoanLedger


model = Model()
   
def test_model_attributes():
    model = Model()
    assert isinstance(model,Model) == True
    assert isinstance(model.deposit_ledger, DepositLedger) == True
    assert isinstance(model.loan_ledger, LoanLedger) == True
    assert isinstance(model.government, Government)
    assert isinstance(model.central_bank, CentralBank)
    assert isinstance(model.banks, list) == True
    
def test_model_default_time_attributes():
    model = Model()
    assert model.schedule.days_in_year == 252
    assert model.schedule.days_in_month == 21   

def test_model_custom_days_in_year():
    model = Model(days_in_month=20)
    assert model.schedule.days_in_year == 240
    assert model.schedule.days_in_month == 20

def test_model_days_in_year_adjusted_to_multiple_of_twelve():
    model = Model(days_in_month=20.6)
    assert model.schedule.days_in_year == 252
    assert model.schedule.days_in_month == 21
    
    model = Model(days_in_month=8.2)
    assert model.schedule.days_in_year == 96
    assert model.schedule.days_in_month == 8
    
def test_model_calendar():
    model = Model()
    assert model.schedule.day == 0
    assert model.schedule.year == 0
    assert model.schedule.month == 0
    assert model.schedule.year_day == 0
    assert model.schedule.month_day == 0
    assert model.schedule.start_of_this_year == 0
    assert model.schedule.start_of_this_month == 0
    
    model.schedule.steps += 1
    assert model.schedule.day == 1
    assert model.schedule.year == 0
    assert model.schedule.month == 0
    assert model.schedule.year_day == 1
    assert model.schedule.month_day == 1
    assert model.schedule.start_of_this_year == 0
    assert model.schedule.start_of_this_month == 0
    
    model.schedule.steps += 42
    assert model.schedule.day == 43
    assert model.schedule.year == 0
    assert model.schedule.month == 2
    assert model.schedule.year_day == 43
    assert model.schedule.month_day == 1
    assert model.schedule.start_of_this_year == 0
    assert model.schedule.start_of_this_month == 42
    
    model.schedule.steps += 1000
    
    assert model.schedule.day == 1043
    assert model.schedule.year == 4
    assert model.schedule.month == 1
    assert model.schedule.year_day == 35
    assert model.schedule.month_day == 14
    assert model.schedule.start_of_this_year == 1008
    assert model.schedule.start_of_this_month == 1029