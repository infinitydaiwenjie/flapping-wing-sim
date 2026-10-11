# 扑翼飞行器机械仿真

[English](README.md)

本仓库提供 X 翼扑翼飞行器的 MuJoCo 机械模型与 Python 接口，
包含 CAD 几何、关节与连杆机构、基础仿真工具，以及 DA-PPO 学习框架概述。

控制先验初始化与漂移感知学习的流程见[方法概述](docs/method_outline_zh.md)。

## 功能

- 机械网格、关节层级和闭链连接关系。
- 模型复位、仿真步进、关节状态读取接口。
- 可选交互窗口的开环机构演示。
- 需要使用者自行提供参数的通用电机与翼素力计算工具。
- 不可执行的算法概念流程。

## 快速开始

使用 Python 3.10–3.12，在仓库根目录执行：

```bash
python -m pip install -r requirements.txt
python -B -m flapping_sim.demo
python -B -m flapping_sim.demo --viewer --steps 8000
```

macOS 的交互窗口使用 `mjpython` 替代 `python`。无窗口模式无需图形界面。
演示运行开环机械机构，可设置驱动转速与运行时长。

## Python 接口

```python
from flapping_sim import MechanismEnv

env = MechanismEnv()
state = env.reset()
state = env.step([2.0, 2.0], substeps=10)
```

输入为左右两侧的驱动转速，单位为执行器坐标下的弧度每秒。
返回状态包含时间、关节位置和关节速度。详见[接口文档](docs/environment.md)。

## 模型与方法范围

所附模型使用示例动力学参数，演示固定机身条件下的机械机构运动。
电机与翼素工具是独立的扩展辅助函数。DA-PPO 以概念伪代码说明；
仓库不包含训练实现、训练好的策略及论文实验使用的标定飞行配置。
各模块范围见 [release_scope.md](docs/release_scope.md)。

## 检查

```bash
python -B tools/check_release.py
python -B -m unittest discover -s tests
```

软件检查覆盖接口与通用物理工具；文件清单校验检查文件内容，并识别新增或修改的文件。

## 许可证

当前尚未指定发布许可证。MuJoCo 和 NumPy 单独安装，遵循各自的许可证。
