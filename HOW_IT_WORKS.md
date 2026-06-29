# AI Infra 论文采集工作流说明

本文档记录如何从 arXiv 采集 AI Infrastructure 相关论文，并仅以根目录下的双语 Markdown 文件归档，不保留本地 PDF，避免仓库臃肿。

## 设计原则

- **无本地 PDF**：所有论文只通过 arXiv 链接引用，不下载到仓库。
- **单文件归档**：每个日期只保留一份根目录下的 `YYYY-MM-DD.md`（中英双语）。
- **临时中间文件**：`YYYY-MM-DD_candidates.md` 仅在 agent 筛选期间存在，最终会被自动删除。
- **可复现**：任何 agent 接手仓库后，按照本文档步骤即可继续更新。

## 项目结构

```
.
├── AGENTS.md                  # 面向 AI agent 的项目上下文
├── HOW_IT_WORKS.md            # 本说明文档
├── collect_candidates.py      # 阶段 1：按 CS 分类拉取并粗筛候选论文
├── generate_index.py          # 阶段 3：生成英文索引并清理中间文件
├── .venv/                     # Python 虚拟环境
├── 2026-06-25.md              # 示例：最终双语索引
└── 2026-06-26.md              # 示例：最终双语索引
```

## 工作流（三阶段）

### 阶段 1：按 CS 分类拉取并粗筛候选

脚本：`collect_candidates.py`

1. 严格按指定日期搜索 arXiv。
2. 扫描多个 CS 分类：`cs.LG`, `cs.CL`, `cs.AI`, `cs.AR`, `cs.DC`, `cs.SE`, `cs.OS`, `cs.DB`, `cs.NE`, `cs.CV`。
3. 用 AI Infra 强相关关键词对标题+摘要做粗筛。
4. 在仓库根目录生成临时文件 `YYYY-MM-DD_candidates.md`。

运行：

```bash
source .venv/bin/activate
python collect_candidates.py --date 2026-06-25
```

### 阶段 2：Agent 人工筛选

1. Agent 读取根目录下的 `YYYY-MM-DD_candidates.md`。
2. 根据标题和摘要判断是否与 AI Infrastructure 相关。
3. 对要保留的论文，将其条目下的 `- [ ] Select` 改为 `- [x] Select`。

**筛选规则（核心）**：

> 优先保留与**开源框架（如 vLLM）和开源模型（如 Qwen，或公司基于开源模型后训练的私有模型）的部署优化**直接相关的论文，目标是提高推理延迟、吞吐量、显存效率、部署密度等指标。

**高优先级方向**：

- LLM 推理加速：投机解码、多 token 预测、解码延迟优化
- 模型量化与压缩：AWQ、GPTQ、INT4/FP4/三值量化、剪枝、稀疏化
- KV Cache 与显存优化：KV cache 压缩、驱逐、量化、重用、PagedAttention
- Serving 系统：vLLM、continuous batching、request scheduling、并行策略

**低优先级 / 通常排除**：

- 纯训练效率、分布式训练优化器
- 特定应用领域（如自动驾驶、医学影像）的效率优化，除非可直接迁移
- 纯模型架构改进而没有明确部署/推理收益
- 可解释性、安全对齐、数据增强等非系统方向

每日精选数量建议控制在 **5-10 篇**。

### 阶段 3：生成英文索引（自动）

脚本：`generate_index.py`

1. 读取 `YYYY-MM-DD_candidates.md` 中选中的条目。
2. 通过 arXiv API 获取完整元数据。
3. 在仓库根目录生成 `YYYY-MM-DD.md`（英文版）。
4. 自动删除临时文件 `YYYY-MM-DD_candidates.md`。

运行：

```bash
source .venv/bin/activate
python generate_index.py --date 2026-06-25
```

### 阶段 4：翻译成中英双语（Agent 手动）

Agent 读取根目录下的 `YYYY-MM-DD.md`，在每条英文摘要下方补充中文翻译，保存为根目录下的同名文件。格式要求：

```markdown
## 1. Paper Title

> 中文标题

- **arXiv ID:** xxx
- **Authors / 作者:** ...
- **Published / 发布日期:** ...
- **Categories / 分类:** ...
- **arXiv URL:** http://arxiv.org/abs/xxx

### Abstract / 摘要

English abstract here...

中文摘要 here...

---
```

**默认行为**：阶段 2 完成后，agent 应立即自动执行阶段 3 和阶段 4，无需再次询问用户确认。

## 关于日期

- **周末通常无新论文**：arXiv 的 CS 分类一般只在工作日（周一至周五）发布新论文，周六和周日通常没有新论文。因此，如果指定日期是周末，脚本会生成空的 `YYYY-MM-DD_candidates.md`。
- **未来日期**：如果指定日期在未来，arXiv 上自然没有论文。
- **节假日**：部分节假日可能也无新论文发布。

若当天没有论文，脚本会明确提示，并生成空的候选文件（可直接删除）。

## 环境要求

- Python 3.10+
- 依赖：`arxiv` Python 包

虚拟环境已配置：

```bash
source .venv/bin/activate
```

如需重新安装依赖：

```bash
python -m venv .venv
source .venv/bin/activate
pip install arxiv
```

## 关键词策略

`collect_candidates.py` 中的 `INFRA_KEYWORDS` 只保留与 AI Infra 强相关的技术关键词，例如：

- `inference acceleration`, `inference optimization`, `decoding acceleration`
- `speculative decoding`, `multi-token prediction`
- `quantization`, `pruning`, `sparsity`, `model compression`, `knowledge distillation`, `AWQ`, `GPTQ`
- `KV cache`, `paged attention`, `memory efficient`
- `model parallelism`, `tensor parallelism`, `pipeline parallelism`, `distributed training`, `distributed inference`
- `mixture of experts`, `MoE`
- `training efficiency`, `gradient compression`, `federated learning`
- `long context`, `efficient attention`, `linear attention`

弱关键词（如 `inference`, `serving`, `latency`, `NPU`, `kernel` 等）已被移除，以减少假阳性。

## 未来改进方向

1. **LLM 自动筛选**：接入 LLM API，让模型根据标题和摘要自动判断相关性，替代阶段 2 的人工审查。
2. **自动翻译**：接入翻译 API，从英文 `YYYY-MM-DD.md` 自动生成中英双语版本。
3. **命令行增强**：支持 `--categories`、`--keywords`、`--min-matches` 等参数。

## 注意事项

- 本工作流不下载 PDF，所有引用均通过 arXiv URL 链接。
- arXiv API 有速率限制，脚本已做合理控制。
- 中文翻译为辅助阅读，学术引用请以 arXiv 页面和 PDF 原文为准。
