# MyPoxy 🚀

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)

一款轻量级的高性能代理服务器，支持 TCP/UDP 协议，提供实时流量捕获和可视化分析功能。

**GitHub 仓库**: [https://github.com/ChaiByte1/MyPoxy](https://github.com/ChaiByte1/MyPoxy)

---

## ✨ 核心特性

- **多协议支持**: 完整实现 SOCKS5 协议，兼容 TCP/UDP 代理
- **流量捕获**: 实时捕获并存储代理流量，支持原始数据查看
- **Web 管理界面**: 提供友好的流量监控面板（端口 8080）
- **高性能架构**: 基于多线程模型，支持高并发连接
- **跨平台**: 支持 Windows/Linux/macOS 系统

---

## 🛠️ 快速开始

启动代理服务器
```bash
# 默认代理端口 9527，Web 界面端口 8080
python mypoxy.py

# 自定义端口启动
python mypoxy.py --port=9000 --web-port=8000
```
###📖 使用指南
客户端配置
1.SOCKS5 代理设置
配置客户端使用 SOCKS5 协议，地址：127.0.0.1，端口：9527

2.UDP 穿透支持
确保客户端启用 UDP 中继功能（默认通过端口 9528）

流量分析
+实时查看捕获的流量列表
+点击「查看详情」可分析原始报文
+自动清理历史缓存（重启服务后生效）

###⚙️ 配置参数
|参数|描述|默认值|
|:-----|-----:|:----:|
|--port|代理服务监听端口|9527|
|--web-port|Web 管理界面端口|8080

###🤝 贡献指南
欢迎通过 Issues 或 Pull Requests 参与改进！
1.Fork 本仓库
2.创建功能分支 (git checkout -b feature/your-idea)
3.提交修改 (git commit -m 'Add awesome feature')
4.推送分支 (git push origin feature/your-idea)
5.创建 Pull Request

###📜 许可证
本项目采用 MIT License 开源协议



