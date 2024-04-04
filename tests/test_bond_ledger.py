# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 18:34:16 2022

@author: ABE
"""


import pytest
import pandas as pd
import numpy as np
import re
from agent_based_economy.ledgers import Ledger, BondLedger
from agent_based_economy.model import Model
from agent_based_economy.agents.agent import Agent
from agent_based_economy.agents.individual import Individual
from agent_based_economy.agents.government import Government
   
def test_basic_properties():    
    model = Model()
    
    ledger = BondLedger(model)
    assert isinstance(ledger,Ledger) == True
    assert isinstance(ledger.df, pd.DataFrame) == True
    assert isinstance(ledger.model,Model) == True
    assert isinstance(ledger.counter,int) == True
    
def test_bond_ledger_next_id():    
    model = Model()
    
    ledger = BondLedger(model)
    unique_id = ledger.next_id()
    assert unique_id == 0
    unique_id = ledger.next_id()
    assert unique_id == 1
    unique_id = ledger.next_id()
    assert unique_id == 2
    unique_id = ledger.next_id()
    assert unique_id == 3
    unique_id = ledger.next_id()
    assert unique_id == 4
    
def test_bond_ledger_create():    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)
    assert len(ledger) == 0
    
    reference_number = ledger.create(government, 2, 1)
    assert len(ledger) == 1
    assert reference_number == 0
    
    reference_number = ledger.create(government, 2, 1)
    assert len(ledger) == 2
    assert reference_number == 1
    
    reference_number = ledger.create(government, 2, 1)
    assert len(ledger) == 3
    assert reference_number == 2

def test_bond_ledger_drop():    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)
    
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.drop(1)
    assert success == True
    assert len(ledger) == 2
    assert (ledger.df.index == [0,2]).all()

def test_bond_ledger_drop_invalid_index():    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)
    
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.drop(10)
    assert success == False
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()

def test_bond_ledger_close():    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)
    
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.close(1)
    assert success == True
    assert len(ledger) == 2
    assert (ledger.df.index == [0,2]).all()
    
def test_bond_ledger_close_invalid_index():    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)
    
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.close(10)
    assert success == False
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()

def test_bond_ledger_close_non_self_owned():    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)
    
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    ledger.create(government, 2, 1)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    ledger.transfer(1, Individual(model))
    
    success = ledger.close(1)
    assert success == False
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
def test_bond_ledger_get_record():    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 2, 1)
    reference_number_2 = ledger.create(government, 2, 1)
    reference_number_3 = ledger.create(government, 2, 1)
    
    record_1 = ledger.get(reference_number_1)
    assert record_1['issuer'] == government
    assert record_1['holder'] == government
    assert record_1['value'] == 100
    assert record_1['issue_date'] == 0
    assert record_1['maturity_date'] == 252
    assert record_1['interest_rate'] == 2
    
def test_bond_ledger_maturity_length():    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 2, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 2, 5)
    reference_number_4 = ledger.create(government, 2, 1/2)
    reference_number_5 = ledger.create(government, 2, 1/4)
    reference_number_6 = ledger.create(government, 2, 1/12)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    record_4 = ledger.get(reference_number_4)
    record_5 = ledger.get(reference_number_5)
    record_6 = ledger.get(reference_number_6)
    
    assert record_1['issue_date'] == 0
    assert record_1['maturity_date'] == 252
    
    assert record_2['issue_date'] == 0
    assert record_2['maturity_date'] == 504
    
    assert record_3['issue_date'] == 0
    assert record_3['maturity_date'] == 1260
    
    assert record_4['issue_date'] == 0
    assert record_4['maturity_date'] == 126
    
    assert record_5['issue_date'] == 0
    assert record_5['maturity_date'] == 63
    
    assert record_6['issue_date'] == 0
    assert record_6['maturity_date'] == 21
    
def test_non_integer_long_term_bond_maturity(): 
    # These are bonds rather than bills, i.e. greater than 1 year and coupon paying
    # Specified maturity is round UP to nearest whole year    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 2, 0.9)
    reference_number_2 = ledger.create(government, 2, 1.5)
    reference_number_3 = ledger.create(government, 2, 4.3)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_1['maturity_date'] == 252
    
    assert record_2['issue_date'] == 0
    assert record_2['maturity_date'] == 504
    
    assert record_3['issue_date'] == 0
    assert record_3['maturity_date'] == 1260
    
def test_invalid_short_term_bond_maturity():
    # These are bills rather than bonds, i.e. less than 1 year and non coupon paying    
    model = Model()
    government = Government(model)
    
    ledger = BondLedger(model)    
    
    with pytest.raises(ValueError):
        ledger.create(government, 0, 1/5)
    
    with pytest.raises(ValueError):
        ledger.create(government, 0, 1/7)
    
    with pytest.raises(ValueError):
        ledger.create(government, 0, 1/9)

def test_short_term_bond_maturity_date_issued_within_first_month():    
    model = Model()
    government = model.government
    
    # [model.stepsss() for x in range(5)]
    model.schedule.steps =5
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/2)
    reference_number_2 = ledger.create(government, 0, 1/4)
    reference_number_3 = ledger.create(government, 0, 1/12)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_1['maturity_date'] == 126
    
    assert record_2['issue_date'] == 0
    assert record_2['maturity_date'] == 63
    
    assert record_3['issue_date'] == 0
    assert record_3['maturity_date'] == 21
        
def test_short_term_bond_maturity_date_issued_within_second_month():    
    model = Model()
    government = model.government
    
    # [model.steps() for x in range(25)]
    model.schedule.steps = 25
        
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/2)
    reference_number_2 = ledger.create(government, 0, 1/4)
    reference_number_3 = ledger.create(government, 0, 1/12)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 21
    assert record_1['maturity_date'] == 147
    
    assert record_2['issue_date'] == 21
    assert record_2['maturity_date'] == 84
    
    assert record_3['issue_date'] == 21
    assert record_3['maturity_date'] == 42
    
def test_long_term_bond_maturity_date_issued_within_first_year():      
    model = Model()
    government = model.government
    
    # [model.steps() for x in range(100)]
    model.schedule.steps =100
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 2, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 2, 5)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_1['maturity_date'] == 252
    
    assert record_2['issue_date'] == 0
    assert record_2['maturity_date'] == 504
    
    assert record_3['issue_date'] == 0
    assert record_3['maturity_date'] == 1260
    
def test_long_term_bond_maturity_date_issued_within_second_year():      
    model = Model()
    government = model.government
    
    # [model.steps() for x in range(300)]
    model.schedule.steps = 300
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 2, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 2, 5)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 252
    assert record_1['maturity_date'] == 504
    
    assert record_2['issue_date'] == 252
    assert record_2['maturity_date'] == 756
    
    assert record_3['issue_date'] == 252
    assert record_3['maturity_date'] == 1512
        
def test_long_term_bond_maturity_dates_converge():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)  
    
    for x in range(1000):
        ledger.create(government, 2, 1)
        ledger.create(government, 2, 2)
        ledger.create(government, 2, 5)
        
        model.schedule.steps += 1
    # all maturity dates should be multiples of end/start of year day
    assert np.any(ledger.df.maturity_date.unique() == np.arange(1,9)*252)
    
def test_short_term_bond_maturity_dates_converge():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)  
    
    for x in range(1000):
        ledger.create(government, 0, 1/12)
        ledger.create(government, 0, 1/4)
        ledger.create(government, 0, 1/2)
        
        model.schedule.steps += 1
    
    # all maturity dates should be multiples of end/start of month day
    assert np.any(ledger.df.maturity_date.unique() == np.arange(1,54)*21)
        
def test_short_term_bond_interest_rate_is_zero():        
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/2)
    reference_number_2 = ledger.create(government, 1, 1/4)
    reference_number_3 = ledger.create(government, 5, 1/12)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)

    assert record_1['interest_rate'] == 0
    assert record_2['interest_rate'] == 0
    assert record_3['interest_rate'] == 0

def test_long_term_bond_interest_rate_is_as_specified():        
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 10)
    reference_number_3 = ledger.create(government, 5, 30)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)

    assert record_1['interest_rate'] == 1
    assert record_2['interest_rate'] == 2
    assert record_3['interest_rate'] == 5

def test_bulk_create():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    
    assert len(ledger) == 0
    reference_numbers = ledger.create_bulk_value(government, 1000, 2, 1)
    assert len(ledger) == 10
    
    record_1 = ledger.get(reference_numbers[0])
    record_2 = ledger.get(reference_numbers[5])
    record_3 = ledger.get(reference_numbers[9])
    
    assert record_1['value'] == 100
    assert record_2['value'] == 100
    assert record_3['value'] == 100
    assert record_1['maturity_date'] == 252
    assert record_2['maturity_date'] == 252
    assert record_3['maturity_date'] == 252
    
def test_transfer_ownership():       
    model = Model()
    government = model.government
    neil  = Individual(model)
    andy  = Individual(model)
    rich  = Individual(model)
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 10)
    reference_number_3 = ledger.create(government, 5, 30)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1.holder == government
    assert record_2.holder == government
    assert record_3.holder == government
    
    ledger.transfer(reference_number_1, andy)
    ledger.transfer(reference_number_2, neil)
    ledger.transfer(reference_number_3, rich)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1.holder == andy
    assert record_2.holder == neil
    assert record_3.holder == rich
    
def test_cant_transfer_ownership_to_eixsting_holder():       
    model = Model()
    government = model.government
    neil  = Individual(model)
    andy  = Individual(model)
    rich  = Individual(model)
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 10)
    reference_number_3 = ledger.create(government, 5, 30)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1.holder == government
    assert record_2.holder == government
    assert record_3.holder == government
    
    ledger.transfer(reference_number_1, andy)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    
    assert record_1.holder == andy
    assert record_2.holder == government
    
    with pytest.raises(ValueError):
        ledger.transfer(reference_number_1, andy)
    
    with pytest.raises(ValueError):
        ledger.transfer(reference_number_2, government)

def test_long_term_bond_coupon_details():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 5, 5)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_2['issue_date'] == 0
    assert record_3['issue_date'] == 0
    assert record_1['maturity_date'] == 252
    assert record_2['maturity_date'] == 504
    assert record_3['maturity_date'] == 1260
    assert record_1['maturity_days'] == 252
    assert record_2['maturity_days'] == 504
    assert record_3['maturity_days'] == 1260
    assert record_1['days_to_maturity'] == 252
    assert record_2['days_to_maturity'] == 504
    assert record_3['days_to_maturity'] == 1260
    assert record_1['number_of_outstanding_coupon_payments'] == 2
    assert record_2['number_of_outstanding_coupon_payments'] == 4
    assert record_3['number_of_outstanding_coupon_payments'] == 10
    assert record_1['next_coupon_date'] == 126
    assert record_2['next_coupon_date'] == 126
    assert record_3['next_coupon_date'] == 126
    
def test_long_term_bond_coupon_details_time_shift():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 5, 5)
    
    # [model.steps() for x in range(15)]
    model.schedule.steps = 15
    ledger.recalculate()
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_2['issue_date'] == 0
    assert record_3['issue_date'] == 0
    assert record_1['maturity_date'] == 252
    assert record_2['maturity_date'] == 504
    assert record_3['maturity_date'] == 1260
    assert record_1['maturity_days'] == 252
    assert record_2['maturity_days'] == 504
    assert record_3['maturity_days'] == 1260
    assert record_1['days_to_maturity'] == 237
    assert record_2['days_to_maturity'] == 489
    assert record_3['days_to_maturity'] == 1245
    assert record_1['number_of_outstanding_coupon_payments'] == 2
    assert record_2['number_of_outstanding_coupon_payments'] == 4
    assert record_3['number_of_outstanding_coupon_payments'] == 10
    assert record_1['next_coupon_date'] == 126
    assert record_2['next_coupon_date'] == 126
    assert record_3['next_coupon_date'] == 126
    
def test_long_term_bond_coupon_details_larger_time_shift():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 5, 5)
    
    # [model.steps() for x in range(200)]
    model.schedule.steps = 200
    ledger.recalculate()
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_2['issue_date'] == 0
    assert record_3['issue_date'] == 0
    assert record_1['maturity_date'] == 252
    assert record_2['maturity_date'] == 504
    assert record_3['maturity_date'] == 1260
    assert record_1['maturity_days'] == 252
    assert record_2['maturity_days'] == 504
    assert record_3['maturity_days'] == 1260
    assert record_1['days_to_maturity'] == 52
    assert record_2['days_to_maturity'] == 304
    assert record_3['days_to_maturity'] == 1060
    assert record_1['number_of_outstanding_coupon_payments'] == 1
    assert record_2['number_of_outstanding_coupon_payments'] == 3
    assert record_3['number_of_outstanding_coupon_payments'] == 9
    assert record_1['next_coupon_date'] == 252
    assert record_2['next_coupon_date'] == 252
    assert record_3['next_coupon_date'] == 252
    
def test_short_term_bond_coupon_details():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/12)
    reference_number_2 = ledger.create(government, 0, 1/4)
    reference_number_3 = ledger.create(government, 0, 1/2)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_2['issue_date'] == 0
    assert record_3['issue_date'] == 0
    assert record_1['maturity_date'] == 21
    assert record_2['maturity_date'] == 63
    assert record_3['maturity_date'] == 126
    assert record_1['maturity_days'] == 21
    assert record_2['maturity_days'] == 63
    assert record_3['maturity_days'] == 126
    assert record_1['days_to_maturity'] == 21
    assert record_2['days_to_maturity'] == 63
    assert record_3['days_to_maturity'] == 126
    assert record_1['number_of_outstanding_coupon_payments'] == 0
    assert record_2['number_of_outstanding_coupon_payments'] == 0
    assert record_3['number_of_outstanding_coupon_payments'] == 0
    assert np.isnan(record_1['next_coupon_date'])
    assert np.isnan(record_2['next_coupon_date'])
    assert np.isnan(record_3['next_coupon_date'])
    
def test_short_term_bond_coupon_details_time_shift():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/12)
    reference_number_2 = ledger.create(government, 0, 1/4)
    reference_number_3 = ledger.create(government, 0, 1/2)
    
    # [model.steps() for x in range(15)]
    model.schedule.steps = 15
    ledger.recalculate()
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_2['issue_date'] == 0
    assert record_3['issue_date'] == 0
    assert record_1['maturity_date'] == 21
    assert record_2['maturity_date'] == 63
    assert record_3['maturity_date'] == 126
    assert record_1['maturity_days'] == 21
    assert record_2['maturity_days'] == 63
    assert record_3['maturity_days'] == 126
    assert record_1['days_to_maturity'] == 6
    assert record_2['days_to_maturity'] == 48
    assert record_3['days_to_maturity'] == 111
    assert record_1['number_of_outstanding_coupon_payments'] == 0
    assert record_2['number_of_outstanding_coupon_payments'] == 0
    assert record_3['number_of_outstanding_coupon_payments'] == 0
    assert np.isnan(record_1['next_coupon_date'])
    assert np.isnan(record_2['next_coupon_date'])
    assert np.isnan(record_3['next_coupon_date'])
    
def test_short_term_bond_coupon_details_larger_time_shift():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/12)
    reference_number_2 = ledger.create(government, 0, 1/4)
    reference_number_3 = ledger.create(government, 0, 1/2)
    
    # [model.steps() for x in range(30)]
    model.schedule.steps = 30
    ledger.recalculate()
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['issue_date'] == 0
    assert record_2['issue_date'] == 0
    assert record_3['issue_date'] == 0
    assert record_1['maturity_date'] == 21
    assert record_2['maturity_date'] == 63
    assert record_3['maturity_date'] == 126
    assert record_1['maturity_days'] == 21
    assert record_2['maturity_days'] == 63
    assert record_3['maturity_days'] == 126
    assert record_1['days_to_maturity'] == -9
    assert record_2['days_to_maturity'] == 33
    assert record_3['days_to_maturity'] == 96
    assert record_1['number_of_outstanding_coupon_payments'] == 0
    assert record_2['number_of_outstanding_coupon_payments'] == 0
    assert record_3['number_of_outstanding_coupon_payments'] == 0
    assert np.isnan(record_1['next_coupon_date'])
    assert np.isnan(record_2['next_coupon_date'])
    assert np.isnan(record_3['next_coupon_date']) 

def test_long_term_bond_hold_to_maturity_value():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 5, 5)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['hold_to_maturity_value'] == 100 + 100 * (1/100/2) * 2
    assert record_2['hold_to_maturity_value'] == 100 + 100 * (2/100/2) * 4
    assert record_3['hold_to_maturity_value'] == 100 + 100 * (5/100/2) * 10
    
def test_long_term_bond_hold_to_maturity_value_time_shift():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 5, 5)
    
    # [model.steps() for x in range(15)]
    model.schedule.steps = 0
    ledger.recalculate()
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['hold_to_maturity_value'] == 100 + 100 * (1/100/2) * 2
    assert record_2['hold_to_maturity_value'] == 100 + 100 * (2/100/2) * 4
    assert record_3['hold_to_maturity_value'] == 100 + 100 * (5/100/2) * 10
    
def test_long_term_bond_hold_to_maturity_value_larger_time_shift():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 1, 1)
    reference_number_2 = ledger.create(government, 2, 2)
    reference_number_3 = ledger.create(government, 5, 5)
    
    # [model.steps() for x in range(200)]
    model.schedule.steps = 200
    ledger.recalculate()
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['hold_to_maturity_value'] == 100 + 100 * (1/100/2) * 1
    assert record_2['hold_to_maturity_value'] == 100 + 100 * (2/100/2) * 3
    assert record_3['hold_to_maturity_value'] == 100 + 100 * (5/100/2) * 9
    
def test_short_term_hold_to_maturity_value_details():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/12)
    reference_number_2 = ledger.create(government, 0, 1/4)
    reference_number_3 = ledger.create(government, 0, 1/2)
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['hold_to_maturity_value'] == 100 
    assert record_2['hold_to_maturity_value'] == 100 
    assert record_3['hold_to_maturity_value'] == 100 
    
def test_short_term_bond_hold_to_maturity_value_time_shift():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/12)
    reference_number_2 = ledger.create(government, 0, 1/4)
    reference_number_3 = ledger.create(government, 0, 1/2)
    
    # [model.steps() for x in range(15)]
    model.schedule.steps = 15
    ledger.recalculate()
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['hold_to_maturity_value'] == 100 
    assert record_2['hold_to_maturity_value'] == 100 
    assert record_3['hold_to_maturity_value'] == 100 
    
def test_short_term_bond_hold_to_maturity_value_larger_time_shift():    
    model = Model()
    government = model.government
    
    ledger = BondLedger(model)    
    reference_number_1 = ledger.create(government, 0, 1/12)
    reference_number_2 = ledger.create(government, 0, 1/4)
    reference_number_3 = ledger.create(government, 0, 1/2)
    
    # [model.steps() for x in range(30)]
    model.schedule.steps =30
    ledger.recalculate()
    
    record_1 = ledger.get(reference_number_1)
    record_2 = ledger.get(reference_number_2)
    record_3 = ledger.get(reference_number_3)
    
    assert record_1['hold_to_maturity_value'] == 100 
    assert record_2['hold_to_maturity_value'] == 100 
    assert record_3['hold_to_maturity_value'] == 100 

# def test_retrieve_issuer_by_index():     
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240)
    
#     assert ledger.issuer(acc1) == neil
    
# def test_retrieve_holder_by_index():     
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240)
    
#     assert ledger.holder(acc1) == andy
    
# def test_loan_ledger_extend():    
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 0, 0, 0)
#     acc2 = ledger.create(andy, rich, 0, 0, 0)
#     acc3 = ledger.create(rich, andy, 0, 0, 0)
    
#     assert ledger.get(acc1).value == 0
#     assert ledger.get(acc2).value == 0
#     assert ledger.get(acc3).value == 0
    
#     assert ledger.get(acc1).maturity_date == 0
#     assert ledger.get(acc2).maturity_date == 0
#     assert ledger.get(acc3).maturity_date == 0
    
#     ledger.extend_loan(acc1, 39, 240)
    
#     assert ledger.get(acc1).value == 39
#     assert ledger.get(acc2).value == 0
#     assert ledger.get(acc3).value == 0
    
#     assert ledger.get(acc1).maturity_date == 240
#     assert ledger.get(acc2).maturity_date == 0
#     assert ledger.get(acc3).maturity_date == 0
    
   
# def test_loan_ledger_credit_invalid_account():   
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 0, 0, 0)
#     acc2 = ledger.create(andy, rich, 0, 0, 0)
#     acc3 = ledger.create(rich, andy, 0, 0, 0)
    
#     assert ledger.get(acc1).value == 0
#     assert ledger.get(acc2).value == 0
#     assert ledger.get(acc3).value == 0
    
#     with pytest.raises(ValueError):
#         ledger.extend_loan(40, 39, 240)
    
#     with pytest.raises(ValueError):
#         ledger.extend_loan('andy', 39, 240)
    
# def test_loan_ledger_writedown():    
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240)
#     acc2 = ledger.create(andy, rich, 50, 1, 240)
#     acc3 = ledger.create(rich, andy, 20, 1, 240)
    
#     assert ledger.get(acc1).value == 100
#     assert ledger.get(acc2).value == 50
#     assert ledger.get(acc3).value == 20
    
#     ledger.writedown_loan(acc2, 23)
    
#     assert ledger.get(acc1).value == 100
#     assert ledger.get(acc2).value == 27
#     assert ledger.get(acc3).value == 20

# def test_loan_ledger_writedown_overdraft():   
#     # Overdraft constraints to reside on loanIssuer role
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240)
#     acc2 = ledger.create(andy, rich, 50, 1, 240)
#     acc3 = ledger.create(rich, andy, 20, 1, 240)
    
#     assert ledger.get(acc1).value == 100
#     assert ledger.get(acc2).value == 50
#     assert ledger.get(acc3).value == 20
    
#     ledger.writedown_loan(acc2, 1000)
    
#     assert ledger.get(acc1).value == 100
#     assert ledger.get(acc2).value == -950
#     assert ledger.get(acc3).value == 20
   
# def test_loan_ledger_extend_invalid_accout():    
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240)
#     acc2 = ledger.create(andy, rich, 50, 1, 240)
#     acc3 = ledger.create(rich, andy, 20, 1, 240)
    
#     assert ledger.get(acc1).value == 100
#     assert ledger.get(acc2).value == 50
#     assert ledger.get(acc3).value == 20
    
#     with pytest.raises(ValueError):
#         ledger.extend_loan(12, 1000, 240)
    
#     with pytest.raises(ValueError):
#         ledger.extend_loan('andy', 39, 240)
    
# def test_loan_ledger_apply_interest():       
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240, 1)
#     acc2 = ledger.create(andy, rich,  50, 1, 240, 2)
#     acc3 = ledger.create(rich, andy,  20, 1, 240, 3)
    
#     assert ledger.get(acc1).value == 100
#     assert ledger.get(acc2).value == 50
#     assert ledger.get(acc3).value == 20
    
#     ledger.apply_daily_interest()
    
#     assert ledger.get(acc1).value == 100 * (1 + ((1/100)/240))
#     assert ledger.get(acc2).value == 50 * (1 + ((2/100)/240))
#     assert ledger.get(acc3).value == 20 * (1 + ((3/100)/240))
        
# def test_get_records_by_holder():          
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240, 1)
#     acc2 = ledger.create(andy, rich,  50, 1, 240, 2)
#     acc3 = ledger.create(rich, andy,  20, 1, 240, 3)
    
#     records = ledger.records_by_holder(andy)
#     assert len(records) == 2
#     assert records.value.sum() == 120
    
#     records = ledger.records_by_holder(rich)
#     assert len(records) == 1
#     assert records.value.sum() == 50
    
#     records = ledger.records_by_holder(neil)
#     assert len(records) == 0
#     assert records.value.sum() == 0
    
# def test_get_records_by_issuer():          
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240, 1)
#     acc2 = ledger.create(neil, rich,  50, 1, 240, 2)
#     acc3 = ledger.create(rich, andy,  20, 1, 240, 3)
    
#     records = ledger.records_by_issuer(neil)
#     assert len(records) == 2
#     assert records.value.sum() == 150
    
#     records = ledger.records_by_issuer(rich)    
#     assert len(records) == 1
#     assert records.value.sum() == 20
    
#     records = ledger.records_by_issuer(andy)
#     assert len(records) == 0
#     assert records.value.sum() == 0
    
# def test_update_interest_rate_by_lender():
#     ledger = BondLedger(model)    
#     acc1 = ledger.create(neil, andy, 100, 1, 240, 1)
#     acc2 = ledger.create(neil, rich,  50, 1, 240, 2)
#     acc3 = ledger.create(rich, andy,  20, 1, 240, 3)
    
#     records = ledger.records_by_issuer(neil)
    
#     assert records.loc[0].interest_rate == 1
#     assert records.loc[1].interest_rate == 2
    
#     ledger.update_interest_rate_by_lender(andy, 5)
    
#     records = ledger.records_by_issuer(neil)
    
#     assert records.loc[0].interest_rate == 5
#     assert records.loc[1].interest_rate == 2
    