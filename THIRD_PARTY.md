# 第三方组件与边界

本项目自研内容主要是比赛复现配置、训练封装、模型核验、实验记录和技术文档。以下组件
属于第三方，不将其模型架构或代码声明为本项目原创。

| 组件 | 用途 | 固定版本/来源 | 许可证说明 |
|---|---|---|---|
| Hy-Embodied-0.5-VLA | 基础模型、训练与 RoboDojo 数据管线 | commit `af57e7507ec5964b52fdf6296741e553cbcd3288` | 上游仓库声明 Apache-2.0 |
| XPolicyLab | Hy-VLA 策略适配、WebSocket policy server/client | 训练记录 `3dddc0f...`；本机闭环评测 `432f82b1758c5b1202e42a3dfe014546dbc50871` | 上游仓库 Apache-2.0 |
| RoboDojo | 数据、仿真任务和评测环境 | commit `36bfcb7c580b149c6e39ed2eb77d60689152e570` | 上游仓库 MIT；资产可能另有条款 |
| GOAI/RoboDojo 数据 | 监督微调数据 | 比赛官方渠道 | 不在本仓库重新分发，以官方授权为准 |
| NVIDIA Isaac Sim | 仿真运行时 | 本机评测日志记录 5.1 | 遵循 NVIDIA 软件许可 |
| NVIDIA CUDA/PyTorch | 模型训练与推理 | 训练环境清单待发布 | 遵循各自许可证 |

## 商业 API 与闭源模型

核心训练和推理不依赖商业 API，也不以闭源模型作为核心能力。W&B 仅用于实验可视化；
离线 CSV/PNG 会随仓库提供，因此不要求评委拥有 W&B 账号才能审阅结果。

## 模型权重

微调权重不进入 Git 历史。评审使用受控 ModelScope 仓库获取权重，地址和 SHA-256 见
`artifacts/checkpoint_manifest.json`。仓库默认保持 Private，需显式授予主办方账号访问
权限。使用者还应遵守基础模型许可证和比赛数据授权条款。
