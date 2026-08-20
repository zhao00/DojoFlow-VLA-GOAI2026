# DojoFlow-VLA- GOAI2026

面向 GOAI 2026「具身未来」赛道一的通用双臂协作项目。项目以
[Hy-Embodied-0.5-VLA](https://github.com/Tencent-Hunyuan/Hy-Embodied-0.5-VLA)
为基础模型，使用 GOAI/RoboDojo 官方 HDF5 数据进行全参数监督微调，并通过
[XPolicyLab](https://github.com/XPolicyLab/XPolicyLab) 连接策略服务器与
RoboDojo/X-Eval 仿真环境。

## 项目状态

| 环节 | 状态 | 说明 |
|---|---|---|
| 数据检查 | 已完成 | 12 个任务、1,200 条轨迹、592,432 个时间步 |
| 归一化统计 | 已完成 | 25 步 action chunk、UMI 坐标系 |
| HyVLA 微调 | 已完成 | 4×H200、BF16、全参数、200,000 step |
| 模型导出与校验 | 已完成 | checkpoint、tokenizer、norm stats、SHA-256 |
| 本地闭环冒烟测试 | 已完成 | Generalization 24 个配置均产生有效结果 |
| 官方初赛评测 | 主办方处理中 | 正式结果以主办方通知为准 |

## 模型对比与最终选择

以下是同一 RoboDojo 环境中的独立本地冒烟测试，不是官方比赛成绩：

| 模型 | 测试范围 | 成功 | 成功率 | 平均分 |
|---|---:|---:|---:|---:|
| ACT | `stack_bowls` 5 episodes | 0/5 | 0% | — |
| StarVLA PI-v3 | 24 configs，seed 0 | 2/24 | 8.33% | 10.42 |
| HyVLA-70k | 24 configs，seed 0 | 1/24 | 4.17% | 7.08 |
| **HyVLA-200k** | **24 configs，seed 0** | **3/24** | **12.50%** | **15.00** |

HyVLA-200k 在三个完整 24 配置测试模型中取得最高成功数和平均分，因此作为最终候选。
ACT 的测试范围不同，不参与严格同口径排名。详细说明见
[模型对比与方案选择](docs/模型对比与方案选择.md)，成功视频见 [Demo](demo/README.md)。

## 评测口径

仓库保留两批互不合并的 HyVLA-200k 本地记录：

- 主线批次：seed 0 完成 24 个配置，成功 2/24，原始 `score` 平均 11.67；另在 seed 1
  补充测试中观察到 `pour_liquid_into_cup` 成功。
- 独立模型对比批次：seed 0 完成 24 个配置，成功 3/24，平均分 15.00。

两批记录来自不同机器和运行批次，只用于验证端到端闭环与模型选择，不能合并或视为正式
榜单成绩。逐任务数据见 [冒烟测试报告](docs/冒烟测试报告.md)和
[结果目录](results/README.md)。

## 技术路线

```text
语言指令 + 头部/双腕 RGB 历史 + 双臂状态
                    │
                    ▼
      HyVLA 视觉语言主干 + Flow-Matching 动作专家
                    │
                    ▼
       25 步双臂相对末端位姿动作（action_type=ee）
                    │
                    ▼
     XPolicyLab Policy Server ──WebSocket── RoboDojo/X-Eval
```

训练使用约 45 亿参数的 `Hy-Embodied-0.5-VLA-UMI`、三视角六帧视觉历史、4×H200、
DeepSpeed ZeRO-2 和 BF16。完整参数见
[`configs/train_hyvla_robodojo_4xh200.yaml`](configs/train_hyvla_robodojo_4xh200.yaml)。

## 仓库结构

```text
├── artifacts/   # checkpoint 与 norm stats 清单
├── configs/     # 训练和部署配置
├── demo/        # 按模型/checkpoint 分类的成功主视角视频
├── docs/        # 技术、数据、复现、部署与评测文档
├── results/     # 训练曲线和本地评测数据
└── scripts/     # 数据统计、训练、绘图和模型校验脚本
```

## 快速复现

本仓库不复制第三方完整源码。请先准备 RoboDojo、XPolicyLab、HyVLA 基础模型和官方数据，
再按 [复现指南](docs/复现指南.md)配置路径。

```bash
# 1. 生成与训练一致的 norm stats
bash scripts/compute_norm_stats.sh

# 2. 单机四卡训练
bash scripts/train_hyvla_4gpu.sh

# 3. 验证导出的模型包
python scripts/verify_checkpoint.py /path/to/HyVLA-GOAI-step-199999
```

## 文档导航

- [技术方案](docs/技术方案.md)
- [数据集说明](docs/数据集说明.md)
- [训练与复现指南](docs/复现指南.md)
- [评测方案](docs/评测方案.md)
- [测评部署记录](docs/测评部署记录.md)
- [冒烟测试报告](docs/冒烟测试报告.md)
- [模型对比与方案选择](docs/模型对比与方案选择.md)
- [实验结果](results/README.md)
- [成功 Demo](demo/README.md)

## 模型与数据

模型权重和官方数据集不进入 Git 历史。仓库只保存可复现配置、训练脚本、归一化统计、
校验清单、训练曲线、本地评测汇总和成功 Demo。

最终模型和评测适配代码通过
[ModelScope](https://modelscope.cn/models/kong00/HyVLA-GOAI) 公开发布；模型文件与校验值见
[`artifacts/checkpoint_manifest.json`](artifacts/checkpoint_manifest.json)。

## 结果声明

训练过程中的 proxy validation 指标只用于监控训练稳定性，不能替代 RoboDojo 闭环成功率。
仓库中的本地小样本结果不代表官方比赛成绩，正式结果以主办方发布为准。

## License

本仓库自研脚本与文档采用 Apache License 2.0。第三方模型、代码、数据和仿真资产遵循各自
许可证，详见 [THIRD_PARTY.md](THIRD_PARTY.md)。
