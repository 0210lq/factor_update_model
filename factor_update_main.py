#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
因子数据更新主入口

支持命令行参数:
    --no-sql        不保存数据到数据库
    --date          指定目标日期 (YYYY-MM-DD 格式)
    --start-date    历史更新起始日期
    --end-date      历史更新结束日期
    --history       启用历史模式更新

用法示例:
    # 日常更新 (自动计算日期，保存到数据库)
    python factor_update_main.py

    # 日常更新，不保存到数据库
    python factor_update_main.py --no-sql

    # 指定日期更新
    python factor_update_main.py --date 2025-01-20

    # 历史数据更新
    python factor_update_main.py --history --start-date 2024-01-01 --end-date 2024-12-31

    # 历史更新，不保存到数据库
    python factor_update_main.py --history --start-date 2024-01-01 --end-date 2024-12-31 --no-sql
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到 Python 路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 检查并加载环境变量
path = os.getenv('GLOBAL_TOOLSFUNC_new')
if path is None:
    raise EnvironmentError(
        "环境变量 GLOBAL_TOOLSFUNC_new 未设置。\n"
        "请设置该环境变量指向 global_tools 模块路径。\n"
        "Windows: set GLOBAL_TOOLSFUNC_new=D:\\path\\to\\global_tools\n"
        "Linux/Mac: export GLOBAL_TOOLSFUNC_new=/path/to/global_tools"
    )
sys.path.append(path)

# 导入模块 - 使用新的 src 路径
from src.factor_update.factor_update import FactorData_update
from src.time_tools.time_tools import time_tools
from src.timeseries_update.time_series_data_update import timeSeries_data_update
from src.config_loader import ConfigLoader, get_config
import global_tools as gt


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='因子数据更新工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                                    # 日常更新
  %(prog)s --no-sql                           # 日常更新，不保存到数据库
  %(prog)s --date 2025-01-20                  # 指定日期更新
  %(prog)s --history --start-date 2024-01-01 --end-date 2024-12-31  # 历史更新
        """
    )

    parser.add_argument(
        '--no-sql',
        action='store_true',
        dest='no_sql',
        help='不将数据保存到数据库'
    )

    parser.add_argument(
        '--date',
        type=str,
        default=None,
        metavar='YYYY-MM-DD',
        help='指定目标日期 (格式: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--history',
        action='store_true',
        help='启用历史模式更新'
    )

    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        metavar='YYYY-MM-DD',
        dest='start_date',
        help='历史更新起始日期 (需要与 --history 配合使用)'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        metavar='YYYY-MM-DD',
        dest='end_date',
        help='历史更新结束日期 (需要与 --history 配合使用)'
    )

    parser.add_argument(
        '--no-timeseries',
        action='store_true',
        dest='no_timeseries',
        help='不更新时间序列数据'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出'
    )

    args = parser.parse_args()

    # 验证参数
    if args.history:
        if not args.start_date or not args.end_date:
            parser.error('--history 模式需要同时指定 --start-date 和 --end-date')

    # 验证日期格式
    date_format = '%Y-%m-%d'
    for date_arg, date_name in [(args.date, '--date'),
                                 (args.start_date, '--start-date'),
                                 (args.end_date, '--end-date')]:
        if date_arg:
            try:
                datetime.strptime(date_arg, date_format)
            except ValueError:
                parser.error(f'{date_name} 日期格式错误，应为 YYYY-MM-DD')

    return args


def FactorData_update_main(is_sql=True, target_date=None, include_timeseries=True, verbose=False):
    """
    因子数据更新主函数

    参数:
        is_sql (bool): 是否将数据写入SQL数据库，默认为True
        target_date (str): 指定目标日期，为 None 时自动计算
        include_timeseries (bool): 是否更新时间序列数据
        verbose (bool): 是否显示详细输出

    功能:
        1. 自动计算需要更新的日期范围
        2. 更新因子暴露度数据
        3. 更新因子收益率数据
        4. 更新因子股票池数据
        5. 更新因子协方差矩阵
        6. 更新因子特异性风险
        7. 更新时间序列数据 (可选)
    """
    # 获取配置
    config = ConfigLoader()
    factor_rollback = config.get('update.factor_rollback_days', 3)
    timeseries_rollback = config.get('update.timeseries_rollback_days', 10)

    if verbose:
        print(f"配置加载自: {config.get_config_path()}")
        print(f"因子回滚天数: {factor_rollback}")
        print(f"时间序列回滚天数: {timeseries_rollback}")

    # 确定目标日期
    if target_date:
        date = gt.strdate_transfer(target_date)
    else:
        tt = time_tools()
        date = tt.target_date_decision_factor()
        date = gt.strdate_transfer(date)

    if verbose:
        print(f"目标日期: {date}")
        print(f"保存到 SQL: {is_sql}")

    # 回滚工作日用于时间序列更新
    start_date2 = date
    for i in range(timeseries_rollback):
        start_date2 = gt.last_workday_calculate(start_date2)

    # 回滚工作日用于因子数据更新
    start_date = date
    for i in range(factor_rollback):
        start_date = gt.last_workday_calculate(start_date)

    if verbose:
        print(f"因子更新起始日期: {start_date}")
        print(f"时间序列更新起始日期: {start_date2}")

    # 创建更新对象
    fu = FactorData_update(start_date, date, is_sql)

    # 执行因子数据更新
    fu.FactorData_update_main()

    # 执行时间序列数据更新 (可选)
    # 注释原因：时序CSV不在本地生成，数据直接写入数据库
    # if include_timeseries:
    #     tdu = timeSeries_data_update(start_date2, date)
    #     tdu.Factordata_update_main()


def FactorData_history_update(start_date, end_date, is_sql=True, include_timeseries=True, verbose=False):
    """
    历史因子数据更新函数

    参数:
        start_date (str): 起始日期，格式为 'YYYY-MM-DD'
        end_date (str): 结束日期，格式为 'YYYY-MM-DD'
        is_sql (bool): 是否将数据写入SQL数据库，默认为True
        include_timeseries (bool): 是否同时更新时间序列数据，默认为True
        verbose (bool): 是否显示详细输出

    功能:
        更新指定日期范围内的历史因子数据
        可选：同时更新时间序列数据
    """
    if verbose:
        print(f"历史更新模式")
        print(f"起始日期: {start_date}")
        print(f"结束日期: {end_date}")
        print(f"保存到 SQL: {is_sql}")
        print(f"更新时间序列: {include_timeseries}")

    # 更新因子数据
    fu = FactorData_update(start_date, end_date, is_sql)
    fu.FactorData_update_main()

    # 可选：更新时间序列数据
    # 注释原因：时序CSV不在本地生成，数据直接写入数据库
    # if include_timeseries:
    #     tdu = timeSeries_data_update(start_date, end_date)
    #     tdu.Factordata_update_main()


def main():
    """主入口函数"""
    args = parse_args()

    is_sql = not args.no_sql
    include_timeseries = not args.no_timeseries

    if args.history:
        # 历史模式
        FactorData_history_update(
            start_date=args.start_date,
            end_date=args.end_date,
            is_sql=is_sql,
            include_timeseries=include_timeseries,
            verbose=args.verbose
        )
    else:
        # 日常更新模式
        FactorData_update_main(
            is_sql=is_sql,
            target_date=args.date,
            include_timeseries=include_timeseries,
            verbose=args.verbose
        )


if __name__ == '__main__':
    main()
