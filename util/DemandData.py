# _*_ coding: utf-8 _*_
import xlrd
from cn.modelICE.Parameters import Parameters


class DemandData:
    def __init__(self):
        summer_ele_demand = xlrd.open_workbook(r'E:/pythonProject/model/resources/Summer_ele_demand.xlsx')
        winter_ele_demand = xlrd.open_workbook(r'E:/pythonProject/model/resources/Winter_ele_demand.xlsx')
        transition_ele_demand = xlrd.open_workbook(r'E:/pythonProject/model/resources/Transition_ele_demand.xlsx')
        winter_heat_demand = xlrd.open_workbook(r'E:/pythonProject/model/resources/Winter_heat_demand.xlsx')
        summer_cold_demand = xlrd.open_workbook(r'E:/pythonProject/model/resources/Summer_cold_demand.xlsx')

        summer_steam_demand = xlrd.open_workbook(r'E:/pythonProject/model/resources/Summer_steam_demand.xlsx')
        winter_steam_demand = xlrd.open_workbook(r'E:/pythonProject/model/resources/Winter_steam_demand.xlsx')
        transition_steam_demand = xlrd.open_workbook(r'E:/pythonProject/model/resources/Transition_steam_demand.xlsx')

        summer_e_sheet = summer_ele_demand.sheet_by_name('Sheet1')
        winter_e_sheet = winter_ele_demand.sheet_by_name('Sheet1')
        transition_e_sheet = transition_ele_demand.sheet_by_name('Sheet1')
        winter_h_sheet = winter_heat_demand.sheet_by_name('Sheet1')
        summer_c_sheet = summer_cold_demand.sheet_by_name('Sheet1')

        winter_steam_sheet = winter_steam_demand.sheet_by_name('Sheet1')
        summer_steam_sheet = summer_steam_demand.sheet_by_name('Sheet1')
        transition_steam_sheet = transition_steam_demand.sheet_by_name('Sheet1')

        self.E_sheetnrows = summer_e_sheet.nrows  # 行
        self.E_sheetncols = summer_e_sheet.ncols  # 列
        self.H_sheetnrows = winter_h_sheet.nrows
        self.H_sheetncols = winter_h_sheet.ncols
        self.C_sheetnrows = summer_c_sheet.nrows
        self.C_sheetncols = summer_c_sheet.ncols

        self.Steam_sheetnrows = summer_steam_sheet.nrows
        self.Steam_sheetncols = summer_steam_sheet.ncols

        self.cold_E = []
        self.heat_E = []
        self.transition_E = []
        self.H = []
        self.C = []

        self.cold_Steam = []
        self.heat_Steam = []
        self.transition_Steam = []

        for i in range(0, 24, 1):  # e_sheetnrows = h_sheetnrows = c_sheetnrows
            self.cold_E.append(summer_e_sheet.cell(i + 1, 2).value / Parameters.delttime)
            self.heat_E.append(winter_e_sheet.cell(i + 1, 2).value / Parameters.delttime)
            self.transition_E.append(transition_e_sheet.cell(i + 1, 2).value / Parameters.delttime)
            self.H.append(winter_h_sheet.cell(i + 1, 2).value / Parameters.delttime)
            self.C.append(summer_c_sheet.cell(i + 1, 2).value
                          / Parameters.delttime)

            self.cold_Steam.append(summer_steam_sheet.cell(i + 1, 2).value / Parameters.delttime)
            self.heat_Steam.append(winter_steam_sheet.cell(i + 1, 2).value / Parameters.delttime)
            self.transition_Steam.append(transition_steam_sheet.cell(i + 1, 2).value / Parameters.delttime)

        self.sum_cold_E = sum(self.cold_E)
        self.sum_heat_E = sum(self.heat_E)
        self.sum_transition_E = sum(self.transition_E)
        self.sum_H = sum(self.H)
        self.sum_C = sum(self.C)

        self.sum_cold_Steam = sum(self.cold_Steam)
        self.sum_heat_Steam = sum(self.heat_Steam)
        self.sum_transition_Steam = sum(self.transition_Steam)

        length = len(self.cold_E)
        self.average_cold_E = self.sum_cold_E / length
        self.average_heat_E = self.sum_heat_E / length
        self.average_transition_E = self.sum_transition_E / length
        self.average_H = self.sum_H / length
        self.average_C = self.sum_C / length

        self.average_cold_Steam = self.sum_cold_Steam / length
        self.average_heat_Steam = self.sum_heat_Steam / length
        self.average_transition_Steam = self.sum_transition_Steam / length

