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
- 完整构建与目标 APK 补丁应用验证将在开发分支运行，结果补充于此。没有控制用户设备；实机菜单、登录请求和文件写入仍需实际安装验证。
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
