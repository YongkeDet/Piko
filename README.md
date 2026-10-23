# Piko 中文补丁

当前版本 **X.26.15**（基于上游 v3.61.0，支持 X 12.36.1-prod.01），共 1316 条中文界面文本。

本版完整纳入上游 v3.61.0 的 NewX 功能与修复，包括 Morphe Patcher 2.0、新版时间线恢复、设置入口、分隔线及回复排序适配，再叠加本仓库的下载增强和汉化。新版与旧版安装包的离线验证详见 [X.26.15 升级记录](docs/newx-resolver-linter/2026-10-23-x-12-36-1-upgrade.md)。

## 管理功能开关中文名称

在“Piko 设置 → 高级 → 功能开关 → 管理功能开关”中，为从当前 X 12.35 安装包识别出的 796 个开关提供中文名称。支持按中文名称或原始英文键名搜索，列表及编辑窗口保留原始键名，布尔值、空列表和空字符串增加中文显示。界面沿用 Piko 的字体、列表、搜索高亮和主题。

中文名称是对键名的释义；未收录的动态开关显示原名。不会向列表添加未发现的开关，也不会修改任何实际键名、保存值、导入导出格式或已有覆盖配置。原始字符串、列表项及数值保留原值。详见 [X.26.11 汉化记录](docs/2026-10-23-feature-switch-chinese.md)。

## 用户主页批量下载

打开用户主页的“媒体”，进入 Piko 图片画廊，点击“下载全部图片和视频”，选择全部媒体、仅图片或仅视频。入口和分类使用原有 ListItem、图标、字体、底部弹窗和主题配色，适配 X 的浅色、深色及 Dim 主题。开关位于“帖子操作与媒体 → 下载全部主页媒体”，默认开启；需要同时启用图片画廊、内嵌下载及相关依赖补丁。

通过 X 原生 Photos/Videos 控制器翻页，依次读取所选分类中当前账号可以访问的媒体。下载沿用目录、画质、文件名、重名策略和按作者分文件夹设置；画质为“每次询问”时批量任务使用最高可用画质。最多同时排队四个文件，显示保存、跳过、失败及不可用数量。下载期间保持当前主页及进度窗口打开，关闭进度窗口或取消会停止任务并保留已完成的文件。

原生分页结束后显示全部处理完成。连续三页没有新增媒体、重复页面、限流、读取错误或恢复次数达到上限时显示对应停止原因；保护停止不会提示全部完成。翻页进展在分类筛选及文件去重前判断，防止“仅图片”下载遇到视频页时提前停止。选择全部媒体时，图片阶段触发无新增保护后仍会处理视频阶段。

下载功能支持 X `12.35.0-prod.01` 和 `12.36.1-prod.01`。构建、离线应用补丁和实际使用的验证范围见 [整合记录](docs/newx-resolver-linter/2026-10-23-native-profile-integration.md)。此前 API 方案和分页问题记录保留在 Git 历史及 [实现记录](docs/newx-resolver-linter/2026-10-23-profile-media-download.md)、[分页修复记录](docs/newx-resolver-linter/2026-10-23-profile-pagination.md) 中。

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

固定来源地址不变，检查更新即可获取 X.26.15；已安装的 X 需要重新应用补丁后更新安装。也可在 [X.26.15 发布页](https://github.com/YongkeDet/Piko/releases/tag/X.26.15) 下载 `.mpp`。来源格式遵循 [Morphe 官方说明](https://github.com/MorpheApp/morphe-manager/blob/main/docs/patch-sources.md)。订阅仅在构建和发布成功后更新。

## 构建与回退

云端使用 `UPSTREAM.json` 固定的源码及构建脚本，并应用 `source-patches/`。工作流验证中文资源和占位符，运行分页与时间线测试、NewX resolver 检查和完整构建，生成补丁包、构建信息及 SHA-256 校验值。沿用上游兼容列表：X `12.34.0-prod.01`、`12.35.0-prod.01` 和 `12.36.1-prod.01`；主页批量下载支持后两者。补丁引擎升级为 Morphe Patcher 2.0，需要使用支持该引擎的 Morphe（离线验证使用官方 Morphe Desktop 1.19.0）。仓库不包含第三方 X 安装包。

- X.26.15 单独发布，更新前 main 保存在 `backup/before-X.26.15`（`f29c16237275e2a01debffd322ef0be5f442d2e1`），X.26.11 的标签与发布产物保留。
- X.26.11 单独发布，更新前的 main 保存在 `backup/before-X.26.11`（`1223942160541711ac16bacca252a299f550958a`）；X.26.10、X.26.04 及此前版本的标签和发布产物保留。
- 更新前已发布源码：`backup/before-X.26.10`（`9beddd580ecf928e1b034c9132c1fa1f32eb712e`）。
- 此前 API 下载预览：`backup/profile-api-preview-before-X.26.10`（`5708520271180cdc648d26e783544996ef43484d`）。
- 回退补丁时下载旧 Releases 中的 `.mpp`；查看旧源码时从对应标签或备份分支创建分支，保留现有历史。
- 后续发布修改 `RELEASE.json` 版本号后提交即可。每次发布的 `build-info.json` 记录源码、覆盖补丁及产物校验值。

## 来源与许可

构建脚本基于 [crimera/piko-newx](https://github.com/crimera/piko-newx)，补丁源码来自 [crimera/piko 的 x-lite 分支](https://github.com/crimera/piko/tree/x-lite)，由 Morphe 提供补丁工具。

X.26.10 的原生批量下载控制器、分页状态机、宿主关系解析和原始媒体快照机制改编自 [YongkeDet/piko-custom](https://github.com/YongkeDet/piko-custom/tree/006e9a547e7606935242f08f1b0c65702a2d0c3a) 的同名实现，再整合本仓库的无新增保护、下载选项及原有 Piko 界面。覆盖源码与原项目许可证声明保持一致，来源和修改范围详见整合记录。
