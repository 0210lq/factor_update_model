import pandas as pd
import os
from pathlib import Path
def get_top_dir_path(current_path, levels_up=2):
    """
    从当前路径向上退指定层数，获取顶层目录的完整路径。
    :param current_path: 当前路径（Path对象）
    :param levels_up: 向上退的层数，默认为2
    :return: 顶层目录的完整路径（Path对象）
    """
    for _ in range(levels_up):
        current_path = current_path.parent
    return current_path
def config_path_finding():
    inputpath = os.path.split(os.path.realpath(__file__))[0]
    inputpath_output=None
    should_break=False
    for i in range(10):
        if should_break:
            break
        inputpath = os.path.dirname(inputpath)
        input_list = os.listdir(inputpath)
        for input in input_list:
            if should_break:
                break
            if str(input)=='config':
                inputpath_output=os.path.join(inputpath,input)
                inputpath_output=os.path.dirname(inputpath_output)
                should_break=True
    return inputpath_output
def config_path_processing():
    # 获取当前文件的磁盘
    current_drive = os.path.splitdrive(os.path.dirname(__file__))[0]
    # 获取当前文件的绝对路径
    current_file_path = Path(__file__).resolve()
    # 获取顶层目录的名称
    top_dir_name = get_top_dir_path(current_file_path, levels_up=2)
    # 获取输入路径
    inputpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    inputpath_config = os.path.join(inputpath, 'config_path\data_update_path_config.xlsx')
    #E:\Optimizer\Data_update\data_update_path_config.xlsx

    # 读取Excel文件
    # df_sub = pd.read_excel(inputpath_config, sheet_name='sub_folder')
    # df_main = pd.read_excel(inputpath_config, sheet_name='main_folder')
    try:
        df_sub = pd.read_excel(inputpath_config, sheet_name='sub_folder')
        df_main = pd.read_excel(inputpath_config, sheet_name='main_folder')
    except FileNotFoundError:
        print(f"配置文件未找到，请检查路径: {inputpath_config}")
        return
    inputpath_config_sbjzq=config_path_finding()
    # 合并DataFrame
    df_sub = df_sub.merge(df_main, on='folder_type', how='left')
    # 检查是否有行的MPON和RON都为1
    if ((df_sub['MPON'] == 1) & (df_sub['RON'] == 1)).any():
        print(f"{inputpath_config}配置文件有问题：存在MPON和RON都为1的行")
        return
    # 构建完整路径
    df_sub['path'] = df_sub['path'] + os.sep + df_sub['folder_name']
    # 筛选出SON为1的行，并添加最上层的项目名
    df_sub.loc[df_sub['MPON'] == 1, 'path'] = df_sub.loc[df_sub['MPON'] == 1, 'path'].apply(
        lambda x: os.path.join(top_dir_name, x))
    # 筛选出RON为1的行，并添加磁盘名
    df_sub.loc[df_sub['RON'] == 1, 'path'] = df_sub.loc[df_sub['RON'] == 1, 'path'].apply(
        lambda x: os.path.join(current_drive,os.sep, x))
    df_sub.loc[df_sub['RON'] == 'config', ['path']] = df_sub.loc[df_sub['RON'] == 'config']['path'].apply(
        lambda x: os.path.join(inputpath_config_sbjzq, x)).tolist()
    # 选择需要的列
    df_sub = df_sub[['data_type', 'path']]
    return df_sub

def _init():
    df=config_path_processing()
    df.set_index('data_type',inplace=True,drop=True)
    global inputpath_dic
    inputpath_dic=df.to_dict()
    inputpath_dic=inputpath_dic.get('path')
    return inputpath_dic
def get(name):
    try:
        return inputpath_dic[name]
    except:
        return 'not found'
_init()
# print(dic)
# config_path_processing()
