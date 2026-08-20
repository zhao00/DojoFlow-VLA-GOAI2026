# DojoFlow-VLA

面向 GOAI 2026「具身未来」赛道赛题一——通用双臂协作操作能力测试的开源参赛项目。

本项目不重新实现一个虚构的双臂框架，而是记录并开放一条已经执行的工程路线：以
[Hy-Embodied-0.5-VLA](https://github.com/Tencent-Hunyuan/Hy-Embodied-0.5-VLA)
为基础模型，使用 GOAI/RoboDojo 官方 HDF5 数据进行全参数监督微调，再通过
[XPolicyLab](https://github.com/XPolicyLab/XPolicyLab) 内置的
`Hy_Embodied_05_VLA` 适配器连接策略服务器与 RoboDojo/X-Eval 环境客户端。

## 项目状态

| 环节 | 状态 | 说明 |
|---|---|---|
| 官方数据检查 | 已完成 | 12 个任务、1,200 条轨迹、592,432 个时间步 |
| 归一化统计 | 已完成 | 25 步 action chunk、UMI 坐标系 |
| Hy-VLA 微调 | 已完成 | 4×H200、BF16、全参数、200,000 step |
| 模型导出与校验 | 已完成 | 最终 checkpoint、tokenizer、norm stats、SHA-256 |
| 本机闭环冒烟测试 | 已完成 | Generalization 24 配置各 1 episode，24/24 产生有效结果 |
| 官方初赛评测 | 主办方处理中 | 公网 WSS 不稳定后已改为代码与 checkpoint 受控交付；截止提交时结果字段暂以占位内容提交 |
| 真机评测 | 待官方阶段确认 | 不在当前仓库中宣称已完成 |

## 本机冒烟结果

固定 checkpoint `HyVLA-GOAI-step-199999`、`action_type=ee`，对 12 个标准配置和
12 个 `_random` 配置各完成至少 1 个 episode；成功覆盖统计采用每个配置已经观察到的
成功结果，其中 `pour_liquid_into_cup` 采用补充测试的 seed 1：

| 指标 | 全部 24 配置 | 标准 12 配置 | Random 12 配置 |
|---|---:|---:|---:|
| 端到端结果文件 | 24/24 | 12/12 | 12/12 |
| 二元成功覆盖 | 3/24（12.50%） | 3/12（25.00%） | 0/12（0%） |
| 原始 seed 0 `score` 简单平均 | 11.67 | 21.25 | 2.08 |

已观察到二元成功的配置为 `fold_clothes`、`stack_bowls` 和 `pour_liquid_into_cup`；第三项
来自 seed 1 补充测试。`pack_objects_into_box` 等任务获得部分分数但未达到成功条件。这里
的样本量很小，目的是验证模型加载、仿真、推理、动作执行
和结果保存链路，**不是官方初赛成绩**。详见 [冒烟测试报告](docs/冒烟测试报告.md)。

## 为什么叫 DojoFlow-VLA

Hy-VLA 的动作专家采用条件流匹配，而不是把动作离散成语言 token。训练时，将真实动作
`a` 与高斯噪声 `ε` 插值得到 `x_t`，学习速度场 `u_t = ε - a`；推理时从噪声出发，
通过 Euler 积分得到连续双臂动作。本项目使用该动作专家在 RoboDojo 数据上进行微调，
因此使用 `DojoFlow-VLA` 作为参赛项目名。

## 已执行的训练配置

- 基础模型：`Hy-Embodied-0.5-VLA-UMI`
- 模型规模：约 4.527B 参数
- 数据：GOAI/RoboDojo 官方 12 个仿真任务
- 输入：头部相机 + 左右腕部相机、6 帧视觉历史、语言指令、双臂状态
- 输出：25 步双臂相对末端位姿动作，20 维训练动作表征
- 训练：4×NVIDIA H200、DeepSpeed ZeRO-2、BF16
- 每卡 batch：8；全局 batch：32；梯度累积：1
- 总步数：200,000，约 10.8 个数据 epoch
- 学习率：`5e-5`，warmup 1,000，cosine decay 150,000，底值 `5e-6`
- checkpoint：每 10,000 step；代理 validation：每 5,000 step

完整脱敏记录见 [训练配置](configs/train_hyvla_robodojo_4xh200.yaml)和
[训练与复现说明](docs/复现指南.md)。

## 仓库导航

- [项目简介](docs/项目简介.md)
- [技术方案](docs/技术方案.md)
- [数据集说明](docs/数据集说明.md)
- [复现指南](docs/复现指南.md)
- [评测方案](docs/评测方案.md)
- [测评部署记录](docs/测评部署记录.md)
- [冒烟测试报告](docs/冒烟测试报告.md)
- [初赛提交清单](docs/初赛提交清单.md)
- [提交与访问控制](docs/提交与访问控制.md)
- [开源与第三方依赖](THIRD_PARTY.md)
- [实验结果说明](results/README.md)

## 快速入口

```bash
# 1. 生成与训练一致的 RoboDojo norm stats
bash scripts/compute_norm_stats.sh

# 2. 单机四卡训练（所有路径均通过环境变量传入）
bash scripts/train_hyvla_4gpu.sh

# 3. 验证导出的模型包
python scripts/verify_checkpoint.py /path/to/HyVLA-GOAI-step-199999
```

闭环评测应在已安装 RoboDojo 与 XPolicyLab 的独立环境中执行，命令和固定参数见
[测评部署记录](docs/测评部署记录.md)。

## 模型与数据

模型权重和官方数据集不进入 Git 历史。仓库只保存：

- 可复现配置和脚本；
- 数据来源、规模与格式说明；
- `norm_stats.pkl` 及其 SHA-256；
- 模型 manifest 与最终 tar 的 SHA-256；
- 静态训练曲线和闭环评测汇总。

最终模型和评测适配代码已上传到受控的
[ModelScope 仓库](https://modelscope.cn/models/kong00/HyVLA-GOAI)。该仓库保持 Private，
仅向主办方指定账号授权。模型清单见
[checkpoint_manifest.json](artifacts/checkpoint_manifest.json)。

## 结果声明

训练内的 `val/loss` 和 `val/angle dist` 使用训练 dataloader 抽样，只用于监控训练是否
稳定，不能替代 RoboDojo 闭环成功率。仓库不会把训练代理指标或单次冒烟结果描述为比赛
成绩；截至材料提交时主办方仍在执行正式评测，正式结果字段均为明确标记的占位内容，待
结果邮件返回后按 [评测方案](docs/评测方案.md)回填。

## License

本仓库自研脚本与文档采用 Apache License 2.0。第三方模型、代码、数据和仿真资产分别
遵循其原始许可证，详见 [THIRD_PARTY.md](THIRD_PARTY.md)。
