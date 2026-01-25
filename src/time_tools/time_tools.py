import datetime
from datetime import date
import os
import sys

import pandas as pd

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
class time_tools:
    def time_zoom_decision(self):
        inputpath = glv.get('time_tools_config')
        df_config = pd.read_excel(inputpath, sheet_name='time_zoon')
        df_config['start_time'] = df_config['start_time'].apply(lambda x: x.strftime("%H:%M"))
        df_config['end_time'] = df_config['end_time'].apply(lambda x: x.strftime("%H:%M"))
        time_now = datetime.datetime.now().strftime("%H:%M")
        df_config['now'] = time_now
        df_config['status'] = 'Not_activate'
        df_config.loc[(df_config['now'] >= df_config['start_time']) & (df_config['now'] <= df_config['end_time']), [
            'status']] = 'activate'
        zoom_list = df_config[df_config['status'] == 'activate']['zoom_name'].tolist()
        return zoom_list[0]

    def target_date_decision_score(self):
        inputpath = glv.get('time_tools_config')
        df_config = pd.read_excel(inputpath, sheet_name='critical_time')
        critical_time = df_config[df_config['zoom_name'] == 'time_1']['critical_time'].tolist()[0]
        critical_time = critical_time.strftime("%H:%M")
        if gt.is_workday_auto() == True:
            today = date.today()
            next_day = gt.next_workday_calculate(today)
            time_now = datetime.datetime.now().strftime("%H:%M")
            if time_now >= critical_time:
                return next_day
            else:
                today = gt.strdate_transfer(today)
                return today
        else:
            today = date.today()
            next_day = gt.next_workday_calculate(today)
            return next_day

    def target_date_decision_mkt(self):
        inputpath = glv.get('time_tools_config')
        df_config = pd.read_excel(inputpath, sheet_name='critical_time')
        critical_time = df_config[df_config['zoom_name'] == 'time_2']['critical_time'].tolist()[0]
        critical_time = critical_time.strftime("%H:%M")
        if gt.is_workday_auto() == True:
            today = date.today()
            last_day = gt.last_workday_calculate(today)
            time_now = datetime.datetime.now().strftime("%H:%M")
            if time_now >= critical_time:
                return today
            else:
                return last_day
        else:
            today = date.today()
            last_day = gt.last_workday_calculate(today)
            return last_day

    def target_date_decision_factor(self):
        inputpath = glv.get('time_tools_config')
        df_config = pd.read_excel(inputpath, sheet_name='critical_time')
        critical_time = df_config[df_config['zoom_name'] == 'time_3']['critical_time'].tolist()[0]
        critical_time = critical_time.strftime("%H:%M")
        if gt.is_workday_auto() == True:
            today = date.today()
            last_day = gt.last_workday_calculate(today)
            time_now = datetime.datetime.now().strftime("%H:%M")
            if time_now >= critical_time:
                return today
            else:
                return last_day
        else:
            today = date.today()
            last_day = gt.last_workday_calculate(today)
            return last_day




