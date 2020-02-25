# _*_ coding: utf-8 _*_
from cn.modelICE.model.InternalCombustionEngine import InternalCombustionEngine
from cn.modelICE.model.Boiler import Boiler
from cn.modelICE.model.CHP import CHPInternalCombustionEngine
from cn.modelICE.model.ColdStorage import ColdStorage
from cn.modelICE.model.EleStorage import EleStorage
from cn.modelICE.model.HeatStorage import HeatStorage
from cn.modelICE.util.DemandData import DemandData
from cn.modelICE.Parameters import Parameters


class EleDrive:
    def __init__(self, t, temporary, number, ele_stor, season):
        ice = InternalCombustionEngine(number, temporary)
        demand = DemandData()
        elestorage = EleStorage(temporary)
        if season == 0:
            demand_ele = demand.cold_E
        elif season == 1:
            demand_ele = demand.heat_E
        else:
            demand_ele = demand.transition_E
        if demand_ele[t] <= elestorage.get_E_out_max(ele_stor):
            self.status = 0
            self.elestorage_in = 0
            self.elestorage_out = demand_ele[t]
            self.ele = 0
            self.ele_bought = 0
        elif((demand_ele[t] > elestorage.get_E_out_max(ele_stor))
             & (demand_ele[t] <= elestorage.get_E_out_max(ele_stor) + Parameters.pl_min * ice.nominal)):
            self.status = 1
            self.elestorage_out = elestorage.get_E_out_max(ele_stor)
            self.ele = Parameters.pl_min * ice.nominal
            self.elestorage_in = self.ele + self.elestorage_out - demand_ele[t]
            self.ele_bought = 0
        elif ((demand_ele[t] > elestorage.get_E_out_max(ele_stor) + Parameters.pl_min * ice.nominal)
              & (demand_ele[t] <= elestorage.get_E_out_max(ele_stor) + ice.nominal)):
            self.status = 1
            self.elestorage_in = 0
            self.elestorage_out = elestorage.get_E_out_max(ele_stor)
            self.ele = demand_ele[t] - self.elestorage_out
            self.ele_bought = 0
        else:
            self.status = 1
            self.elestorage_in = 0
            self.elestorage_out = elestorage.get_E_out_max(ele_stor)
            self.ele = ice.nominal
            self.ele_bought = demand_ele[t] - self.elestorage_out - self.ele
        self.ele_stor = elestorage.get_S(ele_stor, self.elestorage_in, self.elestorage_out)


class EleFollow:
    def __init__(self, t, temporary, ele_stor, ele, season):  # 写这里！！！
        demand = DemandData()
        elestorage = EleStorage(temporary)
        self.ele = ele
        if season == 0:
            demand_ele = demand.cold_E
        elif season == 1:
            demand_ele = demand.heat_E
        else:
            demand_ele = demand.transition_E
        if demand_ele[t] <= elestorage.get_E_out_max(ele_stor):
            self.elestorage_out = demand_ele[t]
            self.elestorage_in = self.ele
            self.ele_bought = 0
        elif ((demand_ele[t] > elestorage.get_E_out_max(ele_stor))
              & (demand_ele[t] <= elestorage.get_E_out_max(ele_stor) + self.ele)):
            self.elestorage_out = elestorage.get_E_out_max(ele_stor)
            self.elestorage_in = self.ele + self.elestorage_out - demand_ele[t]
            self.ele_bought = 0
        else:
            self.elestorage_out = elestorage.get_E_out_max(ele_stor)
            self.elestorage_in = 0
            self.ele_bought = demand_ele[t] - self.ele - self.elestorage_out
        self.ele_stor = elestorage.get_S(ele_stor, self.elestorage_in, self.elestorage_out)


class HeatSteamDrive:
    def __init__(self, t, temporary, number, season):
        demand = DemandData()
        chp = CHPInternalCombustionEngine(temporary, number)
        boiler = Boiler(temporary)
        if season == 0:
            demand_steam = demand.cold_Steam
        elif season == 1:
            demand_steam = demand.heat_Steam
        else:
            demand_steam = demand.transition_Steam
        if demand_steam[t] <= Parameters.pl_min * chp.heat_steam_out_max:
            self.steam = Parameters.pl_min * chp.heat_steam_out_max
            self.gas_boiler_out_for_steam = 0
        elif ((demand_steam[t] > Parameters.pl_min * chp.heat_steam_out_max)
              & (demand_steam[t] <= chp.heat_steam_out_max)):
            self.steam = demand_steam[t]
            self.gas_boiler_out_for_steam = 0
        else:
            self.steam = chp.heat_steam_out_max
            self.gas_boiler_out_for_steam = demand_steam[t] - self.steam
        self.exhaust_gas = boiler.get_H_in(self.steam)


class HeatDriveChiller:  # exhaust gas进入制冷机制热  jacket water直接供热
    def __init__(self, t, temporary, number, heat_stor):
        demand = DemandData()
        heatstorage = HeatStorage(temporary)
        chp = CHPInternalCombustionEngine(temporary, number)
        if demand.H[t] <= heatstorage.get_H_out_max(heat_stor):
            self.heatstorage_out = demand.H[t]
            self.heat = 0
            self.gas_boiler_out = 0
        elif ((demand.H[t] > heatstorage.get_H_out_max(heat_stor))
              & (demand.H[t] <= heatstorage.get_H_out_max(heat_stor) + Parameters.pl_min * chp.heat_space_water_max)):
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heat = Parameters.pl_min * chp.heat_space_water_max
            self.heatstorage_in = self.heat + self.heatstorage_out - demand.H[t]
            self.gas_boiler_out = 0
        elif ((demand.H[t] > heatstorage.get_H_out_max(heat_stor) + Parameters.pl_min * chp.heat_space_water_max)
              & (demand.H[t] <= heatstorage.get_H_out_max(heat_stor) + chp.heat_space_water_max)):
            self.heatstorage_in = 0
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heat = demand.H[t] - self.heatstorage_out
            self.gas_boiler_out = 0
        else:
            self.heatstorage_in = 0
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heat = chp.heat_space_water_max
            self.gas_boiler_out = demand.H[t] - self.heatstorage_out - self.heat
        self.heat_stor = heatstorage.get_S(heat_stor, self.heatstorage_in, self.heatstorage_out)


class HeatDriveBoiler:  # exhaust gas进入锅炉制热  jacket water直接供热
    def __init__(self, t, temporary, number, heat_stor):
        demand = DemandData()
        heatstorage = HeatStorage(temporary)
        chp = CHPInternalCombustionEngine(temporary, number)
        if demand.H[t] <= heatstorage.get_H_out_max(heat_stor):
            self.heatstorage_in = 0
            self.heatstorage_out = demand.H[t]
            self.heat = 0
            self.gas_boiler_out = 0
        elif ((demand.H[t] > heatstorage.get_H_out_max(heat_stor))
              & (demand.H[t] <= heatstorage.get_H_out_max(heat_stor) + Parameters.pl_min * chp.heat_out_max)):
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heat = Parameters.pl_min * chp.heat_out_max
            self.heatstorage_in = self.heat + self.heatstorage_out - demand.H[t]
            self.gas_boiler_out = 0
        elif ((demand.H[t] > heatstorage.get_H_out_max(heat_stor) + Parameters.pl_min * chp.heat_out_max)
              & (demand.H[t] <= heatstorage.get_H_out_max(heat_stor) + chp.heat_out_max)):
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heatstorage_in = 0
            self.heat = demand.H[t] - self.heatstorage_out
            self.gas_boiler_out = 0
        else:
            self.heatstorage_in = 0
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heat = chp.heat_out_max
            self.gas_boiler_out = demand.H[t] - self.heatstorage_out - self.heat
        self.heat_stor = heatstorage.get_S(heat_stor, self.heatstorage_in, self.heatstorage_out)


class HeatDriveJW:  # exhaust gas进入制冷机制冷  jacket water直接供热
    def __init__(self, t, temporary, number, heat_stor):
        demand = DemandData()
        heatstorage = HeatStorage(temporary)
        ice = InternalCombustionEngine(number, temporary)
        if demand.H[t] <= heatstorage.get_H_out_max(heat_stor):
            self.heatstorage_in = 0
            self.heatstorage_out = demand.H[t]
            self.heat = 0
            self.gas_boiler_out = 0
        elif ((demand.H[t] > heatstorage.get_H_out_max(heat_stor))
              & (demand.H[t] <= heatstorage.get_H_out_max(heat_stor) + Parameters.pl_min * ice.get_jacket_water_pl(1))):
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heat = Parameters.pl_min * ice.get_jacket_water_pl(1)
            self.heatstorage_in = self.heat + self.heatstorage_out - demand.H[t]
            self.gas_boiler_out = 0
        elif ((demand.H[t] > heatstorage.get_H_out_max(heat_stor) + Parameters.pl_min * ice.get_jacket_water_pl(1))
              & (demand.H[t] <= heatstorage.get_H_out_max(heat_stor) + ice.get_jacket_water_pl(1))):
            self.heatstorage_in = 0
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heat = demand.H[t] - self.heatstorage_out
            self.gas_boiler_out = 0
        else:
            self.heatstorage_in = 0
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heat = ice.get_jacket_water_pl(1)
            self.gas_boiler_out = demand.H[t] - self.heatstorage_out - self.heat
        self.heat_stor = heatstorage.get_S(heat_stor, self.heatstorage_in, self.heatstorage_out)


class HeatFollow:
    def __init__(self, t, temporary, heat_stor, heat):  # heat为chp产热（空间热+热水热）
        demand = DemandData()
        heatstorage = HeatStorage(temporary)
        self.heat_out = heat
        if demand.H[t] <= heatstorage.get_H_out_max(heat_stor):
            self.heatstorage_out = demand.H[t]
            self.heatstorage_in = self.heat_out
            self.gas_boiler_out = 0
        elif ((demand.H[t] > heatstorage.get_H_out_max(heat_stor))
              & (demand.H[t] <= heatstorage.get_H_out_max(heat_stor) + self.heat_out)):
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heatstorage_in = self.heatstorage_out + self.heat_out - demand.H[t]
            self.gas_boiler_out = 0
        else:
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heatstorage_in = 0
            self.gas_boiler_out = demand.H[t] - self.heatstorage_out - self.heat_out
        self.heat_stor = heatstorage.get_S(heat_stor, self.heatstorage_in, self.heatstorage_out)


class HeatFollowWithSteam:
    def __init__(self, t, temporary, heat_stor, heat, demand_heat):  # heat为chp产热（空间热+热水热）
        heatstorage = HeatStorage(temporary)
        self.heat_out = heat
        if demand_heat[t] <= heatstorage.get_H_out_max(heat_stor):
            self.heatstorage_out = demand_heat[t]
            self.heatstorage_in = self.heat_out
            self.gas_boiler_out = 0
        elif ((demand_heat[t] > heatstorage.get_H_out_max(heat_stor))
              & (demand_heat[t] <= heatstorage.get_H_out_max(heat_stor) + self.heat_out)):
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heatstorage_in = self.heatstorage_out + self.heat_out - demand_heat[t]
            self.gas_boiler_out = 0
        else:
            self.heatstorage_out = heatstorage.get_H_out_max(heat_stor)
            self.heatstorage_in = 0
            self.gas_boiler_out = demand_heat[t] - self.heatstorage_out - self.heat_out
        self.heat_stor = heatstorage.get_S(heat_stor, self.heatstorage_in, self.heatstorage_out)


class ColdDrive:
    def __init__(self, t, temporary, number, cold_stor):
        demand = DemandData()
        coldstorage = ColdStorage(temporary)
        chp = CHPInternalCombustionEngine(temporary, number)
        if demand.C[t] <= coldstorage.get_C_out_max(cold_stor):
            self.cold = 0
            self.coldstorage_in = 0
            self.coldstorage_out = demand.C[t]
            self.heat_pump_out = 0
        elif ((demand.C[t] > coldstorage.get_C_out_max(cold_stor))
              & (demand.C[t] <= coldstorage.get_C_out_max(cold_stor) + Parameters.pl_min * chp.cold_out_max)):
            self.cold = Parameters.pl_min * chp.cold_out_max
            self.coldstorage_out = coldstorage.get_C_out_max(cold_stor)
            self.coldstorage_in = self.cold + self.coldstorage_out - demand.C[t]
            self.heat_pump_out = 0
        elif ((demand.C[t] > coldstorage.get_C_out_max(cold_stor) + Parameters.pl_min * chp.cold_out_max)
              & (demand.C[t] <= coldstorage.get_C_out_max(cold_stor) + chp.cold_out_max)):
            self.coldstorage_in = 0
            self.coldstorage_out = coldstorage.get_C_out_max(cold_stor)
            self.cold = demand.C[t] - self.coldstorage_out
            self.heat_pump_out = 0
        else:
            self.coldstorage_in = 0
            self.coldstorage_out = coldstorage.get_C_out_max(cold_stor)
            self.cold = chp.cold_out_max
            self.heat_pump_out = demand.C[t] - self.coldstorage_out - self.cold
        self.cold_stor = coldstorage.get_S(cold_stor, self.coldstorage_in, self.coldstorage_out)


class ColdFollow:
    def __init__(self, t, temporary, cold_stor, cold):
        demand = DemandData()
        coldstorage = ColdStorage(temporary)
        self.cold = cold
        if demand.C[t] <= coldstorage.get_C_out_max(cold_stor):
            self.coldstorage_out = demand.C[t]
            self.coldstorage_in = self.cold
            self.heat_pump_out = 0
        elif ((demand.C[t] > coldstorage.get_C_out_max(cold_stor))
              & (demand.C[t] <= coldstorage.get_C_out_max(cold_stor) + self.cold)):
            self.coldstorage_out = coldstorage.get_C_out_max(cold_stor)
            self.coldstorage_in = self.coldstorage_out + self.cold - demand.C[t]
            self.heat_pump_out = 0
        else:
            self.coldstorage_out = coldstorage.get_C_out_max(cold_stor)
            self.coldstorage_in = 0
            self.heat_pump_out = demand.C[t] - self.coldstorage_out - self.cold
        self.cold_stor = coldstorage.get_S(cold_stor, self.coldstorage_in, self.coldstorage_out)


class ColdFollowWithSteam:
    def __init__(self, t, temporary, cold_stor, cold, demand_cold):
        coldstorage = ColdStorage(temporary)
        self.cold = cold
        if demand_cold[t] <= coldstorage.get_C_out_max(cold_stor):
            self.coldstorage_out = demand_cold[t]
            self.coldstorage_in = self.cold
            self.heat_pump_out = 0
        elif ((demand_cold[t] > coldstorage.get_C_out_max(cold_stor))
              & (demand_cold[t] <= coldstorage.get_C_out_max(cold_stor) + self.cold)):
            self.coldstorage_out = coldstorage.get_C_out_max(cold_stor)
            self.coldstorage_in = self.coldstorage_out + self.cold - demand_cold[t]
            self.heat_pump_out = 0
        else:
            self.coldstorage_out = coldstorage.get_C_out_max(cold_stor)
            self.coldstorage_in = 0
            self.heat_pump_out = demand_cold[t] - self.coldstorage_out - self.cold
        self.cold_stor = coldstorage.get_S(cold_stor, self.coldstorage_in, self.coldstorage_out)
