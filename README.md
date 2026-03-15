# 这个项目是为你量身打造的 Cloudflare Tunnel (TryCloudflare) 一键式可视化工具。它将复杂的隧道指令简化为一个“填空题”，特别适合需要快速公网预览、HTTPS 调试的开发者。

# 打包命令：
pyinstaller --noconsole --onefile --add-data "cloudflared32.exe;." --add-data "cloudflared64.exe;." cf_tunnel_gui.py

# 以下是该项目的核心介绍：

# 1. 项目定位：极简 HTTPS 穿透
Cloudflare Tunnel 是目前全球最稳定的内网穿透方案之一。本项目通过 Python GUI 封装了其 TryCloudflare（匿名隧道）功能：

无需账号：不用注册 Cloudflare 账号，不用买域名。

原生 HTTPS：自动分配合规的 SSL 证书，解决小程序、支付回调等必须 HTTPS 的痛点。

零配置：不需要编写 YAML 配置文件，输入端口即用。

# 2. 核心技术亮点
双内核自适应：

内置 cloudflared32.exe 和 cloudflared64.exe。

智能识别：运行时自动探测 Windows 系统架构（x86/x64），精准调用对应内核。

单文件绿色化：

按需释放：运行后才将内核解压到程序同级目录，保持 EXE 体积精简。

无痕清理：关闭程序或停止服务时，自动删除释放出的内核文件，不给系统留“垃圾”。

编码优化：

针对 Windows 中文环境（GBK）做了专门的 UTF-8 兼容处理，彻底解决了日志输出时的乱码或崩溃（Codec Error）问题。

可视化增强：

实时解析：自动从海量日志中抓取 https://*.trycloudflare.com 动态域名，高亮显示。

一键跳转：点击按钮直接调用系统默认浏览器打开公网地址。

# 3. 使用场景
Web 开发调试：本地写的网页，一秒变公网链接给客户演示。

移动端测试：手机通过公网域名直接访问你电脑上的开发环境。

技术平权：让即使不懂命令行的用户，也能享受到全球顶级 CDN 厂商提供的网络隧道服务。

# 4. 界面设计理念
直观优先：舍弃了复杂的 URL 配置，只保留“端口”输入，符合用户直觉。

清爽风格：采用浅色系扁平化设计，不仅在 Win10/11 上好看，在 Win7 环境下也能保持良好的原生感。
