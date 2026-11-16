# 自动化（GitHub Actions）

三条流水线，都在 `.github/workflows/`：

| 工作流 | 触发 | 做什么 |
|---|---|---|
| `verify` | 每次 push / PR（涉及 docs、tools、html、CHANGELOG） | 跑 `tools/verify.py`：课页数＝成人页数、插图＝2N、占位框 0、base64 图互不重复、页码连续、根目录合览同源、单课页齐备、入口链接无死链、版本号已记入 CHANGELOG |
| `rebuild` | 改动 `tools/lessons_*.py`、`assets/**`、`tools/build.py` 时自动；也可手动 Run | 用指定装配器（默认 `build_book.py`，即总装）`--full` 重出单课页与合册，校验通过后自动提交 |
| `live-check` | 每天 09:00（UTC+8）+ 手动 | `tools/check_live.py --all`：线上 `index.html`、`book.html`（字节数与仓库一致）、全部单课页是否 200 |

## 日常怎么用

1. 新一课的文稿、配图按既有流程落进 `tools/lessons_*.py` 与 `assets/`，直接 push。`rebuild` 会自己重拼整本、校验、提交；`verify` 随后再核一遍（自动提交带 `[skip ci]`，不会循环触发）。
2. `git push` 后，`verify` 自动跑；失败会在 Actions 里列出具体是哪一项不一致（例如「已改为 72 课但入口只列 71 条」）。
3. 手动重出：Actions → `rebuild` → 填装配器名（默认 `build_book.py`）→ Run。提交信息带 `[skip ci]` 避免循环触发。
4. 线上部署有延迟，`live-check` 内置 6 次 × 30 秒重试；也可以手动 Run 一次确认刚推的版本已生效。

## 本地同款命令

```bash
python3 tools/verify.py        # 结构校验
python3 tools/check_live.py    # 线上核对（--all 含每课）
```

## 边界

- `verify` 只校验结构与一致性，不判断文案内容；义理口径仍需人工过稿。
- `tools/build_book.py` 是总装：封面按课数与 CHANGELOG 版本年月生成，第 1–5 课沿用 `docs/book.html` 里的原页（已定稿，无内容模块），第 6 课起由 `tools/lessons_*.py` 逐课渲染。所以它能把第 6 课以后任意改动重拼成整本，但第 1–5 课的正文仍以那份原页为准。
- `--check` 只比对不写盘，适合确认「内容模块是否与已发布合册一致」。
- Pages 走 `main:/docs` 分支部署，工作流不接管部署，只做校验与重建。
