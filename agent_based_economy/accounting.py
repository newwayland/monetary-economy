# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 08:23:07 2023

@author: andre
"""

import numpy as np
import pandas as pd
from tabulate import tabulate

class BalanceSheet:
    
    @staticmethod
    def consolidated_balance_sheet(agents, descriptor='', **kwargs):        
        all_assets_df = pd.DataFrame()
        for agent in agents:
            all_assets_df = pd.concat([all_assets_df, pd.DataFrame(agent.assets_dict(except_counterparties=agents), index=[id(agent)])])
        
        
        all_liabilities_df = pd.DataFrame()
        for agent in agents:
            all_liabilities_df = pd.concat([all_liabilities_df, pd.DataFrame(agent.liabilities_dict(except_counterparties=agents), index=[id(agent)])])
            
        all_assets_dict = {}
        all_liabilities_dict = {}
        
        for col in all_assets_df.columns:
            all_assets_dict[col] = all_assets_df[col].sum()
        
        for col in all_liabilities_df.columns:
            all_liabilities_dict[col] = all_liabilities_df[col].sum()
            
        return BalanceSheet(all_assets_dict, all_liabilities_dict, descriptor, **kwargs)
    
    def from_owner(owner, **kwargs):        
        assets      = owner.assets_dict()
        liabilities = owner.liabilities_dict()
        descriptor  = f'{owner.__class__.__name__}: {id(owner)}'
        
        return BalanceSheet(assets, liabilities, descriptor, **kwargs)
        
    def __init__(self, assets_dict, liabilities_dict, descriptor='', table_fmt='fancy_grid', 
                 show_equity=True, show_sum=True, show_meta=True, pad_table=True):
        '''
        table_fmt: "plain", "simple", "github", "grid", "simple_grid", "rounded_grid", "heavy_grid"
                   "mixed_grid", "double_grid", "fancy_grid", "outline", "simple_outline", "rounded_outline"
                   "heavy_outline", "mixed_outline", "double_outline", "fancy_outline", "pipe", "orgtbl", 
                   "asciidoc", "jira", "presto", "pretty", "psql", "rst", "mediawiki", "moinmoin", "youtrack", 
                   "html", "unsafehtml", "latex", "latex_raw", "latex_booktabs", "latex_longtable", "textile",
                   "tsv" (https://pypi.org/project/tabulate/)

        '''
        self.descriptor  = descriptor
        self.assets      = assets_dict
        self.liabilities = liabilities_dict
        self.show_equity = show_equity 
        self.show_sum    = show_sum 
        self.show_meta   = show_meta 
        self.table_fmt   = table_fmt
        self.pad_table   = pad_table
        
    @property
    def total_assets(self):
        return np.round(np.sum([*self.assets.values()]),2)
    
    @property
    def total_liabilities(self):
        return np.round(np.sum([*self.liabilities.values()]),2)
    
    @property
    def equity(self):
        return np.round(self.total_assets-self.total_liabilities,2)
    
    def to_dict(self, show_equity=True): 
        balance_sheet = {}
        balance_sheet['assets'] = {}      
        balance_sheet['assets']['items'] = self.assets.copy()
        balance_sheet['assets']['sum']   = self.total_assets
        
        balance_sheet['liabilities'] = {}  
        balance_sheet['liabilities']['items'] = self.liabilities.copy()
        
        if self.show_equity | show_equity:              
            equity = self.equity
            balance_sheet['liabilities']['items']['equity'] = equity 
            balance_sheet['liabilities']['sum']   = self.total_liabilities  + equity
        else:
            balance_sheet['liabilities']['sum']   = self.total_liabilities 
        
        return balance_sheet
    
    def __str__(self):
        balance_sheet_dict = self.to_dict(show_equity=self.show_equity)
        
        asset_labels     = [*balance_sheet_dict['assets']['items'].keys()]
        asset_values     = [*balance_sheet_dict['assets']['items'].values()]
        liability_labels = [*balance_sheet_dict['liabilities']['items'].keys()]
        liability_values = [*balance_sheet_dict['liabilities']['items'].values()]
        
        table = list()
        
        for i in np.arange(np.max([len(asset_labels), len(liability_labels)])):
            asset_label     = asset_labels[i]     if i < len(asset_labels)     else ''
            asset_value     = asset_values[i]     if i < len(asset_values)     else ''
            liability_label = liability_labels[i] if i < len(liability_labels) else ''
            liability_value = liability_values[i] if i < len(liability_values) else ''
            
            table.append([asset_label, asset_value, liability_label, liability_value])
        
        if self.show_sum:    
            table.append(['','','',''])
            table.append(['Sum', balance_sheet_dict['assets']['sum'], 
                          '',    balance_sheet_dict['liabilities']['sum']])

        table_string = tabulate(table, 
                                headers  = ['Assets','Value','Liabilities','Value'], 
                                tablefmt = self.table_fmt, 
                                floatfmt = ".2f",
                                colalign = ['right','decimal','right','decimal'])
        
        if self.show_meta:            
            table_string = self.descriptor+'\n'+table_string
        
        if self.pad_table:
            table_string = '\n'+table_string+'\n'  
            
        return table_string
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        