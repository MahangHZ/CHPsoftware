# _*_ coding: utf-8 _*_
import math
from cn.modelICE.util.GasTurbine_database import GasTurbineDatabase
from cn.modelICE.Parameters import Parameters


class GasTurbine:
    # 输入：PL，nominal"

    def __init__(self, number, temporary):  # number: 燃气轮机编号
        database = GasTurbineDatabase()
        self.gas_turbine_database_one = database.gas_turbine_database[number - 1]
        if number == 1:  # number=1 不用数据库
            self.nominal = Parameters.get_nominal_GasTurbine(temporary)  # nominal: KW
        else:  # number >1,选用数据库中燃气轮机
            self.nominal = self.gas_turbine_database_one[0]
        self.effi_ele_nom = 0.04049 * math.log(self.nominal) - 0.0687
        self.effi_th_nom = -0.025 * math.log(self.nominal) + 0.64
        self.heat_ele_ratio = self.effi_th_nom / self.effi_ele_nom
        # print(self.effi_ele_nom, self.effi_th_nom)

    def get_effi_ele_pl(self, ele_out):
        pl = ele_out/self.nominal
        effi_ele_pl = self.gas_turbine_database_one[2] * pl + self.gas_turbine_database_one[3]
        return effi_ele_pl

    def get_effi_th_pl(self, ele_out):
        pl = ele_out / self.nominal
        effi_th_pl = self.gas_turbine_database_one[4] * pl + self.gas_turbine_database_one[5]
        return effi_th_pl

    def get_fuel(self, ele_out):
        pl = ele_out / self.nominal
        effi_ele_pl = self.gas_turbine_database_one[2] * pl + self.gas_turbine_database_one[3]
        fuel = ele_out * 3600 / effi_ele_pl / Parameters.heatvalue * Parameters.delttime  # m³
        return fuel

    def get_heat_out(self, ele_out):
        pl = ele_out / self.nominal
        effi_ele_pl = self.gas_turbine_database_one[2] * pl + self.gas_turbine_database_one[3]
        effi_th_pl = self.gas_turbine_database_one[4] * pl + self.gas_turbine_database_one[5]
        heat_out = ele_out/effi_ele_pl*effi_th_pl
        return heat_out

    def get_ele_out_through_heat(self, heat_out):
        ele_out = heat_out / self.heat_ele_ratio
        return ele_out
