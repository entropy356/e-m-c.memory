# 在 DeepSeek Harness 中使用 e-m-c Memory

`dsh-emc-memory` 将 [Memory v0.1](memory-model.md) 接入 DeepSeek Harness。DSH 通过 Cordis 注册两个工具，Python 负责神经元集群分配、突触学习和记忆唤起。

## 安装

需要 DeepSeek Harness `0.2.2-rc.1`、Node.js 24.9+、pnpm，以及装有 NumPy 的 Python 3.10+。从仓库根目录运行：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install numpy
dsh plugin --profile web add "$PWD"
dsh --profile web --dump-config
```

在 `$DSH_HOME/profiles/web/cordis.patch.yml` 中为 `emc-memory` 设置虚拟环境的 Python 绝对路径。未设置 `DSH_HOME` 时默认使用 `~/.dsh`。已有其他设置时，将以下条目追加到 YAML 列表中。

```yaml
- id: emc-memory
  config:
    python: /absolute/path/to/e-m-c/.venv/bin/python
```

Windows 下的虚拟环境解释器位于 `.venv/Scripts/python.exe`。如果 DSH 启动时的 `python3` 已装有 NumPy，可省略此配置。运行 `dsh web` 或重启 Web profile，打开一个工作区后试用：

- 「请用 `emc_memory_write` 记住：项目的部署数据库使用 PostgreSQL，生产环境启用了每日备份。」
- 「请用 `emc_memory_recall` 查询『部署数据库』。」

## 工作方式

- `emc_memory_write` 写入一段文本并返回记忆 ID。每段文本最长 16 KiB UTF-8。
- `emc_memory_recall` 从静息状态按查询唤起记忆，最多返回三条原文及其激活评分。唤起不改动长期状态。模型仅在调用工具时读写记忆。
- 编码器在本机对词和汉字片段做确定性哈希。它提供词面线索，适合验证写入和唤起流程。语义改写及长期联想效果仍待验证。
- 快照保存在 `$DSH_HOME/emc-memory/<工作区绝对路径的 SHA-256>/memory.sqlite3`。同一 DSH home 中，同一路径下的会话和 profile 共享记忆。使用 `dsh plugin --profile web remove dsh-emc-memory` 可卸载工具。若要清空某个工作区的全部记忆，先关闭使用该工作区记忆的 DSH 进程，再删除对应的 SQLite 文件。

## 官方文档

- [编写工具](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/tool.md)
- [打包并安装插件](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/publish.md)
- [插件配置](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/config.md)
