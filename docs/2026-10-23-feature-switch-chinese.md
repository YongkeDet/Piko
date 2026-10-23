# X.26.11 管理功能开关汉化

更新前源码：`1223942160541711ac16bacca252a299f550958a`，Git 备份分支 `backup/before-X.26.11`。上游固定版本和 X.26.10 的四个源码覆盖补丁保留，新增 `source-patches/0005-feature-switch-chinese.patch`。

## 显示与数据

对当前提供的 X `12.35.0-prod.01`（versionCode `312350001`）基础 APK 做只读清点，按字节码中的功能仓库类型和七类 getter 的实际字符串参数，识别出 796 个字面量键。基础 APK SHA-256 为 `c6d61ece0141104fd09c7c345ad139a010061c94c2e052e8a3299c9814a06817`。该清单不宣称覆盖服务端将来下发的所有动态开关。

名称资源保存在 `localizations/values/newx/feature-switches.xml` 和现有中文 `strings.xml`。默认语言保留英文原键，简体中文显示键名释义。内部缩写和产品名称保留，例如 GSIG、CKEY、Grok；不把推测写成官方功能说明。历史开关标为“启用 Android 历史聚合页”，未宣称能开启视频观看历史。

列表显示中文名称及原始英文键名；编辑窗口同时显示两者。资源 ID 缓存不缓存译文，语言变化后仍按当前 Resources 取词。未知键或未知资源显示原始键名，不按词片段猜测，也不向实际 Store 注册额外开关。

搜索在 UI 层对原始键名和当前语言名称匹配，保持原有覆盖、新发现和排序逻辑。列表中的真/假、空列表、空字符串只改变显示；编辑器、保存、运行时解析、已有配置及 JSON 导入导出继续使用原始键和值。复用原有 SettingsUi 字体、列表、主题、高亮及编辑弹窗。

## 构建与验证

共 1316 条中文资源，包括 796 个名称及 4 条值显示文本。构建时合并全部默认语言 XML，严格验证中文名称集合、重复资源和格式占位符；构建信息新增每个默认语言资源文件的 SHA-256。

未修改 bytecode resolver 或功能开关拦截契约；未安装、启动或控制设备，实际界面行为待用户使用反馈。

### 构建和离线验证结果

- 功能提交 `6d005178d37ecf5b4e469e43b0b4a30b1bb4a3dc`；PR 预览构建提交 `4b36734b219e5213e05c620c4ff3d91c1b1d1e88`。
- [Actions 39966878001](https://github.com/YongkeDet/Piko/actions/runs/39966878001) 完成完整构建、1316 条资源及占位符检查、设置聚合、resolver lint、20 项分页及 2 项时间线测试。
- Actions 附件 `12508100091`，ZIP SHA-256 `92e65e269d970ba38c119dcb84eefd709515788fb1596a32c4b4f08a75eb32ba`；MPP SHA-256 `8aff5aaac028561d50fb88f14d56502ddbc89872b264aa87f81d796b509dbe81`。五个覆盖补丁和全部中英文资源哈希与当前源码一致。
- 使用该 MPP、同一源码的 `patch-twitter.sh`、`morphe-desktop-1.11.0-all.jar` 和原始基础 APK，在 `PATCHER_MAX_HEAP_MB=512` 下 **47/47 补丁通过**，退出 0 并签名保存 `.build/X2611-patched-512.apk`；SHA-256 `d87ab62762e41463e2cf0438821a38028159b3d4aaf645f8f35413a0e8b93339`。
- 直接解析最终 `resources.arsc`：796 个中文名称全部与源码相符，默认语言仍为完整原始键名，布尔值中文正确打包；核对 Store 与导入导出生产源码逐字节未变。
- 最终 DEX：中文标题、原始键名字幕、中文及原名搜索、编辑窗口双语副标题均可达；显示别名没有进入 Store 的保存或解析路径，原生七类 getter 仍调用原有 resolveBoolean/Int/Long/Float/Double/String/List。原有主页下载的 8 个原生控制器桥接、媒体 getter、入口和保护停止路径通过复核。

### 正式发布核验

PR #2 已合并为 `b414fb9e5034f9d96762ed9d65525cb27114faf1`，标签 `X.26.11` 指向同一提交。[正式 Actions 39967862821](https://github.com/YongkeDet/Piko/actions/runs/39967862821) 构建、发布和订阅更新成功。

[X.26.11 发布](https://github.com/YongkeDet/Piko/releases/tag/X.26.11) 的 MPP SHA-256：`9d43b0c74a875304ad5210034b1e95cb1fde83ff1002590de673e4d050682e30`。正式附件 `12508052409` 的 ZIP SHA-256：`d61d0e0cb7bbf4809d50f1414ac0fa16c65cbf3232ed14096eb3da8401dbc377`。正式 MPP 与已测试预览的 1090 个条目中，仅 `META-INF/MANIFEST.MF` 的 Timestamp 不同，其余代码、扩展 DEX、资源和清单字段完全相同。五个覆盖补丁及全部中英文资源的哈希已再次核对。

正式发布的 MPP、构建信息、SHA256SUMS、订阅文件四个资产摘要均与已下载的正式构建附件一致。[固定订阅](https://raw.githubusercontent.com/YongkeDet/Piko/main/patches-bundle.json) 已核验版本为 `X.26.11`，下载地址指向正式的 `X.26.11.mpp`。

X.26.10 发布 ID、资产 ID 和所有资产摘要保持原样；`backup/before-X.26.11` 分支保留更新前源码。此前版本和历史备份继续保留。
