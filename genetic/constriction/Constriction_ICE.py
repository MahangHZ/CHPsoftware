# _*_ coding: utf-8 _*_
from cn.modelICE.genetic.constriction.ICE_mode_coldheat_first import SeasonColdCHF
from cn.modelICE.genetic.constriction.ICE_mode_coldheat_first import SeasonHeatCHF
# from cn.modelICE.genetic.constriction.ICE_mode_coldheat_first import SeasonHeatColdCHF
# from cn.modelICE.genetic.constriction.ICE_mode_coldheat_first import SeasonHeatAllCHF
from cn.modelICE.genetic.constriction.ICE_mode_coldheat_first import SeasonHeatColdAllCHF
from cn.modelICE.genetic.constriction.ICE_mode_coldheat_first import SeasonElectricOnlyCHF
from cn.modelICE.genetic.constriction.ICE_mode_ele_first import SeasonColdEF
from cn.modelICE.genetic.constriction.ICE_mode_ele_first import SeasonHeatEF
# from cn.modelICE.genetic.constriction.ICE_mode_ele_first import SeasonHeatColdEF
from cn.modelICE.genetic.constriction.ICE_mode_ele_first import SeasonElectricOnlyEF
from cn.modelICE.genetic.constriction.ICE_base_load import SeasonColdBL
from cn.modelICE.genetic.constriction.ICE_base_load import SeasonHeatBL
from cn.modelICE.genetic.constriction.ICE_base_load import SeasonElectricOnlyBL


class ConstrictionICE:
    def __init__(self, temporary, number, season, mode, steam_or_not):  # 此处temporary是翻译过的
        if steam_or_not == 0:  # 无蒸汽需求
            if mode == 0:  # 以冷热定电
                if season == 0:  # 制冷模式
                    show = SeasonColdCHF(temporary, number)
                elif season == 1:  # 制热模式  不含热蒸汽
                    show = SeasonHeatCHF(temporary, number)
                else:  # season == 2 仅有电 过渡季
                    show = SeasonElectricOnlyCHF(temporary, number)
                '''
                else:  # season == 3 冷热电模式，不含热蒸汽
                    show = SeasonHeatColdCHF(temporary, number)
                
                elif season == 4:   # 制热模式 含热蒸汽
                    show = SeasonHeatAllCHF(temporary, number)
                else:  # season == 5 冷热电模式，含热蒸汽
                    show = SeasonHeatColdAllCHF(temporary, number)
                '''
            elif mode == 1:  # mode == 1 以电定冷热（此时定无热蒸汽需求）
                if season == 0:  # 制冷模式
                    show = SeasonColdEF(temporary, number)
                elif season == 1:  # 制热模式  不含热蒸汽
                    show = SeasonHeatEF(temporary, number)
                else:  # 仅有电
                    show = SeasonElectricOnlyEF(temporary, number)
                # else:  # season == 3 冷热电模式，不含热蒸汽
                    # show = SeasonHeatColdEF(temporary, number)
            else:  # mode == 2 base load模式
                if season == 0:  # 供冷季，冷+电
                    show = SeasonColdBL(temporary, number)
                elif season == 1:  # 供热季，热+ 电
                    show = SeasonHeatBL(temporary, number)
                else:  # season == 2 仅有电
                    show = SeasonElectricOnlyBL(temporary, number)
        else:  # 有蒸汽需求
            show = SeasonHeatColdAllCHF(temporary, number, season)

        self.judge = show.judge
        if self.judge == 1:
            self.fuel_sum = sum(show.fuel)
            self.ele_bought_sum = sum(show.ele_bought)

            self.ele_waste = sum(show.ele_waste)
            if season == 0:
                self.cold_waste = sum(show.cold_waste)
                self.heat_waste = 0
            elif season == 1:
                self.cold_waste = 0
                self.heat_waste = sum(show.heat_waste)
            else:
                self.cold_waste = 0
                self.heat_waste = 0
        else:
            self.ele_waste = pow(10, 20)
            self.cold_waste = pow(10, 20)
            self.heat_waste = pow(10, 20)


'''
a = [22000, 8000, 20000, 98000, 162000, 92000, 84000, 100000]
b = SeasonHeatBL(a, 1)
print("supplying heat")
print("ele_ice:", b.ele_ice)
print("heat:", b.heat)
print("heat_gas_boiler:", b.heat_gas_boiler)
print("heat_stor:", b.heat_stor)
print("ele_stor:", b.ele_stor)
print("ele_waste:", b.ele_waste)
print("heat_waste:", b.heat_waste)

c = SeasonColdBL(a, 1)
print("supplying cold")
print("ele_ice:", c.ele_ice)
print("cold:", c.cold_absorption_chiller)
print("cold_heat_pump:", c.cold_heat_pump)
print("cold_stor:", c.cold_stor)
print("ele_stor:", c.ele_stor)
print("ele_waste:", c.ele_waste)
print("cold_waste:", c.cold_waste)

d = SeasonElectricOnlyBL(a, 1)
print("supplying only ele")
print("ele_ice:", d.ele_ice)
print("ele_stor:", d.ele_stor)
print("ele_waste:", d.ele_waste)
'''
