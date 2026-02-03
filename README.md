# langchain-agent

该 README 由项目内 PDF 文档自动提取并转换为 Markdown：`PYTHON_REFACTOR_ARCHITECTURE.pdf`。

## SuperBizAgent（Python 重构版）技术栈与架构规划
## 0. 目标与范围

保留现有 Java 项目的功能边界与交互方式（接口、会话管理、文件上传/向量化、RAG 问答、 AIOps 多 Agent 运维报告）。

将实现重构为 Python + FastAPI + LangChain/LangGraph，使项目更贴近 Agent/AI 应用主流生态，便于作品集展示与二次扩展。

本文档描述的是目标 Python 版本架构（不是当前 Java 代码的实现说明）。

## 1. 现有 Java 版本的核心功能抽象（用于对齐迁移）

### 1.1. API 形态（保持不变/尽量兼容）

- `POST /api/chat`

非流式对话（支持工具调用）

- `POST /api/chat_stream`

SSE 流式对话（支持工具调用）

- `POST /api/upload`

上传文件并自动向量化写入向量库（支持覆盖更新）

- `POST /api/ai_ops`

AIOps 多 Agent 分析（Planner-Executor-Replanner + Supervisor 编排），输出《告警分析报告》

- `POST /api/chat/clear`

- `GET /api/chat/session/{sessionId}`

会话管理

### 1.2. 知识库/RAG 关键点

文档分片（chunk size / overlap 可配置）

上传文件覆盖更新：按 _source 删除旧向量再插入新分片

向量库：Milvus（collection 内字段： id/vector/content/metadata ）

Embedding：DashScope embedding

### 1.3. AIOps 关键点

多 Agent：Planner + Executor + Supervisor

规则：禁止编造数据；工具连续失败需停止并在报告中说明

工具：时间、内部文档检索、Prometheus 告警/指标、（可选）日志查询（Java 里通过 MCP/Mock 注入）

## 2. Python 重构版技术栈（替换为目标栈）

### 2.1. 语言与基础框架

Python 3.11+

FastAPI（REST + SSE 流式）

Uvicorn（本地运行）/ Gunicorn + UvicornWorker（生产）

Pydantic v2（DTO/校验/结构化输出）

### 2.2. LLM / Agent / 工作流

LangChain（模型调用、Prompt 模板、Tool 封装、RAG 组件）

LangGraph（推荐，用于多 Agent/状态机编排：Supervisor ↔ Planner ↔ Executor 循环）

模型提供方（与现有保持一致优先）：DashScope（Qwen）

langchain-community / langchain-openai 等按实际 provider 选择

### 2.3. RAG 与向量库

pymilvus（Milvus 客户端）

向量库：Milvus（保持现有 schema 设计：id/vector/content/metadata）

文档解析：

轻量：纯文本/Markdown（与现有保持一致）

可扩展：pypdf/docx/unstructured（后续迭代）

切分：LangChain Text Splitters（递归切分 + overlap）

### 2.4. 外部系统集成（AIOps 工具层）

Prometheus：HTTP API + httpx （异步请求）

日志系统：

优先保持 Java 版本的思路：通过“工具服务器”注入（可选）

Python 侧可实现：

方案 A：直接调用云厂商日志 API

方案 B：对接 MCP Server（如 SSE/HTTP 工具网关）

### 2.5. 存储与缓存（可选增强）

Redis（会话/对话短期 memory、rate limit、任务队列中转）

PostgreSQL/MySQL（可选，用于对话/审计/任务等持久化）

SQLAlchemy 2.x（可选）

### 2.6. 异步任务（建议）

Celery + Redis（文档批量向量化、重建索引等长任务）

### 2.7. 可观测性与工程化

structlog/loguru（结构化日志二选一）

OpenTelemetry（链路追踪，可选）

pytest（测试）

ruff + black（格式与 lint）

Docker + docker-compose（Milvus/Redis/服务编排）

## 3. 目标目录结构（对齐 Java 的分层）

本仓库根目录（`langchain-agent/`）即 Python 项目根目录，结构如下：

```text
langchain-agent/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── routes_chat.py
│   │   ├── routes_aiops.py
│   │   ├── routes_upload.py
│   │   └── routes_session.py
│   ├── core/
│   │   ├── settings.py
│   │   ├── logging.py
│   │   └── dependencies.py
│   ├── schemas/
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── rag_service.py
│   │   ├── aiops_service.py
│   │   └── session_store.py
│   ├── rag/
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── indexing.py
│   ├── agents/
│   │   ├── tools/
│   │   │   ├── datetime_tool.py
│   │   │   ├── internal_docs_tool.py
│   │   │   ├── prometheus_tool.py
│   │   │   └── logs_tool.py
│   │   ├── chat_agent.py
│   │   └── aiops_graph.py
│   └── clients/
│       ├── dashscope_client.py
│       └── prometheus_client.py
├── tests/
└── pyproject.toml
```

## 4. 核心数据流（Python 版）

### 4.1. /api/upload → 向量化入库

上传文件落盘（保持“同名覆盖”语义）

读取内容 → chunk（chunk_size/overlap）

对每个 chunk：embedding → insert Milvus

覆盖更新策略：

以 metadata._source == normalized_path 删除旧记录后再插入

### 4.2. /api/chat （非流式）

从 session store 取 history（窗口大小与 Java 一致：例如 6 对消息）

构造 system prompt（可保留 Java 的“把历史拼进 prompt”做法，或使用 LangChain memory）

调用 Chat Agent（工具：时间/内部文档/Prometheus/日志）

返回完整 answer，并写回 history

### 4.3. /api/chat_stream （SSE 流式）

与非流式相同的前置步骤

LLM 以 streaming 模式输出 token/chunk

服务端转为 SSE：

{"type":"content","data":"..."}

{"type":"done"} / {"type":"error"}

结束后落库 history

### 4.4. /api/ai_ops （AIOps 多 Agent）

使用 LangGraph 构建状态机：

Supervisor：决定调用 Planner 还是 Executor，或 FINISH

Planner：输出结构化计划（PLAN/EXECUTE/FINISH + step + tool hints）

Executor：只执行第一步，返回 evidence/summary/status

强约束：

所有结论必须来自工具证据

同一工具连续失败 N 次（建议 3 次）终止并在报告中说明

输出：固定 Markdown 报告模板（与 Java 一致）

## 5. 配置设计（与现有 application.yml 对齐）

建议 Python 使用环境变量 + .env （开发）+ 配置类 Settings ：

APP_PORT=9900

DASHSCOPE_API_KEY=...

MILVUS_HOST=localhost

MILVUS_PORT=19530

UPLOAD_DIR=./uploads

DOC_CHUNK_MAX_SIZE=800

DOC_CHUNK_OVERLAP=100

RAG_TOP_K=3

LLM_MODEL=qwen3-max

EMBEDDING_MODEL=text-embedding-v4

PROMETHEUS_BASE_URL=http://localhost:9090

## 6. 迁移计划（里程碑）

Milestone 1：Python 项目骨架与基础 API（1-2 天） 搭建 FastAPI 工程结构、配置体系、日志

定义与现有前端兼容的 DTO（Id/Question/统一响应）

打通 /api/chat （先不接工具，先能对话）

Milestone 2：工具层与会话管理（2-4 天） Session store（内存版 → 可选 Redis）

Tool：datetime、Prometheus（最小可用）

/api/chat_stream SSE（前端可直接复用）

Milestone 3：RAG（索引 + 检索 + 生成）（3-6 天） Milvus schema 对齐（id/vector/content/metadata）

/api/upload + 覆盖更新删除逻辑

RAG：retriever + prompt + streaming

Milestone 4：AIOps LangGraph（4-8 天） 复刻 Java 的 Planner/Executor/Supervisor 逻辑

固定报告模板输出 + 工具失败熔断

可选：对接日志系统（直连 API 或 MCP 网关）

Milestone 5：工程化与作品集打磨（持续） Docker compose 一键启动（Milvus + API + Redis）

关键路径测试（上传→RAG→AIOps）

增加可观测性（trace/prompt 记录）与 README 演示

## 7. 命名约定（替换“OnCall Agent”相关命名）

对外展示名统一使用： SuperBiz 智能助手 / SuperBizAgent

避免在文档与代码中使用 oncallagent 作为项目名或包名

## 8. 你需要掌握的主要技术栈（除 FastAPI / LangChain /

LangGraph）
### 8.1. Python 工程与异步

Python asyncio / async / await （理解 I/O 并发、避免阻塞）

httpx （异步 HTTP 客户端：调用 Prometheus、日志平台、模型网关等）

数据校验与 DTO：Pydantic v2（含 pydantic-settings 配置管理）

### 8.2. SSE/流式输出（前后端契约）

SSE（Server-Sent Events）协议与实现方式（FastAPI 侧输出事件流、前端消费）

### 8.3. 向量库与 RAG 工程化

Milvus（collection/schema/index/search、过滤表达式、批量写入）

pymilvus （Milvus Python SDK）

文档切分/清洗：chunking 策略、overlap、去重与元数据设计

### 8.4. 模型服务与 Function Calling

DashScope（通义千问/Qwen）OpenAI 兼容接口

Embedding API（向量化模型选择、维度与成本）

Function Calling（工具调用）/ 结构化输出（Pydantic schema）

### 8.5. AIOps 工具侧集成

Prometheus（HTTP API、PromQL 基础、告警/指标查询）

日志系统对接（云日志 API 或 MCP 工具网关）

### 8.6. 部署与依赖（作品集加分项）

Docker / Docker Compose（Milvus + API + Redis 一键启动）

Redis（会话/缓存/限流/任务队列中转）

Celery（可选：文档批量向量化、重建索引等长任务）

### 8.7. 可观测性与工程质量

日志：structlog 或 loguru（二选一即可）

OpenTelemetry（可选：trace/metrics/logs）

测试：pytest（建议补最小回归集：上传→索引→检索→AIOps）

代码质量：ruff + black（必备）

### 8.8. 鉴权（如果你要把项目做成“可上线 demo”）

OAuth2 + JWT（FastAPI 官方示例即可）

## 9. 推荐学习文档（中文优先）

说明：以下优先给“官方中文”；若官方无中文，给高质量中文社区/翻译站点，并标注“非官方”。

### 9.1. Milvus / PyMilvus

Milvus 官方文档（含中文入口）：https://milvus.io/docs/zh/

Milvus 快速入门（官方）：https://milvus.io/docs/quickstart.md

用 Milvus 构建 RAG（官方中文页）：https://milvus.io/docs/zh/text_search_engine.md

安装 PyMilvus（官方）：https://milvus.io/docs/install-pymilvus.md

Milvus 中文文档仓库（非官方/社区）：https://github.com/aidoczh/milvus-doc-zh

### 9.2. DashScope（通义千问/Qwen）

Qwen API Reference（官方中文）：https://help.aliyun.com/zh/model-studio/qwen-api-refere nce/

第一次调用 Qwen API（官方中文）：https://help.aliyun.com/zh/model-studio/first-api-call-toqwen

Function Calling（官方中文）：https://help.aliyun.com/zh/model-studio/qwen-function-callin g

向量化 Embedding（官方中文）：https://help.aliyun.com/zh/model-studio/embedding

### 9.3. Prometheus / PromQL

Prometheus 中文手册（非官方翻译）：https://hulining.gitbook.io/prometheus/

Prometheus Handbook（非官方/总结型）：https://github.com/yangchuansheng/prometheus -handbook

### 9.4. Docker / Docker Compose

Docker Compose 官方文档（英文为主）：https://docs.docker.com/compose/

Docker Compose 中文镜像站（非官方）：https://dockerdocs.cn/compose/

Compose 文件规范（官方）：https://docs.docker.com/reference/compose-file/

### 9.5. Redis

Redis 中文教程（中文站）：https://redis.com.cn/tutorial.html

Redis 官方文档（英文）：https://redis.io/docs/latest/

### 9.6. Celery（异步任务，可选）

Celery 中文手册（非官方）：https://www.celerycn.io/

Celery 官方文档（英文）：https://docs.celeryq.dev/

### 9.7. SQLAlchemy（可选：持久化）

SQLAlchemy 中文文档（社区翻译）：https://docs.sqlalchemy.org.cn/en/20/

SQLAlchemy 官方文档（英文）：https://docs.sqlalchemy.org/en/20/

### 9.8. OpenTelemetry（可选：可观测性）

OpenTelemetry 中文文档（官方）：https://opentelemetry.io/zh/docs/

### 9.9. SSE（流式输出必备概念）

MDN SSE（中文）：https://developer.mozilla.org/zh-CN/docs/Web/API/Server-sent_events

### 9.10. httpx / Pydantic / pytest（补充）

httpx 官方 Quickstart（英文）：https://www.python-httpx.org/quickstart/

httpx 中文教程（非官方）：https://www.w3cschool.cn/httpx/httpx-quickstart.html

Pydantic 官方文档（英文）：https://docs.pydantic.dev/latest/

pytest 官方文档（英文）：https://docs.pytest.org/en/stable/contents.html

状态：规划文档已生成，可按此逐步落地 Python 版本实现。
