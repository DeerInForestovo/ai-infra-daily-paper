# AI Infra Daily Paper

每日从 arXiv 采集 AI Infrastructure 相关论文，以中英双语 Markdown 索引形式归档。

## 归档方式

- 每个工作日生成一个文件：`YYYY-MM-DD.md`，直接放在仓库根目录。
- 每篇论文包含标题、作者、分类、arXiv 链接和中英双语摘要。
- **不下载 PDF**，所有引用均通过 arXiv 链接访问，保持仓库轻量。

## 关注方向

本仓库优先收录与开源框架（如 vLLM）和开源模型（如 Qwen，以及基于开源模型后训练的私有模型）部署优化直接相关的论文，包括：

- LLM 推理加速（投机解码、多 token 预测）
- 模型量化与压缩（AWQ、GPTQ、INT4/FP4、三值量化、剪枝、稀疏化）
- KV Cache 与显存优化（压缩、驱逐、重用、PagedAttention）
- Serving 系统（vLLM、continuous batching、request scheduling、并行策略）

## 工作流

1. 运行 `collect_candidates.py` 拉取当天 CS 分类论文并粗筛候选。
2. Agent 人工审查候选，标记相关论文。
3. 运行 `generate_index.py` 生成英文索引并清理临时文件。
4. Agent 将英文摘要翻译为中文，保存为 `YYYY-MM-DD.md`。

详细说明见 [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md) 和 [`AGENTS.md`](AGENTS.md)。

## 文件说明

| 文件 | 说明 |
|------|------|
| `collect_candidates.py` | 从 arXiv 拉取候选论文 |
| `generate_index.py` | 生成最终英文索引并清理临时文件 |
| `HOW_IT_WORKS.md` | 完整工作流文档 |
| `AGENTS.md` | 面向 AI agent 的项目上下文 |
| `YYYY-MM-DD.md` | 每日中英双语论文索引 |

## 依赖

- Python 3.10+
- `arxiv` Python 包

```bash
python -m venv .venv
source .venv/bin/activate
pip install arxiv
```

## 许可

本仓库仅收录论文元数据和摘要，论文版权归各自作者所有。
