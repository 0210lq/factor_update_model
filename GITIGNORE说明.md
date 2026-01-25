# .gitignore 配置说明

本项目的 `.gitignore` 文件已配置为自动忽略以下内容：

## 1. Python相关文件
- `__pycache__/` - Python缓存目录
- `*.pyc`, `*.pyo` - 编译的Python文件
- `*.egg-info/` - Python包信息
- `venv/`, `env/` - 虚拟环境目录

## 2. 敏感配置文件 ⚠️
以下文件会被自动忽略，避免敏感信息泄露：
- `config_project/sql_connection.yaml` - 数据库连接配置（包含密码）
- `config_project/L4_config/*.py` - L4配置文件（除了__init__.py）
- `*.yaml`（示例文件除外）

**注意**：
- 保留了 `*.yaml.example` 示例文件，可以提交到仓库
- 实际使用时，复制示例文件并填入真实配置

## 3. 数据文件
为避免仓库过大，数据文件会被忽略：
- `*.csv` - CSV数据文件
- `*.xlsx`, `*.xls` - Excel数据文件（配置文件除外）
- `*.mat` - MATLAB数据文件
- `*.h5`, `*.hdf5` - HDF5数据文件
- `config_path/` - 配置路径目录（包含data_update_path_config.xlsx）

**保留的文件**：
- 文件名包含 `config` 或 `template` 的Excel文件不会被忽略

## 4. 日志文件
- `logs/` - 日志目录
- `*.log` - 所有日志文件

## 5. IDE和编辑器文件
- `.vscode/` - VS Code配置
- `.idea/` - PyCharm配置
- 其他IDE的配置文件

## 6. 操作系统临时文件
- `.DS_Store` - macOS文件
- `Thumbs.db` - Windows缩略图
- `nul` - Windows空文件

## 7. 环境变量文件
- `.env` - 环境变量配置（可能包含密钥）

---

## 重要提醒 ⚠️

### 已提交的敏感信息
如果以下文件已经提交到Git仓库，需要从历史记录中删除：
- `config_project/L4_config/data_prepared_new.py`
- `config_project/L4_config/rz_hfdb_core.py`

这些文件包含硬编码的数据库密码，需要：

1. **立即从仓库中删除**：
   ```bash
   git rm --cached config_project/L4_config/data_prepared_new.py
   git rm --cached config_project/L4_config/rz_hfdb_core.py
   git commit -m "Remove sensitive database credentials"
   ```

2. **清理Git历史**（如果已推送到远程）：
   ```bash
   # 使用 BFG Repo-Cleaner（推荐）
   bfg --delete-files "data_prepared_new.py"
   bfg --delete-files "rz_hfdb_core.py"
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive

   # 或使用 git filter-branch
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch config_project/L4_config/data_prepared_new.py config_project/L4_config/rz_hfdb_core.py" \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. **修改泄露的密码**：
   - 立即更改数据库密码
   - 泄露的密码：`Abcd1234#`（用户：wc）

### 配置文件最佳实践

1. **使用示例文件**：
   ```bash
   # 复制示例文件
   cp config_project/sql_connection.yaml.example config_project/sql_connection.yaml
   # 编辑并填入真实配置
   ```

2. **永远不要提交**：
   - 真实的数据库密码
   - API密钥
   - 个人路径配置
   - 真实数据文件

3. **检查是否正确忽略**：
   ```bash
   # 查看将要提交的文件
   git status

   # 确保敏感文件不在列表中
   git add -A
   git status
   ```

---

## 使用方法

`.gitignore` 文件会自动生效，无需任何配置。

### 测试忽略规则
```bash
# 查看被忽略的文件
git status --ignored

# 检查某个文件是否被忽略
git check-ignore -v config_project/sql_connection.yaml
```

### 强制添加被忽略的文件
如果确实需要添加被忽略的文件：
```bash
git add -f <file>
```

**警告**：除非确定该文件不包含敏感信息，否则不要使用 `-f` 强制添加。

---

## 定制化

如果需要修改忽略规则，编辑 `.gitignore` 文件：

```bash
# 编辑
vim .gitignore

# 或
code .gitignore
```

### 常用规则语法
- `*.log` - 忽略所有 .log 文件
- `!important.log` - 但不忽略 important.log
- `logs/` - 忽略整个 logs 目录
- `**/temp` - 忽略任何位置的 temp 目录

---

## 相关文档
- Git官方文档：https://git-scm.com/docs/gitignore
- GitHub .gitignore 模板：https://github.com/github/gitignore
