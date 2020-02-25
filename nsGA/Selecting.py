from cn.modelICE.nsGA.ParetoSorting import ParetoSorting
from cn.modelICE.nsGA.ParetoSorting import ReverseParetoSorting
from cn.modelICE.nsGA.ParetoSorting import ResultsOfObjectives
from cn.modelICE.nsGA.Congestion import CongestionDistance
from cn.modelICE.genetic.GeneticConstant import Constant
from cn.modelICE.genetic.Translation import translation


class NextGeneration:
    def __init__(self, mover, new_population, number, mode, way_pareto, steam_or_not):
        selecting = Selecting(mover, new_population, number, mode, way_pareto, steam_or_not)

        self.ele_waste_0 = selecting.ele_waste_0
        self.ele_waste_1 = selecting.ele_waste_1
        self.ele_waste_2 = selecting.ele_waste_2
        self.heat_waste = selecting.heat_waste
        self.cold_waste = selecting.cold_waste

        self.cost_pareto_best = selecting.pareto_sorting_best_cost_result
        self.emission_pareto_best = selecting.pareto_sorting_best_emission_result
        self.pei_pareto_best = selecting.pareto_sorting_best_pei_result

        self.selecting_queue = selecting.chosen
        self.pareto_sorting_best = selecting.pareto_sorting_best
        self.length_of_best = selecting.length_of_best


class Selecting:
    def __init__(self, mover, new_population, number, mode, way_pareto, steam_or_not):
        translation_result = translation(new_population)
        if way_pareto == 0:
            pareto_sorting = ParetoSorting(mover, new_population, number, mode, steam_or_not)
        else:
            pareto_sorting = ReverseParetoSorting(mover, new_population, number, mode, steam_or_not)

        self.ele_waste_0 = pareto_sorting.ele_waste_0
        self.ele_waste_1 = pareto_sorting.ele_waste_1
        self.ele_waste_2 = pareto_sorting.ele_waste_2
        self.heat_waste = pareto_sorting.heat_waste
        self.cold_waste = pareto_sorting.cold_waste

        self.pareto_sorting_best = pareto_sorting.pareto_sorting_best

        self.pareto_sorting_best_cost_result = pareto_sorting.pareto_sorting_best_cost_result
        self.pareto_sorting_best_emission_result = pareto_sorting.pareto_sorting_best_emission_result
        self.pareto_sorting_best_pei_result = pareto_sorting.pareto_sorting_best_pei_result

        hierarchy_list = pareto_sorting.pareto_sorting_result
        # print("hierarchy list:", hierarchy_list)
        self.chosen = []  # 被选中的编号
        chosen_quantity = 0
        i = 0
        # 先把级别高的帕累托层级选入下一代，直到超出population_size
        while chosen_quantity + len(hierarchy_list[i]) < Constant.population_size:
            chosen_quantity = chosen_quantity + len(hierarchy_list[i])
            for j in range(len(hierarchy_list[i])):
                self.chosen.append(hierarchy_list[i][j])
            i = i + 1
        # print("hierarchy入选部分：", self.chosen)
        # 计算下一代剩余位置，将此层的帕累托解写出，translation_result结果也写出
        position_left = Constant.population_size - chosen_quantity
        if position_left != 0:
            translation_result_to_be_queued = []
            for m in range(len(hierarchy_list[i])):
                translation_result_to_be_queued.append(translation_result[hierarchy_list[i][m]])
        # 将此层的translation_result代入拥挤度计算中，排序  final_choosing_queue为排序结果
            congestion_queue = QueuingForCertainHierarchyTranslationResult(mover, translation_result_to_be_queued,
                                                                           number, mode, steam_or_not)
            final_choosing_queue = congestion_queue.final_choosing_queue
        # 将final_choosing_queue的排序结果代入要排序的hierarchy_list[i]中，按position_left结果，选hierarchy_list[i]中标号
        # （即为父代+遗传变异后的种群中，最终被选入下一代的染色体的标号）
            for m in range(position_left):
                serial_number = final_choosing_queue[m]
                self.chosen.append(hierarchy_list[i][serial_number])
            # print("hierarchy+congestion选择：", self.chosen)
        if len(hierarchy_list[0]) <= Constant.population_size:
            self.length_of_best = len(hierarchy_list[0])
        else:
            self.length_of_best = Constant.population_size


class QueuingForCertainHierarchyTranslationResult:
    def __init__(self, mover, translation_result_to_be_queued, number, mode, steam_or_not):
        # hierarchy_to_be_queued是待排序（拥挤度排序）的某帕累托层级，数组
        results_of_objectives = ResultsOfObjectives(mover, translation_result_to_be_queued, number, mode, steam_or_not)
        cost_list = results_of_objectives.cost_objective
        emission_list = results_of_objectives.emission_objective
        pei_list = results_of_objectives.pei_objective
        chosen_list_number = Constant.chosen_list_number  # 依据哪个函数来排序
        congestion = CongestionDistance(cost_list, emission_list, pei_list, chosen_list_number)
        number_to_choose = congestion.congestion_queue  # 选translation_result_to_be_queued的顺序
        # print("congestion选中的:", number_to_choose)
        self.final_choosing_queue = number_to_choose
