# 数据库配置安全处理说明

## 已完成的安全措施

### 1. 更新 .gitignore

已将以下敏感文件添加到 `.gitignore`：

```
# 数据库表配置（包含连接字符串和密码）
config_project/dataUpdate_sql.yaml
config/tables/dataUpdate_sql.yaml

# 数据库连接配置
**/sql_connection.yaml

# 测试和检查脚本（包含敏感信息）
check_database.py
test_db_connection.py
```

### 2. 从 Git 中删除敏感文件

已从 git 缓存中删除：
- `config_project/dataUpdate_sql.yaml` - 包含数据库连接字符串和密码

### 3. 创建示例文件

已创建以下示例文件供参考：
- `config_project/sql_connection.yaml.example` - 数据库连接配置示例
- `config_project/dataUpdate_sql.yaml.example` - 数据表配置示例
- `config/config_project/sql_connection.yaml.example` - 数据库连接配置示例（新结构）

## 使用说明

### 首次配置

1. **复制示例文件**：
   ```bash
   # 复制数据库连接配置
   cp config_project/sql_connection.yaml.example config_project/sql_connection.yaml
   cp config_project/sql_connection.yaml.example config/config_project/sql_connection.yaml

   # 复制数据表配置
   cp config_project/dataUpdate_sql.yaml.example config_project/dataUpdate_sql.yaml
   ```

2. **填入实际的数据库信息**：

   编辑 `config_project/sql_connection.yaml`：
   ```yaml
   database:
     host: "your-actual-host"
     port: 3306
     user: "your-username"
     password: "your-password"
     database: "your-database"
   ```

   编辑 `config_project/dataUpdate_sql.yaml`：
   - 将所有 `YOUR_USER` 替换为实际用户名
   - 将所有 `YOUR_PASSWORD` 替换为实际密码
   - 将所有 `YOUR_HOST` 替换为实际主机地址
   - 将所有 `YOUR_DATABASE` 替换为实际数据库名

3. **验证配置**：
   ```bash
   # 确认敏感文件不会被 git 跟踪
   git status

   # 应该看不到 sql_connection.yaml 和 dataUpdate_sql.yaml
   ```

### 批量替换数据库连接信息

如果需要批量替换 `dataUpdate_sql.yaml` 中的连接信息，可以使用以下命令：

```bash
# Linux/Mac
sed -i 's/YOUR_USER/actual_user/g; s/YOUR_PASSWORD/actual_password/g; s/YOUR_HOST/actual_host/g; s/YOUR_DATABASE/actual_database/g' config_project/dataUpdate_sql.yaml

# Windows (Git Bash)
sed -i 's/YOUR_USER/actual_user/g; s/YOUR_PASSWORD/actual_password/g; s/YOUR_HOST/actual_host/g; s/YOUR_DATABASE/actual_database/g' config_project/dataUpdate_sql.yaml
```

## 安全注意事项

### ⚠️ 重要提醒

1. **永远不要提交包含真实密码的文件到 git**
2. **定期更换数据库密码**
3. **不要在代码中硬编码密码**
4. **不要通过聊天工具发送包含密码的配置文件**

### 检查清单

在提交代码前，请确认：

- [ ] `git status` 中没有显示 `sql_connection.yaml`
- [ ] `git status` 中没有显示 `dataUpdate_sql.yaml`
- [ ] `git status` 中没有显示 `check_database.py`
- [ ] `git status` 中没有显示 `test_db_connection.py`
- [ ] 只提交了 `.example` 示例文件

### 验证命令

```bash
# 检查哪些文件会被 git 忽略
git check-ignore -v config_project/sql_connection.yaml
git check-ignore -v config_project/dataUpdate_sql.yaml
git check-ignore -v check_database.py
git check-ignore -v test_db_connection.py

# 应该都显示被 .gitignore 规则匹配
```

## 如果不小心提交了敏感信息

如果已经将包含密码的文件提交到了 git，需要：

1. **立即更改数据库密码**
2. **从 git 历史中删除敏感信息**：
   ```bash
   # 使用 git filter-branch 或 BFG Repo-Cleaner
   # 这会重写 git 历史，需要谨慎操作
   ```
3. **联系团队成员更新本地仓库**

## 团队协作

### 新成员加入

新成员需要：
1. 克隆代码仓库
2. 从团队获取实际的数据库配置信息
3. 按照"首次配置"步骤创建配置文件
4. 验证配置文件不会被 git 跟踪

### 配置文件更新

如果需要更新配置文件结构（不是密码）：
1. 更新 `.example` 示例文件
2. 提交示例文件到 git
3. 通知团队成员更新本地配置文件

## 当前状态

✅ 已完成：
- 更新 .gitignore
- 从 git 中删除 `config_project/dataUpdate_sql.yaml`
- 创建示例文件
- 验证敏感文件被正确忽略

⚠️ 待处理：
- 需要手动配置本地的 `config_project/dataUpdate_sql.yaml`
- 建议更改数据库密码（因为旧密码可能在 git 历史中）

## 相关文件

- `.gitignore` - Git 忽略规则
- `config_project/sql_connection.yaml.example` - 数据库连接示例
- `config_project/dataUpdate_sql.yaml.example` - 数据表配置示例
- `CODE_REVIEW_REPORT.md` - 完整的代码审查报告
