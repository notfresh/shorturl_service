# Podcast Markdown to CSV Converter Skill

## 概述

这是一个用于将 Podcast Markdown 导航文件转换为 CSV 格式的技能。

**目的**: 快速提取 markdown 中的播客元数据（标题、音频链接、字幕链接等），生成结构化的 CSV 数据。

**应用场景**:
- 📊 数据分析和统计
- 📱 导入到数据库或播放器应用
- 🔍 内容搜索和索引
- 📈 批量处理播客元数据

---

## 功能特性

✅ **自动解析 Markdown 格式**
- 识别 `[标题](链接)` 格式的链接
- 智能提取标题和 URL
- 处理多行链接（链接可能跨行）

✅ **生成结构化 CSV**
- 标准四列格式: `title`, `audio_url`, `subtitle_text`, `subtitle_url`
- UTF-8 编码支持中文
- 完整的数据验证和错误处理

✅ **灵活的输出选项**
- 自动输出到同名 `.csv` 文件
- 支持 `-o` 参数自定义输出文件名

✅ **详细的操作反馈**
- 处理完成后显示统计信息
- 错误信息清晰明确

---

## 使用方法

### 基本用法

```bash
python podcast_markdown_to_csv.py Podcast-Subtitle/pie-podcast-nav-v2.md
```

输出文件: `pie-podcast-nav-v2.csv`

### 自定义输出文件

```bash
python podcast_markdown_to_csv.py Podcast-Subtitle/pie-podcast-nav-v2.md -o podcasts.csv
```

### 帮助信息

```bash
python podcast_markdown_to_csv.py -h
```

---

## 输出 CSV 格式

| 列名 | 说明 | 示例 |
|------|------|------|
| **title** | 播客标题 | 第204期 _千问与玄学 |
| **audio_url** | 音频链接 | https://cdn2.wavpub.com/hosting.wavpub.cn/wp-content/uploads/sites/28/2026/03/pie-ep204.mp3 |
| **subtitle_text** | 字幕标签文本 | 字幕 |
| **subtitle_url** | 字幕文件链接（相对项目根目录） | Podcast-Subtitle/pie-srt/v2/pie-ep204.mp3.srt |

> ⚠️ **路径自动转换**：脚本会自动将 Markdown 中的相对路径（如 `./pie-srt/v2/...`）转换为相对于项目根目录的路径（如 `Podcast-Subtitle/pie-srt/v2/...`），前缀从输入文件路径自动推导。

---

## 技术细节

### 实现原理

1. **文件读取**: UTF-8 编码读取 Markdown 文件
2. **正则解析**: 使用正则表达式匹配 `[...](...)` 格式
3. **数据结构**: 将解析结果存储为 Python 字典列表
4. **CSV 写入**: 使用 Python csv 模块标准库写入

### 支持的 Markdown 格式

```markdown
[标题文本](链接地址)
[字幕](字幕链接)

[下一个标题](链接地址)
[字幕](字幕链接)
```

### 错误处理

- ❌ 文件不存在: 报告错误并退出
- ❌ 未找到有效条目: 提示警告信息
- ❌ 写入失败: 捕获 IO 异常并报告

---

## 依赖项

- **Python 3.6+**
- 标准库: `re`, `csv`, `pathlib`, `sys`, `argparse`

无需安装第三方包！

---

## 文件结构

```
shorturl_service/
├── Podcast-Subtitle/                       # git submodule
│   ├── pie-podcast-nav-v2.md               # 播客导航文件（输入）
│   └── pie-srt/v2/                         # 字幕文件目录
└── .agents/skills/podcast-markdown-to-csv/
    ├── podcast_markdown_to_csv.py           # 核心脚本
    └── SKILL.md                             # 本文件（使用说明）
```

---

## 示例输出

**处理 Podcast-Subtitle/pie-podcast-nav-v2.md:**

```
✅ 转换完成！
   输入文件: Podcast-Subtitle/pie-podcast-nav-v2.md
   输出文件: pie-podcast-nav-v2.csv
   总条数: 126
```

**CSV 内容预览 (前 3 行):**

```csv
title,audio_url,subtitle_text,subtitle_url
特别篇 ④周年庆,https://cdn2.wavpub.com/hosting.wavpub.cn/wp-content/uploads/sites/28/2026/03/pie-4th-anniversary.mp3,字幕,Podcast-Subtitle/pie-srt/v2/pie-4th-anniversary.mp3.srt
第204期 _千问与玄学,https://cdn2.wavpub.com/hosting.wavpub.cn/wp-content/uploads/sites/28/2026/03/pie-ep204.mp3,字幕,Podcast-Subtitle/pie-srt/v2/pie-ep204.mp3.srt
```

---

## 常见问题

### Q: 脚本能处理多少条记录?
**A**: 理论上可以处理无限数量的记录。当前已验证 126 条记录正常转换。

### Q: 支持其他 Markdown 格式吗?
**A**: 目前仅支持 `[文本](链接)` 格式。其他格式需要修改正则表达式。

### Q: 如何在其他项目使用此脚本?
**A**: 直接复制 `podcast_markdown_to_csv.py` 到目标目录，然后运行命令即可。

### Q: 生成的 CSV 如何导入到 Excel?
**A**: 用 Excel/Numbers/Google Sheets 直接打开 `.csv` 文件，会自动识别列结构。

---

## 扩展功能建议

🔧 **可以添加的功能:**
- [ ] 支持多种 Markdown 格式（列表、表格等）
- [ ] 添加日期提取（从标题中自动提取发布日期）
- [ ] 批量转换多个文件
- [ ] 支持 JSON、SQLite 等输出格式
- [ ] 添加数据去重和验证功能
- [ ] 命令行交互模式

---

## 许可证

MIT License - 自由使用和修改

## 更新日志

### v1.0 (2026-03-22)
- ✨ 初始版本发布
- 支持基本的 Markdown 到 CSV 转换
- 验证 126 条播客记录
