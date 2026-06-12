# AI 大模型资讯站

> 由 Codex AI 与人类协作打造的 AI 内容资讯站

## 项目简介

这是一个静态内容网站，包含五个模块：

| 模块 | 内容 | 文章数 |
|------|------|--------|
| 💻 本地 Skills | Codex 系统中已安装的 17 个本体 Skill | 17 |
| 🔌 插件 Skills | Codex 插件提供的 17 个扩展 Skill | 17 |
| 🧠 AI 大模型新闻 | Claude、GPT、开源模型等重要动态 | 3 |
| 🔥 GitHub 精选 Skills | GitHub 上热门的 AI 相关项目 | 6 |
| 🏆 GitHub Top 100 | GitHub 上最受欢迎的 AI Skills 排行榜 | 2 |

## 项目结构

\\\
ai-news-site/
├── content/          # Markdown 内容源文件
│   ├── skills/       # 本地 Skills
│   ├── plugin-skills/ # 插件 Skills
│   ├── news/         # AI 新闻
│   ├── github-skills/ # GitHub Skills
│   └── top-100/      # Top 100 排行榜
├── src/
│   ├── build.py      # 站点构建脚本
├── docs/             # 生成后的静态网站（可直接打开）
├── README.md         # 本文件
\\\

## 如何预览

直接在浏览器中打开 \docs/index.html\ 即可。

或者启动本地服务器：
\\\ash
python src/serve.py
\\\
然后访问 http://localhost:3000

## 如何更新内容

1. 编辑 \content/\ 目录下的 Markdown 文件
2. 运行构建命令：\python src/build.py\
3. 刷新浏览器即可看到更新

## 添加新文章

在对应模块的 \content/\ 目录下新建 \.md\ 文件，
文件头部包含以下格式的元信息：

\\\markdown
---
title: "文章标题"
description: "文章简介"
tags: "标签1,标签2"
source: "数据来源"
date: "2026-06-12"
---

# 文章标题

正文内容...
\\\

然后运行 \python src/build.py\ 即可自动生成页面。

## 技术栈

- Python（构建脚本）
- Markdown（内容管理）
- Tailwind CSS（UI 样式）
- 纯静态 HTML（无需后端服务器）

## 数据来源

所有文章底部均标注了数据来源，确保信息的可追溯性。
