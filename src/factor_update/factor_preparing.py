import os
import sys

import pandas as pd
import numpy as np
from scipy.io import loadmat

# 设置环境变量
path = os.getenv('GLOBAL_TOOLSFUNC_new')
if path is None:
    raise EnvironmentError(
        "环境变量 GLOBAL_TOOLSFUNC_new 未设置。\n"
        "请设置该环境变量指向 global_tools 模块路径。"
    )
sys.path.append(path)
import global_tools as gt

# 使用新的 src 路径
import src.global_setting.global_dic as glv
from src.config.unified_config import config

class FactorData_prepare:
    def __init__(self,available_date):
        self.available_date=gt.intdate_transfer(available_date)

    def index_dic_processing(self):
        return config.get_all_index_mapping('monthly')

    def index_dic_processing2(self):
        return config.get_all_index_mapping('short')
    def stock_pool_processing(self,df):
        inputpath_stockuniverse = glv.get('data_other')
        inputpath_stockuniverse_new = os.path.join(inputpath_stockuniverse, 'StockUniverse_new.csv')
        inputpath_stockuniverse_old = os.path.join(inputpath_stockuniverse, 'StockUniverse.csv')
        df_new=gt.readcsv(inputpath_stockuniverse_new)
        df_old=gt.readcsv(inputpath_stockuniverse_old)
        code_list_new=df_new['S_INFO_WINDCODE'].tolist()
        code_list_old=df_old['S_INFO_WINDCODE'].tolist()
        if len(df)==len(df_new):
            df['code']=code_list_new
        elif len(df)==len(df_old):
            df['code']=code_list_old
        return df

    def wind_factor_exposure_update(self):  # available_date这里是YYYYMMDD格式
        inputpath_factor = glv.get('input_factor_wind')
        inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
        try:
            annots = loadmat(inputpath_factor)['lnmodel_active_daily']['factorexposure'][0][0]
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            status = 1
        except:
            status = 0
        if status == 1:
            df_factor_exposure = pd.DataFrame(annots, columns=barra_name + industry_name)
            df_factor_exposure.drop(columns=['country'], inplace=True)
            df_factor_exposure=self.stock_pool_processing(df_factor_exposure)
            df_factor_exposure['valuation_date']=gt.strdate_transfer(self.available_date)
            df_factor_exposure=df_factor_exposure[['valuation_date','code']+df_factor_exposure.columns.tolist()[:-2]]
        else:
            df_factor_exposure = pd.DataFrame()
        return df_factor_exposure

    def jy_factor_exposure_update(self):  # available_date这里是YYYYMMDD格式
        inputpath_factor = glv.get('input_factor_jy')
        inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
        try:
            annots = loadmat(inputpath_factor)['lnmodel_active_daily']['factorexposure'][0][0]
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            status = 1
        except:
            status = 0
        if status == 1:
            df_factor_exposure = pd.DataFrame(annots, columns=barra_name + industry_name)
            df_factor_exposure.drop(columns=['country'], inplace=True)
            df_factor_exposure = self.stock_pool_processing(df_factor_exposure)
            df_factor_exposure['valuation_date'] = gt.strdate_transfer(self.available_date)
            df_factor_exposure = df_factor_exposure[['valuation_date', 'code'] + df_factor_exposure.columns.tolist()[:-2]]
        else:
            df_factor_exposure = pd.DataFrame()
        return df_factor_exposure
    def jy_factor_exposure_update_old(self):  # available_date这里是YYYYMMDD格式
        inputpath_factor = glv.get('input_factor_jy_old')
        inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
        try:
            annots = loadmat(inputpath_factor)['lnmodel_active_daily']['factorexposure'][0][0]
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            status = 1
        except:
            status = 0
        if status == 1:
            df_factor_exposure = pd.DataFrame(annots, columns=barra_name + industry_name)
            df_factor_exposure.drop(columns=['country'], inplace=True)
            df_factor_exposure = self.stock_pool_processing(df_factor_exposure)
            df_factor_exposure['valuation_date'] = gt.strdate_transfer(self.available_date)
            df_factor_exposure = df_factor_exposure[['valuation_date', 'code'] + df_factor_exposure.columns.tolist()[:-2]]
        else:
            df_factor_exposure = pd.DataFrame()
        return df_factor_exposure

    def wind_factor_return_update(self):
        inputpath_factor = glv.get('input_factor_wind')
        try:
            inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
            annots = loadmat(inputpath_factor)['lnmodel_active_daily']['factorret'][0][0]
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            status = 1
        except:
            status = 0
        if status == 1:
            df_factor_return = pd.DataFrame(annots, columns=barra_name + industry_name)
            df_factor_return.drop(columns=['country'], inplace=True)
            available_date2 = pd.to_datetime(self.available_date)
            available_date2 = available_date2.strftime('%Y-%m-%d')
            df_factor_return['valuation_date'] = available_date2
            df_factor_return = df_factor_return[['valuation_date'] + barra_name[1:] + industry_name]
        else:
            df_factor_return = pd.DataFrame()
        return df_factor_return

    def jy_factor_return_update(self):
        inputpath_factor = glv.get('input_factor_jy')
        try:
            inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
            annots = loadmat(inputpath_factor)['lnmodel_active_daily']['factorret'][0][0]
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            status = 1
        except:
            status = 0
        if status == 1:
            df_factor_return = pd.DataFrame(annots, columns=barra_name + industry_name)
            df_factor_return.drop(columns=['country'], inplace=True)
            available_date2 = pd.to_datetime(self.available_date)
            available_date2 = available_date2.strftime('%Y-%m-%d')
            df_factor_return['valuation_date'] = available_date2
            df_factor_return = df_factor_return[['valuation_date'] + barra_name[1:] + industry_name]
        else:
            df_factor_return = pd.DataFrame()
        return df_factor_return

    def wind_factor_stockpool_update(self):  # 计算每天因子有效的股票数据
        df_stockpool = pd.DataFrame()
        inputpath_factor = glv.get('input_factor_wind')
        inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
        try:
            df_factor_exposure = self.wind_factor_exposure_update()
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            df_factor_exposure=self.stock_pool_processing(df_factor_exposure)
            status = 1
        except:
            status = 0
        if status == 1:
            slice_df = df_factor_exposure[barra_name[1:-2]].copy()
            slice_df.dropna(inplace=True, axis=0)
            stock_code = df_factor_exposure['code'].tolist()
            available_date2 = gt.strdate_transfer(self.available_date)
            df_stockpool['code'] = stock_code
            df_stockpool['valuation_date']=available_date2
            df_stockpool=df_stockpool[['valuation_date','code']]
        else:
            df_stockpool = pd.DataFrame()
        return df_stockpool

    def jy_factor_stockpool_update(self):  # 计算每天因子有效的股票数据
        df_stockpool = pd.DataFrame()
        inputpath_factor = glv.get('input_factor_jy')
        inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
        try:
            df_factor_exposure = self.jy_factor_exposure_update()
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            df_factor_exposure = self.stock_pool_processing(df_factor_exposure)
            status = 1
        except:
            status = 0
        if status == 1:
            slice_df = df_factor_exposure[barra_name[1:-2]].copy()
            slice_df.dropna(inplace=True, axis=0)
            stock_code = df_factor_exposure['code'].tolist()
            available_date2 = gt.strdate_transfer(self.available_date)
            df_stockpool['code'] = stock_code
            df_stockpool['valuation_date'] = available_date2
            df_stockpool = df_stockpool[['valuation_date', 'code']]
        else:
            df_stockpool = pd.DataFrame()
        return df_stockpool

    def wind_factor_index_exposure_update(self,index_type):
        dic_index = self.index_dic_processing2()
        file_name = dic_index[index_type]
        inputpath_factor = glv.get('input_factor_wind')
        inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
        inputpath_indexcomponent = glv.get('output_indexcomponent')
        inputpath_indexcomponent = os.path.join(inputpath_indexcomponent, file_name)
        inputpath_stockuniverse = glv.get('data_other')
        inputpath_stockuniverse = os.path.join(inputpath_stockuniverse, 'StockUniverse_new.csv')
        df_stockuniverse = gt.readcsv(inputpath_stockuniverse)
        df_stockuniverse = df_stockuniverse[df_stockuniverse.columns.tolist()[:-2]]
        df_stockuniverse.rename(columns={'S_INFO_WINDCODE': 'code'}, inplace=True)
        stock_code = df_stockuniverse['code'].tolist()
        try:
            df_factor_exposure = self.wind_factor_exposure_update()
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            status = 1
        except:
            status = 0
        if status == 1:
            df_factor_exposure['code'] = stock_code
            inputpath_indexcomponent = gt.file_withdraw(inputpath_indexcomponent, self.available_date)
            df_component = gt.readcsv(inputpath_indexcomponent)
            df_component = df_component[['code', 'weight', 'status']]
            df_component = df_component[df_component['status'] == 1]
            index_code_list = df_component['code'].tolist()
            slice_df_stock_universe = df_stockuniverse[df_stockuniverse['code'].isin(index_code_list)]
            slice_df_stock_universe.reset_index(inplace=True)
            slice_df_stock_universe = slice_df_stock_universe.merge(df_component, on='code', how='left')
            index_code_list_index = slice_df_stock_universe['index'].tolist()
            slice_df = df_factor_exposure[barra_name[1:-2]].copy()
            slice_df.dropna(inplace=True, axis=0)
            index_list = slice_df.index
            df_barra = df_factor_exposure.iloc[index_list][barra_name[1:]]
            df_industry = df_factor_exposure.iloc[index_list][industry_name]
            df_industry.fillna(0, inplace=True)
            df_barra.fillna(0, inplace=True)
            df_final = pd.concat([df_barra, df_industry], axis=1)
            df_final.reset_index(inplace=True)
            df_final = df_final[df_final['index'].isin(index_code_list_index)]
            slice_df_stock_universe = slice_df_stock_universe[slice_df_stock_universe['index'].isin(index_list)]
            weight = slice_df_stock_universe['weight'].astype(float).tolist()
            df_final.drop(columns='index', inplace=True)
            index_factor_exposure = list(
                np.array(np.dot(np.mat(df_final.values).T, np.mat(weight).T)).flatten())
            index_factor_exposure = [index_factor_exposure]
            df_final = pd.DataFrame(np.array(index_factor_exposure), columns=barra_name[1:] + industry_name)
            available_date2 = gt.strdate_transfer(self.available_date)
            df_final['valuation_date'] = available_date2
            df_final = df_final[['valuation_date'] + barra_name[1:] + industry_name]
        else:
            df_final = pd.DataFrame()
        return df_final

    def jy_factor_index_exposure_update(self, index_type):
        dic_index = self.index_dic_processing2()
        file_name = dic_index[index_type]
        inputpath_stockuniverse = glv.get('data_other')
        inputpath_factor = glv.get('input_factor_jy')
        inputpath_stockuniverse = os.path.join(inputpath_stockuniverse, 'StockUniverse_new.csv')
        inputpath_factor = os.path.join(inputpath_factor, 'LNMODELACTIVE-' + str(self.available_date) + '.mat')
        # inputpath_indexcomponent = glv.get('output_indexcomponent')
        # inputpath_indexcomponent = os.path.join(inputpath_indexcomponent, file_name)
        df_stockuniverse = gt.readcsv(inputpath_stockuniverse)
        df_stockuniverse = df_stockuniverse[df_stockuniverse.columns.tolist()[:-2]]
        df_stockuniverse.rename(columns={'S_INFO_WINDCODE': 'code'}, inplace=True)
        stock_code = df_stockuniverse['code'].tolist()
        try:
            df_factor_exposure = self.jy_factor_exposure_update()
            barra_name, industry_name = gt.factor_name(inputpath_factor)
            status = 1
        except:
            status = 0
        if status == 1:
            df_factor_exposure['code'] = stock_code
            # inputpath_indexcomponent = gt.file_withdraw(inputpath_indexcomponent, self.available_date)
            # df_component = gt.readcsv(inputpath_indexcomponent)
            available_date2 = gt.strdate_transfer(self.available_date)
            df_component = gt.index_weight_withdraw(file_name, available_date2)
            print(df_component)
            df_component= df_component[['code', 'weight']]
            # df_component = df_component[df_component['status'] == 1]
            df_component.fillna(0,inplace=True)
            index_code_list = df_component['code'].tolist()
            slice_df_stock_universe = df_stockuniverse[df_stockuniverse['code'].isin(index_code_list)]
            slice_df_stock_universe.reset_index(inplace=True)
            slice_df_stock_universe = slice_df_stock_universe.merge(df_component, on='code', how='left')
            index_code_list_index = slice_df_stock_universe['index'].tolist()
            slice_df = df_factor_exposure[barra_name[1:-2]].copy()
            slice_df.dropna(inplace=True, axis=0)
            index_list = slice_df.index
            df_barra = df_factor_exposure.iloc[index_list][barra_name[1:]]
            df_industry = df_factor_exposure.iloc[index_list][industry_name]
            df_industry.fillna(0, inplace=True)
            df_barra.fillna(0, inplace=True)
            df_final = pd.concat([df_barra, df_industry], axis=1)
            df_final.reset_index(inplace=True)
            df_final = df_final[df_final['index'].isin(index_code_list_index)]
            slice_df_stock_universe = slice_df_stock_universe[slice_df_stock_universe['index'].isin(index_list)]
            weight = slice_df_stock_universe['weight'].astype(float).tolist()
            df_final.drop(columns='index', inplace=True)
            index_factor_exposure = list(
                np.array(np.dot(np.mat(df_final.values).T, np.mat(weight).T)).flatten())
            index_factor_exposure = [index_factor_exposure]
            df_final = pd.DataFrame(np.array(index_factor_exposure), columns=barra_name[1:] + industry_name)
            available_date2 = gt.strdate_transfer(self.available_date)
            df_final['valuation_date'] = available_date2
            df_final = df_final[['valuation_date'] + barra_name[1:] + industry_name]
        else:
            df_final = pd.DataFrame()
        return df_final

    def factor_jy_covariance_update(self):
        barra_name, industry_name = gt.factor_name_new()
        inputpath = glv.get('input_factor_cov_jy')
        input_list = os.listdir(inputpath)
        input_list = [i for i in input_list if str(i)[-3:] == 'csv']
        try:
            file_name = [file for file in input_list if self.available_date in file][0]
        except:
            print('there is not available_date that you search in the file' + inputpath)
            file_name = None
        if file_name != None:
            inputpath_result = os.path.join(inputpath, file_name)
        else:
            inputpath_result = None
        if inputpath_result != None:
            df = gt.readcsv(inputpath_result)
            df.drop(columns='Observations',inplace=True)
            df.columns=barra_name + industry_name
            df['factor_name'] = barra_name + industry_name
            df['valuation_date']=gt.strdate_transfer(self.available_date)
            df=df[['valuation_date','factor_name']+df.columns.tolist()[:-2]]
        else:
            df = pd.DataFrame()
        return df

    def factor_wind_covariance_update(self):
        barra_name, industry_name = gt.factor_name_new()
        inputpath = glv.get('input_factor_cov_wind')
        input_list = os.listdir(inputpath)
        input_list = [i for i in input_list if str(i)[-3:] == 'csv']
        try:
            file_name = [file for file in input_list if self.available_date in file][0]
        except:
            print('there is not available_date that you search in the file' + inputpath)
            file_name = None
        if file_name != None:
            inputpath_result = os.path.join(inputpath, file_name)
        else:
            inputpath_result = None
        if inputpath_result != None:
            df = gt.readcsv(inputpath_result)
            df.drop(columns='Observations', inplace=True)
            df.columns = barra_name + industry_name
            df['factor_name'] = barra_name + industry_name
            df['valuation_date'] = gt.strdate_transfer(self.available_date)
            df = df[['valuation_date', 'factor_name'] + df.columns.tolist()[:-2]]
        else:
            df = pd.DataFrame()
        return df

    def factor_jy_SpecificRisk_update(self):
        inputpath = glv.get('input_factor_specific_jy')
        input_list = os.listdir(inputpath)
        input_list = [i for i in input_list if str(i)[-3:] == 'csv']
        df_universe = gt.factor_universe_withdraw()
        stock_code_list = df_universe['S_INFO_WINDCODE'].tolist()
        try:
            file_name = [file for file in input_list if self.available_date in file and len(file) == 31][0]
        except:
            print('there is not available_date that you search in the file' + inputpath)
            file_name = None
        if file_name != None:
            inputpath_result = os.path.join(inputpath, file_name)
        else:
            inputpath_result = None
        if inputpath_result != None:
            df = gt.readcsv(inputpath_result)
            df.columns = stock_code_list
            df=df.T
            df.reset_index(inplace=True)
            df.columns=['code','specificrisk']
            df['valuation_date'] = gt.strdate_transfer(self.available_date)
            df = df[['valuation_date'] + df.columns.tolist()[:-1]]
        else:
            df = pd.DataFrame()
        return df

    def factor_wind_SpecificRisk_update(self):
        inputpath = glv.get('input_factor_specific_wind')
        input_list = os.listdir(inputpath)
        input_list = [i for i in input_list if str(i)[-3:] == 'csv']
        df_universe = gt.factor_universe_withdraw()
        stock_code_list = df_universe['S_INFO_WINDCODE'].tolist()
        try:
            file_name = [file for file in input_list if self.available_date in file and len(file) == 31][0]
        except:
            print('there is not available_date that you search in the file' + inputpath)
            file_name = None
        if file_name != None:
            inputpath_result = os.path.join(inputpath, file_name)
        else:
            inputpath_result = None
        if inputpath_result != None:
            df = gt.readcsv(inputpath_result)
            df.columns = stock_code_list
            df=df.T
            df.reset_index(inplace=True)
            df.columns=['code','specificrisk']
            df['valuation_date'] = gt.strdate_transfer(self.available_date)
            df = df[['valuation_date'] + df.columns.tolist()[:-1]]
        else:
            df = pd.DataFrame()
        return df
if __name__ == '__main__':
    working_days_list=gt.working_days_list('2024-12-30','2024-12-31')
    for date in working_days_list:
        fp=FactorData_prepare(date)
        fp.factor_jy_covariance_update()
