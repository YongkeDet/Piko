# 用户主页批量下载

- 基线：YongkeDet/Piko `9beddd580ecf928e1b034c9132c1fa1f32eb712e`，固定上游 `11ea728b9e0a907b2162b79445368cbcef21e783`。
- 实际检查的 APK：`com.twitter.android`，`12.35.0-prod.01`，构建号 `312350001`；基础 APK SHA-256 `c6d61ece0141104fd09c7c345ad139a010061c94c2e052e8a3299c9814a06817`。
- 实现：新覆盖补丁 `0004-profile-media-download.patch`。保留 X.26.04 的三个既有覆盖补丁，只修改新功能涉及的扩展、下载入队结果、构建验证和资源。
- UI：在原生 ProfileMenuItem 列表转换为不可变列表之前添加菜单项；复用原生菜单布局和下载图标。底部选择与进度弹窗使用现有 BottomSheetView、ListItem、ButtonView 和 Theme。菜单点击采用弱引用身份匹配，不通过同名文案或相等性推断目标用户。
- 字节码依据：实际目标 APK 的 ProfileMenuItem(text=、ProfileUser(id=、Icon(drawableRes=、原生列表转换及 Function0 点击回调；原生 GraphQL composer 中 URL / variables / features 语义锚点。所有应用混淆类型、字段、构造器和方法都在补丁应用时解析，使用 morphe-bytecode 生成调用，不使用运行时反射或固定混淆类名。
- 网络：调用本 APK 的 UserProfileMediaTimelineQuery 生成类和原生 GraphQL composer 构建 URL、参数及功能标记，使用账号自带的 OkHttp 客户端和 OAuth 签名拦截器请求。新页重新签名，不保存令牌，不要求先进入媒体标签页。
- 分页：读取原生 media_timeline_v2 的 Timeline 指令；支持模块、底部游标、空中间页及 Bottom 终止指令。错误、权限变化、账号 ID 变化、重复游标和结构漂移停止任务并保留已完成的文件。账号 ID 来自客户端的原生账号拦截器，可兼容 OkHttp 克隆客户端；不读取或解析令牌。
- 媒体：只读取当前主页作者的帖子附件，排除引用帖子、头像和卡片。使用原图、最高码率 video/mp4，按媒体 ID 去重。文件名、重名策略、SAF 目录及按作者分文件夹通过现有 InlineDownloadButton 入队流程处理。
- 队列：保留自己的 DownloadHandle，最多四个未结束文件；取消仅影响本次任务的网络请求和文件。进度中的“已保存”来自传输终态，而非入队数量。关闭进度窗口继续下载，再从主页菜单打开。
- 本地验证：四个原生响应结构回归测试通过；505 条中英文资源及格式占位符检查通过；覆盖补丁可依次应用于固定上游源码；Python 语法检查通过。
- 完整构建、12.35 基础 APK 与完整 APKM 的补丁应用，以及最终 DEX 挂钩检查均已通过，产物和命令见文末。没有控制用户设备；实机菜单、登录请求和文件写入仍需实际安装验证。
- 发布：不创建 Release，不更新已发布的 X.26.04 或固定订阅；PR 构建仅生成 Actions 附件。

## 实际 APK 验证发现及修复

- 构建代码提交 `bcf6fc2f527b1e7b5fa1fe4085020b264cfe4062`，Actions 合并验证提交 `d27c23593cae9fdf8e322635fd7b598c55012be5`，上游源码不变。Morphe Desktop `1.11.0`，MPP SHA-256 `5bbc57c1828b4daa169653aa25341de124ef2047826159b30919d0f8bc18a3e2`。
- 完整 29 分包 APKM 在默认 512 MB 堆下合并资源时发生 `java.lang.OutOfMemoryError: Java heap space`，栈位于 `com.reandroid.arsc.pool.StringPool.merge` / `ApkBundle.mergeModules`；尚未执行任何补丁。这是工具合并阶段的内存限制，与新解析器或 linter 无关。
- 同一版本基础 APK 通过 `patch-twitter.sh E:/Artificial Intelligence/Piko/tmp_2b7ccc14/base.apk` 在默认 512 MB 下进入实际补丁阶段。失败补丁 `NewX: Download all profile media`，完整异常如下：

```text
app.morphe.patcher.patch.PatchException: Failed to match the fingerprint: app.morphe.patcher.Fingerprint@57b7d357
	at app.morphe.patcher.Fingerprint.patchException(Fingerprint.kt:664)
	at app.crimera.patches.utils.ScopedFingerprintMatchingKt.scopedMatchAll(ScopedFingerprintMatching.kt:178)
	at app.crimera.patches.newx.misc.profiledownload.ProfileMediaDownloadPatchKt.newXProfileMediaDownloadPatch$lambda$0$0(ProfileMediaDownloadPatch.kt:122)
	at app.morphe.patcher.patch.Patch.execute(Patch.kt:126)
	at app.morphe.patcher.patch.BytecodePatch.execute$morphe_patcher(Patch.kt:241)
	at app.morphe.patcher.Patcher$invoke$1.invokeSuspend$execute(Patcher.kt:96)
	at app.morphe.patcher.Patcher$invoke$1.invokeSuspend(Patcher.kt:120)
	at app.morphe.patcher.Patcher$invoke$1.invoke(Patcher.kt)
	at app.morphe.patcher.Patcher$invoke$1.invoke(Patcher.kt)
	at kotlinx.coroutines.flow.SafeFlow.collectSafely(Builders.kt:57)
	at kotlinx.coroutines.flow.AbstractFlow.collect(Flow.kt:226)
	at app.morphe.cli.command.PatchCommand$call$3$3$1.invokeSuspend(PatchCommand.kt:794)
	at kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:34)
	at kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:100)
	at kotlinx.coroutines.EventLoopImplBase.processNextEvent(EventLoop.common.kt:256)
	at kotlinx.coroutines.BlockingCoroutine.joinBlocking(Builders.kt:54)
	at kotlinx.coroutines.BuildersKt__BuildersKt.runBlockingImpl(Builders.kt:30)
	at kotlinx.coroutines.BuildersKt.runBlockingImpl(Unknown Source)
	at kotlinx.coroutines.BuildersKt__Builders_concurrentKt.runBlockingK(Builders.concurrent.kt:172)
	at kotlinx.coroutines.BuildersKt.runBlockingK(Unknown Source)
	at kotlinx.coroutines.BuildersKt__Builders_concurrentKt.runBlockingK$default(Builders.concurrent.kt:157)
	at kotlinx.coroutines.BuildersKt.runBlockingK$default(Unknown Source)
	at app.morphe.cli.command.PatchCommand.call$lambda$13$2(PatchCommand.kt:793)
	at app.morphe.cli.command.model.PatchingResultKt.addStepResult(PatchingResult.kt:29)
	at app.morphe.cli.command.PatchCommand.call(PatchCommand.kt:790)
	at app.morphe.cli.command.PatchCommand.call(PatchCommand.kt:55)
	at picocli.CommandLine.executeUserObject(CommandLine.java:2031)
	at picocli.CommandLine.access$1500(CommandLine.java:148)
	at picocli.CommandLine$RunLast.executeUserObjectOfLastSubcommandWithSameParent(CommandLine.java:2469)
	at picocli.CommandLine$RunLast.handle(CommandLine.java:2461)
	at picocli.CommandLine$RunLast.handle(CommandLine.java:2423)
	at picocli.CommandLine$AbstractParseResultHandler.execute(CommandLine.java:2277)
	at picocli.CommandLine$RunLast.execute(CommandLine.java:2425)
	at picocli.CommandLine.execute(CommandLine.java:2174)
	at app.morphe.MorpheLauncherKt.main(MorpheLauncher.kt:23)
 
严重:
```

- 定位：composer 指纹的 InstructionFilter 按顺序匹配 URL → variables → features，实际 12.35 的同一方法先加载 features 再加载 variables。原因属于解析器逻辑，不是 linter 或基数辅助函数。
- 修复：仅用端点字符串作候选索引，再通过 `isNativeProfileMediaComposer` 检查三个标签的集合、HTTP 返回类型和参数形状；字符串加载顺序不再作为契约。
- 回归：加入既有 `NewXResolverLinterTest`，覆盖两种标签顺序、缺少 features、错误返回类型，直接调用生产选择条件。

### 查询类与查询注册表重名

- 后续代码提交 `129ae3ef7afa812fa95ab475f695383c3e5e7f41`，构建验证提交 `1518e9e0b30b3f16baf6a9aa665de5fb8c6a6e95`；MPP SHA-256 `a9e8ab9dfc952bdfc1e6e3c05e552e32f95487f1cd3204963c5c21594b0dad24`。同一基础 APK、CLI、脚本和 512 MB 堆，异常如下：

```text
app.morphe.patcher.patch.PatchException: Expected exactly one profile download UserProfileMediaTimelineQuery class, found 2: [Lcom/x/android/p0;, Lcom/x/android/main/e11;]
	at app.crimera.patches.common.ResolverCardinalityKt.requireExactlyOne(ResolverCardinality.kt:15)
	at app.crimera.patches.common.ResolverCardinalityKt.requireExactlyOne$default(ResolverCardinality.kt:8)
	at app.crimera.patches.newx.misc.profiledownload.ProfileMediaDownloadPatchKt.markedClass(ProfileMediaDownloadPatch.kt:265)
	at app.crimera.patches.newx.misc.profiledownload.ProfileMediaDownloadPatchKt.newXProfileMediaDownloadPatch$lambda$0$0(ProfileMediaDownloadPatch.kt:124)
	at app.morphe.patcher.patch.Patch.execute(Patch.kt:126)
	at app.morphe.patcher.patch.BytecodePatch.execute$morphe_patcher(Patch.kt:241)
	at app.morphe.patcher.Patcher$invoke$1.invokeSuspend$execute(Patcher.kt:96)
	at app.morphe.patcher.Patcher$invoke$1.invokeSuspend(Patcher.kt:120)
	at app.morphe.patcher.Patcher$invoke$1.invoke(Patcher.kt)
	at app.morphe.patcher.Patcher$invoke$1.invoke(Patcher.kt)
	at kotlinx.coroutines.flow.SafeFlow.collectSafely(Builders.kt:57)
	at kotlinx.coroutines.flow.AbstractFlow.collect(Flow.kt:226)
	at app.morphe.cli.command.PatchCommand$call$3$3$1.invokeSuspend(PatchCommand.kt:794)
	at kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:34)
	at kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:100)
	at kotlinx.coroutines.EventLoopImplBase.processNextEvent(EventLoop.common.kt:256)
	at kotlinx.coroutines.BlockingCoroutine.joinBlocking(Builders.kt:54)
	at kotlinx.coroutines.BuildersKt__BuildersKt.runBlockingImpl(Builders.kt:30)
	at kotlinx.coroutines.BuildersKt.runBlockingImpl(Unknown Source)
	at kotlinx.coroutines.BuildersKt__Builders_concurrentKt.runBlockingK(Builders.concurrent.kt:172)
	at kotlinx.coroutines.BuildersKt.runBlockingK(Unknown Source)
	at kotlinx.coroutines.BuildersKt__Builders_concurrentKt.runBlockingK$default(Builders.concurrent.kt:157)
	at kotlinx.coroutines.BuildersKt.runBlockingK$default(Unknown Source)
	at app.morphe.cli.command.PatchCommand.call$lambda$13$2(PatchCommand.kt:793)
	at app.morphe.cli.command.model.PatchingResultKt.addStepResult(PatchingResult.kt:29)
	at app.morphe.cli.command.PatchCommand.call(PatchCommand.kt:790)
	at app.morphe.cli.command.PatchCommand.call(PatchCommand.kt:55)
	at picocli.CommandLine.executeUserObject(CommandLine.java:2031)
	at picocli.CommandLine.access$1500(CommandLine.java:148)
	at picocli.CommandLine$RunLast.executeUserObjectOfLastSubcommandWithSameParent(CommandLine.java:2469)
	at picocli.CommandLine$RunLast.handle(CommandLine.java:2461)
	at picocli.CommandLine$RunLast.handle(CommandLine.java:2423)
	at picocli.CommandLine$AbstractParseResultHandler.execute(CommandLine.java:2277)
	at picocli.CommandLine$RunLast.execute(CommandLine.java:2425)
	at picocli.CommandLine.execute(CommandLine.java:2174)
	at app.morphe.MorpheLauncherKt.main(MorpheLauncher.kt:23)
```

- 定位：操作名称同时存在于注册表 `Lcom/x/android/p0;` 和生成类 `Lcom/x/android/main/e11;`。基数校验正确拒绝歧义；问题属于解析器缺少查询契约筛选，不是 linter 或辅助函数故障。
- 修复：候选必须同时提供操作名方法、媒体查询文档和已验证的双 String 构造器，再要求恰好一项。没有写入上述混淆类名。
- 回归：既有 `NewXResolverLinterTest` 通过生产选择入口覆盖“注册表 + 正确查询”、仅注册表和多个生成查询。

- 后续完整字节码审计发现 OAuth 范围内另有一个保存 UserIdentifier 的拦截器。账号桥接进一步要求原生 `X-Twitter-Active-User` 请求头语义锚点；既有 fixture 集加入对应正反例。此项是在再次应用前发现的歧义，不属于实机失败。

### Apollo Query 标记接口

- 代码提交 `c319f80576651d9b4497c89c6e79e6831767c2ed`，验证构建提交 `487dea3a1b2251475b62606c54558f5eb3899661`，MPP SHA-256 `2fc517b1eff5ed73485dfff528c88be0481f13fff182ee33c62e8d2d772d9a7f`。同一基础 APK 和 512 MB 堆，异常如下：

```text
app.morphe.patcher.patch.PatchException: Native profile query is not an Apollo operation
	at app.crimera.patches.newx.misc.profiledownload.ProfileMediaDownloadPatchKt.newXProfileMediaDownloadPatch$lambda$0$0(ProfileMediaDownloadPatch.kt:135)
	at app.morphe.patcher.patch.Patch.execute(Patch.kt:126)
	at app.morphe.patcher.patch.BytecodePatch.execute$morphe_patcher(Patch.kt:241)
	at app.morphe.patcher.Patcher$invoke$1.invokeSuspend$execute(Patcher.kt:96)
	at app.morphe.patcher.Patcher$invoke$1.invokeSuspend(Patcher.kt:120)
	at app.morphe.patcher.Patcher$invoke$1.invoke(Patcher.kt)
	at app.morphe.patcher.Patcher$invoke$1.invoke(Patcher.kt)
	at kotlinx.coroutines.flow.SafeFlow.collectSafely(Builders.kt:57)
	at kotlinx.coroutines.flow.AbstractFlow.collect(Flow.kt:226)
	at app.morphe.cli.command.PatchCommand$call$3$3$1.invokeSuspend(PatchCommand.kt:794)
	at kotlin.coroutines.jvm.internal.BaseContinuationImpl.resumeWith(ContinuationImpl.kt:34)
	at kotlinx.coroutines.DispatchedTask.run(DispatchedTask.kt:100)
	at kotlinx.coroutines.EventLoopImplBase.processNextEvent(EventLoop.common.kt:256)
	at kotlinx.coroutines.BlockingCoroutine.joinBlocking(Builders.kt:54)
	at kotlinx.coroutines.BuildersKt__BuildersKt.runBlockingImpl(Builders.kt:30)
	at kotlinx.coroutines.BuildersKt.runBlockingImpl(Unknown Source)
	at kotlinx.coroutines.BuildersKt__Builders_concurrentKt.runBlockingK(Builders.concurrent.kt:172)
	at kotlinx.coroutines.BuildersKt.runBlockingK(Unknown Source)
	at kotlinx.coroutines.BuildersKt__Builders_concurrentKt.runBlockingK$default(Builders.concurrent.kt:157)
	at kotlinx.coroutines.BuildersKt.runBlockingK$default(Unknown Source)
	at app.morphe.cli.command.PatchCommand.call$lambda$13$2(PatchCommand.kt:793)
	at app.morphe.cli.command.model.PatchingResultKt.addStepResult(PatchingResult.kt:29)
	at app.morphe.cli.command.PatchCommand.call(PatchCommand.kt:790)
	at app.morphe.cli.command.PatchCommand.call(PatchCommand.kt:55)
	at picocli.CommandLine.executeUserObject(CommandLine.java:2031)
	at picocli.CommandLine.access$1500(CommandLine.java:148)
	at picocli.CommandLine$RunLast.executeUserObjectOfLastSubcommandWithSameParent(CommandLine.java:2469)
	at picocli.CommandLine$RunLast.handle(CommandLine.java:2461)
	at picocli.CommandLine$RunLast.handle(CommandLine.java:2423)
	at picocli.CommandLine$AbstractParseResultHandler.execute(CommandLine.java:2277)
	at picocli.CommandLine$RunLast.execute(CommandLine.java:2425)
	at picocli.CommandLine.execute(CommandLine.java:2174)
	at app.morphe.MorpheLauncherKt.main(MorpheLauncher.kt:23)
```

- 实际继承链为生成 Query → Query 标记接口 → Operation。共享库 0.8.0 的 `isAssignableTo` 检查直接接口和父类，没有遍历接口的父接口，所以直接传生成类产生了假阴性。
- 本补丁只适配已验证的 Apollo Query 标记契约：对生成类明确声明的标记接口调用现有共享辅助函数，再验证它可赋给原生请求的 Operation。没有复制通用层级遍历器，也没有修改共享库或影响旧的集合检查。
- 回归：既有原生查询 fixture 增加真实两级类型链、注册表和不兼容 Operation 控制例，通过生产入口 `supportsNativeProfileOperation` 验证。

### 目录授权静态审计

- 批量任务复用 `NewXDownloadFolders.isConfigured` 检查目标目录，同时接受持久授权 `PERSISTED` 和进程内有效授权 `LIVE`。此前只接受 `LIVE` 会误拒绝正常持久授权的目录；检查在本次 APK 验证前纠正，未发布。

## 最终验证

- 功能源码提交：`a1ab6d6721922cb9605f34a10ca384d5cdf472e0`；[Actions 39916942540](https://github.com/YongkeDet/Piko/actions/runs/39916942540) 成功，PR 合并验证提交 `d2009ad74cbe38ed399a292784461d05ea19e5f4`。
- 当前源码构建通过：两个时间线测试、四个原生媒体响应解析测试、505 条中文及格式占位符校验、Android lint、`:patches:build`（含设置聚合及解析器回归 fixture）、`:patches:lintNewxResolvers`。Gradle 结果 `BUILD SUCCESSFUL`。
- Actions 附件 `12485695796`，ZIP SHA-256 `c6881a07110a148724e0529a098e5fe08ba9ab4370db7d31c982b429896c4595`；MPP SHA-256 `03cf7bab32c0d8b06dbdd8e687f7bbcd6c61118dcd9dc00a86213af762c88355`。已核对附件、全部四个源码覆盖补丁、中文资源和 MPP 的构建信息哈希。
- 使用 Morphe Desktop `1.11.0`，只通过当前源码的 `patch-twitter.sh` 运行下列两项离线验证（`MORPHE_CLI_JAR` 指向相同的本地工具，`PIKO_PATCH_OUTPUT` 分别指定下表产物）；未传入 `--install`。

| 输入 | 堆与命令 | 结果与本地产物 |
| --- | --- | --- |
| `tmp_2b7ccc14/base.apk`，版本及哈希见文首 | `PATCHER_MAX_HEAP_MB=512 ./patch-twitter.sh 'E:/Artificial Intelligence/Piko/tmp_2b7ccc14/base.apk'` | 47 个补丁全部 Applied，包括 `NewX: Download all profile media`；编译、对齐、签名及 Saved to 成功。`.build/profile-patched-base-verified.apk`，SHA-256 `80ac801b584576903e6836479bcedb516f5a1217ffb84256cbe0986842e5dd56`。 |
| 原始 `com.twitter.android_12.35.0-prod.01-312350001_2arch_2dpi_24lang_86a8e9ed2169398a8bba24d64522cf43_apkmirror.com.apkm`，SHA-256 `16607ce5e435eccb23b8b8385cbd173e672ff06f533f159e7acf2412087d6f3b` | `PATCHER_MAX_HEAP_MB=4096 ./patch-twitter.sh 'E:/Artificial Intelligence/Piko/com.twitter.android_12.35.0-prod.01-312350001_2arch_2dpi_24lang_86a8e9ed2169398a8bba24d64522cf43_apkmirror.com.apkm'` | 分包合并、47 个补丁、编译、对齐、签名及 Saved to 全部成功。`.build/profile-patched-complete-verified.apk`（arm64-v8a），SHA-256 `551a4f3f6c457b10e4d1aa57eab002bee4d26ae23b9a300f937ce8c342b1aeef`。 |

- 两个最终 APK 的 DEX 均核对：菜单列表添加调用 1 处、原生点击拦截 2 处、composer 捕获 1 处、OkHttp 客户端捕获 1 处；5 个桥接方法在原抛错桩之前读取/调用已解析的原生字段及方法并返回。原有两条 `Function1.invoke` 菜单事件路径保留。另核对桥接的宽寄存器、invoke/result 配对及账号不匹配返回 null 的分支。
- 本地日志：`.build/profile-patch-base-verified.log`、`.build/profile-patch-complete-verified.log`。交付预览：`dist/profile-media-preview/Piko-profile-media-preview.mpp`，附原始 `build-info.json` 和 SHA256SUMS。
- 验证边界：未提供 12.34 原始 APK，未验证该版本的新功能；未安装、启动或控制设备。实际菜单布局、账号签名请求、SAF 写入、取消和长列表翻页仍需实机确认。已发布版本与订阅保持 X.26.04 原状。
