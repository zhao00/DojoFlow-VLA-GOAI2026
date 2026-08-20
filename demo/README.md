# 成功任务 Demo

本目录收录本地 RoboDojo 冒烟测试中成功 episode 的头部主视角视频。左右腕部视角、失败
视频和同一模型同一任务的重复运行不纳入仓库。

| 模型 | Checkpoint | 任务 | 视频 |
|---|---|---|---|
| StarVLA PI-v3 | `steps_100000` | `fold_clothes` | [播放](starvla/step_100000/fold_clothes.mp4) |
| StarVLA PI-v3 | `steps_100000` | `stack_bowls` | [播放](starvla/step_100000/stack_bowls.mp4) |
| HyVLA-70k | `step-69999` | `stack_bowls` | [播放](hyvla/step_69999/stack_bowls.mp4) |
| HyVLA-200k | `step-199999` | `fold_clothes` | [播放](hyvla/step_199999/fold_clothes.mp4) |
| HyVLA-200k | `step-199999` | `pour_liquid_into_cup` | [播放](hyvla/step_199999/pour_liquid_into_cup.mp4) |
| HyVLA-200k | `step-199999` | `stack_bowls` | [播放](hyvla/step_199999/stack_bowls.mp4) |

ACT 在 5 个本地 episode 中没有成功，因此没有成功视频。这里的 Demo 仅证明本地闭环
运行结果，不是主办方正式评测录像或正式成绩。文件来源、大小、时长与 SHA-256 见
[`manifest.csv`](manifest.csv) 和 [`SHA256SUMS`](SHA256SUMS)。
