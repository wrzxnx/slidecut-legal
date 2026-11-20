# 图格 / Slidecut 法律页面

正式版本：支持与帮助、隐私政策与使用条款，支持简体中文、英文、繁体中文、日文、韩文、泰文、土耳其文、越南文、俄文。

开发者：wangrui。联系邮箱：wrzxnx@gmail.com。

## 已确认的应用行为

- 所有照片与生成图片完全在设备本地处理，绝不上传至开发者或第三方服务器，也不进入 Firebase、友盟或 AdMob 报告。
- Firebase、友盟用于设备标识统计和崩溃诊断。诊断上下文可能包含设备型号、系统及应用版本、时间和调用堆栈；联网也可能形成技术连接日志。
- 广告使用 Google AdMob；按 SDK 设置、权限和同意状态，可能处理广告相关标识符、网络、展示互动与诊断信息。
- Premium 条款按一次性买断编写，保留有效历史购买权益。
- 数据保存按必要目的、服务商设置和公开政策描述，未虚构固定期限或未经确认的处理国家。

## 独立仓库部署

目标仓库为 `wrzxnx/slidecut-legal`。已上线：https://wrzxnx.github.io/slidecut-legal/ 。全部源码在仓库根目录，静态文件由 `build.py --release` 生成到 `docs/`。共支持 9 种语言。工作流 `.github/workflows/pages.yml` 将构建结果同步至 gh-pages 分支，并请求 GitHub Pages 构建；Pages 从 gh-pages 分支根目录发布。

通用入口为 `privacy.html?lang=zh-Hans` 和 `terms.html?lang=zh-Hans`。支持 zh-Hans、en、zh-Hant、ja、ko、th、tr、vi、ru。指定语言页面位于对应语言目录。页面语言切换及隐私政策正文与已完成版本保持一致。

## 后续维护

1. 修改 `content/*.json` 对应语言的正文，并在 `config.json` 中更新日期与实际 SDK 情况。
2. 执行 `python3 build.py --release` 和 `python3 check.py`。
3. 将源码与生成结果提交到独立仓库的 main 分支，工作流自动检查、同步 gh-pages 并请求发布。
4. 确认 Pages 构建与线上页面成功。

本项目不依赖第三方 Python 包。网页不加载统计、广告脚本或外部字体。请让 App Store Connect 隐私标签、SDK 实际设置和 App 内授权流程始终与政策保持一致。提供网页不会自动改变 App 的数据处理行为。


页面顶部、favicon 和 Apple touch icon 使用开发者提供的 AppIcon-Any.png 原图。

## Support 支持页面

Support 通用链接为 `https://wrzxnx.github.io/slidecut-legal/support.html`，可用于 App Store Connect 的支持网址。添加 `?lang=zh-Hans`、`?lang=en` 或 `?lang=ru` 等参数指定语言；所有现有九种语言均支持。每种语言的固定页面为 `语言代码/support.html`。

页面包括邮箱联系入口、反馈所需信息、照片选择和保存权限、导出画质、Premium 恢复、激励广告、照片本地处理及 Apple 退款帮助。点击邮件按钮打开用户的邮件应用，不会自动发送消息。没有承诺未经确认的回复时限、电话客服或在线聊天服务。
