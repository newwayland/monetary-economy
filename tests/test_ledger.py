# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 18:34:16 2022

@author: ABE
"""


import pytest
import pandas as pd
import numpy as np
from agent_based_economy.ledgers import Ledger, DepositLedger, BondLedger, LoanLedger
from agent_based_economy.model import Model
from agent_based_economy.agents.agent import Agent

model = Model()
neil  = Agent(model)
andy  = Agent(model)
rich  = Agent(model)
   
def test_basic_properties():
    ledger = Ledger(model)
    assert isinstance(ledger,Ledger) == True
    assert isinstance(ledger.df, pd.DataFrame) == True
    assert isinstance(ledger.model,Model) == True
    assert isinstance(ledger.counter,int) == True
    
def test_ledger_next_id():
    ledger = Ledger(model)
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
    
def test_ledger_create():
    ledger = Ledger(model)
    assert len(ledger) == 0
    
    acc = ledger.create(issuer=neil, holder=andy, value=100)
    assert len(ledger) == 1
    assert acc == 0
    
    acc = ledger.create(issuer=andy, holder=rich, value=50)
    assert len(ledger) == 2
    assert acc == 1
    
    acc = ledger.create(issuer=rich, holder=andy, value=20)
    assert len(ledger) == 3
    assert acc == 2

def test_ledger_drop():
    ledger = Ledger(model)
    
    acc = ledger.create(issuer=neil, holder=andy, value=100)
    acc = ledger.create(issuer=andy, holder=rich, value=50)
    acc = ledger.create(issuer=rich, holder=andy, value=20)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.drop(1)
    assert success == True
    assert len(ledger) == 2
    assert (ledger.df.index == [0,2]).all()

def test_ledger_drop_invalid_index():
    ledger = Ledger(model)
    
    acc = ledger.create(issuer=neil, holder=andy, value=100)
    acc = ledger.create(issuer=andy, holder=rich, value=50)
    acc = ledger.create(issuer=rich, holder=andy, value=20)
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
    success = ledger.drop(10)
    assert success == False
    assert len(ledger) == 3
    assert (ledger.df.index == [0,1,2]).all()
    
def test_ledger_get_record():
    ledger = Ledger(model)    
    acc1 = ledger.create(issuer=neil, holder=andy, value=100)
    acc2 = ledger.create(issuer=andy, holder=rich, value=50)
    acc3 = ledger.create(issuer=rich, holder=andy, value=20)
    
    rec1 = ledger.get(acc1)
    assert rec1['issuer'] == neil
    assert rec1['holder'] == andy
    assert rec1['value'] == 100
    
    rec3 = ledger.get(acc3)
    assert rec3['issuer'] == rich
    assert rec3['holder'] == andy
    assert rec3['value']  == 20
    
def test_ledger_defaults():    
    ledger = Ledger(model)    
    acc1 = ledger.create(issuer=neil, holder=andy, value=100)
    
    rec1 = ledger.get(acc1)
    assert np.isnan(rec1['interest_rate']) == True
    
def test_ledger_options():   
    ledger = Ledger(model)    
    acc1 = ledger.create(issuer=neil, holder=andy, value=100,
                         interest_rate=2)
    
    rec1 = ledger.get(acc1)
    assert rec1['interest_rate'] == 2
    
    
    
# def test_ledger_init():
#     L = Ledger(A1)
#     assert isinstance(A1,Agent) == True
#     assert isinstance(L,Ledger) == True
#     assert L.counter == 0
#     assert L.columns == ['unique_id','holder','value', 'interest_rate', 
#                          'interest_frequency', 'interest_day']
#     assert isinstance(L.df, DataFrame)
#     assert L.df.shape == (0,6)
#     assert L.df.columns.get_loc('unique_id') == 0
#     assert L.df.columns.get_loc('value') == 2
#     assert L.df.columns.get_loc('interest_day') == 5
  
# def test_ledger_generate_unique_id():
#     L = Ledger(A1)
#     assert L.generate_unique_id() == str(0)
#     assert L.generate_unique_id() == str(1)
#     assert L.generate_unique_id() == str(2)
#     assert L.generate_unique_id() == str(3)

# def test_ledger_create_empty():
#     L = Ledger(A1)
#     assert L.counter == 0
#     assert L.df.shape == (0,6)    
#     ref = L.create()
#     assert L.counter == 1
#     assert L.df.shape == (1,6)
#     assert ref == str(0)
#     assert L.df.iloc[0,0] == str(0)
#     assert np.isnan(L.df.iloc[0,1]) == True
#     assert np.isnan(L.df.iloc[0,2]) == True
#     assert np.isnan(L.df.iloc[0,3]) == True
#     assert np.isnan(L.df.iloc[0,4]) == True
#     assert np.isnan(L.df.iloc[0,5]) == True

# def test_ledger_create():
#     L = Ledger(A1)
#     assert L.counter == 0
#     assert L.df.shape == (0,6)    
#     ref = L.create(holder=A2,value=100, interest_rate=2)
#     assert L.counter == 1
#     assert L.df.shape == (1,6)
#     assert ref == str(0)
#     assert L.df.iloc[0,0] == ref
#     assert L.df.iloc[0,1] == A2
#     assert L.df.iloc[0,2] == 100
#     assert L.df.iloc[0,3] == 2
#     assert np.isnan(L.df.iloc[0,4]) == True
#     assert np.isnan(L.df.iloc[0,5]) == True
    
# def test_ledger_create_multiple():
#     L = Ledger(A1)
#     assert L.counter == 0
#     assert L.df.shape == (0,6)    
#     ref = L.create(holder=A2,value=100, interest_rate=2)
#     ref = L.create(holder=A2,value=50,  interest_rate=2)
#     ref = L.create(holder=A2,value=25,  interest_rate=5)
#     ref = L.create(holder=A2,value=10,  interest_rate=5)
#     assert L.counter == 4
#     assert L.df.shape == (4,6)
#     assert ref == str(3)
#     assert L.df.iloc[0]['value'] == 100
#     assert L.df.iloc[2]['value'] == 25
#     assert L.df.iloc[1]['interest_rate'] == 2
#     assert L.df.iloc[3]['interest_rate'] == 5
  
# def get_ledger_idx_from_id():
#     L = Ledger(A1)
#     assert L.counter == 0
#     assert L.df.shape == (0,6)      
#     L.create(holder=A2,value=100, interest_rate=2)
#     L.create(holder=A2,value=50,  interest_rate=2)
#     L.create(holder=A2,value=25,  interest_rate=5)
#     L.create(holder=A2,value=10,  interest_rate=5)
#     assert L.get_idx_from_id('0') == 0
#     assert L.get_idx_from_id('1') == 1
#     assert L.get_idx_from_id('2') == 2
#     assert L.get_idx_from_id('3') == 3
    
# def test_ledger_drop():
#     L = Ledger(A1)
#     assert L.counter == 0
#     assert L.df.shape == (0,6)      
#     L.create(holder=A2,value=100, interest_rate=2)
#     L.create(holder=A2,value=50,  interest_rate=2)
#     L.create(holder=A2,value=25,  interest_rate=5)
#     L.create(holder=A2,value=10,  interest_rate=5)
#     assert L.counter == 4
#     assert L.df.shape == (4,6)
#     assert L.df.iloc[0]['value'] == 100
#     assert L.df.iloc[1]['value'] == 50
#     assert L.df.iloc[2]['value'] == 25
#     L.drop('1')    
#     assert L.counter == 4
#     assert L.df.shape == (3,6)
#     assert L.df.iloc[0]['value'] == 100
#     assert L.df.iloc[1]['value'] == 25
#     assert L.df.iloc[2]['value'] == 10
    
# def test_ledger_get():    
#     L = Ledger(A1)
#     assert L.counter == 0
#     assert L.df.shape == (0,6)      
#     L.create(holder=A2,value=100, interest_rate=2)
#     record = L.get('0')
#     assert isinstance(record, DataFrame)
#     assert record.iloc[0]['holder'] == A2
#     assert record.iloc[0]['value'] == 100
#     assert record.iloc[0]['interest_rate'] == 2
    
# #%%

# def test_advance_ledger_init():
#     AL = AdvanceLedger(A1)
#     assert isinstance(A1,Agent) == True
#     assert isinstance(AL,Ledger) == True
#     assert isinstance(AL,AdvanceLedger) == True
#     assert AL.counter == 0
#     assert AL.columns == ['unique_id','holder','value', 'interest_rate', 
#                          'interest_frequency', 'interest_day', 'overdraft']
#     assert isinstance(AL.df, DataFrame)
#     assert AL.df.shape == (0,7)
#     assert AL.df.columns.get_loc('unique_id') == 0
#     assert AL.df.columns.get_loc('value') == 2
#     assert AL.df.columns.get_loc('interest_day') == 5
#     assert AL.df.columns.get_loc('overdraft') == 6

# def test_advance_ledger_create_empty():
#     AL = AdvanceLedger(A1)
#     assert AL.counter == 0
#     assert AL.df.shape == (0,7)  
#     with pytest.raises(TypeError, match=re.escape("create() missing 3 required positional arguments: 'holder', 'value', and 'interest_rate'")):
#           AL.create()

# def test_advance_ledger_create_minimal():
#     AL = AdvanceLedger(A1)
#     assert AL.counter == 0
#     assert AL.df.shape == (0,7)    
#     ref = AL.create(A2,100,2) # default optional args
#     assert AL.counter == 1
#     assert AL.df.shape == (1,7)
#     assert ref == str(0)
#     assert AL.df.iloc[0,0] == ref
#     assert AL.df.iloc[0,1] == A2
#     assert AL.df.iloc[0,2] == 100
#     assert AL.df.iloc[0,3] == 2
#     assert AL.df.iloc[0,4] == 12
#     assert AL.df.iloc[0,5] == 1
#     assert AL.df.iloc[0,6] == 0
    
# def test_advance_ledger_create_specific():
#     AL = AdvanceLedger(A1)
#     assert AL.counter == 0
#     assert AL.df.shape == (0,7)    
#     ref = AL.create(A2,100,2, interest_frequency=365, interest_day=1, overdraft=500)
#     assert AL.counter == 1
#     assert AL.df.shape == (1,7)
#     assert ref == str(0)
#     assert AL.df.iloc[0,0] == ref
#     assert AL.df.iloc[0,1] == A2
#     assert AL.df.iloc[0,2] == 100
#     assert AL.df.iloc[0,3] == 2
#     assert AL.df.iloc[0,4] == 365
#     assert AL.df.iloc[0,5] == 1
#     assert AL.df.iloc[0,6] == 500
    
# #%%

# def test_bond_ledger_init():
#     BL = BondLedger(A1)
#     assert isinstance(A1,Agent) == True
#     assert isinstance(BL,Ledger) == True
#     assert isinstance(BL,BondLedger) == True
#     assert BL.counter == 0
#     assert BL.columns == ['unique_id','holder','value', 'interest_rate', 
#                          'interest_frequency', 'interest_day', 'issue_date',
#                          'maturity_date']
#     assert isinstance(BL.df, DataFrame)
#     assert BL.df.shape == (0,8)
#     assert BL.df.columns.get_loc('unique_id') == 0
#     assert BL.df.columns.get_loc('value') == 2
#     assert BL.df.columns.get_loc('interest_day') == 5
#     assert BL.df.columns.get_loc('issue_date') == 6

# def test_bond_ledger_create_empty():
#     BL = BondLedger(A1)
#     assert BL.counter == 0
#     assert BL.df.shape == (0,8)   
#     with pytest.raises(TypeError, match=re.escape("create() missing 2 required positional arguments: 'interest_rate' and 'maturity_date'")):
#           BL.create() 

# def test_bond_ledger_create():
#     BL = BondLedger(A1)
#     assert BL.counter == 0
#     assert BL.df.shape == (0,8)    
#     ref = BL.create(2,365) # default optional args
#     assert BL.counter == 1
#     assert BL.df.shape == (1,8)
#     assert ref == str(0)
#     assert BL.df.iloc[0,0] == ref
#     assert BL.df.iloc[0,1] == A1 # bonds owned by issuer at first
#     assert BL.df.iloc[0,2] == 100
#     assert BL.df.iloc[0,3] == 2
#     assert BL.df.iloc[0,4] == 2
#     assert BL.df.iloc[0,5] == 1
#     assert BL.df.iloc[0,6] == 0
#     assert BL.df.iloc[0,7] == 365
    
# def test_bond_ledger_transfer():
#     BL = BondLedger(A1)
#     assert BL.counter == 0
#     assert BL.df.shape == (0,8)    
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args
#     assert BL.counter == 4
#     assert BL.df.shape == (4,8)
#     assert BL.df.iloc[0,1] == A1 # bonds owned by issuer at first
#     assert BL.df.iloc[1,1] == A1 # bonds owned by issuer at first
#     assert BL.df.iloc[2,1] == A1 # bonds owned by issuer at first
#     assert BL.df.iloc[3,1] == A1 # bonds owned by issuer at first
#     BL.transfer('2', A2)
#     BL.transfer('3', A2)
#     assert BL.counter == 4
#     assert BL.df.shape == (4,8)
#     assert BL.df.iloc[0,1] == A1 
#     assert BL.df.iloc[1,1] == A1 
#     assert BL.df.iloc[2,1] == A2 
#     assert BL.df.iloc[3,1] == A2        
  
# def test_bonds_ledger_self_owned_idxs():    
#     BL = BondLedger(A1)  
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args
#     BL.transfer('0', A2)
#     BL.transfer('1', A2)
#     ref_idxs =  BL.self_owned_idxs()
#     assert len(ref_idxs) == 2
#     assert ref_idxs[0] == 2
#     assert ref_idxs[1] == 3

# def test_bonds_ledger_self_owned_ids():    
#     BL = BondLedger(A1)  
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args 
#     BL.create(2,365) # default optional args
#     BL.transfer('0', A2)
#     BL.transfer('1', A2)
#     ref_idxs =  BL.self_owned_ids()
#     assert len(ref_idxs) == 2
#     assert ref_idxs[0] == '2'
#     assert ref_idxs[1] == '3'
    
# def test_bond_ledger_close():
#     BL = BondLedger(A1)
#     assert len(BL.df) == 0      
#     BL.create(2,30)     
#     BL.create(2,90)     
#     BL.create(2,180)     
#     BL.create(2,365)
#     assert len(BL.df) == 4
#     ref_idxs =  BL.self_owned_ids()
#     assert len(ref_idxs) == 4
#     BL.transfer('0', A2)
#     BL.transfer('1', A2)
#     ref_idxs =  BL.self_owned_ids()
#     assert len(ref_idxs) == 2
#     success_or_failure = BL.close('0')
#     assert success_or_failure == False
#     success_or_failure = BL.close('1')
#     assert success_or_failure == False
#     success_or_failure = BL.close('2')
#     assert success_or_failure == True
#     success_or_failure = BL.close('3')
#     assert success_or_failure == True
#     assert len(BL.df) == 2
#     ref_idxs =  BL.self_owned_ids()
#     assert len(ref_idxs) == 0
#     assert BL.df.iloc[0]['unique_id'] == '0'
#     assert BL.df.iloc[1]['unique_id'] == '1'
    


    
# #%%

# # def test_pierson_moskowitz_values():
# #     assert 1 == pytest.approx(1.1573908, abs=0.0001)      # specified f x 2