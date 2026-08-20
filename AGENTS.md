# AGENTS.md

## 项目目标

维护 GOAI 2026 赛道一双臂协作项目的训练、部署、测评和模型对比材料。

## 内容约定

- 保留现有 DojoFlow-VLA 和 HyVLA-200k 主线。
- ACT、StarVLA、HyVLA-70k、HyVLA-200k 分开记录。
- 不同机器、seed 和评测批次不得混写。
- runner PASS 不代表任务成功。
- README 保持精简，详细内容放入 docs 和 results。
- Demo 只保留头部主视角。
- 同一模型同一任务只保留一个成功 Demo。

## 禁止提交

- 模型权重、checkpoint 和压缩包。
- 数据集、仿真资产、缓存和完整日志。
- 密钥、Token、密码和机器绝对路径。

## 安全边界

删除文件、修改密钥、commit、push、rebase、强制推送和公开发布前，必须取得明确授权。

## 验证要求

修改后运行 JSON 校验、git diff --check 和 git status --short。
