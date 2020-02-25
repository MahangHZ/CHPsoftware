# _*_ coding: utf-8 _*_


class Parameters:
    heatvalue = 38931  # 天然气热值 KJ/m³
    delttime = 1  # h 时间间隔
    effi_Boiler = 0.8  # 余热锅炉热效率，待定
    COP_AbsorptionChiller = 1.3  # 制冷机COP， 待定
    COP_DoubleEffectAbsorptionChiller_double = 1.3
    COP_DoubleEffectAbsorptionChiller_single = 0.7
    COP_DoubleEffectAbsorptionChiller_heat = 0.7
    ratio_cold_nominal_to_heat_nominal_DoubleEffectAbsorptionChiller = 0.7
    effi_GasBoiler = 0.8  # 燃气锅效率，待定
    effi_HeatPump = 3  # 热泵COP，《魏大钧》
    effi_HeatStorage_relea = 0.95  # 储热放能效率，待定
    effi_HeatStorage_abs = 0.95  # 储热充能效率，待定
    effi_ColdStorage_relea = 0.95  # 储冷放能效率，待定
    effi_ColdStorage_abs = 0.95  # 储冷充能效率，待定
    effi_EleStorage_relea = 0.95  # 蓄电池放电效率，待定
    effi_EleStorage_abs = 0.95  # 蓄电池充电效率，待定
    effi_grid = 0.3  # 电网发电效率
    loss_HeatStorage = 0.05  # 储热能量耗散系数，待定
    loss_ColdStorage = 0.05  # 储冷能量耗散系数，待定
    loss_EleStorage = 0.05  # 储电能量耗散系数，待定
    the_giant_number = pow(10, 50)  # 染色体不符合限制的惩罚值

    # 以下为经济性参数
    price_Gas = 2  # 元|m³
    price_Ele = 1  # 元| kWh
    base_rate = 0.1  # 瞎写的
    price_ele_sold = 1  # 元| kWh
    price_heat_sold = 2  # 元| kWh
    price_steam_sold = 2  # 元| kWh
    price_cold_sold = 1  # 元| kWh
    price_sold_back_to_grid = 0.7  # 元| kWh  余电售回给电网
    maintenance_factor = 0.025  # 年运行维护费用比例系数（来自魏大钧）
    life_time = 10  # 使用寿命，年
    income_tax_rate = 0.25  # 所得税税率
    loan_factor = 0.5  # 贷款比例

    # 以下为成本参数：
    cost_GasTurbine_per_kw = 3000  # 元/kW
    cost_InternalCombustionEngine_per_kw = 3000
    cost_Boiler_per_kw = 300
    cost_AbsorptionChiller = 1200
    cost_GasBoiler_per_kw = 300
    cost_HeatPump_per_kw = 970
    cost_HeatStorage_per_kwh = 230
    cost_ColdStorage_per_kwh = 230
    cost_EleStorage_per_kwh = 230

    # 以下为emission参数：
    factor_co2_gas = 0.2  # kg/kWh
    factor_co2_grid = 0.749  # kg/kWh

    # 以下为供冷季，供暖季，过渡季天数
    days_of_cold = 122
    days_of_heat = 90
    days_of_transition = 153

    # 以下为对内燃机的负荷率限制
    pl_min = 0.2

    def __init__(self):
        pass

    @staticmethod
    def get_nominal_GasTurbine(temporary):
        nominal_GasTurbine = temporary[0]
        return nominal_GasTurbine

    @staticmethod
    def get_nominal_InternalCombustionEngine(temporary):
        nominal_internal_combustion_engine = temporary[0]
        return nominal_internal_combustion_engine

    @staticmethod
    def get_nominal_Boiler(temporary):
        nominal_Boiler = temporary[1]
        return nominal_Boiler

    @staticmethod
    def get_nominal_AbsorptionChiller(temporary):
        nominal_AbsorptionChiller = temporary[2]
        return nominal_AbsorptionChiller

    @staticmethod
    def get_nominal_GasBoiler(temporary):
        nominal_GasBoiler = temporary[3]
        return nominal_GasBoiler

    @staticmethod
    def get_nominal_HeatPump(temporary):
        nominal_HeatPump = temporary[4]
        return nominal_HeatPump

    @staticmethod
    def get_nominal_HeatStorage(temporary):
        nominal_HeatStorage = temporary[5]
        return nominal_HeatStorage

    @staticmethod
    def get_nominal_ColdStorage(temporary):
        nominal_ColdStorage = temporary[6]
        return nominal_ColdStorage

    @staticmethod
    def get_nominal_EleStorage(temporary):
        nominal_EleStorage = temporary[7]
        return nominal_EleStorage


