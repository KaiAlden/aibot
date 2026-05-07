# TCM RAG Service

企业级 RAG 中医体质辨识与商品推荐知识问答系统后端服务。

## 当前阶段

已初始化第一阶段基础骨架：

- FastAPI 应用入口与健康检查接口
- `.env` 配置读取
- 核心 Pydantic 数据对象
- SQLAlchemy MySQL 模型
- Redis JSON 工具封装
- Milvus Collection 初始化脚本
- 多租户商品查询的最小测试

## 本地启动

```bash
cp .env.example .env
uvicorn app.main:app --reload
```

健康检查：

```bash
GET /api/v1/health
```

## 验证

```bash
pytest
```

## 初始化 MySQL

先确认 `.env` 中的 `MYSQL_DSN` 已配置到目标数据库，然后执行：

```bash
conda run -n aibot python -m scripts.init_mysql
```

## 商品字段映射

商品 Excel 导入采用字段映射配置，示例见：

```text
examples/product_field_mapping.json
```

映射规则左侧是系统字段，右侧是商家 Excel 表头。
