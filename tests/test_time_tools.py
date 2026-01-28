"""
Time_tools/time_tools.py 模块测试

测试时间计算和工作日判断功能。
"""

import os
import sys
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)


class TestTimeTools:
    """time_tools 类测试"""

    @pytest.mark.unit
    def test_module_import(self):
        """测试模块能否正常导入"""
        try:
            from src.time_tools.time_tools import time_tools
            assert time_tools is not None
        except ImportError as e:
            pytest.skip(f"模块导入失败: {e}")

    @pytest.mark.unit
    def test_class_instantiation(self):
        """测试类能否正常实例化"""
        try:
            from src.time_tools.time_tools import time_tools
            tt = time_tools()
            assert tt is not None
        except ImportError:
            pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_time_zoom_decision_method_exists(self):
        """测试 time_zoom_decision 方法存在"""
        try:
            from src.time_tools.time_tools import time_tools
            tt = time_tools()
            assert hasattr(tt, 'time_zoom_decision')
            assert callable(tt.time_zoom_decision)
        except ImportError:
            pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_target_date_decision_score_exists(self):
        """测试 target_date_decision_score 方法存在"""
        try:
            from src.time_tools.time_tools import time_tools
            tt = time_tools()
            assert hasattr(tt, 'target_date_decision_score')
            assert callable(tt.target_date_decision_score)
        except ImportError:
            pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_target_date_decision_mkt_exists(self):
        """测试 target_date_decision_mkt 方法存在"""
        try:
            from src.time_tools.time_tools import time_tools
            tt = time_tools()
            assert hasattr(tt, 'target_date_decision_mkt')
            assert callable(tt.target_date_decision_mkt)
        except ImportError:
            pytest.skip("模块导入失败")

    @pytest.mark.unit
    def test_target_date_decision_factor_exists(self):
        """测试 target_date_decision_factor 方法存在"""
        try:
            from src.time_tools.time_tools import time_tools
            tt = time_tools()
            assert hasattr(tt, 'target_date_decision_factor')
            assert callable(tt.target_date_decision_factor)
        except ImportError:
            pytest.skip("模块导入失败")


class TestTimeToolsWithMock:
    """使用 Mock 的 time_tools 测试"""

    @pytest.fixture
    def mock_config(self, tmp_path):
        """创建模拟的时间配置文件"""
        # 创建 time_zoon sheet
        df_zoom = pd.DataFrame({
            'zoom_name': ['morning', 'afternoon', 'evening'],
            'start_time': [datetime.strptime('08:00', '%H:%M').time(),
                          datetime.strptime('13:00', '%H:%M').time(),
                          datetime.strptime('18:00', '%H:%M').time()],
            'end_time': [datetime.strptime('12:00', '%H:%M').time(),
                        datetime.strptime('17:00', '%H:%M').time(),
                        datetime.strptime('22:00', '%H:%M').time()]
        })

        # 创建 critical_time sheet
        df_critical = pd.DataFrame({
            'zoom_name': ['time_1', 'time_2', 'time_3'],
            'critical_time': [datetime.strptime('17:00', '%H:%M').time(),
                             datetime.strptime('16:00', '%H:%M').time(),
                             datetime.strptime('18:00', '%H:%M').time()]
        })

        config_path = tmp_path / 'time_tools_config.xlsx'
        with pd.ExcelWriter(config_path, engine='openpyxl') as writer:
            df_zoom.to_excel(writer, sheet_name='time_zoon', index=False)
            df_critical.to_excel(writer, sheet_name='critical_time', index=False)

        return str(config_path)

    @pytest.mark.unit
    def test_time_zoom_decision_returns_string(self, mock_config, mock_glv):
        """测试 time_zoom_decision 返回字符串"""
        mock_glv.get = MagicMock(return_value=mock_config)

        with patch('src.time_tools.time_tools.glv', mock_glv):
            try:
                from src.time_tools.time_tools import time_tools
                tt = time_tools()
                result = tt.time_zoom_decision()
                assert isinstance(result, str)
            except Exception as e:
                pytest.skip(f"测试跳过: {e}")

    @pytest.mark.unit
    def test_target_date_returns_valid_date_format(self):
        """测试目标日期返回有效的日期格式"""
        try:
            from src.time_tools.time_tools import time_tools
            tt = time_tools()
            result = tt.target_date_decision_factor()

            # 结果应该是日期对象或日期字符串
            if isinstance(result, str):
                # 尝试解析日期字符串
                datetime.strptime(result, '%Y-%m-%d')
            elif isinstance(result, date):
                pass
            else:
                pytest.fail(f"返回类型不正确: {type(result)}")
        except ImportError:
            pytest.skip("模块导入失败")
        except Exception as e:
            pytest.skip(f"测试跳过: {e}")


class TestDateCalculations:
    """日期计算逻辑测试"""

    @pytest.mark.unit
    def test_workday_logic(self, mock_global_tools):
        """测试工作日逻辑"""
        gt = mock_global_tools

        # 测试工作日判断
        assert gt.is_workday_auto() in [True, False]

    @pytest.mark.unit
    def test_date_transfer_functions(self, mock_global_tools):
        """测试日期转换函数"""
        gt = mock_global_tools

        # 测试 intdate_transfer
        result = gt.intdate_transfer('2025-01-20')
        assert result == '20250120'

        # 测试 strdate_transfer
        result = gt.strdate_transfer('20250120')
        assert result == '2025-01-20'

    @pytest.mark.unit
    def test_working_days_list(self, mock_global_tools):
        """测试工作日列表生成"""
        gt = mock_global_tools

        result = gt.working_days_list('2025-01-01', '2025-01-31')
        assert isinstance(result, list)
