#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
比较两个数据库中的因子数据
"""
import pymysql
import pandas as pd
from datetime import datetime

# 数据库配置
db1_config = {
    'name': 'jzq@data_prepared_jzq (新实例)',
    'host': 'rm-cn-fhh4gzo9900083vo.rwlb.rds.aliyuncs.com',
    'port': 3306,
    'user': 'jzq',
    'password': 'Abcd1234#',
    'database': 'data_prepared_jzq'
}

db2_config = {
    'name': 'kai@data_prepared_new (参考实例)',
    'host': 'rm-bp1o6we7s3o1h76x1to.mysql.rds.aliyuncs.com',
    'port': 3306,
    'user': 'kai',
    'password': 'Abcd1234#',
    'database': 'data_prepared_new'
}

# 要比较的表
tables = [
    'data_factorexposure',
    'data_factorreturn',
    'data_factorpool',
    'data_factorcov',
    'data_factorspecificrisk'
]

def connect_db(config):
    """连接数据库"""
    return pymysql.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )

def get_table_info(conn, table):
    """获取表的基本信息"""
    with conn.cursor() as cursor:
        # 获取记录总数
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_count = cursor.fetchone()[0]

        # 获取不同日期的数量
        cursor.execute(f"SELECT COUNT(DISTINCT valuation_date) FROM {table}")
        date_count = cursor.fetchone()[0]

        # 获取最新的5个日期
        cursor.execute(f"SELECT DISTINCT valuation_date FROM {table} ORDER BY valuation_date DESC LIMIT 5")
        latest_dates = [row[0] for row in cursor.fetchall()]

        # 获取最早的日期
        cursor.execute(f"SELECT MIN(valuation_date) FROM {table}")
        earliest_date = cursor.fetchone()[0]

        # 获取最晚的日期
        cursor.execute(f"SELECT MAX(valuation_date) FROM {table}")
        latest_date = cursor.fetchone()[0]

        return {
            'total_count': total_count,
            'date_count': date_count,
            'latest_dates': latest_dates,
            'earliest_date': earliest_date,
            'latest_date': latest_date
        }

def get_date_data_count(conn, table, date):
    """获取指定日期的数据量"""
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE valuation_date = %s", (date,))
        return cursor.fetchone()[0]

def get_sample_data(conn, table, date, limit=5):
    """获取指定日期的样本数据"""
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table} WHERE valuation_date = %s LIMIT {limit}", (date,))
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=columns)

def compare_databases():
    """比较两个数据库"""
    print("=" * 80)
    print("数据库比较报告")
    print("=" * 80)
    print(f"\n数据库1: {db1_config['name']}")
    print(f"数据库2: {db2_config['name']}")
    print(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80)

    try:
        # 连接两个数据库
        print("\n正在连接数据库...")
        conn1 = connect_db(db1_config)
        conn2 = connect_db(db2_config)
        print("[OK] 数据库连接成功")

        comparison_results = []

        for table in tables:
            print(f"\n{'=' * 80}")
            print(f"表: {table}")
            print("=" * 80)

            try:
                # 获取两个数据库的表信息
                info1 = get_table_info(conn1, table)
                info2 = get_table_info(conn2, table)

                # 打印基本信息
                print(f"\n【基本信息】")
                print(f"{'指标':<30} {'数据库1':<20} {'数据库2':<20} {'差异':<20}")
                print("-" * 90)

                total_diff = info1['total_count'] - info2['total_count']
                date_diff = info1['date_count'] - info2['date_count']

                print(f"{'总记录数':<30} {info1['total_count']:<20,} {info2['total_count']:<20,} {total_diff:+,}")
                print(f"{'不同日期数':<30} {info1['date_count']:<20} {info2['date_count']:<20} {date_diff:+}")
                print(f"{'最早日期':<30} {info1['earliest_date']:<20} {info2['earliest_date']:<20}")
                print(f"{'最晚日期':<30} {info1['latest_date']:<20} {info2['latest_date']:<20}")

                # 打印最新日期
                print(f"\n【最新的5个日期】")
                print(f"数据库1: {', '.join(info1['latest_dates'])}")
                print(f"数据库2: {', '.join(info2['latest_dates'])}")

                # 找出共同的日期
                common_dates = set(info1['latest_dates']) & set(info2['latest_dates'])
                if common_dates:
                    print(f"\n【共同日期的数据量比较】")
                    print(f"{'日期':<20} {'数据库1':<20} {'数据库2':<20} {'差异':<20}")
                    print("-" * 80)

                    for date in sorted(common_dates, reverse=True):
                        count1 = get_date_data_count(conn1, table, date)
                        count2 = get_date_data_count(conn2, table, date)
                        diff = count1 - count2
                        status = "[OK] 一致" if diff == 0 else f"[X] 差异 {diff:+,}"
                        print(f"{date:<20} {count1:<20,} {count2:<20,} {status}")

                # 只在数据库1中的日期
                only_in_db1 = set(info1['latest_dates']) - set(info2['latest_dates'])
                if only_in_db1:
                    print(f"\n【仅在数据库1中的日期】: {', '.join(sorted(only_in_db1, reverse=True))}")

                # 只在数据库2中的日期
                only_in_db2 = set(info2['latest_dates']) - set(info1['latest_dates'])
                if only_in_db2:
                    print(f"\n【仅在数据库2中的日期】: {', '.join(sorted(only_in_db2, reverse=True))}")

                # 记录比较结果
                comparison_results.append({
                    'table': table,
                    'db1_count': info1['total_count'],
                    'db2_count': info2['total_count'],
                    'diff': total_diff,
                    'db1_dates': info1['date_count'],
                    'db2_dates': info2['date_count'],
                    'match': total_diff == 0
                })

            except Exception as e:
                print(f"[X] 比较表 {table} 时出错: {str(e)}")
                comparison_results.append({
                    'table': table,
                    'error': str(e)
                })

        # 打印总结
        print(f"\n{'=' * 80}")
        print("总结")
        print("=" * 80)

        print(f"\n{'表名':<30} {'数据库1记录数':<20} {'数据库2记录数':<20} {'状态':<20}")
        print("-" * 90)

        for result in comparison_results:
            if 'error' not in result:
                status = "[OK] 一致" if result['match'] else f"[X] 差异 {result['diff']:+,}"
                print(f"{result['table']:<30} {result['db1_count']:<20,} {result['db2_count']:<20,} {status}")

        # 关闭连接
        conn1.close()
        conn2.close()

        print("\n" + "=" * 80)
        print("比较完成")
        print("=" * 80)

    except Exception as e:
        print(f"\n[X] 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_databases()
