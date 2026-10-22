# Piko 中文补丁

当前版本 `X.26.03`：开启“时间线 → 禁用时间线自动刷新”后，已有列表仅允许手动下拉刷新；首次进入时加载内容，以及向下浏览时加载更多照常。适用于“为你推荐”“正在关注”等该开关原本覆盖的时间线。

保留前版的 487 条中文设置和下载窗口文案。此开关关闭时使用原有刷新行为；打开帖子详情不在主页时间线刷新限制范围内。

## 订阅补丁

在 Android 设备上打开 [一键添加到 Morphe](https://morphe.software/add-source?github=YongkeDet/Piko)。

或在 Morphe 的“来源 → 添加 → 远程”中输入：

```text
https://github.com/YongkeDet/Piko
```

固定 JSON 订阅地址：

```text
https://raw.githubusercontent.com/YongkeDet/Piko/main/patches-bundle.json
```

以后在同一来源中检查更新，无需重复导入本地 `.mpp`。订阅更新的是补丁包；已安装的 X 仍需重新应用补丁后更新安装。

来源格式遵循 [Morphe 官方说明](https://github.com/MorpheApp/morphe-manager/blob/main/docs/patch-sources.md)。发布流程只在新版本构建和上传成功后更新订阅，不覆盖历史版本的文件或标签。

## 下载与构建

订阅后选择对应的原始 X 安装包应用补丁。也可以前往 [Releases](https://github.com/YongkeDet/Piko/releases) 下载指定版本的 `.mpp` 文件，用于手动安装或回退。

云端工作流会编译固定版本的源码，检查资源名称和格式占位符，生成补丁包、构建信息和 SHA-256 校验值。当前适用 X `12.34.0-prod.01` 和 `12.35.0-prod.01`。此仓库不包含第三方 X 安装包。

在 [Actions](https://github.com/YongkeDet/Piko/actions/workflows/build.yml) 中可以手动重新构建。更新构建配置或翻译也会触发构建。已发布版本的标签和文件不会被覆盖。

## 版本与回退

- 第一版标签和发布名称：`X.26.01`；本次行为调整为 `X.26.03`，此前版本的标签和产物全部保留。版本信息保存在 `RELEASE.json`。
- 汉化前基线：`upstream-baseline` 分支；最初的仓库提交也保留在 Git 历史中。
- 查看第一版：`git switch --detach X.26.01`。
- 查看汉化前版本：`git switch upstream-baseline`。
- 恢复此前已发布版本时，下载对应 Releases 产物，或从其标签创建修复分支；不要覆盖旧标签。
- 后续发布先修改 `RELEASE.json` 中的版本号，例如 `X.26.04`，再提交修改。

`UPSTREAM.json` 固定上游源码和构建脚本的提交；每次发布的 `build-info.json` 记录实际构建提交和文件校验值。

## 上游

构建脚本基于 [crimera/piko-newx](https://github.com/crimera/piko-newx)；补丁源码来自 [crimera/piko 的 x-lite 分支](https://github.com/crimera/piko/tree/x-lite)，由 Morphe 提供补丁工具。上游源码的许可证和声明保留在其原仓库。本仓库仅维护中文资源和相关构建配置。
