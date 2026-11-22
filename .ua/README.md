# Mika 中文知识图谱

使用 [Understand-Anything 的 understand 技能](https://github.com/Egonex-AI/Understand-Anything/blob/a6ea4024767df85ce4f99140d4f12ecfc5a81eb6/understand-anything-plugin/skills/understand/SKILL.md)生成，源码基准为 `f3bbbdf92caeb4259d55922e12f61f6da11469fd`，工具固定在 `a6ea4024767df85ce4f99140d4f12ecfc5a81eb6`（版本号 `2.9.8`）。

<!-- generation-status -->
正在生成。分支中的恢复点用于避免工作环境重置导致分析丢失。
<!-- /generation-status -->

## 查看

安装技能后，在本仓库运行 `/understand-dashboard`。使用启动日志中的完整 URL，保留 `?token=...` 参数。

也可以直接从固定工具源码启动（Node.js ≥22、pnpm ≥10）：

```bash
MIKA_REPO=/absolute/path/to/Mika
git clone https://github.com/Egonex-AI/Understand-Anything.git understand-anything
cd understand-anything
git checkout a6ea4024767df85ce4f99140d4f12ecfc5a81eb6
cd understand-anything-plugin
pnpm install --frozen-lockfile
pnpm --filter @understand-anything/core build
cd packages/dashboard
GRAPH_DIR="$MIKA_REPO" pnpm exec vite --host 127.0.0.1
```

## 产物

| 文件 | 用途 |
| --- | --- |
| [knowledge-graph.json](knowledge-graph.json) | 节点、关系、架构层及中文学习导览 |
| [STUDY_GUIDE.md](STUDY_GUIDE.md) | 可直接在 GitHub 阅读的架构概览与学习路线 |
| [analysis-report.json](analysis-report.json) | 分析来源、覆盖范围与限制 |
| [validation-report.json](validation-report.json) | 结构、覆盖、导入关系与指纹校验结果 |
| [fingerprints.json](fingerprints.json) | 官方结构指纹，供增量更新使用 |
| [intermediate/scan-result.json](intermediate/scan-result.json) | 官方文件清单和内部导入关系 |
| [meta.json](meta.json) | 分析时间与源码提交 |
| [config.json](config.json) | 中文输出偏好，未开启提交时自动更新 |

保留源码、测试、文档和资源，排除默认忽略项、5个二进制文件及 `.ua/` 自身。
原始标识符与路径不改，说明使用中文。图谱结合静态解析、源码注释和语义审阅；函数/类按重要性筛选，动态调用不保证穷举，具体解析限制见报告。

## 校验与更新

在仓库根目录运行 `python3 .ua/validate.py`，检查完整文件覆盖、节点ID、行号、引用、导入关系、层与导览，以及源码指纹。

源码变化后运行 `/understand --language zh`；需要全量重建时添加 `--full`。更新后将图谱、元数据、指纹与清单一起提交。
图谱内的提交号表示被分析的源码，保存图谱产生的后续提交不改变这个基准。
