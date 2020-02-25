# _*_ coding: utf-8 _*_
from cn.modelICE.Parameters import Parameters
from cn.modelICE.model.CHP import CHP
from cn.modelICE.model.ColdStorage import ColdStorage
from cn.modelICE.model.EleStorage import EleStorage
from cn.modelICE.model.GasBoiler import GasBoiler
from cn.modelICE.model.GasTurbine import GasTurbine
from cn.modelICE.model.HeatPump import HeatPump
from cn.modelICE.model.HeatStorage import HeatStorage
from cn.modelICE.util.DemandData import DemandData


def mode_base_load(t, temporary, number, cold_stor, heat_stor, ele_stor, season, steam_or_not):
    chp = CHP(temporary, number)
    gasturbine = GasTurbine(number, temporary)
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

    remainder = t % 24
    if (remainder >= 7) & (remainder <= 21):  # 7:00-22:00
        gasturbine_ele_out = gasturbine.nominal
        gasturbine_fuel = gasturbine.get_fuel(gasturbine_ele_out)
        boiler_heat_out = chp.H_out_max
        boiler_heat_out_users = boiler_heat_out * (1 - ratio_of_steam_into_chiller)
        absorptionchiller_cold_out = chp.C_out_max
        if demand_ele[t] <= gasturbine_ele_out:  # 电量先由chp提供，再由储能提供
            elestorage_ele_in = gasturbine_ele_out - demand_ele[t]
            elestorage_ele_out = 0
            powergrid_ele_out = 0
        elif ((demand_ele[t] > gasturbine_ele_out)
              & (demand_ele[t] <= gasturbine_ele_out + elestorage.get_E_out_max(ele_stor))):
            elestorage_ele_in = 0
            elestorage_ele_out = gasturbine_ele_out + elestorage.get_E_out_max(ele_stor) - demand_ele[t]
            powergrid_ele_out = 0
        else:
            elestorage_ele_in = 0
            elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
            powergrid_ele_out = demand_ele[t] - gasturbine_ele_out - elestorage_ele_out

        if demand_heat[t] <= boiler_heat_out_users:
            heatstorage_heat_in = boiler_heat_out_users - demand_heat[t]
            heatstorage_heat_out = 0
            gasboiler_heat_out = 0
        elif((demand_heat[t] > boiler_heat_out_users)
             & (demand_heat[t] <= boiler_heat_out_users + heatstorage.get_H_out_max(heat_stor))):
            heatstorage_heat_in = 0
            heatstorage_heat_out = demand_heat[t] - boiler_heat_out_users
            gasboiler_heat_out = 0
        else:
            heatstorage_heat_in = 0
            heatstorage_heat_out = heatstorage.get_H_out_max(heat_stor)
            gasboiler_heat_out = demand_heat[t] - boiler_heat_out_users - heatstorage_heat_out
        gasboiler_fuel = gasboiler.get_Fuel_in(gasboiler_heat_out)

        if demand_cold[t] <= absorptionchiller_cold_out:
            coldstorage_cold_in = absorptionchiller_cold_out - demand_cold[t]
            coldstorage_cold_out = 0
            heatpump_cold_out = 0
        elif((demand_cold[t] > absorptionchiller_cold_out)
             & (demand_cold[t] <= absorptionchiller_cold_out + coldstorage.get_C_out_max(cold_stor))):
            coldstorage_cold_in = 0
            coldstorage_cold_out = demand_cold[t] - absorptionchiller_cold_out
            heatpump_cold_out = 0
        else:
            coldstorage_cold_in = 0
            coldstorage_cold_out = coldstorage.get_C_out_max(cold_stor)
            heatpump_cold_out = demand_cold[t] - absorptionchiller_cold_out - coldstorage_cold_out
        heatpump_powergrid = heatpump.get_E_in(heatpump_cold_out)
    else:  # 22:00-凌晨7：00
        gasturbine_ele_out = 0
        boiler_heat_out = 0
        absorptionchiller_cold_out = 0
        gasturbine_fuel = 0
        elestorage_ele_in = 0
        heatstorage_heat_in = 0
        coldstorage_cold_in = 0

        if demand_ele[t] <= elestorage.get_E_out_max(ele_stor):
            elestorage_ele_out = demand_ele[t]
            powergrid_ele_out = 0
        else:
            elestorage_ele_out = elestorage.get_E_out_max(ele_stor)
            powergrid_ele_out = demand_ele[t] - elestorage_ele_out

        if demand_heat[t] <= heatstorage.get_H_out_max(heat_stor):
            heatstorage_heat_out = demand_heat[t]
            gasboiler_heat_out = 0
        else:
            heatstorage_heat_out = heatstorage.get_H_out_max(heat_stor)
            gasboiler_heat_out = demand_heat[t] - heatstorage_heat_out
        gasboiler_fuel = gasboiler.get_Fuel_in(gasboiler_heat_out)

        if demand_cold[t] <= coldstorage.get_C_out_max(cold_stor):
            coldstorage_cold_out = demand_cold[t]
            heatpump_cold_out = 0
        else:
            coldstorage_cold_out = coldstorage.get_C_out_max(cold_stor)
            heatpump_cold_out = demand_cold[t] - coldstorage_cold_out
        heatpump_powergrid = heatpump.get_E_in(heatpump_cold_out)

    result = (coldstorage_cold_in, coldstorage_cold_out, heatstorage_heat_in, heatstorage_heat_out,
              elestorage_ele_in, elestorage_ele_out, absorptionchiller_cold_out, boiler_heat_out, gasturbine_ele_out,
              heatpump_cold_out, gasboiler_heat_out, powergrid_ele_out, gasboiler_fuel, gasturbine_fuel,
              heatpump_powergrid)
    return result
