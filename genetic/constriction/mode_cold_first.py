# _*_ coding: utf-8 _*_
from cn.modelICE.Parameters import Parameters
from cn.modelICE.model.AbsorptionChiller import AbsorptionChiller
from cn.modelICE.model.Boiler import Boiler
from cn.modelICE.model.CHP import CHP
from cn.modelICE.model.ColdStorage import ColdStorage
from cn.modelICE.model.EleStorage import EleStorage
from cn.modelICE.model.GasBoiler import GasBoiler
from cn.modelICE.model.GasTurbine import GasTurbine
from cn.modelICE.model.HeatPump import HeatPump
from cn.modelICE.model.HeatStorage import HeatStorage
from cn.modelICE.util.DemandData import DemandData


def signal_cold(t, temporary, number, cold_stor, heat_stor, ele_stor, season, steam_or_not):    # 储冷不够

    chp = CHP(temporary, number)
    gasturbine = GasTurbine(number, temporary)
    boiler = Boiler(temporary)
    absorptionchiller = AbsorptionChiller(temporary)
    gasboiler = GasBoiler(temporary)
    heatpump = HeatPump(temporary)
    elestorage = EleStorage(temporary)
    heatstorage = HeatStorage(temporary)
    coldstorage = ColdStorage(temporary)
    demand = DemandData()
    if season == 0:
        demand_ele = demand.cold_E
        demand_cold = demand.C
        if steam_or_not == 0:  # 供冷季
            ratio_of_steam_into_chiller = 1
            demand_heat = []
            for hour in range(24):
                demand_heat.append(0)
        else:
            demand_heat = demand.cold_Steam
            ratio_of_steam_into_chiller = ((demand.sum_C / Parameters.COP_AbsorptionChiller)
                                           / (demand.sum_C / Parameters.COP_AbsorptionChiller + demand.sum_cold_Steam))
    elif season == 1:  # 供热季
        ratio_of_steam_into_chiller = 0
        demand_ele = demand.heat_E
        if steam_or_not == 0:
            demand_heat = demand.H
        else:  # 过渡季
            demand_heat = []
            for hour in range(24):
                demand_heat.append(demand.H[hour] + demand.heat_Steam[hour])
        demand_cold = []
        for hour in range(24):
            demand_cold.append(0)
    else:
        ratio_of_steam_into_chiller = 0
        demand_ele = demand.transition_E
        demand_cold = []
        if steam_or_not == 0:
            demand_heat = []
            for hour in range(24):
                demand_heat.append(0)
                demand_cold.append(0)
        else:
            demand_heat = demand.transition_Steam
            for hour in range(24):
                demand_cold.append(0)

    coldstorage_cold_out = coldstorage.get_C_out_max(cold_stor)
    coldstorage_cold_in = 0
    if demand_cold[t] > (coldstorage.get_C_out_max(cold_stor) + chp.C_out_max):
        # 储冷 + CHP + 热泵满足
        heatpump_cold_out = demand_cold[t] - coldstorage.get_C_out_max(cold_stor) - chp.C_out_max
        # 热泵产冷
        absorptionchiller_cold_out = chp.C_out_max
    else:          # 储冷+ CHP 满足
        heatpump_cold_out = 0
        absorptionchiller_cold_out = max(Parameters.pl_min * chp.C_out_max,
                                         demand_cold[t] - coldstorage.get_C_out_max(cold_stor))
    heatpump_ele_in = heatpump.get_E_in(heatpump_cold_out)  # 热泵耗电
    absorptionchiller_heat_in = absorptionchiller.get_H_in(absorptionchiller_cold_out)
    boiler_heat_out = absorptionchiller_heat_in / ratio_of_steam_into_chiller
    boiler_heat_out_users = boiler_heat_out*(1-ratio_of_steam_into_chiller)
    boiler_heat_in = boiler.get_H_in(boiler_heat_out)
    gasturbine_heat_out = boiler_heat_in
    gasturbine_ele_out = gasturbine_heat_out/chp.heat_ele_ratio
    gasturbine_fuel = gasturbine.get_fuel(gasturbine_ele_out)
    if gasturbine_ele_out >= heatpump_ele_in:
        gasturbine_ele_out_users = gasturbine_ele_out - heatpump_ele_in   # 别忘了
        heatpump_powergrid = 0
    else:
        gasturbine_ele_out_users = 0
        heatpump_powergrid = heatpump_ele_in - gasturbine_ele_out
    if demand_heat[t] <= heatstorage.get_H_out_max(heat_stor):   # 储热即可满足
        heatstorage_heat_in = boiler_heat_out_users
        heatstorage_heat_out = demand_heat[t]
        gasboiler_heat_out = 0
    elif((demand_heat[t] > heatstorage.get_H_out_max(heat_stor)) &
            (demand_heat[t] <= boiler_heat_out_users + heatstorage.get_H_out_max(heat_stor))):
        # 储热+ CHP 满足，多余存入储热
        heatstorage_heat_in = boiler_heat_out_users + heatstorage.get_H_out_max(heat_stor) - demand_heat[t]
        # 储热先供热，CHP产热再存入储热
        heatstorage_heat_out = heatstorage.get_H_out_max(heat_stor)
        gasboiler_heat_out = 0
    else:  # DemandData.H[t] > (boiler_heat_out_users + heatstorage.get_H_out_max(heat_stor)):   # 储热+ CHP + 燃气锅炉 满足
        gasboiler_heat_out = demand_heat[t] - boiler_heat_out_users - heatstorage.get_H_out_max(heat_stor)
        heatstorage_heat_in = 0
        heatstorage_heat_out = heatstorage.get_H_out_max(heat_stor)
    gasboiler_fuel = gasboiler.get_Fuel_in(gasboiler_heat_out)
    if demand_ele[t] <= elestorage.get_E_out_max(ele_stor):   # 储电满足
        elestorage_ele_in = gasturbine_ele_out_users
        elestorage_ele_out = demand_ele[t]
        powergrid_ele_out = 0
    elif((demand_ele[t] > elestorage.get_E_out_max(ele_stor)) &
            (demand_ele[t] <= elestorage.get_E_out_max(ele_stor) + gasturbine_ele_out_users)):
        # 储电 + CHP 满足，多余存入储电
        elestorage_ele_in = elestorage.get_E_out_max(ele_stor) + gasturbine_ele_out_users - demand_ele[t]
        elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
        powergrid_ele_out = 0
    else:                                          # 储电+ CHP + 电网
        elestorage_ele_in = 0
        elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
        powergrid_ele_out = (demand_ele[t] - elestorage.get_E_out_max(ele_stor) -
                             gasturbine_ele_out_users)
    result = (coldstorage_cold_in, coldstorage_cold_out, heatstorage_heat_in, heatstorage_heat_out,
              elestorage_ele_in, elestorage_ele_out, absorptionchiller_cold_out, boiler_heat_out, gasturbine_ele_out,
              heatpump_cold_out, gasboiler_heat_out, powergrid_ele_out, gasboiler_fuel, gasturbine_fuel,
              heatpump_powergrid)  # 15 项
    return result


def signal_heat(t, temporary, number, heat_stor, ele_stor, season, steam_or_not):   # 储冷> 冷需求， 储热 < 热需求

    chp = CHP(temporary, number)
    gasturbine = GasTurbine(number, temporary)
    boiler = Boiler(temporary)
    absorptionchiller = AbsorptionChiller(temporary)
    gasboiler = GasBoiler(temporary)
    elestorage = EleStorage(temporary)
    heatstorage = HeatStorage(temporary)
    demand = DemandData()
    if season == 0:
        demand_ele = demand.cold_E
        demand_cold = demand.C
        if steam_or_not == 0:  # 供冷季
            ratio_of_steam_into_chiller = 1
            demand_heat = []
            for hour in range(24):
                demand_heat.append(0)
        else:
            demand_heat = demand.cold_Steam
            ratio_of_steam_into_chiller = ((demand.sum_C / Parameters.COP_AbsorptionChiller)
                                           / (demand.sum_C / Parameters.COP_AbsorptionChiller + demand.sum_cold_Steam))
    elif season == 1:  # 供热季
        ratio_of_steam_into_chiller = 0
        demand_ele = demand.heat_E
        if steam_or_not == 0:
            demand_heat = demand.H
        else:  # 过渡季
            demand_heat = []
            for hour in range(24):
                demand_heat.append(demand.H[hour] + demand.heat_Steam[hour])
        demand_cold = []
        for hour in range(24):
            demand_cold.append(0)
    else:
        ratio_of_steam_into_chiller = 0
        demand_ele = demand.transition_E
        demand_cold = []
        if steam_or_not == 0:
            demand_heat = []
            for hour in range(24):
                demand_heat.append(0)
                demand_cold.append(0)
        else:
            demand_heat = demand.transition_Steam
            for hour in range(24):
                demand_cold.append(0)

    heatpump_powergrid = 0
    heatpump_cold_out = 0
    coldstorage_cold_out = demand_cold[t]
    heatstorage_heat_out = heatstorage.get_H_out_max(heat_stor)
    heatstorage_heat_in = 0
    if demand_heat[t] > heatstorage.get_H_out_max(heat_stor) + chp.H_out_max:   # 储热+ CHP + 燃气锅炉
        gasboiler_heat_out = demand_heat[t] - heatstorage.get_H_out_max(heat_stor) - chp.H_out_max
        boiler_heat_out_users = chp.H_out_max
    else:                                                # 储热+ CHP
        boiler_heat_out_users = max(Parameters.pl_min * chp.H_out_max,
                                    demand_heat[t] - heatstorage.get_H_out_max(heat_stor))
        gasboiler_heat_out = 0
    gasboiler_fuel = gasboiler.get_Fuel_in(gasboiler_heat_out)
    boiler_heat_out = boiler_heat_out_users / (1-ratio_of_steam_into_chiller)
    boiler_heat_in = boiler.get_H_in(boiler_heat_out)
    gasturbine_heat_out = boiler_heat_in
    gasturbine_ele_out = gasturbine_heat_out / chp.heat_ele_ratio
    gasturbine_fuel = gasturbine.get_fuel(gasturbine_ele_out)
    if boiler_heat_out * ratio_of_steam_into_chiller <= absorptionchiller.heat_in_max:    # 防止锅炉产热*P.k 大于制冷机允许进入的热量
        absorptionchiller_heat_in = boiler_heat_out * ratio_of_steam_into_chiller
    else:
        absorptionchiller_heat_in = absorptionchiller.heat_in_max
    absorptionchiller_cold_out = absorptionchiller.get_C_out(absorptionchiller_heat_in)
    coldstorage_cold_in = absorptionchiller.get_C_out(absorptionchiller_heat_in)
    if demand_ele[t] <= elestorage.get_E_out_max(ele_stor):           # 储电
        elestorage_ele_out = demand_ele[t]
        elestorage_ele_in = gasturbine_ele_out
        powergrid_ele_out = 0
    elif((demand_ele[t] > elestorage.get_E_out_max(ele_stor)) &
            (demand_ele[t] <= elestorage.get_E_out_max(ele_stor) + gasturbine_ele_out)):
        # 储电+ CHP
        elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
        elestorage_ele_in = (gasturbine_ele_out + elestorage.get_E_out_max(ele_stor)
                             - demand_ele[t] / Parameters.delttime)
        powergrid_ele_out = 0
    else:                        # 储电+ CHP + 电网
        elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
        elestorage_ele_in = 0
        powergrid_ele_out = demand_ele[t] - elestorage.get_E_out_max(ele_stor) - gasturbine_ele_out
    result = (coldstorage_cold_in, coldstorage_cold_out, heatstorage_heat_in, heatstorage_heat_out,
              elestorage_ele_in, elestorage_ele_out, absorptionchiller_cold_out, boiler_heat_out, gasturbine_ele_out,
              heatpump_cold_out, gasboiler_heat_out, powergrid_ele_out, gasboiler_fuel, gasturbine_fuel,
              heatpump_powergrid)
    return result


def signal_ele(t, temporary, number, ele_stor, season, steam_or_not):
    chp = CHP(temporary, number)
    gasturbine = GasTurbine(number, temporary)
    boiler = Boiler(temporary)
    absorptionchiller = AbsorptionChiller(temporary)
    gasboiler = GasBoiler(temporary)
    elestorage = EleStorage(temporary)
    demand = DemandData()
    if season == 0:
        demand_ele = demand.cold_E
        demand_cold = demand.C
        if steam_or_not == 0:  # 供冷季
            ratio_of_steam_into_chiller = 1
            demand_heat = []
            for hour in range(24):
                demand_heat.append(0)
        else:
            demand_heat = demand.cold_Steam
            ratio_of_steam_into_chiller = ((demand.sum_C / Parameters.COP_AbsorptionChiller)
                                           / (demand.sum_C / Parameters.COP_AbsorptionChiller + demand.sum_cold_Steam))
    elif season == 1:  # 供热季
        ratio_of_steam_into_chiller = 0
        demand_ele = demand.heat_E
        if steam_or_not == 0:
            demand_heat = demand.H
        else:  # 过渡季
            demand_heat = []
            for hour in range(24):
                demand_heat.append(demand.H[hour] + demand.heat_Steam[hour])
        demand_cold = []
        for hour in range(24):
            demand_cold.append(0)
    else:
        ratio_of_steam_into_chiller = 0
        demand_ele = demand.transition_E
        demand_cold = []
        if steam_or_not == 0:
            demand_heat = []
            for hour in range(24):
                demand_heat.append(0)
                demand_cold.append(0)
        else:
            demand_heat = demand.transition_Steam
            for hour in range(24):
                demand_cold.append(0)

    heatpump_powergrid = 0
    heatpump_cold_out = 0
    gasboiler_heat_out = 0
    gasboiler_fuel = gasboiler.get_Fuel_in(gasboiler_heat_out)
    coldstorage_cold_out = demand_cold[t]
    heatstorage_heat_out = demand_heat[t]
    elestorage_ele_in = 0
    elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
    if demand_ele[t] > (elestorage.get_E_out_max(ele_stor) + chp.E_out_max) * Parameters.delttime:      # 储电+ CHP + 电网
        powergrid_ele_out = demand_ele[t] - elestorage.get_E_out_max(ele_stor) - chp.E_out_max
        gasturbine_ele_out = chp.E_out_max  # kWh
    else:                                                     # 储电+ CHP
        gasturbine_ele_out = max(Parameters.pl_min * gasturbine.nominal,
                                 demand_ele[t] - elestorage.get_E_out_max(ele_stor))
        powergrid_ele_out = 0
    gasturbine_heat_out = gasturbine.get_heat_out(gasturbine_ele_out)
    gasturbine_fuel = gasturbine.get_fuel(gasturbine_ele_out)
    if gasturbine_heat_out <= boiler.heat_in_max:        # 防止汽轮机输出热量 > 余热锅炉允许进入热量
        boiler_heat_in = gasturbine_heat_out
    else:
        boiler_heat_in = boiler.heat_in_max
    boiler_heat_out = boiler.get_H_out(boiler_heat_in)
    boiler_heat_out_users = boiler_heat_out * (1-ratio_of_steam_into_chiller)
    absorptionchiller_heat_in = boiler_heat_out * ratio_of_steam_into_chiller
    absorptionchiller_cold_out = absorptionchiller.get_C_out(absorptionchiller_heat_in)
    coldstorage_cold_in = absorptionchiller_cold_out
    heatstorage_heat_in = boiler_heat_out_users
    result = (coldstorage_cold_in, coldstorage_cold_out, heatstorage_heat_in, heatstorage_heat_out,
              elestorage_ele_in, elestorage_ele_out, absorptionchiller_cold_out, boiler_heat_out, gasturbine_ele_out,
              heatpump_cold_out, gasboiler_heat_out, powergrid_ele_out, gasboiler_fuel, gasturbine_fuel,
              heatpump_powergrid)  # 15项
    return result


def mode_cold_first(t, temporary, number, cold_stor, heat_stor, ele_stor, season, steam_or_not):
    elestorage = EleStorage(temporary)
    heatstorage = HeatStorage(temporary)
    coldstorage = ColdStorage(temporary)
    demand = DemandData()
    if season == 0:
        demand_ele = demand.cold_E
        demand_cold = demand.C
        if steam_or_not == 0:  # 供冷季
            demand_heat = []
            for hour in range(24):
                demand_heat.append(0)
        else:
            demand_heat = demand.cold_Steam
    elif season == 1:  # 供热季
        demand_ele = demand.heat_E
        if steam_or_not == 0:
            demand_heat = demand.H
        else:  # 过渡季
            demand_heat = []
            for hour in range(24):
                demand_heat.append(demand.H[hour] + demand.heat_Steam[hour])
        demand_cold = []
        for hour in range(24):
            demand_cold.append(0)
    else:
        demand_ele = demand.transition_E
        demand_cold = []
        if steam_or_not == 0:
            demand_heat = []
            for hour in range(24):
                demand_heat.append(0)
                demand_cold.append(0)
        else:
            demand_heat = demand.transition_Steam
            for hour in range(24):
                demand_cold.append(0)

    if demand_ele[t] <= elestorage.get_E_out_max(ele_stor):
        signal_e = 0     # 储电够用
    else:
        signal_e = 1    # 储电不够用，需要开启CHP
    if demand_heat[t] <= heatstorage.get_H_out_max(heat_stor):
        signal_h = 0    # 储热够用
    else:
        signal_h = 1    # 储热不够用，需要开启CHP
    if demand_cold[t] <= coldstorage.get_C_out_max(cold_stor):
        signal_c = 0    # 储冷够用
    else:
        signal_c = 1   # 储冷不够用，需要开启CHP
    if (signal_e == 0) & (signal_h == 0) & (signal_c == 0):
        elestorage_ele_in = 0
        elestorage_ele_out = demand_ele[t]
        heatstorage_heat_in = 0
        heatstorage_heat_out = demand_heat[t]
        coldstorage_cold_in = 0
        coldstorage_cold_out = demand_cold[t]
        result = (coldstorage_cold_in, coldstorage_cold_out, heatstorage_heat_in, heatstorage_heat_out,
                  elestorage_ele_in, elestorage_ele_out, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    elif signal_c == 1:
        result = signal_cold(t, temporary, number, cold_stor, heat_stor, ele_stor, season, steam_or_not)
    elif (signal_c == 0) & (signal_h == 1):
        result = signal_heat(t, temporary, number, heat_stor, ele_stor, season, steam_or_not)
    else:  # (signal_C == 0) & (signal_H == 0) & (signal_E == 1):
        result = signal_ele(t, temporary, number, ele_stor, season, steam_or_not)
    return result
