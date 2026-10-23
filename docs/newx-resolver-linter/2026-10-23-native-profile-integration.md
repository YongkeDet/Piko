# X.26.10 原生主页媒体下载整合

## 来源与回退点

- 已发布基线：`9beddd580ecf928e1b034c9132c1fa1f32eb712e`，远程备份 `backup/before-X.26.10`。
- API 预览：`5708520271180cdc648d26e783544996ef43484d`，远程备份 `backup/profile-api-preview-before-X.26.10`。
- 固定上游 `crimera/piko`：`11ea728b9e0a907b2162b79445368cbcef21e783`。
- 参考及改编源码 `YongkeDet/piko-custom`：`006e9a547e7606935242f08f1b0c65702a2d0c3a`。改编 `ProfileBulkDownload`、`ProfileBulkPager`、原生 typed 桥接、宿主解析及其两个回归测试，以及画廊媒体导出、过滤前快照传递和媒体模块展平逻辑。保留来源及原项目许可；未搬入其其他补丁或设置分类。

## 选择与修改

采用 piko-custom 原生 Photos/Videos 控制器及状态机，避免自行组合网络查询、登录凭据和分页响应。使用当前控制器的可用标签、Success/Empty/Failure 状态、加载标记、原生加载更多与刷新操作。解析原生宿主和请求时要求语义契约唯一匹配，失败即停止补丁；使用 morphe-bytecode typed emitters，不引入反射或硬编码混淆类。

入口使用现有图片画廊中的 Piko ListItem，分类选择与进度使用 BottomSheetView、Theme 和原有字体/图标。下载复用已有引擎、目录权限、重名策略、文件名、作者目录与画质设置，单任务最多四个排队/运行文件。窗口关闭会取消，不再声称后台继续。批量任务聚合完成提示，正常单文件提示不受影响。

全局文件去重与每阶段翻页进展分开：原始媒体候选在类型筛选、文件存在和下载失败之前计入进展；过滤前原生 Success 身份及 copy lineage 保留，已隐藏的媒体仍可读取。连续三个成功且游标不同的页面没有新候选时单独返回 STOPPED；原生终止 DONE 优先。All 模式的图片保护停止后继续视频阶段，最终显示部分结果提示。刷新会清空阶段进展集合，保留文件去重，并限制每阶段最多三次刷新，防止恢复重置预算导致无限运行。

## 已复现问题与回归

用户报告“页数增加，媒体数不变”。对参考状态机的原始 15 个测试与实际类构造模拟运行：空媒体、Success、canPage=true、持续变化游标连续 100 页仍请求 NEXT。这是缺少新增媒体边界保护的确定性模拟，不等同于真实服务器或设备重现。

整合后的 `ProfileBulkPagerTest` 共 20 项测试，通过真实生产状态机覆盖原生加载/Empty/Failure/等待/重试、无新增三页保护、分类前候选进展、同页复制不消耗预算、原生结束优先及成功刷新不能无限重置恢复次数。`ProfileBulkHostResolverTest` 保留参考实现的两项实际故障回归：避免把协程捕获对象误识别为原生标签宿主，以及解析 Empty/Refresh 单例。

旧 API 预览的两个文档是历史证据，其构建与哈希不用于本次原生整合验证。

## 验证范围

新增补丁的集中兼容元数据只声明 X `12.35.0-prod.01`；原有补丁的 12.34/12.35 元数据保持原样。当前提供的确切离线输入：

- package `com.twitter.android`，版本 `12.35.0-prod.01`，versionCode `312350001`，production。
- 基础 APK SHA-256：`c6d61ece0141104fd09c7c345ad139a010061c94c2e052e8a3299c9814a06817`。
- 完整 APKM SHA-256：`16607ce5e435eccb23b8b8385cbd173e672ff06f533f159e7acf2412087d6f3b`。
- 使用当前提交云端构建 MPP，再通过同一源码的 `patch-twitter.sh` 显式指定输入；不混用旧 MPP。

本地 ECJ/Java 17 编译生产 Pager 与测试，JUnit **20/20 通过**。设备行为尚未验证，未安装、启动或控制设备。

### 首轮构建依赖修复

提交 `0f298ea854edfbd0da7f43e970cd6cbf1b9501ac` 的 [Actions 39926398213](https://github.com/YongkeDet/Piko/actions/runs/39926398213) 在 `:patches:compileKotlin` 失败：`ProfileBulkDownloadPatch.kt:12:40 Unresolved reference 'modelFieldsByAppendOrder'`，后续类型推断错误由此派生；Android 扩展 Java 编译、516 条资源、2 项时间线和 20 项分页测试均已通过，未产出 MPP 或执行 APK 补丁。

原因是参考项目额外提供了 `models/BooleanModelLabels.kt`，固定上游中没有该文件。同步改编此辅助函数：按 StringBuilder 追加顺序追踪字段和 R8 静态 helper，拒绝条件控制流、过深嵌套及歧义标签。属于源码依赖遗漏，不是 resolver linter、cardinality helper 或 APK 合同失败。

### 整合验证通过

- 功能及依赖修复提交：`c1e927ccee82109bae692b9a1644f6cf61375080`；PR 合并预览构建提交：`f48ec475daa7ecf19708f145ec0af78724e1055c`。
- [Actions 39927078181](https://github.com/YongkeDet/Piko/actions/runs/39927078181) 成功完成 `clean buildAndroid :patches:build :patches:lintNewxResolvers --no-daemon`，包含设置聚合测试、两项宿主解析回归；独立 2 项时间线和 20 项生产分页测试通过。Resolver lint passed。
- Actions 附件 `12489592559` 的 ZIP SHA-256：`3a3ff1dc99d472849c6e833c60d3a774b7d77a3a0d90a9805b9fc8f157847a50`。
- MPP SHA-256：`bed81d9f3fd6a836fed3ca13e0c3255dd4181040a3720dcf85a33b13a8d2a011`。构建信息中的源码覆盖补丁和翻译哈希均与本次源码相符。
- 原始完整 APKM，堆 `4096 MB`：通过同一源码的 `patch-twitter.sh` 成功应用 **47/47** 补丁，包含 `NewX: Download all profile media`，签名保存 `.build/native-X.26.10-full.apk`；SHA-256 `28b9d30e4dacfc29b4927adf297249476fa9cd22c8b417a03304510e580c8114`。
- 原始基础 APK，堆 `512 MB`：同一脚本和 MPP 成功应用 **47/47** 补丁，签名保存 `.build/native-X.26.10-base-512.apk`；SHA-256 `f7139f1d20c03a259d9c429c90506d1c84c7400d6c2da9d2824a167d8b7a56cf`。
- 最终 DEX：8 个控制器桥接及画廊媒体 getter 全部替换为已解析的原生成员访问，无残留 throw stub；两个原生 child 返回路径绑定宿主；Success 构造器接入过滤前快照和 autoplay gate，copy 接入快照继承；Piko 画廊入口可达。旧 API Session/Downloader 类不存在。
- 直接检查生产控制流：成功原生结束先返回 DONE；无新增计数达到 3 才返回 STOPPED；Session 设置 `protectedStop` 后推进分类，最终提示 `pagination_stopped`，正常结束提示 `completed`；每阶段刷新次数上限为 3。

离线命令使用当前构建的 `patches/build/libs/patches-X.26.10.mpp`，环境设置 `MORPHE_CLI_JAR` 指向 `morphe-desktop-1.11.0-all.jar`、`PIKO_PATCH_OUTPUT` 指向上述测试文件，分别执行 `PATCHER_MAX_HEAP_MB=4096 ./patch-twitter.sh <原始完整APKM>` 与 `PATCHER_MAX_HEAP_MB=512 ./patch-twitter.sh <原始基础APK>`。两个命令均退出 0；没有使用安装参数。
