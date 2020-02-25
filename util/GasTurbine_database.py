# _*_ coding: utf-8 _*_
import xlrd


class GasTurbineDatabase:
    def __init__(self):
        gas_turbine_database = xlrd.open_workbook(r'E:/pythonProject/model/resources/GasTurbine_database.xlsx')
        gas_turbine_sheet = gas_turbine_database.sheet_by_name('database')
        self.gas_turbine_database_rows = gas_turbine_sheet.nrows
        self.gas_turbine_database_cols = gas_turbine_sheet.ncols
        self.gas_turbine_database = []
        for i in range(1, self.gas_turbine_database_rows):
            gas_turbine_database_one = []
            for j in range(1, self.gas_turbine_database_cols):
                gas_turbine_database_one.append(gas_turbine_sheet.cell(i, j).value)
            self.gas_turbine_database.append(gas_turbine_database_one)
