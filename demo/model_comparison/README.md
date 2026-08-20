# 模型对比成功 Demo

本目录只收录成功任务的头部主视角视频。左右腕部相机、失败视频和同一模型同一任务的重复运行未纳入。

| 模型 | Checkpoint | 任务 | 主视角视频 |
|---|---|---|---|
| StarVLA PI-v3 | `steps_100000` | `fold_clothes` | [播放](starvla_step100000_fold_clothes_cam_head_success.mp4) |
| StarVLA PI-v3 | `steps_100000` | `stack_bowls` | [播放](starvla_step100000_stack_bowls_cam_head_success.mp4) |
| HyVLA-70k | `step-69999` | `stack_bowls` | [播放](hyvla_step69999_stack_bowls_cam_head_success.mp4) |
| HyVLA-200k | `step-199999` | `fold_clothes` | [播放](hyvla_step199999_fold_clothes_cam_head_success.mp4) |
| HyVLA-200k | `step-199999` | `pour_liquid_into_cup` | [播放](hyvla_step199999_pour_liquid_into_cup_cam_head_success.mp4) |
| HyVLA-200k | `step-199999` | `stack_bowls` | [播放](hyvla_step199999_stack_bowls_cam_head_success.mp4) |

ACT 在 5 个本地 episode 中没有成功，因此没有 ACT 成功视频。

视频大小、时长、来源和 SHA-256 见 `manifest.csv` 与 `SHA256SUMS`。
