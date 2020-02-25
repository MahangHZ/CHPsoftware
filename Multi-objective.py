# _*_ coding: utf-8 _*_
from cn.modelICE.genetic.GeneticConstant import Constant
from cn.modelICE.genetic.HeredityMutation import newpopulation
from cn.modelICE.genetic.Species import SpeciesOrigin
from cn.modelICE.nsGA.ParetoSorting import ParetoSorting
from cn.modelICE.nsGA.ParetoSorting import ReverseParetoSorting
from cn.modelICE.nsGA.Selecting import NextGeneration
from cn.modelICE.genetic.EconomyIndex import EconomyIndex
# import xlwt


class RemoveTheSame:
    def __init__(self, list_a):  # a是某二维数组
        self.after_removing = []
        self.after_removing.append(list_a[0])
        for compare in range(1, len(list_a)):
            duplicate_or_not = DuplicateOrNot(list_a[compare], self.after_removing)
            if duplicate_or_not.leave == 1:
                self.after_removing.append(list_a[compare])


class DuplicateOrNot:
    def __init__(self, component, the_list):  # component是元素(一维数组),the list是二位数组
        self.status = []  # 0 不留下 1 留下
        for l in range(0, len(the_list), 1):
            self.status.append(1)
            for q in range(0, len(component), 1):
                if component[q] != the_list[l][q]:
                    self.status[l] = 0
                    break
        if sum(self.status) == 0:
            self.leave = 1
        else:
            self.leave = 0


class MultiObjectiveGA:
    def __init__(self, times, mover, number, mode, way_pareto, storage_or_not, steam_or_not, back_to_grid_or_not):
        # way_pareto=0:正pareto，其他：反pareto  steam_or_not = 0:无蒸汽需求 其他：有蒸汽需求
        if steam_or_not == 1:  # 若有蒸汽需求，必须是以冷热定电模式运行
            mode = 0
        population = SpeciesOrigin(mover, number, Constant.population_size, storage_or_not).population
        next_species_result = population
        print("the original", next_species_result)
        self.pareto_best = []
        if way_pareto == 0:
            pareto_sorting = ParetoSorting(mover, next_species_result, number, mode, steam_or_not)
        else:
            pareto_sorting = ReverseParetoSorting(mover, next_species_result, number, mode, steam_or_not)
        print("original_best:", pareto_sorting.pareto_sorting_result)

        self.list_evaluation_of_cost = []
        self.list_evaluation_of_emission = []
        self.list_evaluation_of_pei = []
        self.average_evaluation_of_cost = []
        self.average_evaluation_of_emission = []
        self.average_evaluation_of_pei = []

        for i in range(times):
            solution_best_of_this_generation = []
            new_population_first = newpopulation(next_species_result, number, storage_or_not)  # 遗传变异
            # print("new_population:", new_population)
            new_population = RemoveTheSame(new_population_first).after_removing
            selecting_process = NextGeneration(mover, new_population, number, mode, way_pareto, steam_or_not)
            selecting_queue = selecting_process.selecting_queue

            self.list_evaluation_of_cost.append(selecting_process.cost_pareto_best)
            self.list_evaluation_of_emission.append(selecting_process.emission_pareto_best)
            self.list_evaluation_of_pei.append(selecting_process.pei_pareto_best)
            self.average_evaluation_of_cost.append(sum(selecting_process.cost_pareto_best)
                                                   / len(selecting_process.cost_pareto_best))
            self.average_evaluation_of_emission.append(sum(selecting_process.emission_pareto_best)
                                                       / len(selecting_process.emission_pareto_best))
            self.average_evaluation_of_pei.append(sum(selecting_process.pei_pareto_best)
                                                  / len(selecting_process.pei_pareto_best))
            print("selecting_queue:", selecting_queue)
            next_species_result = []
            for m in range(Constant.population_size):
                next_species_result.append(new_population[selecting_queue[m]])
            print("next_species_result:", next_species_result)

            cost_best_of_this_generation = []
            emission_best_of_this_generation = []
            pei_best_of_this_generation = []

            for n in range(selecting_process.length_of_best):
                solution_best_of_this_generation.append(next_species_result[n])
                cost_best_of_this_generation.append(selecting_process.cost_pareto_best[n])
                emission_best_of_this_generation.append(selecting_process.emission_pareto_best[n])
                pei_best_of_this_generation.append(selecting_process.pei_pareto_best[n])
            self.pareto_best.append(solution_best_of_this_generation)
            print("time:", i, self.pareto_best[i])  # 每代最优解集合
            print("solution_best_of_this_generation:", solution_best_of_this_generation)
            print("cost:", cost_best_of_this_generation)
            print("emission:", emission_best_of_this_generation)
            print("pei:", pei_best_of_this_generation)
        set_of_best = self.pareto_best[times - 1]
        remove_the_same = RemoveTheSame(set_of_best)  # 去除重复项
        set_of_best_after = remove_the_same.after_removing
        if way_pareto == 0:
            pareto_again = ParetoSorting(mover, set_of_best_after, number, mode, steam_or_not)
        else:
            pareto_again = ReverseParetoSorting(mover, set_of_best_after, number, mode, steam_or_not)
        self.final_pareto_best = pareto_again.pareto_sorting_best
        self.final_cost_best = pareto_again.pareto_sorting_best_cost_result
        self.final_emission_best = pareto_again.pareto_sorting_best_emission_result
        self.final_pei_best = pareto_again.pareto_sorting_best_pei_result
        self.final_ele_waste_0 = pareto_again.ele_waste_0
        self.final_ele_waste_1 = pareto_again.ele_waste_1
        self.final_ele_waste_2 = pareto_again.ele_waste_2
        self.final_heat_waste = pareto_again.heat_waste
        self.final_cold_waste = pareto_again.cold_waste
        self.final_irr = []
        self.final_payback_period = []
        self.final_return_on_capital = []
        for sequence in range(len(self.final_pareto_best)):
            economy_index = EconomyIndex(self.final_pareto_best[sequence], mover, number, mode, steam_or_not,
                                         back_to_grid_or_not)
            self.final_irr.append(economy_index.IRR)
            self.final_payback_period.append(economy_index.PaybackPeriod)
            self.final_return_on_capital.append(economy_index.ReturnOnCapital)


# times, mover, number, mode, way_pareto, storage_or_not, steam_or_not, back_to_grid_or_not
# mode = 0:以冷热定电  mode = 1:以电定冷热 mode=2：base load
# way_pareto:0正1反
# storage_or_not:0无1有
# steam_or_not:0无1有
# back_to_grid_or_not : 0不上网  1上网
# number = 1:不用内燃机或燃气轮机数据库 number = 2 - 37 用内燃机或燃气轮机数据库
for which_storage in (0, 2, 1):
    for which_mode in (0, 3, 1):
        a = MultiObjectiveGA(Constant.calculate_times, 0, 2, which_mode, 0, which_storage, 0, 0)
        print("最后一代最优解：", a.final_pareto_best)
        print("最后一代最优解cost：", a.final_cost_best)
        print("最后一代最优解emission：", a.final_emission_best)
        print("最后一代最优解PER：", a.final_pei_best)
        print("最后一代最优解IRR：", a.final_irr)
        print("最后一代最优解PaybackPeriod：", a.final_payback_period)
        print("最后一代最优解ReturnOnCapital：", a.final_return_on_capital)
        print("最后一代最优解ele_waste_0：", a.final_ele_waste_0)
        print("最后一代最优解ele_waste_1：", a.final_ele_waste_1)
        print("最后一代最优解ele_waste_2：", a.final_ele_waste_2)
        print("最后一代最优解heat_waste：", a.final_heat_waste)
        print("最后一代最优解cold_waste：", a.final_cold_waste)
        print("每代最优list层层筛选cost进化：", a.list_evaluation_of_cost)
        print("每代最优list层层筛选emission进化：", a.list_evaluation_of_emission)
        print("每代最优list层层筛选pei进化：", a.list_evaluation_of_pei)
