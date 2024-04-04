# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 18:19:26 2023

@author: andre
"""


import pytest
import pandas as pd
import numpy as np
from agent_based_economy.model import Model
from agent_based_economy.agents.agent import Agent
from agent_based_economy.agents.individual import Individual
from agent_based_economy.agents.firm  import Firm
from agent_based_economy.agents.banks import CommercialBank, CentralBank, Bank
from agent_based_economy.agents.government import Government

model = Model()
   
def test_base_class_introspective_properties():
    agent = Agent(model)
    assert isinstance(agent,Agent) == True
    assert agent.is_bank == False
    assert agent.is_employable == False    
    assert agent.is_employer == False
    assert agent.is_firm == False
    assert agent.is_government == False
    assert agent.is_individual == False
    
def test_individual_introspective_properties():
    agent = Individual(model)
    assert isinstance(agent,Agent) == True
    assert isinstance(agent,Individual) == True
    assert agent.is_bank == False
    assert agent.is_employable == False    # not yet implemented
    assert agent.is_employer == False
    assert agent.is_firm == False
    assert agent.is_government == False
    assert agent.is_individual == True

def test_firm_introspective_properties():
    agent = Firm(model, 25, 68) # goods price, wage price
    assert isinstance(agent,Agent) == True
    assert isinstance(agent,Firm) == True
    assert agent.is_bank == False
    assert agent.is_employable == False
    assert agent.is_employer == False      # not yet implemented
    assert agent.is_firm == True
    assert agent.is_government == False
    assert agent.is_individual == False
    
def test_bank_introspective_properties():
    agent = Bank(model)
    assert isinstance(agent,Agent) == True
    assert isinstance(agent,Firm) == False # banks are not firms under this definition
    assert isinstance(agent,Bank) == True
    assert agent.is_bank == True
    assert agent.is_employable == False    
    assert agent.is_employer == False      # banks arent employers, maybe they should be
    assert agent.is_firm == False
    assert agent.is_government == False
    assert agent.is_individual == False
    assert agent.is_commercial == False
    assert agent.is_central == False
    
def test_commercial_bank_introspective_properties():
    agent = CommercialBank(model)
    assert isinstance(agent,Agent) == True
    assert isinstance(agent,CommercialBank) == True 
    assert isinstance(agent,Bank) == True
    assert agent.is_bank == True
    assert agent.is_employable == False    
    assert agent.is_employer == False      # banks arent employers, maybe they should be
    assert agent.is_firm == False
    assert agent.is_government == False
    assert agent.is_individual == False
    assert agent.is_commercial == True
    assert agent.is_central == False

def test_central_bank_introspective_properties():
    agent = CentralBank(model)
    assert isinstance(agent,Agent) == True
    assert isinstance(agent,CentralBank) == True 
    assert isinstance(agent,Bank) == True
    assert agent.is_bank == True
    assert agent.is_employable == False    
    assert agent.is_employer == False      # banks arent employers, maybe they should be
    assert agent.is_firm == False
    assert agent.is_government == False
    assert agent.is_individual == False
    assert agent.is_commercial == False
    assert agent.is_central == True
    
def test_government_introspective_properties():
    agent = Government(model)
    assert isinstance(agent,Agent) == True
    assert isinstance(agent,Government) == True 
    assert agent.is_bank == False
    assert agent.is_employable == False    
    assert agent.is_employer == False      # banks arent employers, maybe they should be
    assert agent.is_firm == False
    assert agent.is_government == True
    assert agent.is_individual == False
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    