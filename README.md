# Piko — X.26.01

Piko NewX 设置简体中文第一版，覆盖 473 条标题、说明、选项、弹窗和提示。翻译随应用语言切换，不更改补丁的业务逻辑。

## 下载与构建

前往 [Releases](https://github.com/YongkeDet/Piko/releases) 下载 `X.26.01.mpp`。在 Morphe 中导入此本地补丁包，再选择对应的原始 X 安装包应用补丁。

云端工作流会编译固定版本的源码，检查资源名称和格式占位符，生成补丁包、构建信息和 SHA-256 校验值。当前适用 X `12.34.0-prod.01` 和 `12.35.0-prod.01`。此仓库不包含第三方 X 安装包。

在 [Actions](https://github.com/YongkeDet/Piko/actions/workflows/build.yml) 中可以手动重新构建。更新构建配置或翻译也会触发构建。已发布版本的标签和文件不会被覆盖。

## 版本与回退

- 第一版标签和发布名称：`X.26.01`；翻译版本信息保存在 `RELEASE.json`。
- 汉化前基线：`upstream-baseline` 分支；最初的仓库提交也保留在 Git 历史中。
- 查看第一版：`git switch --detach X.26.01`。
- 查看汉化前版本：`git switch upstream-baseline`。
- 恢复此前已发布版本时，下载对应 Releases 产物，或从其标签创建修复分支；不要覆盖旧标签。
- 后续发布先修改 `RELEASE.json` 中的版本号，例如 `X.26.02`，再提交修改。

`UPSTREAM.json` 固定上游源码和构建脚本的提交；每次发布的 `build-info.json` 记录实际构建提交和文件校验值。

## 上游

构建脚本基于 [crimera/piko-newx](https://github.com/crimera/piko-newx)；补丁源码来自 [crimera/piko 的 x-lite 分支](https://github.com/crimera/piko/tree/x-lite)，由 Morphe 提供补丁工具。上游源码的许可证和声明保留在其原仓库。本仓库仅维护中文资源和相关构建配置。
