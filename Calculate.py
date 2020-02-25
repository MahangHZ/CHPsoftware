# _*_ coding: utf-8 _*_
from cn.modelICE.genetic.Fitness import fitness
from cn.modelICE.genetic.Fitness import FitnessICE
from cn.modelICE.genetic.GeneticConstant import Constant
from cn.modelICE.genetic.HeredityMutation import newpopulation
from cn.modelICE.genetic.NextSpecies import nextspecies
from cn.modelICE.genetic.CostMin import annual_cost_min
from cn.modelICE.genetic.CostMin import AnnualCostMinICE
from cn.modelICE.genetic.Selection import selection
from cn.modelICE.genetic.Species import SpeciesOrigin
from cn.modelICE.genetic.Translation import translation
from cn.modelICE.genetic.EconomyIndex import EconomyIndex


# newspecies 是每代种群，10个，newpopulation是每代父本遗传变异后形成的子代，大于10个
def calculate(times, mover, number, mode, storage_or_not, steam_or_not, back_to_grid_or_not):
    if steam_or_not == 1:  # 若有蒸汽需求，必须是以冷热定电模式运行
        mode = 0
    population = SpeciesOrigin(mover, number, Constant.population_size, storage_or_not).population
    next_species_result = population
    print("the original", next_species_result)
    min_result_list = []
    min_powerselection_list = []
    for i in range(times):
        translation_result = translation(next_species_result)  # translation result 也是二维数组
        if mover == 0:
            cost_min_result = annual_cost_min(translation_result, number, mode, steam_or_not)
            min_result = cost_min_result[0]
            minresult_number = cost_min_result[1]
        else:
            cost_min_result = AnnualCostMinICE(translation_result, number, mode, steam_or_not)
            min_result = cost_min_result.min_cost_result
            minresult_number = cost_min_result.array_number
        min_result_list.append(min_result)
        min_temporary = next_species_result[minresult_number]
        min_powerselection_list.append(min_temporary)
        print("time:", i, "minresult:", min_result)
        print("")
        newpopulation_result = newpopulation(next_species_result, number, storage_or_not)
        print("new population length:", len(newpopulation_result))
        if mover == 0:
            fitness_result = fitness(newpopulation_result, number, mode, steam_or_not)
        else:
            fitness_result = FitnessICE(newpopulation_result, number, mode, steam_or_not).fitness1
        selection_result = selection(fitness_result)
        next_species_result = nextspecies(newpopulation_result, selection_result)
    print("min_cost_result_list:", min_result_list)
    perfect = min(min_result_list)
    print("the most min:", round(perfect, 2))
    perfect_number = 0
    while min_result_list[perfect_number] != perfect:
        perfect_number = perfect_number + 1
    print("optimum temporary selection:", min_powerselection_list[perfect_number])
    economy_index = EconomyIndex(min_powerselection_list[perfect_number], mover, number, mode, steam_or_not,
                                 back_to_grid_or_not)
    print("IRR:", economy_index.IRR)
    print("PaybackPeriod:", economy_index.PaybackPeriod)
    print("ReturnOnCapital:", economy_index.ReturnOnCapital)
    # 将数组 min_result_list (遗传算法每次最优结果)的值写入excel中

    return 0


# times, mover, number, mode, storage_or_not, steam_or_not, back_to_grid_or_not
# mover = 0:燃气轮机 mover = 1:内燃机
# season 0:冷模式，1 热模式（无蒸汽） 2 冷热模式（无整齐）3 热模式（有蒸汽） 4 冷热模式（有蒸汽）
# mode = 0:以冷热定电  mode = 1:以电定冷热 mode=2：base load
# way_pareto:0正1反
# storage_or_not:0无1有
# steam_or_not:0无1有
# back_to_grid_or_not : 0不上网  1上网
# number = 1:不用内燃机或燃气轮机数据库 number = 2 - 37 用内燃机或燃气轮机数据库
calculate(Constant.calculate_times, 0, 2, 0, 0, 1, 0)
