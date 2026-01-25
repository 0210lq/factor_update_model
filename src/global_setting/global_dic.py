# -*- coding: utf-8 -*-
"""
全局路径配置模块

提供数据路径的全局配置管理。
路径配置通过 config/config_path/data_update_path_config.xlsx 文件定义。
"""

import os
from pathlib import Path

import pandas as pd


def get_project_root():
    """
    获取项目根目录

    当前文件位于 src/global_setting/global_dic.py
    需要向上 3 层获取项目根目录

    Returns:
        Path: 项目根目录路径
    """
    current_file = Path(__file__).resolve()
    # src/global_setting/global_dic.py -> src/global_setting -> src -> project_root
    return current_file.parent.parent.parent


def get_top_dir_path(current_path, levels_up=2):
    """
    从当前路径向上退指定层数，获取顶层目录的完整路径。

    Args:
        current_path: 当前路径（Path对象）
        levels_up: 向上退的层数，默认为2

    Returns:
        顶层目录的完整路径（Path对象）
    """
    for _ in range(levels_up):
        current_path = current_path.parent
    return current_path


def config_path_finding():
    """
    向上查找 config 目录

    Returns:
        包含 config 目录的父目录路径
    """
    project_root = get_project_root()
    config_dir = project_root / 'config'

    if config_dir.exists():
        return str(project_root)

    # 后备: 向上查找
    inputpath = os.path.split(os.path.realpath(__file__))[0]
    inputpath_output = None
    should_break = False

    for i in range(10):
        if should_break:
            break
        inputpath = os.path.dirname(inputpath)
        input_list = os.listdir(inputpath)
        for input in input_list:
            if should_break:
                break
            if str(input) == 'config':
                inputpath_output = os.path.join(inputpath, input)
                inputpath_output = os.path.dirname(inputpath_output)
                should_break = True

    return inputpath_output


def config_path_processing():
    """
    处理配置路径，读取 Excel 配置文件并构建路径映射

    Returns:
        DataFrame: 包含 data_type 和 path 列的配置数据
    """
    # 获取当前文件的磁盘
    current_drive = os.path.splitdrive(os.path.dirname(__file__))[0]

    # 获取项目根目录
    project_root = get_project_root()

    # 获取顶层目录（用于 MPON=1 的路径）
    # 当前文件位于 src/global_setting/，需要向上 3 层到达项目根目录的父目录（Data_update）
    current_file_path = Path(__file__).resolve()
    top_dir_name = get_top_dir_path(current_file_path, levels_up=3)

    # 配置文件路径（新目录结构）
    inputpath_config = project_root / 'config' / 'config_path' / 'data_update_path_config.xlsx'

    # 兼容旧目录结构
    if not inputpath_config.exists():
        inputpath_config = project_root / 'config_path' / 'data_update_path_config.xlsx'

    try:
        df_sub = pd.read_excel(inputpath_config, sheet_name='sub_folder')
        df_main = pd.read_excel(inputpath_config, sheet_name='main_folder')
    except FileNotFoundError:
        print(f"配置文件未找到，请检查路径: {inputpath_config}")
        return None

    # 获取包含 config 目录的路径
    inputpath_config_sbjzq = config_path_finding()

    # 合并 DataFrame
    df_sub = df_sub.merge(df_main, on='folder_type', how='left')

    # 检查是否有行的 MPON 和 RON 都为 1
    if ((df_sub['MPON'] == 1) & (df_sub['RON'] == 1)).any():
        print(f"{inputpath_config} 配置文件有问题：存在 MPON 和 RON 都为 1 的行")
        return None

    # 构建完整路径
    df_sub['path'] = df_sub['path'] + os.sep + df_sub['folder_name']

    # 筛选出 MPON 为 1 的行，并添加最上层的项目名
    df_sub.loc[df_sub['MPON'] == 1, 'path'] = df_sub.loc[df_sub['MPON'] == 1, 'path'].apply(
        lambda x: os.path.join(top_dir_name, x))

    # 筛选出 RON 为 1 的行，并添加磁盘名
    df_sub.loc[df_sub['RON'] == 1, 'path'] = df_sub.loc[df_sub['RON'] == 1, 'path'].apply(
        lambda x: os.path.join(current_drive, os.sep, x))

    # 处理 RON 为 'config' 的行
    df_sub.loc[df_sub['RON'] == 'config', ['path']] = df_sub.loc[df_sub['RON'] == 'config']['path'].apply(
        lambda x: os.path.join(inputpath_config_sbjzq, x)).tolist()

    # 选择需要的列
    df_sub = df_sub[['data_type', 'path']]
    return df_sub


def _init():
    """
    初始化路径配置字典

    Returns:
        dict: 路径配置字典
    """
    global inputpath_dic

    df = config_path_processing()
    if df is None:
        inputpath_dic = {}
        return inputpath_dic

    df.set_index('data_type', inplace=True, drop=True)
    inputpath_dic = df.to_dict()
    inputpath_dic = inputpath_dic.get('path', {})
    return inputpath_dic


def get(name):
    """
    获取指定类型的路径

    Args:
        name: 数据类型名称

    Returns:
        对应的路径，未找到返回 'not found'
    """
    try:
        return inputpath_dic[name]
    except (KeyError, NameError):
        return 'not found'


# 模块加载时初始化
inputpath_dic = {}
_init()
