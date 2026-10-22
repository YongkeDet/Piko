# 按作者创建下载子目录

- 目标：固定上游 x-lite 提交 `11ea728b9e0a907b2162b79445368cbcef21e783`；适用 X 12.34.0-prod.01 / 12.35.0-prod.01。
- 范围：新增默认关闭的 `newx.content.inline_download.author_subfolders` 设置；补丁文件 `0003-author-download-subfolders.patch` 仅修改下载扩展及该补丁的设置声明，不调整指纹或应用字节码匹配。
- 路径：普通/批量/质量选择下载 → InlineDownloadButton；拼图 → MediaMerger；接管原生下载 → NativeDownloadRouter。三者均把同一 PostContext 解析出的原作者账号传为 DownloadRequest.subpath，在已选的图片或视频目录下创建或复用 `@账号` 文件夹。
- 复用 piko-patches-library 0.8.0 的 SafDestination：子目录创建、复用、文件冲突策略均由已有 SAF 写入流程执行。三个入口共用文档预留锁，避免并发首次下载各自创建同名子目录。
- 账号统一小写，仅允许 ASCII 字母、数字和下划线，拒绝路径分隔符和点路径。作者无法识别时使用 `unknown_user`；关闭开关时传空子路径。已有文件不会移动。
- 本地验证：完整三个覆盖补丁在固定上游源码上依次应用成功；489 条中英文资源名称、格式占位符、Android 转义和文件名占位符检查通过；Python 构建及发布脚本语法通过。
- 发布验证：模拟发布检查通过：五项旧产物备份完成后才能覆盖；备份失败或 main 已变化时停止，既有发布的更新分支不会调用创建 Release。
- 云端 Gradle 构建（编译、Android lint）与已有时间线 JUnit 两项回归通过；没有控制用户设备，下载路径和开关仍需用户在重新应用补丁后实机确认。
- 按用户要求更新现有 X.26.04；更新前 Git 提交保存于 backup/X.26.04-before-user-folders 分支；旧补丁包保存为 X.26.04-before-user-folders.mpp，不新建 Release。

## 发布权限修复

首次构建成功，但 Actions 在为旧提交创建备份标签时返回 HTTP 403（Resource not accessible by integration），发布附件尚未修改。改由已授权的 GitHub 仓库连接创建回退分支，云端只校验其提交，再备份附件和更新当前发布。
