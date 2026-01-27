# 配置文件整理计划

## 当前配置文件结构分析

### 现有配置目录

```
项目根目录/
├── config/                          # 新配置目录（推荐）
│   ├── app_config.yaml             # 主配置文件 ✓
│   ├── config_project/             # 子目录
│   │   └── sql_connection.yaml     # 数据库连接（本地）
│   └── tables/                     # 表定义
│       └── dataUpdate_sql.yaml     # 数据表配置 ✓
│
├── config_project/                  # 旧配置目录（待整理）
│   ├── dataUpdate_sql.yaml         # 数据表配置（本地，包含密码）
│   ├── sql_connection.yaml         # 数据库连接（本地，包含密码）
│   ├── data_source_priority_config.xlsx  # 数据源优先级
│   └── time_tools_config.xlsx      # 时间工具配置
│
└── config_path/                     # 路径配置目录（待整理）
    ├── data_update_path_config.xlsx      # 路径配置
    └── data_update_path_config_test.xlsx # 测试路径配置
```

### 配置文件分类

#### 1. 主配置文件（已整合）
- `config/app_config.yaml` ✓
  - 包含：路径、数据源、时间、日期常量、指数映射、因子列表、日志配置

#### 2. 数据库配置（敏感信息）
- `config_project/sql_connection.yaml` - 数据库连接（本地）
- `config_project/dataUpdate_sql.yaml` - 数据表配置（本地）
- `config/config_project/sql_connection.yaml` - 数据库连接（本地）
- `config/tables/dataUpdate_sql.yaml` - 数据表配置（已提交）

#### 3. Excel配置文件（旧格式，可迁移）
- `config_project/data_source_priority_config.xlsx` - 数据源优先级
- `config_project/time_tools_config.xlsx` - 时间工具配置
- `config_path/data_update_path_config.xlsx` - 路径配置

## 整理方案

### 目标结构

```
config/                              # 统一配置目录
├── app_config.yaml                  # 主配置文件（已有）
├── database.yaml                    # 数据库连接配置（本地，不提交）
├── database.yaml.example            # 数据库连接示例（提交）
├── tables/                          # 表定义目录
│   ├── dataUpdate_sql.yaml         # 数据表配置（本地，不提交）
│   └── dataUpdate_sql.yaml.example # 数据表配置示例（提交）
└── legacy/                          # 旧配置文件（兼容）
    ├── data_source_priority_config.xlsx
    ├── time_tools_config.xlsx
    └── data_update_path_config.xlsx
```

### 整理步骤

#### 阶段1：创建新结构
1. 创建 `config/legacy/` 目录
2. 移动 Excel 配置文件到 legacy 目录
3. 创建 `config/database.yaml` 和示例文件

#### 阶段2：统一数据库配置
1. 将 `config_project/sql_connection.yaml` 移动到 `config/database.yaml`
2. 将 `config_project/dataUpdate_sql.yaml` 移动到 `config/tables/dataUpdate_sql.yaml`
3. 删除 `config/config_project/` 目录

#### 阶段3：更新代码引用
1. 更新 `src/timeseries_update/time_series_data_update.py` 中的配置路径
2. 更新 `src/global_setting/global_dic.py` 中的路径配置引用
3. 更新其他引用旧配置路径的代码

#### 阶段4：清理旧目录
1. 删除 `config_project/` 目录（保留示例文件）
2. 删除 `config_path/` 目录
3. 更新 .gitignore

## 详细操作步骤

### 步骤1：备份当前配置
```bash
# 创建备份
cp -r config_project config_project.backup
cp -r config_path config_path.backup
```

### 步骤2：创建新目录结构
```bash
# 创建 legacy 目录
mkdir -p config/legacy
```

### 步骤3：移动 Excel 配置文件
```bash
# 移动数据源优先级配置
mv config_project/data_source_priority_config.xlsx config/legacy/

# 移动时间工具配置
mv config_project/time_tools_config.xlsx config/legacy/

# 移动路径配置
mv config_path/data_update_path_config.xlsx config/legacy/
mv config_path/data_update_path_config_test.xlsx config/legacy/
```

### 步骤4：统一数据库配置
```bash
# 移动数据库连接配置
mv config_project/sql_connection.yaml config/database.yaml

# 创建示例文件
cp config_project/sql_connection.yaml.example config/database.yaml.example

# 移动数据表配置（如果不同）
# config_project/dataUpdate_sql.yaml 保持本地使用
# config/tables/dataUpdate_sql.yaml 已存在
```

### 步骤5：更新 .gitignore
```gitignore
# 数据库配置（包含敏感信息）
config/database.yaml
config/tables/dataUpdate_sql.yaml

# 旧配置目录（已废弃）
config_project/
config_path/

# 保留示例文件
!config/database.yaml.example
!config/tables/dataUpdate_sql.yaml.example
!config_project/*.example
```

### 步骤6：更新代码引用

#### 文件1: src/timeseries_update/time_series_data_update.py
```python
# 旧代码（第37-46行）
base_dir = os.path.join(get_config_dir(), 'config_project')
for fname in ['sql_connection.yaml', 'sql_connection.yaml.example']:
    cfg_file = os.path.join(base_dir, fname)

# 新代码
base_dir = get_config_dir()
for fname in ['database.yaml', 'database.yaml.example']:
    cfg_file = os.path.join(base_dir, fname)
```

#### 文件2: src/global_setting/global_dic.py
```python
# 旧代码（第106-107行）
path_config_file = os.path.join(project_root, 'config', 'config_path', 'data_update_path_config.xlsx')

# 新代码
path_config_file = os.path.join(project_root, 'config', 'legacy', 'data_update_path_config.xlsx')
```

#### 文件3: src/factor_update/factor_update.py
```python
# 旧代码（第46行）
inputpath = glv.get('data_source_priority')

# 新代码（如果需要更新路径）
# 路径应该指向 config/legacy/data_source_priority_config.xlsx
```

#### 文件4: src/time_tools/time_tools.py
```python
# 旧代码（第23, 36, 55, 73行）
inputpath = glv.get('time_tools_config')

# 新代码（如果需要更新路径）
# 路径应该指向 config/legacy/time_tools_config.xlsx
```

## 代码引用检查清单

需要检查和更新的文件：
- [ ] src/timeseries_update/time_series_data_update.py
- [ ] src/global_setting/global_dic.py
- [ ] src/factor_update/factor_update.py
- [ ] src/time_tools/time_tools.py
- [ ] src/config_loader.py
- [ ] factor_update_main.py

## 测试计划

### 测试1：配置文件加载
```bash
python -c "from src.config_loader import get_config; print(get_config('paths.base_folders.config_folder'))"
```

### 测试2：数据库连接
```bash
python check_database.py
```

### 测试3：程序运行
```bash
python factor_update_main.py --no-sql --date 2025-01-20
```

## 风险评估

### 低风险
- 移动 Excel 配置文件（代码通过 glv.get() 动态获取路径）
- 创建新的目录结构

### 中风险
- 更新数据库配置路径（需要更新代码引用）
- 删除旧目录（需要确保所有引用已更新）

### 高风险
- 无

## 回滚方案

如果出现问题，可以快速回滚：
```bash
# 恢复备份
rm -rf config_project config_path
mv config_project.backup config_project
mv config_path.backup config_path

# 恢复代码
git checkout -- src/
```

## 预期收益

1. **结构清晰**：所有配置文件在一个目录下
2. **易于维护**：统一的配置管理
3. **减少混淆**：不再有多个配置目录
4. **更好的安全性**：敏感文件集中管理
5. **便于团队协作**：清晰的配置文件组织

## 注意事项

1. **保留兼容性**：旧的 Excel 配置文件仍然可用（移到 legacy 目录）
2. **不影响功能**：所有功能保持不变
3. **渐进式迁移**：可以逐步将 Excel 配置迁移到 YAML
4. **文档更新**：需要更新 README 和 SECURITY_SETUP 文档
