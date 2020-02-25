# _*_ coding: utf-8 _*_
from cn.modelICE.Parameters import Parameters
from cn.modelICE.genetic.constriction.mode_cold_first import mode_cold_first
from cn.modelICE.genetic.constriction.mode_ele_frist import mode_ele_first
from cn.modelICE.genetic.constriction.mode_base_load import mode_base_load
from cn.modelICE.model.CHP import CHP
from cn.modelICE.model.ColdStorage import ColdStorage
from cn.modelICE.model.EleStorage import EleStorage
from cn.modelICE.model.GasBoiler import GasBoiler
from cn.modelICE.model.Boiler import Boiler
from cn.modelICE.model.AbsorptionChiller import AbsorptionChiller
from cn.modelICE.model.HeatPump import HeatPump
from cn.modelICE.model.HeatStorage import HeatStorage
from cn.modelICE.util.DemandData import DemandData


def running_judge(temporary, number, season, mode, steam_or_not):
    heatstor = 0
    coldstor = 0
    elestor = 0
    cold_stor_list = []
    heat_stor_list = []
    ele_stor_list = []
    chp = CHP(temporary, number)
    gasboiler = GasBoiler(temporary)
    heatpump = HeatPump(temporary)
    absorption_chiller = AbsorptionChiller(temporary)
    boiler = Boiler(temporary)
    elestorage = EleStorage(temporary)
    heatstorage = HeatStorage(temporary)
    coldstorage = ColdStorage(temporary)
    totalfuel_gasturbine = 0
    totalfuel_gasboiler = 0
    totalele_powergrid = 0
    total_ele_waste = 0
    total_heat_waste = 0
    total_cold_waste = 0
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

    for t in range(0, demand.E_sheetnrows - 1, Parameters.delttime):
        cold_stor_list.append(coldstor)
        heat_stor_list.append(heatstor)
        ele_stor_list.append(elestor)
        if mode == 0:  # 以冷定热再定电
            if season != 0:
                chp_heat = chp.H_out_max
                chp_cold = 0
            else:  # season = 0, 供冷季, ratio_of_steam_into_chiller一定不是0
                chp_cold = min(demand_cold[t], chp.C_out_max)
                boiler_heat_out = absorption_chiller.get_H_in(chp_cold) / ratio_of_steam_into_chiller
                chp_heat = boiler_heat_out * (1 - ratio_of_steam_into_chiller)
            if ((demand_heat[t] > heatstorage.get_H_out_max(heatstor) + chp_heat + gasboiler.nominal)
                    | (demand_cold[t] > coldstorage.get_C_out_max(coldstor) + chp_cold + heatpump.nominal)):
                return 0
            else:
                result = mode_cold_first(t, temporary, number, coldstor, heatstor, elestor, season, steam_or_not)
        elif mode == 1:  # 以电定热再定冷
            chp_ele = min(demand_ele[t], chp.E_out_max)
            boiler_heat_in = chp_ele / chp.heat_ele_ratio
            chp_heat = boiler.get_H_out(boiler_heat_in) * (1 - ratio_of_steam_into_chiller)
            chp_cold = boiler.get_H_out(boiler_heat_in) * ratio_of_steam_into_chiller * Parameters.COP_AbsorptionChiller
            if ((demand_heat[t] > heatstorage.get_H_out_max(heatstor) + chp_heat + gasboiler.nominal)
                    | (demand_cold[t] > coldstorage.get_C_out_max(coldstor) + chp_cold + heatpump.nominal)):
                return 0
            else:
                result = mode_ele_first(t, temporary, number, coldstor, heatstor, elestor, season, steam_or_not)
        else:  # mode = 2 base load运行
            if (t >= 7) & (t <= 21):
                if ((demand_heat[t] > heatstorage.get_H_out_max(heatstor)
                     + chp.H_out_max * (1 - ratio_of_steam_into_chiller) + gasboiler.nominal)
                   | (demand_cold[t] > coldstorage.get_C_out_max(coldstor)
                      + chp.C_out_max * ratio_of_steam_into_chiller + heatpump.nominal)):
                    return 0

            else:
                if ((demand_heat[t] > heatstorage.get_H_out_max(heatstor) + gasboiler.nominal)
                        | (demand_cold[t] > coldstorage.get_C_out_max(coldstor) + heatpump.nominal)):
                    return 0
            result = mode_base_load(t, temporary, number, coldstor, heatstor, elestor, season, steam_or_not)
        coldstorage_cold_in = result[0]
        coldstorage_cold_out = result[1]
        heatstorage_heat_in = result[2]
        heatstorage_heat_out = result[3]
        elestorage_ele_in = result[4]
        elestorage_ele_out = result[5]
        powergrid_ele_out = result[11]
        gasboiler_fuel = result[12]
        gasturbine_fuel = result[13]
        totalfuel_gasturbine = totalfuel_gasturbine + gasturbine_fuel
        totalfuel_gasboiler = totalfuel_gasboiler + gasboiler_fuel
        totalele_powergrid = totalele_powergrid + powergrid_ele_out
        elestor = elestorage.get_S(elestor, elestorage_ele_in, elestorage_ele_out)
        if elestor > elestorage.nominal:
            total_ele_waste = total_ele_waste + elestor - elestorage.nominal
            elestor = elestorage.nominal  # 若冲进的电过多，则剩余部分浪费
        heatstor = heatstorage.get_S(heatstor, heatstorage_heat_in, heatstorage_heat_out)
        if heatstor > heatstorage.nominal:
            total_heat_waste = total_heat_waste + heatstor - heatstorage.nominal
            heatstor = heatstorage.nominal
        coldstor = coldstorage.get_S(coldstor, coldstorage_cold_in, coldstorage_cold_out)
        if coldstor > coldstorage.nominal:
            total_cold_waste = total_cold_waste + coldstor - coldstorage.nominal
            coldstor = coldstorage.nominal
    output = (1, totalfuel_gasturbine, totalfuel_gasboiler, totalele_powergrid, total_ele_waste,
              total_heat_waste, total_cold_waste)
    return output
