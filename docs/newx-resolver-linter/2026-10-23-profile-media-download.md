# 用户主页批量下载

- 基线：YongkeDet/Piko `9beddd580ecf928e1b034c9132c1fa1f32eb712e`，固定上游 `11ea728b9e0a907b2162b79445368cbcef21e783`。
- 实现：新覆盖补丁 `0004-profile-media-download.patch`。保留 X.26.04 的三个既有覆盖补丁，只修改新功能涉及的扩展、下载入队结果、构建验证和资源。
- UI：在原生 ProfileMenuItem 列表转换为不可变列表之前添加菜单项；复用原生菜单布局和下载图标。底部选择与进度弹窗使用现有 BottomSheetView、ListItem、ButtonView 和 Theme。菜单点击采用弱引用身份匹配，不通过同名文案或相等性推断目标用户。
- 字节码依据：实际目标 APK 的 ProfileMenuItem(text=、ProfileUser(id=、Icon(drawableRes=、原生列表转换及 Function0 点击回调；原生 GraphQL composer 中 URL / variables / features 语义锚点。所有应用混淆类型、字段、构造器和方法都在补丁应用时解析，使用 morphe-bytecode 生成调用，不使用运行时反射或固定混淆类名。
- 网络：调用本 APK 的 UserProfileMediaTimelineQuery 生成类和原生 GraphQL composer 构建 URL、参数及功能标记，使用账号自带的 OkHttp 客户端和 OAuth 签名拦截器请求。新页重新签名，不保存令牌，不要求先进入媒体标签页。
- 分页：读取原生 media_timeline_v2 的 Timeline 指令；支持模块、底部游标、空中间页及 Bottom 终止指令。错误、权限变化、账号客户端变化、重复游标和结构漂移停止任务并保留已完成的文件。
- 媒体：只读取当前主页作者的帖子附件，排除引用帖子、头像和卡片。使用原图、最高码率 video/mp4，按媒体 ID 去重。文件名、重名策略、SAF 目录及按作者分文件夹通过现有 InlineDownloadButton 入队流程处理。
- 队列：保留自己的 DownloadHandle，最多四个未结束文件；取消仅影响本次任务的网络请求和文件。进度中的“已保存”来自传输终态，而非入队数量。关闭进度窗口继续下载，再从主页菜单打开。
- 本地验证：四个原生响应结构回归测试通过；505 条中英文资源及格式占位符检查通过；覆盖补丁可依次应用于固定上游源码；Python 语法检查通过。
- 完整构建与目标 APK 补丁应用验证将在开发分支运行，结果补充于此。没有控制用户设备；实机菜单、登录请求和文件写入仍需实际安装验证。
- 发布：不创建 Release，不更新已发布的 X.26.04 或固定订阅；PR 构建仅生成 Actions 附件。
