# Contributing / 贡献指南

Thanks for improving this Codex pet. We accept bug reports, documentation updates,
validator improvements, and complete sprite-row repairs.

感谢你改进这个 Codex 宠物。仓库接受缺陷报告、文档改进、验证器改进和完整动画行修复。

## Before opening a pull request / 提交 PR 前

1. Open an issue for visual or behavioral changes so the intended result is reviewable.
2. Create a focused branch from `main`.
3. Install the development environment with `python -m pip install -e ".[dev]"`.
4. Run `ruff check .`, `mypy src tests`, `pytest`, and `validate-codex-pet .`.
5. Update QA artifacts when `spritesheet.webp` changes.
6. Sign every commit with `git commit -s`.

1. 视觉或行为改动请先创建 Issue，明确可审阅的目标。
2. 从 `main` 创建范围清晰的分支。
3. 使用 `python -m pip install -e ".[dev]"` 安装开发环境。
4. 运行 `ruff check .`、`mypy src tests`、`pytest` 和 `validate-codex-pet .`。
5. 修改 `spritesheet.webp` 时同步更新 QA 产物。
6. 每个提交都使用 `git commit -s` 签署。

## Sprite changes / 精灵图改动

- Preserve the 1536 x 2288, 8 x 11, 192 x 208 Codex v2 contract.
- Repair a complete animation row; do not patch unrelated one-off cells together.
- Keep unused cells fully transparent and clear RGB under zero-alpha pixels.
- Include updated `contact-sheet.png`, `look-directions.png`, `validation.json`, and
  `direction-semantics.json` when relevant.
- Describe visual review evidence in the pull request. CI does not replace human review.

- 保持 1536 x 2288、8 x 11、192 x 208 的 Codex v2 契约。
- 修复完整动画行，不要拼接来源不同的零散单元格。
- 未使用单元格必须完全透明，零 Alpha 像素下的 RGB 必须清零。
- 相关改动需同步提交 `contact-sheet.png`、`look-directions.png`、`validation.json`
  和 `direction-semantics.json`。
- 在 PR 中说明视觉审阅证据；CI 不能替代人工视觉审阅。

## DCO and rights / DCO 与权利声明

The Developer Certificate of Origin sign-off certifies that you have the right to
submit your contribution under the repository's licensing terms. Add it with:

开发者原创声明签署表示你有权按照仓库许可条款提交贡献。使用以下命令添加：

```bash
git commit -s
```

By opening a pull request that includes artwork, you also confirm that you have the
right to contribute that material. The sign-off does not grant rights in Izumi Konata
or *Lucky Star*.

提交包含图像素材的 PR，即表示你确认自己有权贡献该素材。签署不授予泉此方或《幸运星》的相关权利。
