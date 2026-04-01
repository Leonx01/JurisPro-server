# JurisPro

基于 FastAPI 的智能法律助手系统，集成大语言模型能力，支持文档管理、智能问答、知识检索等功能。

## ✨ 功能特性

- 🔐 **权限认证机制** - 实现基于邮箱验证的注册与密码找回；采用 JWT + RBAC 做权限认证，支持动态路由拦截与按钮级权限控制
- 💬 **智能法律问答** - 基于 LangChain 搭建 RAG 流水线，构建“法学三段论”式思维链 Prompt 引导生成，幻觉率下降 30%
- 🔍 **知识检索机制** - 沉淀 923 部法律、4.5 万+法律知识条目，构建父子索引的层级化知识库；引入 Query Rewrite 对齐语义；基于 Elasticsearch 实现语义 + 关键字混合检索，并结合 RRF 重排提升召回与排序效果
- 🧠 **嵌入模型微调** - 基于自建法律语料对 BGE-v1.5 Embedding 模型微调：Recall@1 提升 9.6%（至 82.1%），MRR@10 提升 7.2%（至 87.7%）
- ⚡ **高效数据缓存** - 首轮问题语义匹配命中 FAQ，减少模型调用与响应耗时；结合 Redis 缓存热点��据，整体响应延迟降低 80%
- 🔄 **异步知识更新** - 采用 Logstash 实现 MySQL 增量同步；通过版本覆盖解决 Elasticsearch 幂等更新与碎片残留问题，保障数据一致性
- 📄 **文档管理** - 法律文书生成与管理

<img width="501" height="501" alt="chat" src="https://github.com/user-attachments/assets/b01d82bf-494a-4fc9-a05d-ed3b0508f5af" />

## 🛠️ 技术栈



- **框架**: FastAPI + Uvicorn
- **数据库**: MySQL + SQLAlchemy ORM
- **缓存**: Redis
- **搜索引擎**: Elasticsearch
- **LLM**: LangChain + Ollama/通义千问
- **向量化**: Sentence Transformers

## 📁 项目结构

```
JurisProFastAPI/
├── src/
│   ├── api/          # API 路由层
│   ├── services/     # 业务逻辑层
│   ├── repositories/ # 数据访问层
│   ├── schemas/      # Pydantic 模型
│   ├── utils/        # 工具类
│   ├── exceptions/   # 异常处理
│   ├── data/         # 模型数据文件
│   ├── models.py     # ORM 模型定义
│   ├── configs.py    # 配置管理
│   └── main.py       # 应用入口
├── alembic/          # 数据库迁移
├── tests/            # 测试文件
├── uploads/          # 上传文件目录
├── Dockerfile        # Docker 构建文件
├── docker-compose.yml # Docker Compose 编排
├── requirements.txt  # Python 依赖
└── .env.example      # 环境变量模板
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Docker & Docker Compose（推荐）
- 或手动安装：MySQL 8.0+、Redis 6.0+、Elasticsearch 8.x

### 使用 Docker Compose 启动服务（推荐）

1. **启动基础设施服务**

```bash
# 启动 MySQL + Redis（必需）
docker-compose up -d mysql redis

# 可选：启动 Elasticsearch + Kibana
docker-compose up -d elasticsearch kibana

# 可选：启动 Ollama（本地 LLM）
docker-compose up -d ollama

# 查看服务状态
docker-compose ps
```

2. **启动应用服务**

```bash
# 构建并启动应用
docker-compose up -d --build app

# 查看应用日志
docker-compose logs -f app
```

3. **服务地址**

| 服务 | 地址 | 说明 |
|------|------|------|
| **App** | `http://localhost:8000` | FastAPI 应用 |
| MySQL | `localhost:3306` | 用户: root |
| Redis | `localhost:6379` | 无密码 |
| Elasticsearch | `https://localhost:9200` | 用户: elastic |
| Kibana | `http://localhost:5601` | ES 可视化 |
| Ollama | `http://localhost:11434` | 本地 LLM |

4. **停止服务**

```bash
docker-compose down

# 同时删除数据卷
docker-compose down -v
```

### 仅使用 Docker 构建（不含 Compose）

```bash
# 构建镜像
docker build -t jurispro-api .

# 运行容器
docker run -d \
  --name jurispro-api \
  -p 8000:8000 \
  -e DATABASE_HOST=host.docker.internal \
  -e REDIS_HOST=host.docker.internal \
  -v $(pwd)/uploads:/app/uploads \
  jurispro-api
```

### 手动安装步骤

1. **克隆项目**

```bash
git clone https://github.com/your-username/JurisProFastAPI.git
cd JurisProFastAPI
```

2. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

```bash
cp .env.example src/.env
# 编辑 src/.env 填入实际配置
```

5. **数据库迁移**

```bash
alembic upgrade head
```

6. **启动服务**

```bash
cd src && uvicorn main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DATABASE_HOST` | MySQL 主机地址 | `localhost` |
| `DATABASE_PORT` | MySQL 端口 | `3306` |
| `DATABASE_USER` | 数据库���户名 | `root` |
| `DATABASE_PASSWORD` | 数据库密码 | `your_password` |
| `DATABASE_NAME` | 数据库名称 | `jurispro` |
| `REDIS_HOST` | Redis 主机地址 | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `ELASTIC_HOSTS` | ES 地址 | `https://localhost:9200` |
| `APP_TITLE` | 应用名称 | `JurisPro` |
| `APP_DEBUG` | 调试模式 | `False` |

### LLM 配置

LLM 模型配置存储在数据库 `llms` 表中，支持以下提供商：

| Provider | 说明 |
|----------|------|
| `ollama` | 本地 Ollama 服务 |
| `tongyi` | 阿里云通义千问 |

## 📖 API 文档

启动服务后访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/auth/*` | 登录、注册、邮箱验证 |
| 用户 | `/users/*` | 用户管理 |
| 聊天 | `/chat/*` | 对话管理 |
| 文档 | `/documents/*` | 文书管理 |
| LLM | `/llm/*` | 模型管理 |

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行指定测试
pytest tests/utils/test_common.py -v
```

## 📝 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 📄 License

MIT License
