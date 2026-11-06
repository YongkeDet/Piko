# Piko 中文补丁

当前版本 **X3.74.0**，基于上游 v3.74.0，目标为 **X 12.40.1-prod.01**。本版含 560 条本地化资源。

版本名与上游保持一致并加 `X` 前缀，例如上游 `v3.74.0` 对应 `X3.74.0`。

本版纳入 12.40.1 的时间线刷新和媒体回复栏适配、年龄限制内容显示修复，以及内嵌下载渲染优化。保留批量下载、分页保护、手动刷新、作者子目录和翻译界面汉化。

使用原始 X **12.40.1-prod.01** 或 **12.39.0-prod.01** 完整 APKM 重新应用补丁。自定义主页下载支持这两个正式版。上游还声明 12.38.1 正式版支持，X 12.37.2 及更早版本使用 X.26.17。

验证与回退见 [X3.74.0 升级记录](docs/newx-resolver-linter/2026-11-06-x3-74-0-upgrade.md)。

## 管理功能开关

“Piko 设置 → 高级 → 功能开关 → 管理功能开关”显示原始键名和值，搜索使用原始键名。菜单、按钮和操作提示提供中文。

## 用户主页批量下载

打开用户主页的“媒体”，进入 Piko 图片画廊，点击“下载全部图片和视频”，选择全部媒体、仅图片或仅视频。入口和分类使用原有 ListItem、图标、字体、底部弹窗和主题配色，适配 X 的浅色、深色及 Dim 主题。开关位于“帖子操作与媒体 → 下载全部主页媒体”，默认开启；需要同时启用图片画廊、内嵌下载及相关依赖补丁。

通过 X 原生 Photos/Videos 控制器翻页，依次读取所选分类中当前账号可以访问的媒体。下载沿用目录、画质、文件名、重名策略和按作者分文件夹设置；画质为“每次询问”时批量任务使用最高可用画质。最多同时排队四个文件，显示保存、跳过、失败及不可用数量。下载期间保持当前主页及进度窗口打开，关闭进度窗口或取消会停止任务并保留已完成的文件。

原生分页结束后显示全部处理完成。连续三页没有新增媒体、重复页面、限流、读取错误或恢复次数达到上限时显示对应停止原因；保护停止不会提示全部完成。翻页进展在分类筛选及文件去重前判断，防止“仅图片”下载遇到视频页时提前停止。选择全部媒体时，图片阶段触发无新增保护后仍会处理视频阶段。

本版主页批量下载支持 X `12.39.0-prod.01` 和 `12.40.1-prod.01`。此前 API 方案和分页问题见 [实现记录](docs/newx-resolver-linter/2026-10-23-profile-media-download.md)及[分页修复记录](docs/newx-resolver-linter/2026-10-23-profile-pagination.md)。

## 保留功能

开启“时间线 → 禁用时间线自动刷新”后，已有列表仅允许手动下拉刷新；首次进入加载及向下浏览时加载更多照常。

“帖子操作与媒体 → 内嵌下载 → 按作者分文件夹保存”默认关闭。开启后，图片、视频、GIF 和拼接图片保存到对应目录下的 `@作者账号` 子文件夹，接管原生下载时也生效。无法识别作者时使用 `unknown_user`。关闭后直接保存到已选目录，已有文件不会搬移。

## 订阅与下载

在 Android 设备上打开 [一键添加到 Morphe](https://morphe.software/add-source?github=YongkeDet/Piko)，或在 Morphe 的“来源 → 添加 → 远程”中输入：

```text
https://github.com/YongkeDet/Piko
```

固定 JSON 订阅地址：

```text
https://raw.githubusercontent.com/YongkeDet/Piko/main/patches-bundle.json
```

在 Morphe 中刷新固定来源即可获取 X3.74.0，也可下载 `.mpp`。已安装的 X 需要重新应用补丁后更新安装。[X3.74.0 发布页](https://github.com/YongkeDet/Piko/releases/tag/X3.74.0)

## 构建与回退

云端使用 `UPSTREAM.json` 固定的源码并应用 `source-patches/`。工作流验证中文资源和占位符，运行分页与时间线测试、NewX resolver 检查和完整构建，生成补丁包、构建信息及 SHA-256 校验值。补丁需要支持 Morphe Patcher 2.0 的 Morphe，离线验证使用 Morphe Desktop 1.19.0。

- X3.74.0 可回退到 X3.73.0 的标签与发布资产，发布前 main 为 `d0bed0dd3874dd0012a6018922e87cd88a3db5c0`。
- X3.73.0 按上游版本重新命名并构建，规则及验证见 [版本命名记录](docs/2026-11-02-upstream-version-naming.md)。
- X.26.18 单独发布，升级前 main 为 `backup/before-X.26.18`（`89cf1f94d25c6a8e63373ca36f31d9b0fad44a72`），旧版与全部资产保留。
- X.26.17 单独发布，更新前 main 为 `backup/before-X.26.17`（`d641fe306947fe942d0b6a6776a340ca5ea5f991`）；X.26.16 及此前标签和发布产物保留。
- X.26.16 单独发布，回退基线为 `backup/before-X.26.16`（`aa58d7d4b946a3a1010e8fc72a1cd55e877d5c88`）；X.26.15 及此前资产保留。
- X.26.15 单独发布，更新前 main 保存在 `backup/before-X.26.15`（`f29c16237275e2a01debffd322ef0be5f442d2e1`），X.26.11 的标签与发布产物保留。
- X.26.11 单独发布，更新前的 main 保存在 `backup/before-X.26.11`（`1223942160541711ac16bacca252a299f550958a`）；X.26.10、X.26.04 及此前版本的标签和发布产物保留。
- 更新前已发布源码：`backup/before-X.26.10`（`9beddd580ecf928e1b034c9132c1fa1f32eb712e`）。
- 此前 API 下载预览：`backup/profile-api-preview-before-X.26.10`（`5708520271180cdc648d26e783544996ef43484d`）。
- 回退补丁时下载旧 Releases 中的 `.mpp`；查看旧源码时从对应标签或备份分支创建分支，保留现有历史。
- 后续升级同步更新 `UPSTREAM.json` 和 `RELEASE.json`，版本名必须为 `X` 加上游版本号（去掉上游的 `v` 前缀）。构建入口与工作流共同校验，避免发布不同版本号。每次发布的 `build-info.json` 记录源码、覆盖补丁及产物校验值。

## 来源与许可

构建脚本基于 [crimera/piko-newx](https://github.com/crimera/piko-newx)，补丁源码来自 [crimera/piko 的 x-lite 分支](https://github.com/crimera/piko/tree/x-lite)，由 Morphe 提供补丁工具。

X.26.10 的原生批量下载控制器、分页状态机、宿主关系解析和原始媒体快照机制改编自 [YongkeDet/piko-custom](https://github.com/YongkeDet/piko-custom/tree/006e9a547e7606935242f08f1b0c65702a2d0c3a) 的同名实现，再整合本仓库的无新增保护、下载选项及原有 Piko 界面。覆盖源码与原项目许可证声明保持一致，来源和修改范围详见整合记录。
