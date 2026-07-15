# Izumi Konata Codex Pet / 泉此方 Codex 宠物

[![CI](https://github.com/hacksynth/codex-pet-izumi-konata/actions/workflows/ci.yml/badge.svg)](https://github.com/hacksynth/codex-pet-izumi-konata/actions/workflows/ci.yml)
[![CodeQL](https://github.com/hacksynth/codex-pet-izumi-konata/actions/workflows/codeql.yml/badge.svg)](https://github.com/hacksynth/codex-pet-izumi-konata/actions/workflows/codeql.yml)

An animated Codex v2 pet based on Izumi Konata from *Lucky Star*.

基于《幸运星》泉此方制作的 Codex v2 动画宠物。

## Effect previews / 效果预览

The standard states use Codex's actual frame timing. Look directions sweep clockwise at
an even rate. All previews use a baked checkerboard so transparent edges remain visible
in both GitHub themes.

标准状态使用 Codex 实际帧时长，观察方向按顺时针匀速循环。所有预览均烘焙浅灰棋盘格，确保透明
边缘在 GitHub 深色与浅色主题中都可见。

<table>
  <tr>
    <th>Idle / 待机</th>
    <th>Running right / 向右移动</th>
    <th>Running left / 向左移动</th>
  </tr>
  <tr>
    <td><img src="previews/idle.gif" width="192" alt="Izumi Konata idle animation"></td>
    <td><img src="previews/running-right.gif" width="192" alt="Izumi Konata moving right"></td>
    <td><img src="previews/running-left.gif" width="192" alt="Izumi Konata moving left"></td>
  </tr>
  <tr>
    <th>Waving / 挥手</th>
    <th>Jumping / 跳跃</th>
    <th>Failed / 失败</th>
  </tr>
  <tr>
    <td><img src="previews/waving.gif" width="192" alt="Izumi Konata waving"></td>
    <td><img src="previews/jumping.gif" width="192" alt="Izumi Konata jumping"></td>
    <td><img src="previews/failed.gif" width="192" alt="Izumi Konata failure reaction"></td>
  </tr>
  <tr>
    <th>Waiting / 等待输入</th>
    <th>Running task / 任务处理中</th>
    <th>Review / 审阅结果</th>
  </tr>
  <tr>
    <td><img src="previews/waiting.gif" width="192" alt="Izumi Konata waiting for input"></td>
    <td><img src="previews/running.gif" width="192" alt="Izumi Konata processing a task"></td>
    <td><img src="previews/review.gif" width="192" alt="Izumi Konata reviewing output"></td>
  </tr>
  <tr>
    <th>Look directions / 观察方向</th>
    <th>Direction QA / 方向 QA</th>
    <th></th>
  </tr>
  <tr>
    <td><img src="previews/look-directions.gif" width="192" alt="Izumi Konata clockwise look directions"></td>
    <td><img src="previews/look-directions-labeled.gif" width="192" alt="Labeled Izumi Konata look direction QA"></td>
    <td></td>
  </tr>
</table>

## Install / 安装

Download the latest release and copy `pet.json` and `spritesheet.webp` into:

下载最新 Release，将 `pet.json` 与 `spritesheet.webp` 复制到：

```text
~/.codex/pets/izumi-konata/
```

The package uses an 8 x 11 atlas with 192 x 208 pixel cells, 9 standard animation
states, 16 clockwise look directions, and `spriteVersionNumber: 2`.

该宠物使用 8 x 11 图集、192 x 208 像素单元格、9 种标准动画状态和 16 个顺时针观察方向。

## Validate / 校验

```bash
python -m pip install -e ".[dev]"
validate-codex-pet .
generate-codex-previews . --check
pytest
```

CI also runs Ruff and mypy. Visual semantics remain a human review gate; deterministic
checks cannot prove that a character is looking in the intended direction.

CI 还会运行 Ruff 与 mypy。视觉语义仍需人工审阅，确定性脚本无法证明角色确实看向目标方向。

## Repository files / 仓库文件

- `pet.json`, `spritesheet.webp`: installable pet package / 可安装宠物包
- `contact-sheet.png`, `look-directions.png`: visual review evidence / 视觉审阅证据
- `validation.json`, `direction-semantics.json`: QA records / QA 记录
- `previews/`: deterministic animated effect previews / 确定性动画效果预览
- `src/`, `tests/`: deterministic validator and tests / 确定性验证器与测试

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Use GitHub
Discussions for installation help and showcases.

提交 PR 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。安装答疑与展示请使用 GitHub Discussions。

## Licensing / 许可

Validator code, workflows, and documentation are available under the MIT License.
Character artwork and derived sprite assets are excluded; see [ASSET-NOTICE.md](ASSET-NOTICE.md).

验证代码、工作流和文档采用 MIT 许可证。角色图像与衍生精灵素材不在 MIT 授权范围内，详见
[ASSET-NOTICE.md](ASSET-NOTICE.md)。

This is an unofficial fan-made project. Izumi Konata and *Lucky Star* belong to their
respective rights holders. No affiliation or endorsement is implied.

本项目为非官方同人作品，与相关权利方不存在隶属或背书关系。
