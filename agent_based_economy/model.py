# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 15:31:16 2022

@author: andre
"""

import numpy as np
import pandas as pd
import objgraph
import time
from typing import List, Tuple
# from mesa import Model as MesaModel
# from mesa.datacollection import DataCollector
import random
from agent_based_economy.ledgers import DepositLedger, LoanLedger, BondLedger#, TaxLedger, StockLedger
from agent_based_economy.agents.household import Household#, HouseholdConfig
from agent_based_economy.agents.firm  import Firm#, FirmConfig
from agent_based_economy.agents.banks import CommercialBank, CentralBank
from agent_based_economy.agents.government import Government
from agent_based_economy.agents.stock_registrar import StockRegistrar
from agent_based_economy.markets import InterBankMarket, BondExchange

class Model():
    """
    A Baseline Agent-Based Macroeconomic Model
    which replicates the model described in:
    Lengnick, Matthias. (2013). Agent-based macroeconomics: A
    baseline model. Journal of Economic Behavior & Organization.
    86.10.1016/j.jebo.2012.12.021.
    This version follows the paper as closely as possible
    """

    __slots__ = ('counter','schedule','poverty_level','labour_supply',
                 'deposit_ledger','loan_ledger','bond_ledger',
                 'government','central_bank','banks','firms','households', 
                 'interbank_market', 'bond_exchange', 'datacollector', 'stock_registrar', 'real')
    
    def __init__(self, num_households=1000, num_firms=50, num_banks=5, 
                 firm_goods_price=Firm.initial_goods_price, # per unit
                 firm_wage_rate=Firm.initial_wage_rate,     # per month
                 seed=None, days_in_month=21, real=True, model_reporters=None) -> None:
        
        self.counter = int(0)
        self.real = real
        
        # Set up the scheduler from the model        
        self.schedule = Scheduler(self, days_in_month=days_in_month)
        self.poverty_level = 1
        self.labour_supply = 1
        
        # Set up ledgers for assets/liabilities
        self.deposit_ledger   = DepositLedger(self)
        self.loan_ledger      = LoanLedger(self)
        self.bond_ledger      = BondLedger(self)
        
        # Set up main institutions
        self.government   = Government(self)
        self.central_bank = CentralBank(self)        
        self.banks        = [CommercialBank(self) for i in range(num_banks)]
        
        self.government.open_deposit_account(self.central_bank, overdraft=np.inf)
        self.government.open_borrowing_account(self.central_bank)
        [bank.register_with_central_bank(overdraft=np.inf) for bank in self.banks]
        self.interbank_market = InterBankMarket(self)
        self.bond_exchange = BondExchange(self)
        
        firm_wage_rate  = firm_wage_rate # per month
        self.firms      = [Firm(self, firm_goods_price, firm_wage_rate) for i in range(num_firms)]
        self.households = [Household(self) for i in range(num_households)]
        

        # Needs to be initialised after the households
        self.stock_registrar = StockRegistrar(self)
        self.stock_registrar.open_deposit_account(self.banks[0], overdraft=0)
        
        self.datacollector = DataCollector(self,
            model_reporters=model_reporters,
        )
        
    def next_id(self) -> str:
        this_id = self.counter
        self.counter += 1
        return this_id
    
    @property
    def num_firms(self) -> int:
        """
        The number of firms in the model
        """
        return len(self.firms)

    @property
    def num_households(self) -> int:
        """
        The number of households in the model
        """
        return len(self.households)
    
    @property
    def num_banks(self) -> int:
        """
        The number of households in the model
        """
        return len(self.banks)
    
    def randomly_allocate_banks(self, agents) -> None:
        [agent.open_deposit_account(random.choice(self.banks)) for agent in agents]

    def government_helicopter_drop(self, agents, value_per_agent) -> None:
        [self.government.pay(agent.deposit_account_number, value_per_agent) for agent in agents]
        
    def shuffle_households(self):
        random.shuffle(self.households)
        
    def calculate_shareholdings(self) -> (List[Tuple], int):
        """
        Calculate the 'shareholding' of firms based upon the current
        liquidty of the households.
        Return a tuple containing a list of holders and their imputed holding,
        and a total value for the holding.
        Each firm then distributes their profits to households proportinal
        to the holdings in this list
        """
        shareholding = [(o, o.deposit_balance) for o in self.households]
        return (shareholding, sum([x[1] for x in shareholding]))
        
    def step(self, output_frequency='m', save_output=False, file_name=None) -> None:
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.schedule.step()
    
        if save_output:
            if output_frequency == 'm':
                if self.schedule.is_month_start():
                    self.datacollector.collect(self.schedule.day)
            elif output_frequency == 'd':
                self.datacollector.collect(self.schedule.day)
                
            if self.schedule.is_month_start() and file_name is not None:
                self.datacollector.df.to_csv(file_name, sep=',')
            
class DataCollector:
    
    __slots__ = ('model', 'model_reporters', 'keys', 'df')
    
    def __init__(self,model, model_reporters={}):
        self.model = model
        self.model_reporters = model_reporters or default_model_reporters
        self.df = pd.DataFrame(columns=self.model_reporters.keys())
        self.keys = list(self.model_reporters.keys())
    
    def collect(self, index):        
        for key in self.model_reporters.keys():
            self.df.at[index, key] = self.model_reporters[key](self.model)
             
class Scheduler:
    """
    Bespoke scheduler to run the Baseline Economy by Class and Step
    according to the precise ordering in the paper.
    """
    
    __slots__ = ('model', 'days_in_month', 'steps')

    def __init__(self, model, days_in_month=21) -> None:
        """
        Initialise the scheduler with a reference to the model
        """
        # Instance variables
        self.model = model
        self.days_in_month = np.round(days_in_month).astype(int)
        self.steps = 0
    
    @property
    def days_in_year(self):
        return self.days_in_month*12
    
    @property
    def day(self):
         return self.steps
     
    @property
    def month(self):
         return int(np.floor(self.year_day/self.days_in_month))
    
    @property
    def year(self):
         return int(np.floor(self.day/self.days_in_year))
         
    @property
    def year_day(self):
         return int(self.day%self.days_in_year)
     
    @property
    def month_day(self):
         return int(self.day%self.days_in_month)
     
    @property
    def start_of_this_year(self):
         return int(self.year*self.days_in_year)
     
    @property
    def start_of_this_month(self):
         return int(self.start_of_this_year + self.month*self.days_in_month)
     
    @property
    def start_of_next_year(self):
         return int(self.start_of_this_year + self.days_in_year)
     
    @property
    def end_of_this_year(self):
         return int(self.start_of_next_year - 1)
     
    @property
    def end_of_this_month(self):
         return int(self.start_of_this_month + self.days_in_month - 1)
     
    def is_month_start(self) -> bool:
        """
        Are we at the start of a month?
        Day 1, 22, 43, etc.
        """
        return self.steps % self.days_in_month == 0

    def is_month_end(self) -> bool:
        """
        Are we at the end of a month?
        Day 0, 21, 42, etc.
        """
        return (self.steps+1) % self.days_in_month == 0

    def step(self) -> None:
        
        # Pay daily deposit interest 
        self.model.deposit_ledger.apply_daily_interest(issuer=self.model.central_bank)
        
        for bb in self.model.banks:
            self.model.deposit_ledger.apply_daily_interest(issuer=bb)
        
        # Apply daily loan interest
        self.model.loan_ledger.apply_daily_interest()
        
        # repay interbank loan (with loan increment)
        due_loans = self.model.loan_ledger.loans_due()
        if len(due_loans) != 0:
            for idx, loan in self.model.loan_ledger.df.loc[due_loans].iterrows():
                print(f'REPAY LOAN {loan.value}')
                loan.issuer.make_loan_repayment(loan.value, account_number=idx)
        
        # Pay bond coupons
        # Coupons are 2 yearly so this is a function of date and year length
        if self.model.bond_ledger.coupon_due():
            print('PAYING COUPONS...')
            for idx, bond in self.model.bond_ledger.df.iterrows():
                if bond.issue_date != self.model.schedule.day:
                    coupon_value = bond.value*(bond.interest_rate/self.model.bond_ledger.annual_coupon_frequency)/100.0
                    bond.issuer.pay(bond.holder.deposit_account_number, coupon_value)
        
        # maturing bonds
        maturing_bonds = self.model.bond_ledger.bonds_maturing()
        if len(maturing_bonds) != 0:
            print(f'REPAYING MATURING BOND PRINCIPAL...')
            for idx, bond in self.model.bond_ledger.df.loc[maturing_bonds].iterrows():
                if bond.issuer != bond.holder:
                    bond.issuer.buy_bond(bond.holder, bond.value, idx)
                bond.issuer.close_bond(idx)
        
        # revalue bonds
        self.model.bond_ledger.recalculate()

        if self.model.real:
            # Shuffle the household list once per step
            # self.model.random.shuffle(self.households)
            self.model.shuffle_households()
            
            # Beginning of a month
            # Firms first
            if self.is_month_start():     
                for firm in self.model.firms:
                    firm.month_start()
                for household in self.model.households:
                    household.month_start()
           
            # Lapse of a day
            # Households first  
            for hh in self.model.households:
                hh.day()
            for firm in self.model.firms:
                firm.day()
                
            # End of a month
            # Firms first
            if self.is_month_end():
                # Pay Wages                         
                for firm in self.model.firms:
                    firm.month_end()
                    
                # Calculate householder shareholdings
                shareholder_details = self.model.calculate_shareholdings()
                # Distribute Profits
                for firm in self.model.firms:
                    firm.distribute_profits(*shareholder_details)  
                
                self.model.stock_registrar.pay_dividends()
                
                for hh in self.model.households:
                    hh.month_end()
        
        # Close of business inter bank market
        
        self.model.central_bank.open_standing_lending_facility()
        
        for bank in self.model.banks:
            if bank.deposit_balance < 0:
                # Seek interbank loan
                # Use the central bank lending rate for now
                # Eventually central bank lending rate should functions as the ceiling 
                # on some other rate determining logic on the part of the borrow
                self.model.interbank_market.register_interest(bank,  np.abs(bank.deposit_balance), self.model.central_bank.loan_interest_rate)
            elif bank.deposit_balance > 0:
                # Offer is at central bank policy rate for now
                # Eventually bank policy rate should be floor on some other rate setting logic on
                # the part of the lender
                # How about a unform probability over the central bank's spread range
                # Or maybe it could reference market rate frm yesterday's interbank market?
                offered_rate = self.model.central_bank.deposit_interest_rate #+ np.random.rand()*self.model.central_bank.interest_rate_spread
                self.model.interbank_market.register_offer(bank, bank.deposit_balance, offered_rate)
        
        self.model.interbank_market.clear_market()
        self.model.interbank_market.close_market() # this remove all offers and bids
        
        self.steps += 1
        
# # FUNCTIONS
        
def count_poverty(model) -> int:
    """
    Number of households employed
    """
    return sum(
        [hh.poverty for hh in model.households]
    )


def count_employed(model) -> int:
    """
    Number of households employed
    """
    return sum(
        [hh.employer is not None for hh in model.households]
    )


def count_notice(model) -> int:
    """
    Number of firms with worker on notice
    """
    return sum(
        [f.worker_on_notice is not None for f in model.firms]
    )


def sum_expected_demand(model) -> float:
    """
    Total expected demand over month
    """
    return sum([hh.current_demand for hh in model.households]) * model.schedule.days_in_month


def percent_unsatisfied_demand(model) -> float:
    """
    percentage of unsatisfied demand over expected demand
    """
    try:
        return (
            sum([hh.unsatisfied_demand for hh in model.households]) * 100
            / sum_expected_demand(model)
        )
    except ZeroDivisionError:
        return 0


def compute_gini(model) -> float:
    """
    Calculate the gini coefficient based upon household liquidity
    """
    try:
        x = sorted([hh.deposit_balance for hh in model.households])
        N = len(x)
        B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
        return 1 + (1 / N) - 2 * B
    except ZeroDivisionError:
        return 0


def sum_hh_saving(model) -> float:
    """
    How much money households expect to save
    """
    return sum([hh.planned_saving for hh in model.households])


def sum_hh_liquidity(model) -> int:
    """
    How much money households have
    """
    return sum([hh.deposit_balance for hh in model.households])


def sum_firm_liquidity(model) -> int:
    """
    How much money firms have
    """
    return sum([firm.deposit_balance for firm in model.firms])


def sum_liquidity(model) -> int:
    """
    How much money is in the system
    """
    return sum_firm_liquidity(model) + sum_hh_liquidity(model)


def sum_inventory(model) -> int:
    """
    Total stock in hand
    """
    return sum(
        [f.inventory for f in model.firms]
    )


def average_goods_price(model) -> float:
    """
    Average price of goods
    """
    prices = [f.goods_price for f in model.firms]
    return sum(prices) / len(prices)


def average_wage_rate(model) -> float:
    """
    Average wage rate
    """
    wage_rates = [f.wage_rate for f in model.firms]
    return sum(wage_rates) / len(wage_rates) / model.schedule.days_in_month

def model_date(model) -> float:
    """
    Output the model date to the data collector
    """
    return model.schedule.steps

default_model_reporters={
    "Employed": count_employed,
    "On Notice": count_notice,
    "Poverty Level": count_poverty,
    "Inventory": sum_inventory,
    "Price": average_goods_price,
    "Wage": average_wage_rate,
    "Household planned saving": sum_hh_saving,
    "Gini": compute_gini,
}

