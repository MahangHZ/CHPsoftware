# _*_ coding: utf-8 _*_
from cn.modelICE.Parameters import Parameters
from cn.modelICE.model.InternalCombustionEngine import InternalCombustionEngine
from cn.modelICE.model.CHP import CHPInternalCombustionEngine
from cn.modelICE.model.ColdStorage import ColdStorage
from cn.modelICE.model.EleStorage import EleStorage
from cn.modelICE.model.GasBoiler import GasBoiler
from cn.modelICE.model.HeatPump import HeatPump
from cn.modelICE.model.HeatStorage import HeatStorage
from cn.modelICE.util.DemandData import DemandData


class SeasonColdBL:
    def __init__(self, temporary, number):
        chp = CHPInternalCombustionEngine(temporary, number)
        heat_pump = HeatPump(temporary)
        elestorage = EleStorage(temporary)
        coldstorage = ColdStorage(temporary)
        ice = InternalCombustionEngine(number, temporary)
        demand = DemandData()
        cold_stor = 0
        ele_stor = 0
        self.ele_stor = []
        self.cold_stor = []
        self.ele_stor_day_time = []
        self.cold_stor_day_time = []
        self.fuel = []
        self.fuel_day_time = []
        self.ele_bought = []
        self.ele_bought_day_time = []
        self.ele_ice = []
        self.ele_ice_day_time = []
        self.cold_absorption_chiller = []
        self.cold_absorption_chiller_day_time = []
        self.cold_heat_pump = []
        self.cold_heat_pump_day_time = []
        self.cold_waste = []
        self.cold_waste_day_time = []
        self.ele_waste = []
        self.ele_waste_day_time = []
        for t in range(7, 23, Parameters.delttime):
            ele = ice.nominal
            cold = chp.cold_out_max
            if demand.C[t] > cold + coldstorage.get_C_out_max(cold_stor) + heat_pump.nominal:
                self.judge = 0
                break
            else:
                self.judge = 1
                if demand.C[t] <= cold:
                    cold_stor = coldstorage.get_S(cold_stor, cold - demand.C[t], 0)
                    cold_heat_pump = 0
                    ele_needed_for_heat_pump = 0
                elif (demand.C[t] > cold) & (demand.C[t] <= (cold + coldstorage.get_C_out_max(cold_stor))):
                    coldstorage_cold_out = demand.C[t] - cold
                    cold_stor = coldstorage.get_S(cold_stor, 0, coldstorage_cold_out)
                    cold_heat_pump = 0
                    ele_needed_for_heat_pump = 0
                else:
                    coldstorage_cold_out = coldstorage.get_C_out_max(cold_stor)
                    cold_heat_pump = demand.C[t] - coldstorage.get_C_out_max(cold_stor) - cold
                    ele_needed_for_heat_pump = heat_pump.get_E_in(cold_heat_pump)
                    cold_stor = coldstorage.get_S(cold_stor, 0, coldstorage_cold_out)
                if demand.cold_E[t] <= ele:
                    ele_bought_for_ele = 0
                    if ele_needed_for_heat_pump > 0:
                        if ele - demand.cold_E[t] >= ele_needed_for_heat_pump:
                            elestorage_ele_in = ele - demand.cold_E[t] - ele_needed_for_heat_pump
                            ele_bought_for_heat_pump = 0
                        else:
                            elestorage_ele_in = 0
                            ele_bought_for_heat_pump = ele_needed_for_heat_pump - (ele - demand.cold_E[t])
                    else:
                        elestorage_ele_in = ele - demand.cold_E[t]
                        ele_bought_for_heat_pump = 0
                    ele_stor = elestorage.get_S(ele_stor, elestorage_ele_in, 0)
                elif (demand.cold_E[t] > ele) & (demand.cold_E[t] <= (ele + elestorage.get_E_out_max(ele_stor))):
                    ele_bought_for_ele = 0
                    ele_bought_for_heat_pump = ele_needed_for_heat_pump
                    elestorage_ele_out = demand.cold_E[t] - ele
                    ele_stor = elestorage.get_S(ele_stor, 0, elestorage_ele_out)
                else:
                    ele_bought_for_heat_pump = ele_needed_for_heat_pump
                    ele_bought_for_ele = demand.cold_E[t] - ele - elestorage.get_E_out_max(ele_stor)
                    elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
                    ele_stor = elestorage.get_S(ele_stor, 0, elestorage_ele_out)
                if cold_stor > coldstorage.nominal:
                    self.cold_waste_day_time.append(cold_stor - coldstorage.nominal)
                    cold_stor = coldstorage.nominal
                else:
                    self.cold_waste_day_time.append(0)
                if ele_stor > elestorage.nominal:
                    self.ele_waste_day_time.append(ele_stor - elestorage.nominal)
                    ele_stor = elestorage.nominal
                else:
                    self.ele_waste_day_time.append(0)
                self.ele_stor_day_time.append(ele_stor)
                self.cold_stor_day_time.append(cold_stor)
                self.ele_ice_day_time.append(ele)
                self.cold_absorption_chiller_day_time.append(cold)
                self.cold_heat_pump_day_time.append(cold_heat_pump)
                self.ele_bought_day_time.append(ele_bought_for_heat_pump + ele_bought_for_ele)
                self.fuel_day_time.append(ice.get_fuel(1))
        if self.judge == 1:
            for t in range(23, 24, Parameters.delttime):
                # 把以下cold，ele，heat部分写成class
                cold_during_shut_down = ColdDuringShutDown(temporary, t, cold_stor)
                ele_during_shut_down = EleDuringShutDown(temporary, t, ele_stor, 0)
                cold_stor = cold_during_shut_down.cold_stor
                ele_stor = ele_during_shut_down.ele_stor
                self.ele_stor_day_time.append(ele_stor)
                self.cold_stor_day_time.append(cold_stor)
                self.ele_ice_day_time.append(0)
                self.cold_absorption_chiller_day_time.append(0)
                self.cold_heat_pump_day_time.append(cold_during_shut_down.cold_heat_pump)
                self.ele_bought_day_time.append(ele_during_shut_down.ele_bought_for_ele
                                                + cold_during_shut_down.ele_bought_for_heat_pump)
                self.fuel_day_time.append(0)
                self.cold_waste_day_time.append(0)
                self.ele_waste_day_time.append(0)
            for t in range(0, 7, Parameters.delttime):
                cold_during_shut_down = ColdDuringShutDown(temporary, t, cold_stor)
                ele_during_shut_down = EleDuringShutDown(temporary, t, ele_stor, 0)
                cold_stor = cold_during_shut_down.cold_stor
                ele_stor = ele_during_shut_down.ele_stor
                self.cold_stor.append(cold_stor)
                self.ele_stor.append(ele_stor)
                self.ele_ice.append(0)
                self.cold_absorption_chiller.append(0)
                self.cold_heat_pump.append(cold_during_shut_down.cold_heat_pump)
                self.ele_bought.append(ele_during_shut_down.ele_bought_for_ele
                                       + cold_during_shut_down.ele_bought_for_heat_pump)
                self.fuel.append(0)
                self.cold_waste.append(0)
                self.ele_waste.append(0)
            for i in range(0, 17, 1):
                self.ele_stor.append(self.ele_stor_day_time[i])
                self.cold_stor.append(self.cold_stor_day_time[i])
                self.ele_ice.append(self.ele_ice_day_time[i])
                self.cold_absorption_chiller.append(self.cold_absorption_chiller_day_time[i])
                self.cold_heat_pump.append(self.cold_heat_pump_day_time[i])
                self.ele_bought.append(self.ele_bought_day_time[i])
                self.fuel.append(self.fuel_day_time[i])
                self.cold_waste.append(self.cold_waste_day_time[i])
                self.ele_waste.append(self.ele_waste_day_time[i])


class SeasonHeatBL:  # 无热蒸汽需求，只有空间热和热水,exhaust gas进入锅炉制热，jacket water直接供热
    def __init__(self, temporary, number):
        chp = CHPInternalCombustionEngine(temporary, number)
        ice = InternalCombustionEngine(number, temporary)
        gas_boiler = GasBoiler(temporary)
        elestorage = EleStorage(temporary)
        heatstorage = HeatStorage(temporary)
        demand = DemandData()
        heat_stor = 0
        ele_stor = 0
        self.fuel = []
        self.fuel_day_time = []
        self.ele_bought = []
        self.ele_bought_day_time = []
        self.ele_ice = []
        self.ele_ice_day_time = []
        self.heat = []
        self.heat_day_time = []
        self.heat_gas_boiler = []
        self.heat_gas_boiler_day_time = []
        self.heat_waste = []
        self.heat_waste_day_time = []
        self.ele_waste = []
        self.ele_waste_day_time = []
        self.heat_stor = []
        self.heat_stor_day_time = []
        self.ele_stor = []
        self.ele_stor_day_time = []
        for t in range(7, 23, Parameters.delttime):
            if demand.H[t] > chp.heat_out_max + heatstorage.get_H_out_max(heat_stor) + gas_boiler.nominal:
                self.judge = 0
                break
            else:
                self.judge = 1
                ele = ice.nominal
                heat = chp.heat_out_max
                if demand.H[t] <= heat:
                    heatstorage_heat_in = heat - demand.H[t]
                    heatstorage_heat_out = 0
                    heat_gas_boiler = 0
                elif(demand.H[t] > heat) & (demand.H[t] <= heat + heatstorage.get_H_out_max(heat_stor)):
                    heatstorage_heat_in = 0
                    heatstorage_heat_out = demand.H[t] - heat
                    heat_gas_boiler = 0
                else:
                    heatstorage_heat_in = 0
                    heatstorage_heat_out = heatstorage.get_H_out_max(heat_stor)
                    heat_gas_boiler = demand.H[t] - heat - heatstorage.get_H_out_max(heat_stor)
                heat_stor = heatstorage.get_S(heat_stor, heatstorage_heat_in, heatstorage_heat_out)
                if demand.heat_E[t] <= ele:
                    elestorage_ele_in = ele - demand.heat_E[t]
                    elestorage_ele_out = 0
                    ele_bought = 0
                elif(demand.heat_E[t] > ele) & (demand.heat_E[t] <= ele + elestorage.get_E_out_max(ele_stor)):
                    elestorage_ele_in = 0
                    elestorage_ele_out = demand.heat_E[t] - ele
                    ele_bought = 0
                else:
                    elestorage_ele_in = 0
                    elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
                    ele_bought = demand.heat_E[t] - ele - elestorage.get_E_out_max(ele_stor)
                ele_stor = elestorage.get_S(ele_stor, elestorage_ele_in, elestorage_ele_out)
                if heat_stor > heatstorage.nominal:
                    self.heat_waste_day_time.append(heat_stor - heatstorage.nominal)
                    heat_stor = heatstorage.nominal
                else:
                    self.heat_waste_day_time.append(0)
                if ele_stor > elestorage.nominal:
                    self.ele_waste_day_time.append(ele_stor - elestorage.nominal)
                    ele_stor = elestorage.nominal
                else:
                    self.ele_waste_day_time.append(0)
                self.ele_ice_day_time.append(ele)
                self.heat_day_time.append(heat)
                self.heat_gas_boiler_day_time.append(heat_gas_boiler)
                self.ele_bought_day_time.append(ele_bought)
                self.fuel_day_time.append(ice.get_fuel(1) + gas_boiler.get_Fuel_in(heat_gas_boiler))
                self.heat_stor_day_time.append(heat_stor)
                self.ele_stor_day_time.append(ele_stor)

        if self.judge == 1:
            for t in range(23, 24):
                heat_during_shut_down = HeatDuringShutDown(temporary, t, heat_stor)
                ele_during_shut_down = EleDuringShutDown(temporary, t, ele_stor, 1)
                heat_stor = heat_during_shut_down.heat_stor
                ele_stor = ele_during_shut_down.ele_stor
                self.ele_ice_day_time.append(0)
                self.heat_day_time.append(0)
                self.heat_gas_boiler_day_time.append(heat_during_shut_down.heat_gas_boiler)
                self.fuel_day_time.append(heat_during_shut_down.fuel)
                self.ele_bought_day_time.append(ele_during_shut_down.ele_bought_for_ele)
                self.heat_waste_day_time.append(0)
                self.ele_waste_day_time.append(0)
                self.heat_stor_day_time.append(heat_stor)
                self.ele_stor_day_time.append(ele_stor)
            for t in range(0, 7, Parameters.delttime):
                heat_during_shut_down = HeatDuringShutDown(temporary, t, heat_stor)
                ele_during_shut_down = EleDuringShutDown(temporary, t, ele_stor, 1)
                heat_stor = heat_during_shut_down.heat_stor
                ele_stor = ele_during_shut_down.ele_stor
                self.ele_ice.append(0)
                self.heat.append(0)
                self.heat_gas_boiler.append(heat_during_shut_down.heat_gas_boiler)
                self.fuel.append(heat_during_shut_down.fuel)
                self.ele_bought.append(ele_during_shut_down.ele_bought_for_ele)
                self.heat_waste.append(0)
                self.ele_waste.append(0)
                self.heat_stor.append(heat_stor)
                self.ele_stor.append(ele_stor)
            for i in range(0, 17, 1):
                self.ele_ice.append(self.ele_ice_day_time[i])
                self.heat.append(self.heat_day_time[i])
                self.heat_gas_boiler.append(self.heat_gas_boiler_day_time[i])
                self.ele_bought.append(self.ele_bought_day_time[i])
                self.fuel.append(self.fuel_day_time[i])
                self.heat_waste.append(self.heat_waste_day_time[i])
                self.ele_waste.append(self.ele_waste_day_time[i])
                self.heat_stor.append(self.heat_stor_day_time[i])
                self.ele_stor.append(self.ele_stor_day_time[i])


class SeasonHeatColdBL:  # 空间热负荷+热水+空间冷负荷  电--热--冷  exhaust gas进入制冷机制冷，jacket water供热
    def __init__(self, temporary, number):
        demand = DemandData()
        heatstorage = HeatStorage(temporary)
        coldstorage = ColdStorage(temporary)
        elestorage = EleStorage(temporary)
        gas_boiler = GasBoiler(temporary)
        heat_pump = HeatPump(temporary)
        ice = InternalCombustionEngine(number, temporary)
        chp = CHPInternalCombustionEngine(temporary, number)
        heat_stor = 0
        ele_stor = 0
        cold_stor = 0
        self.fuel = []
        self.fuel_day_time = []
        self.ele_bought = []
        self.ele_bought_day_time = []
        self.ele_ice = []
        self.ele_ice_day_time = []
        self.heat_jacket_water = []
        self.heat_jacket_water_day_time = []
        self.heat_gas_boiler = []
        self.heat_gas_boiler_day_time = []
        self.cold_absorption_chiller = []
        self.cold_absorption_chiller_day_time = []
        self.cold_heat_pump = []
        self.cold_heat_pump_day_time = []
        self.cold_waste = []
        self.cold_waste_day_time = []
        self.heat_waste = []
        self.heat_waste_day_time = []
        self.ele_waste = []
        self.ele_waste_day_time = []
        for t in range(7, 23, Parameters.delttime):
            if ((demand.C[t] > chp.cold_out_max_exhaust_gas + coldstorage.get_C_out_max(cold_stor) + heat_pump.nominal)
                    | (demand.H[t] > (ice.get_jacket_water_pl(1) + heatstorage.get_H_out_max(heat_stor)
                       + gas_boiler.nominal))):
                self.judge = 0
                break
            else:
                self.judge = 1
                ele = ice.nominal
                heat = ice.get_jacket_water_pl(1)
                cold = chp.cold_out_max_exhaust_gas
                if demand.C[t] <= cold:
                    coldstorage_cold_in = cold - demand.C[t]
                    coldstorage_cold_out = 0
                    cold_heat_pump = 0
                    ele_needed_for_heat_pump = 0
                elif(demand.C[t] > cold) & (demand.C[t] <= cold + coldstorage.get_C_out_max(cold_stor)):
                    coldstorage_cold_out = demand.C[t] - cold
                    coldstorage_cold_in = 0
                    cold_heat_pump = 0
                    ele_needed_for_heat_pump = 0
                else:
                    coldstorage_cold_out = coldstorage.get_C_out_max(cold_stor)
                    coldstorage_cold_in = 0
                    cold_heat_pump = demand.C[t] - coldstorage_cold_out - cold
                    ele_needed_for_heat_pump = heat_pump.get_E_in(cold_heat_pump)
                cold_stor = coldstorage.get_S(cold_stor, coldstorage_cold_in, coldstorage_cold_out)
                if demand.transition_E <= ele:
                    ele_bought_for_ele = 0
                    if ele_needed_for_heat_pump > 0:
                        if ele - demand.transition_E[t] >= ele_needed_for_heat_pump:
                            elestorage_ele_in = ele - demand.transition_E[t] - ele_needed_for_heat_pump
                            elestorage_ele_out = 0
                            ele_bought_for_heat_pump = 0
                        else:
                            elestorage_ele_in = 0
                            elestorage_ele_out = 0
                            ele_bought_for_heat_pump = ele_needed_for_heat_pump - (ele - demand.transition_E[t])
                    else:
                        ele_bought_for_heat_pump = 0
                        elestorage_ele_out = 0
                        elestorage_ele_in = ele - demand.transition_E[t]
                elif(demand.transition_E[t] > ele) \
                        & (demand.transition_E[t] < ele + elestorage.get_E_out_max(ele_stor)):
                    ele_bought_for_ele = 0
                    elestorage_ele_out = demand.transition_E[t] - ele
                    elestorage_ele_in = 0
                    ele_bought_for_heat_pump = ele_needed_for_heat_pump
                else:
                    ele_bought_for_ele = demand.transition_E[t] - ele - elestorage.get_E_out_max(ele_stor)
                    elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
                    elestorage_ele_in = 0
                    ele_bought_for_heat_pump = ele_needed_for_heat_pump
                ele_stor = elestorage.get_S(ele_stor, elestorage_ele_in, elestorage_ele_out)
                ele_bought = ele_bought_for_heat_pump + ele_bought_for_ele

                if demand.H[t] <= heat:
                    heatstorage_heat_out = 0
                    heatstorage_heat_in = heat - demand.H[t]
                    heat_gas_boiler = 0
                elif(demand.H[t] > heat) & (demand.H[t] <= heat + heatstorage.get_H_out_max(heat_stor)):
                    heatstorage_heat_out = demand.H[t] - heat
                    heatstorage_heat_in = 0
                    heat_gas_boiler = 0
                else:
                    heatstorage_heat_out = heatstorage.get_H_out_max(heat_stor)
                    heatstorage_heat_in = 0
                    heat_gas_boiler = demand.H[t] - heat - heatstorage.get_H_out_max(heat_stor)
                heat_stor = heatstorage.get_S(heat_stor, heatstorage_heat_in, heatstorage_heat_out)
                if cold_stor > coldstorage.nominal:
                    self.cold_waste_day_time.append(cold_stor - coldstorage.nominal)
                    cold_stor = coldstorage.nominal
                else:
                    self.cold_waste_day_time.append(0)
                if heat_stor > heatstorage.nominal:
                    self.heat_waste_day_time.append(heat_stor - heatstorage.nominal)
                    heat_stor = heatstorage.nominal
                else:
                    self.heat_waste_day_time.append(0)
                if ele_stor > elestorage.nominal:
                    self.ele_waste_day_time.append(ele_stor - elestorage.nominal)
                    ele_stor = elestorage.nominal
                else:
                    self.ele_waste_day_time.append(0)
                self.ele_ice_day_time.append(ele)
                self.heat_jacket_water_day_time.append(heat)
                self.cold_absorption_chiller_day_time.append(cold)
                self.cold_heat_pump_day_time.append(cold_heat_pump)
                self.heat_gas_boiler_day_time.append(heat_gas_boiler)
                self.ele_bought_day_time.append(ele_bought)
                self.fuel_day_time.append(ice.get_fuel(1) + gas_boiler.get_Fuel_in(heat_gas_boiler))
        if self.judge == 1:
            for t in range(23, 24, Parameters.delttime):
                cold_during_shut_down = ColdDuringShutDown(temporary, t, cold_stor)
                heat_during_sut_down = HeatDuringShutDown(temporary, t, heat_stor)
                ele_during_shut_down = EleDuringShutDown(temporary, t, ele_stor, 2)
                cold_stor = cold_during_shut_down.cold_stor
                heat_stor = heat_during_sut_down.heat_stor
                ele_stor = ele_during_shut_down.ele_stor
                self.ele_ice_day_time.append(0)
                self.heat_jacket_water_day_time.append(0)
                self.cold_absorption_chiller_day_time.append(0)
                self.cold_heat_pump_day_time.append(cold_during_shut_down.cold_heat_pump)
                self.heat_gas_boiler_day_time.append(heat_during_sut_down.heat_gas_boiler)
                self.fuel_day_time.append(heat_during_sut_down.fuel)
                self.ele_bought_day_time.append(cold_during_shut_down.ele_bought_for_heat_pump
                                                + ele_during_shut_down.ele_bought_for_ele)
                self.cold_waste_day_time.append(0)
                self.heat_waste_day_time.append(0)
                self.ele_waste_day_time.append(0)
            for t in range(0, 7, Parameters.delttime):
                cold_during_shut_down = ColdDuringShutDown(temporary, t, cold_stor)
                heat_during_sut_down = HeatDuringShutDown(temporary, t, heat_stor)
                ele_during_shut_down = EleDuringShutDown(temporary, t, ele_stor, 2)
                cold_stor = cold_during_shut_down.cold_stor
                heat_stor = heat_during_sut_down.heat_stor
                ele_stor = ele_during_shut_down.ele_stor
                self.ele_ice.append(0)
                self.heat_jacket_water.append(0)
                self.cold_absorption_chiller.append(0)
                self.cold_heat_pump.append(cold_during_shut_down.cold_heat_pump)
                self.heat_gas_boiler.append(heat_during_sut_down.heat_gas_boiler)
                self.fuel.append(heat_during_sut_down.fuel)
                self.ele_bought.append(cold_during_shut_down.ele_bought_for_heat_pump
                                       + ele_during_shut_down.ele_bought_for_ele)
                self.cold_waste.append(0)
                self.heat_waste.append(0)
                self.ele_waste.append(0)
            for i in range(0, 17, 1):
                self.ele_ice.append(self.ele_ice_day_time[i])
                self.heat_jacket_water.append(self.heat_jacket_water_day_time[i])
                self.heat_gas_boiler.append(self.heat_gas_boiler_day_time[i])
                self.cold_absorption_chiller.append(self.cold_absorption_chiller_day_time[i])
                self.cold_heat_pump.append(self.cold_heat_pump_day_time[i])
                self.ele_bought.append(self.ele_bought_day_time[i])
                self.fuel.append(self.fuel_day_time[i])
                self.cold_waste.append(self.cold_waste_day_time[i])
                self.heat_waste.append(self.heat_waste_day_time[i])
                self.ele_waste.append(self.ele_waste_day_time[i])


class SeasonElectricOnlyBL:
    def __init__(self, temporary, number):
        ele_stor = 0
        elestorage = EleStorage(temporary)
        ice = InternalCombustionEngine(number, temporary)
        demand = DemandData()
        self.judge = 1
        self.ele_bought = []
        self.ele_bought_day_time = []
        self.fuel = []
        self.fuel_day_time = []
        self.ele_ice = []
        self.ele_ice_day_time = []
        self.ele_waste = []
        self.ele_waste_day_time = []
        self.ele_stor = []
        self.ele_stor_day_time = []
        for t in range(6, 22, Parameters.delttime):
            ele = ice.nominal
            if demand.transition_E[t] <= ele:
                elestorage_ele_out = 0
                elestorage_ele_in = ele - demand.transition_E[t]
                ele_bought = 0
            elif(demand.transition_E[t] > ele) & (demand.transition_E[t] <= ele + elestorage.get_E_out_max(ele_stor)):
                elestorage_ele_out = demand.transition_E[t] - ele
                elestorage_ele_in = 0
                ele_bought = 0
            else:
                elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
                elestorage_ele_in = 0
                ele_bought = demand.transition_E[t] - ele - elestorage_ele_out
            ele_stor = elestorage.get_S(ele_stor, elestorage_ele_in, elestorage_ele_out)
            if ele_stor > elestorage.nominal:
                self.ele_waste_day_time.append(ele_stor - elestorage.nominal)
                ele_stor = elestorage.nominal
            else:
                self.ele_waste_day_time.append(0)
            self.ele_ice_day_time.append(ele)
            self.fuel_day_time.append(ice.get_fuel(1))
            self.ele_bought_day_time.append(ele_bought)
            self.ele_stor_day_time.append(ele_stor)
        for t in range(22, 24, Parameters.delttime):
            ele_during_shut_down = EleDuringShutDown(temporary, t, ele_stor, 2)
            ele_stor = ele_during_shut_down.ele_stor
            self.ele_ice_day_time.append(0)
            self.fuel_day_time.append(0)
            self.ele_waste_day_time.append(0)
            self.ele_bought_day_time.append(ele_during_shut_down.ele_bought_for_ele)
            self.ele_stor_day_time.append(ele_stor)
        for t in range(0, 7, Parameters.delttime):
            ele_during_shut_down = EleDuringShutDown(temporary, t, ele_stor, 2)
            ele_stor = ele_during_shut_down.ele_stor
            self.ele_bought.append(ele_during_shut_down.ele_bought_for_ele)
            self.ele_ice.append(0)
            self.fuel.append(0)
            self.ele_waste.append(0)
            self.ele_stor.append(ele_stor)
        for i in range(0, 17, 1):
            self.ele_ice.append(self.ele_ice_day_time[i])
            self.ele_bought.append(self.ele_bought_day_time[i])
            self.fuel.append(self.fuel_day_time[i])
            self.ele_waste.append(self.ele_waste_day_time[i])
            self.ele_stor.append(self.ele_stor_day_time[i])


class ColdDuringShutDown:
    def __init__(self, temporary, t, cold_stor):
        heat_pump = HeatPump(temporary)
        coldstorage = ColdStorage(temporary)
        demand = DemandData()
        if coldstorage.get_C_out_max(cold_stor) > 0:
            if demand.C[t] <= coldstorage.get_C_out_max(cold_stor):
                coldstorage_cold_out = demand.C[t]
                self.cold_heat_pump = 0
            else:
                coldstorage_cold_out = coldstorage.get_C_out_max(cold_stor)
                self.cold_heat_pump = demand.C[t] - coldstorage_cold_out
            self.cold_stor = coldstorage.get_S(cold_stor, 0, coldstorage_cold_out)
        else:
            self.cold_heat_pump = demand.C[t]
            self.cold_stor = coldstorage.get_S(cold_stor, 0, 0)
        self.ele_bought_for_heat_pump = heat_pump.get_E_in(self.cold_heat_pump)


class EleDuringShutDown:
    def __init__(self, temporary, t, ele_stor, season):
        elestorage = EleStorage(temporary)
        demand = DemandData()
        if season == 0:
            demand_ele = demand.cold_E
        elif season == 1:
            demand_ele = demand.heat_E
        else:
            demand_ele = demand.transition_E
        if elestorage.get_E_out_max(ele_stor) > 0:
            if demand_ele[t] <= elestorage.get_E_out_max(ele_stor):
                elestorage_ele_out = demand_ele[t]
                self.ele_bought_for_ele = 0
            else:
                elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
                self.ele_bought_for_ele = demand_ele[t] - elestorage_ele_out
            self.ele_stor = elestorage.get_S(ele_stor, 0, elestorage_ele_out)
        else:
            self.ele_stor = elestorage.get_S(ele_stor, 0, 0)
            self.ele_bought_for_ele = demand_ele[t]


class HeatDuringShutDown:
    def __init__(self, temporary, t, heat_stor):
        heatstorage = HeatStorage(temporary)
        gas_boiler = GasBoiler(temporary)
        demand = DemandData()
        if heatstorage.get_H_out_max(heat_stor) > 0:
            if demand.H[t] <= heatstorage.get_H_out_max(heat_stor):
                heatstorage_heat_out = demand.H[t]
                self.heat_gas_boiler = 0
            else:
                heatstorage_heat_out = heatstorage.get_H_out_max(heat_stor)
                self.heat_gas_boiler = demand.H[t] - heatstorage_heat_out
            self.heat_stor = heatstorage.get_S(heat_stor, 0, heatstorage_heat_out)
        else:
            self.heat_stor = heatstorage.get_S(heat_stor, 0, 0)
            self.heat_gas_boiler = demand.H[t]
        self.fuel = gas_boiler.get_Fuel_in(self.heat_gas_boiler)
