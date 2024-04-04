# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 18:34:16 2022

@author: ABE
"""


import pytest
import pandas as pd
import numpy as np
import re
from agent_based_economy.ledgers import Ledger, LoanLedger
from agent_based_economy.model import Model
from agent_based_economy.agents.agent import Agent

model = Model()
neil  = Agent(model)
andy  = Agent(model)
rich  = Agent(model)
   
def test_basic_properties():
    ledger = LoanLedger(model)
    assert isinstance(ledger,Ledger) == True
    assert isinstance(ledger.df, pd.DataFrame) == True
    assert isinstance(ledger.model,Model) == True
    assert isinstance(ledger.counter,int) == True
    
def test_loan_ledger_next_id():
    ledger = LoanLedger(model)
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
    
def test_loan_ledger_create():
    ledger = LoanLedger(model)
    assert len(ledger) == 0
    
    acc = ledger.create(neil, andy, 100, 1, 240)
    assert len(ledger) == 1
    assert acc == 0
    
    acc = ledger.create(andy, rich, 50, 1, 240)
    assert len(ledger) == 2
    assert acc == 1
    
    acc = ledger.create(issuer=rich, holder=andy, value=20, issue_date=1, maturity_date=240)
    assert len(ledger) == 3
    assert acc == 2

def test_loan_ledger_drop():
    ledger = LoanLedger(model)
    
    acc = ledger.create(neil, andy, 100, 1, 240)
    acc = ledger.create(andy, rich, 50, 1, 240)
    acc = ledger.create(rich, andy, 20, 1, 240)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.drop(1)
    assert success == True
    assert len(ledger) == 2
    assert (ledger.df.index == [0,2]).all()

def test_loan_ledger_drop_invalid_index():
    ledger = LoanLedger(model)
    
    acc = ledger.create(neil, andy, 100, 1, 240)
    acc = ledger.create(andy, rich, 50, 1, 240)
    acc = ledger.create(rich, andy, 20, 1, 240)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.drop(10)
    assert success == False
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
def test_loan_ledger_get_record():
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240)
    acc2 = ledger.create(andy, rich, 50, 1, 240)
    acc3 = ledger.create(rich, andy, 20, 1, 240)
    
    rec1 = ledger.get(acc1)
    assert rec1['issuer'] == neil
    assert rec1['holder'] == andy
    assert rec1['value'] == 100
    assert rec1['issue_date'] == 1
    assert rec1['maturity_date'] == 240
    assert rec1['interest_rate'] == 0
    
    rec3 = ledger.get(acc3)
    assert rec3['issuer'] == rich
    assert rec3['holder'] == andy
    assert rec3['value']  == 20
    assert rec1['issue_date'] == 1
    assert rec1['maturity_date'] == 240
    assert rec1['interest_rate'] == 0
    
def test_loan_ledger_defaults():    
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240)
    
    rec1 = ledger.get(acc1)
    assert rec1['interest_rate'] == 0
    assert rec1['issue_date'] == 1
    assert rec1['maturity_date'] == 240
    
def test_loan_ledger_options():   
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 5, 485,
                         interest_rate=2)
    
    rec1 = ledger.get(acc1)
    assert rec1['interest_rate'] == 2
    assert rec1['issue_date'] == 5
    assert rec1['maturity_date'] == 485

def test_retrieve_issuer_by_index():     
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240)
    
    assert ledger.issuer(acc1) == neil
    
def test_retrieve_holder_by_index():     
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240)
    
    assert ledger.holder(acc1) == andy
    
def test_loan_ledger_extend():    
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 0, 0, 0)
    acc2 = ledger.create(andy, rich, 0, 0, 0)
    acc3 = ledger.create(rich, andy, 0, 0, 0)
    
    assert ledger.get(acc1).value == 0
    assert ledger.get(acc2).value == 0
    assert ledger.get(acc3).value == 0
    
    assert ledger.get(acc1).maturity_date == 0
    assert ledger.get(acc2).maturity_date == 0
    assert ledger.get(acc3).maturity_date == 0
    
    ledger.extend_loan(acc1, 39, 1, 240)
    
    assert ledger.get(acc1).value == 39
    assert ledger.get(acc2).value == 0
    assert ledger.get(acc3).value == 0
    
    assert ledger.get(acc1).maturity_date == 240
    assert ledger.get(acc2).maturity_date == 0
    assert ledger.get(acc3).maturity_date == 0
    
   
def test_loan_ledger_credit_invalid_account():   
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 0, 0, 0)
    acc2 = ledger.create(andy, rich, 0, 0, 0)
    acc3 = ledger.create(rich, andy, 0, 0, 0)
    
    assert ledger.get(acc1).value == 0
    assert ledger.get(acc2).value == 0
    assert ledger.get(acc3).value == 0
    
    with pytest.raises(ValueError):
        ledger.extend_loan(40, 39, 1, 240)
    
    with pytest.raises(ValueError):
        ledger.extend_loan('andy', 39, 1, 240)
    
def test_loan_ledger_writedown():    
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240)
    acc2 = ledger.create(andy, rich, 50, 1, 240)
    acc3 = ledger.create(rich, andy, 20, 1, 240)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.writedown_loan(acc2, 23)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 27
    assert ledger.get(acc3).value == 20

def test_loan_ledger_writedown_overdraft():   
    # Overdraft constraints to reside on loanIssuer role
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240)
    acc2 = ledger.create(andy, rich, 50, 1, 240)
    acc3 = ledger.create(rich, andy, 20, 1, 240)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.writedown_loan(acc2, 1000)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == -950
    assert ledger.get(acc3).value == 20
   
def test_loan_ledger_extend_invalid_accout():    
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240)
    acc2 = ledger.create(andy, rich, 50, 1, 240)
    acc3 = ledger.create(rich, andy, 20, 1, 240)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    with pytest.raises(ValueError):
        ledger.extend_loan(12, 1000, 1, 240)
    
    with pytest.raises(ValueError):
        ledger.extend_loan('andy', 39, 1, 240)
    
def test_loan_ledger_apply_interest():       
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240, 1)
    acc2 = ledger.create(andy, rich,  50, 1, 240, 2)
    acc3 = ledger.create(rich, andy,  20, 1, 240, 3)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.apply_daily_interest()
    
    assert ledger.get(acc1).value == 100 * (1 + ((1/100)/252))
    assert ledger.get(acc2).value == 50 * (1 + ((2/100)/252))
    assert ledger.get(acc3).value == 20 * (1 + ((3/100)/252))
        
def test_get_records_by_holder():          
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240, 1)
    acc2 = ledger.create(andy, rich,  50, 1, 240, 2)
    acc3 = ledger.create(rich, andy,  20, 1, 240, 3)
    
    records = ledger.records_by_holder(andy)
    assert len(records) == 2
    assert records.value.sum() == 120
    
    records = ledger.records_by_holder(rich)
    assert len(records) == 1
    assert records.value.sum() == 50
    
    records = ledger.records_by_holder(neil)
    assert len(records) == 0
    assert records.value.sum() == 0
    
def test_get_records_by_issuer():          
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240, 1)
    acc2 = ledger.create(neil, rich,  50, 1, 240, 2)
    acc3 = ledger.create(rich, andy,  20, 1, 240, 3)
    
    records = ledger.records_by_issuer(neil)
    assert len(records) == 2
    assert records.value.sum() == 150
    
    records = ledger.records_by_issuer(rich)    
    assert len(records) == 1
    assert records.value.sum() == 20
    
    records = ledger.records_by_issuer(andy)
    assert len(records) == 0
    assert records.value.sum() == 0
    
def test_update_interest_rate_by_lender():
    ledger = LoanLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1, 240, 1)
    acc2 = ledger.create(neil, rich,  50, 1, 240, 2)
    acc3 = ledger.create(rich, andy,  20, 1, 240, 3)
    
    records = ledger.records_by_issuer(neil)
    
    assert records.loc[0].interest_rate == 1
    assert records.loc[1].interest_rate == 2
    
    ledger.update_interest_rate_by_lender(andy, 5)
    
    records = ledger.records_by_issuer(neil)
    
    assert records.loc[0].interest_rate == 5
    assert records.loc[1].interest_rate == 2
    