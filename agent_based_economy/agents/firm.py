# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 15:33:59 2023

@author: andre
"""

import random 
from random import Random
import numpy as np
import math
from typing import List, Tuple
from agent_based_economy.agents.agent import Agent
from agent_based_economy.agents.roles import DepositHolder, Lender, Borrower, BondHolder
from agent_based_economy.utils import floor_with_precision, ceil_with_precision

# CONFIG

# class FirmConfig:
#     """
#     Calibration Settings for the Firm Agent
#     """

#     # Amount of liquidity assigned to each firm at t=0
#     # Value not stated in paper
#     initial_liquidity = 0

#     # Price of goods at each firm at t=0
#     # Required due to Eq (10)
#     # Value not stated in paper
#     initial_goods_price = 27

#     # Amount of inventory in each firm at t=0
#     # Value not stated in paper
#     initial_inventory = 0

#     # Initial wage rate at t=0
#     # Required due to Eq (5)
#     # Value not stated in paper
#     initial_wage_rate = 70 * 21

#     # The expected demand for goods per month
#     # Required due to Eq (6) and Eq (7)
#     # Value not stated in paper
#     expected_demand = 1

#     # Calibration values (Table 1)
#     #
#     # Number of months of filled positions
#     # before wage will be reduced
#     gamma = 24

#     # Upper bound for the wage adjustment
#     delta = 0.019

#     # Range that inventories can be maintained
#     # relative to demand
#     inventory_uphi = 1
#     inventory_lphi = 0.25

#     # Range that prices can be marked up over
#     # costs
#     goods_price_uphi = 1.15
#     goods_price_lphi = 1.025

#     # Upper bound for the price adjustment
#     upsilon = 0.02

#     # Probability of changing the goods price
#     theta = 0.75

#     # Productivity multiple by which labour power
#     # is turned into labour output
#     # "Positive technology parameter"
#     lambda_val = 3

#     # Percentage of income to reserve to cover bad times
#     chi = 0.1

class Firm(Agent, DepositHolder):    
    
    """
    Firm Agent
    Variables:
        liquidity: amount of monetary units firm posseses
        goods_price: the price of each item in the inventory
        inventory: amount of goods on hand
        wage_rate: the price the firm will pay for labour power
    """
    
    """
    Calibration Settings for the Firm Agent
    """

    # Amount of liquidity assigned to each firm at t=0
    # Value not stated in paper
    initial_liquidity = 0

    # Price of goods at each firm at t=0
    # Required due to Eq (10)
    # Value not stated in paper
    initial_goods_price = 27

    # Amount of inventory in each firm at t=0
    # Value not stated in paper
    initial_inventory = 0

    # Initial wage rate at t=0
    # Required due to Eq (5)
    # Value not stated in paper
    initial_wage_rate = 70 * 21

    # The expected demand for goods per month
    # Required due to Eq (6) and Eq (7)
    # Value not stated in paper
    expected_demand = 1

    # Calibration values (Table 1)
    #
    # Number of months of filled positions
    # before wage will be reduced
    gamma = 24

    # Upper bound for the wage adjustment
    delta = 0.019

    # Range that inventories can be maintained
    # relative to demand
    inventory_uphi = 1
    inventory_lphi = 0.25

    # Range that prices can be marked up over
    # costs
    goods_price_uphi = 1.15
    goods_price_lphi = 1.025

    # Upper bound for the price adjustment
    upsilon = 0.02

    # Probability of changing the goods price
    theta = 0.75

    # Productivity multiple by which labour power
    # is turned into labour output
    # "Positive technology parameter"
    lambda_val = 3

    # Percentage of income to reserve to cover bad times
    chi = 0.1
    
    @classmethod
    def production_amount(cls, labour_power: int) -> int:
        """
        Amount of labour output per unit of labour power
        """
        return cls.lambda_val * labour_power

    @classmethod
    def wage_adjustment(cls, rand_generator: Random) -> float:
        """
        Delta percentage amount to change the wage up or down
        """
        return rand_generator.uniform(0, cls.delta)
    
    @classmethod
    def price_adjustment(cls, rand_generator: Random) -> float:
        """
        Delta percentage amount to change the price up or down
        """
        return rand_generator.uniform(0, cls.upsilon)
    
    __slots__ = ('model', 'unique_id', 'goods_price', 'inventory', 'current_demand', 
                 'wage_rate', 'worker_on_notice', 'workers', 'has_open_position', 
                 'months_since_hire_failure', 'marginal_cost_deflator', 'raised_wage', 
                 'lowered_wage', 'inventories_too_low', 'inventories_too_high', 
                 'worker_on_notice', 'considered_price_change', 'recent_demand', 
                 'current_marginal_cost', 'raised_goods_price', 'lowered_goods_price', 
                 'profit')
    
    def __init__(self, model, initial_goods_price: int, initial_wage_rate: int) -> None:
        """
        Customize the agent
        """
        super().__init__(model)      
        DepositHolder.__init__(self)  
        
        # Producer
        self.goods_price = initial_goods_price
        self.inventory = self.initial_inventory
        self.current_demand = self.expected_demand
        
        # Employer
        self.wage_rate = initial_wage_rate
        self.worker_on_notice = None
        self.workers = []
        self.has_open_position = False
        self.months_since_hire_failure = 0
        
        # Constants
        self.marginal_cost_deflator = (
            self.lambda_val *
            self.model.labour_supply *
            self.model.schedule.days_in_month
        )
        self.reset_monthly_stats()
        
    def month_start(self) -> None:
        """
        Run the month start firm procedures
        """
        self.reset_monthly_stats()
        self.set_wage_rate()
        self.manage_workforce()
        # Is the firm confident enough to change its price?
        if self.with_probability(self.theta):
            self.set_goods_price()
        # Reset monthly accumulators
        self.current_demand = 0

    def day(self) -> None:
        """
        Run the daily firm procedures
        """
        self.produce_output()

    def month_end(self) -> None:
        """
        Run the month end firm procedures
        """
        self.pay_wages()
        self.check_for_hire_failure()

# MONTH START

    def set_wage_rate(self) -> None:
        """
        Changes the wage rates up or down
        Rounds up to the nearest whole money unit on rising wage
        Rounds down to zero on falling wages (Interns)
        """
        if self.should_raise_wage():
            self.raised_wage = True
            self.wage_rate *= (1 + self.wage_adjustment(random))
            self.wage_rate = max(1, np.ceil(self.wage_rate))
        elif self.should_lower_wage():
            self.lowered_wage = True
            self.wage_rate *= (1 - self.wage_adjustment(random))
            self.wage_rate = np.floor(self.wage_rate) 

    def manage_workforce(self) -> None:
        """
        Deal with hiring and firing decisions
        """
        # If inventory is too high, either cancel outstanding notice
        # or offer a new position
        if self.inventory < self.inventory_floor():
            self.inventories_too_low = True
            self.has_open_position = self.worker_on_notice is None
            self.worker_on_notice = None

        # If a worker is on notice, fire them
        if self.worker_on_notice is not None:
            self.fire_worker()

        # Give notice to a worker if inventories are too high
        # Cancel any open position
        if self.inventory > self.inventory_ceiling():
            self.inventories_too_high = True
            self.has_open_position = False
            self.give_notice()

    def set_goods_price(self) -> None:
        """
        Adjust the price up if inventories are too low
        and down if inventories are too high
        """
        self.considered_price_change = (
            self.inventories_too_low |
            self.inventories_too_high
        )
        self.recent_demand = self.current_demand
        self.current_marginal_cost = self.marginal_cost()
        if (self.inventory < self.inventory_floor()) & \
                (self.goods_price <= self.goods_price_ceiling()): # parentheses added
            self.raised_goods_price = True
            self.goods_price *= (1 + self.price_adjustment(random))            
            self.goods_price = np.ceil(self.goods_price) 

        elif (self.inventory > self.inventory_ceiling()) & \
                (self.goods_price > self.goods_price_floor()): # parentheses added
            self.lowered_goods_price = True
            self.goods_price *= (1 - self.price_adjustment(random))
            self.goods_price = max(1, np.floor(self.goods_price))

# DAILY

    def produce_output(self) -> None:
        """
        Work out how much effort the firm can command and
        run it through the production process.
        Accumulate output in the firms inventory
        """
        labour_power = sum([o.labour_amount for o in self.workers])
        self.inventory += self.production_amount(labour_power)

# MONTH END

    def pay_wages(self) -> None:
        """
        Pay wages at the wage rate.
        If that is unaffordable, cut the wage rate to make
        it affordable
        """
        num_workers = len(self.workers)
        # Below a deminimis we can't pay anybody
        # Slash wages and try again next month
        if self.deposit_balance < num_workers:
            self.wage_rate = 0
            return
        if self.deposit_balance < num_workers * self.wage_rate:
            self.lowered_wage = True
            self.wage_rate = self.deposit_balance // num_workers
        
        for hh in self.workers:
            self.pay(hh.deposit_account_number, self.wage_rate)
        
    def distribute_profits(self,
                            shareholding: List[Tuple],
                            total_shares: int) -> None:
        """
        Distribute profits less a labour cost buffer
        to households
        """
        liquidity_buffer = self.calculate_required_buffer()
        self.profit = self.deposit_balance - liquidity_buffer
        
        if self.profit < 0:
            return
        
    #     self.distribute_to_households(
    #         self.profit,
    #         shareholding,
    #         total_shares
    #     )
    # def distribute_to_households(self,
    #                               profits: int,
    #                               shareholding: List[Tuple],
    #                               total_shares: int) -> int:
        """
        Distribute profits to households weighted by their current liquidity
        and rounded down to the nearest integer value
        Return the total amount distributed
        shareholding: list of tuples [(shareholder, holding), ...]
        """
        try:
            dividend_per_share = self.profit / total_shares
        except ZeroDivisionError:
            dividend_per_share = 0
            
        shareholder_dividend = np.floor(np.array([s[1] for s in shareholding]) * dividend_per_share)
        
        self.model.stock_registrar.update_ledger(shareholder_dividend)
        self.pay(self.model.stock_registrar.deposit_account_number, np.sum(shareholder_dividend))

    def check_for_hire_failure(self) -> None:
        """
        Accumulate the number of months since the firm failed to hire
        which feeds into the wage calculation
        """
        if self.has_open_position:
            self.months_since_hire_failure = 0
        else:
            self.months_since_hire_failure += 1

# HELPERS

    def reset_monthly_stats(self):
        """
        Reset the monthly recording attributes
        """
        self.raised_wage = False
        self.lowered_wage = False
        self.considered_price_change = False
        self.inventories_too_low = False
        self.inventories_too_high = False
        self.raised_goods_price = False
        self.lowered_goods_price = False

    def marginal_cost(self) -> float:
        """
        Calcluate the cost of producing one extra unit of
        output
        This should be linked to the labour supply somehow
        """
        return self.wage_rate / self.marginal_cost_deflator

    def goods_price_floor(self) -> float:
        """
        Calculate the lowest level of price relative to
        marginal costs the firm will accept
        """
        return self.goods_price_lphi * self.marginal_cost()

    def goods_price_ceiling(self) -> float:
        """
        Calculate the highest level of price relative to
        marginal costs the firm will accept
        """
        return self.goods_price_uphi * self.marginal_cost()

    def inventory_floor(self) -> float:
        """
        Calculate the lowest level of inventory the firm
        requires
        """
        return self.inventory_lphi * self.current_demand

    def inventory_ceiling(self) -> float:
        """
        Calculate the highest level of inventory the firm
        will accept
        """
        return self.inventory_uphi * self.current_demand

    def give_notice(self) -> None:
        """
        Pick a worker and give them notice
        """
        try:
            self.worker_on_notice = random.choice(self.workers)
        except IndexError:
            # Empty list
            pass

    def fire_worker(self) -> None:
        """
        P45 time
        """
        self.quit_job(self.worker_on_notice)
        self.worker_on_notice = None

    def quit_job(self, worker) -> None:
        """
        Clear up when a worker leaves the firm
        """
        if self.worker_on_notice == worker:
            self.worker_on_notice = None
        self.workers.remove(worker)
        worker.employer = None

    def hire(self, worker) -> None:
        """
        Add worker to the list of current employees
        """
        self.workers.append(worker)
        worker.employer = self
        self.has_open_position = False

    def sell_goods(self, quantity, total_price) -> None:
        """
        Update inventory and demand
        then bank the cash
        """
        self.inventory -= quantity
        self.current_demand += quantity

    def calculate_required_buffer(self) -> int:
        """
        The liquidity buffer is relative to labour costs
        Round up to ensure buffer is big enough
        """
        return math.ceil(self.chi * self.wage_rate * len(self.workers))

# QUERIES

    def should_raise_wage(self) -> bool:
        """
        Does the firm still have a position open
        and needs a better wage?
        """
        return self.has_open_position

    def should_lower_wage(self) -> bool:
        """
        Has the firm been continually successful in hiring
        and can drop its wage rate
        """
        return self.months_since_hire_failure >= self.gamma
