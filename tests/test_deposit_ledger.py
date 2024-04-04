# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 18:34:16 2022

@author: ABE
"""


import pytest
import pandas as pd
import numpy as np
import re
from agent_based_economy.ledgers import Ledger, DepositLedger
from agent_based_economy.model import Model
from agent_based_economy.agents.agent import Agent

model = Model()
neil  = Agent(model)
andy  = Agent(model)
rich  = Agent(model)
   
def test_basic_properties():
    ledger = DepositLedger(model)
    assert isinstance(ledger,Ledger) == True
    assert isinstance(ledger.df, pd.DataFrame) == True
    assert isinstance(ledger.model,Model) == True
    assert isinstance(ledger.counter,int) == True
    
def test_deposit_ledger_next_id():
    ledger = DepositLedger(model)
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
    
def test_deposit_ledger_create():
    ledger = DepositLedger(model)
    assert len(ledger) == 0
    
    acc = ledger.create(neil, andy, 100)
    assert len(ledger) == 1
    assert acc == 0
    
    acc = ledger.create(andy, rich, 50)
    assert len(ledger) == 2
    assert acc == 1
    
    acc = ledger.create(issuer=rich, holder=andy, value=20)
    assert len(ledger) == 3
    assert acc == 2

def test_deposit_ledger_drop():
    ledger = DepositLedger(model)
    
    acc = ledger.create(neil, andy, 100)
    acc = ledger.create(andy, rich, 50)
    acc = ledger.create(rich, andy, 20)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.drop(1)
    assert success == True
    assert len(ledger) == 2
    assert (ledger.df.index == [0,2]).all()

def test_deposit_ledger_drop_invalid_index():
    ledger = DepositLedger(model)
    
    acc = ledger.create(neil, andy, 100)
    acc = ledger.create(andy, rich, 50)
    acc = ledger.create(rich, andy, 20)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.drop(10)
    assert success == False
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
def test_deposit_ledger_get_record():
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    rec1 = ledger.get(acc1)
    assert rec1['issuer'] == neil
    assert rec1['holder'] == andy
    assert rec1['value'] == 100
    
    rec3 = ledger.get(acc3)
    assert rec3['issuer'] == rich
    assert rec3['holder'] == andy
    assert rec3['value']  == 20
    
def test_deposit_ledger_defaults():    
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    
    rec1 = ledger.get(acc1)
    assert rec1['interest_rate'] == 0
    assert rec1['overdraft'] == 0
    
def test_deposit_ledger_options():   
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100,
                         interest_rate=2,
                         overdraft=500)
    
    rec1 = ledger.get(acc1)
    assert rec1['interest_rate'] == 2
    assert rec1['overdraft'] == 500

def test_retrieve_issuer_by_index():     
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    
    assert ledger.issuer(acc1) == neil
    
def test_retrieve_holder_by_index():     
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    
    assert ledger.holder(acc1) == andy
    
def test_deposit_ledger_credit():    
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.credit(acc1, 39)
    
    assert ledger.get(acc1).value == 139
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
   
def test_deposit_ledger_credit_invalid_accout():    
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    with pytest.raises(TypeError):
        ledger.credit(40, 39)
    
    with pytest.raises(TypeError):
        ledger.credit('andy', 39)
    
def test_deposit_ledger_debit():    
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.debit(acc2, 23)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 27
    assert ledger.get(acc3).value == 20

def test_deposit_ledger_debit_overdraft():   
    # Overdraft constraints to reside on DepositIssuer role
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.debit(acc2, 1000)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == -950
    assert ledger.get(acc3).value == 20
   
def test_deposit_ledger_credit_invalid_accout():    
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    with pytest.raises(ValueError):
        ledger.debit(12, 1000)
    
    with pytest.raises(ValueError):
        ledger.debit('andy', 39)
       
def test_deposit_ledger_transfer():
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.transfer(acc2, acc1, 5)
    
    assert ledger.get(acc1).value == 105
    assert ledger.get(acc2).value == 45
    assert ledger.get(acc3).value == 20

def test_deposit_ledger_transfer_overdraft():
    # Overdraft constraints to reside on DepositIssuer role
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.transfer(acc2, acc1, 450)
    
    assert ledger.get(acc1).value == 550
    assert ledger.get(acc2).value == -400
    assert ledger.get(acc3).value == 20
    
def test_deposit_ledger_transfer_invalid_sender():    
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    with pytest.raises(TypeError):
        ledger.transfer(12, 2, 1000)
    
    with pytest.raises(TypeError):
        ledger.debit('andy', 2, 39)

def test_deposit_ledger_transfer_invalid_recipient():    
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    with pytest.raises(TypeError):
        ledger.transfer(1, 12, 1000)
    
    with pytest.raises(TypeError):
        ledger.debit(1, 'andy', 39)

def test_deposit_ledger_transfer_invalid_sender_and_recipient():    
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100)
    acc2 = ledger.create(andy, rich, 50)
    acc3 = ledger.create(rich, andy, 20)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    with pytest.raises(TypeError):
        ledger.transfer(45, 12, 1000)
    
    with pytest.raises(TypeError):
        ledger.debit(18, 'andy', 39)
    
def test_deposit_ledger_apply_interest():       
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1)
    acc2 = ledger.create(andy, rich,  50, 2)
    acc3 = ledger.create(rich, andy,  20, 3)
    
    assert ledger.get(acc1).value == 100
    assert ledger.get(acc2).value == 50
    assert ledger.get(acc3).value == 20
    
    ledger.apply_daily_interest()
    
    assert ledger.get(acc1).value == 100 * (1 + ((1/100)/252))
    assert ledger.get(acc2).value == 50 * (1 + ((2/100)/252))
    assert ledger.get(acc3).value == 20 * (1 + ((3/100)/252))
        
def test_get_records_by_holder():          
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1)
    acc2 = ledger.create(andy, rich,  50, 2)
    acc3 = ledger.create(rich, andy,  20, 3)
    
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
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1)
    acc2 = ledger.create(neil, rich,  50, 2)
    acc3 = ledger.create(rich, andy,  20, 3)
    
    records = ledger.records_by_issuer(neil)
    assert len(records) == 2
    assert records.value.sum() == 150
    
    records = ledger.records_by_issuer(rich)    
    assert len(records) == 1
    assert records.value.sum() == 20
    
    records = ledger.records_by_issuer(andy)
    assert len(records) == 0
    assert records.value.sum() == 0
    
def test_update_interest_rate_by_issuer():
    ledger = DepositLedger(model)    
    acc1 = ledger.create(neil, andy, 100, 1)
    acc2 = ledger.create(neil, rich,  50, 2)
    acc3 = ledger.create(rich, andy,  20, 3)
    
    records = ledger.records_by_issuer(neil)
    
    assert records.loc[0].interest_rate == 1
    assert records.loc[1].interest_rate == 2
    
    ledger.update_interest_rate_by_issuer(neil, 5)
    
    records = ledger.records_by_issuer(neil)
    
    assert records.loc[0].interest_rate == 5
    assert records.loc[1].interest_rate == 5
    