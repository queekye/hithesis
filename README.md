# hithesis 学生使用版

基于 [hithesis/hithesis](https://github.com/hithesis/hithesis) 的非官方学生分支，面向哈尔滨工业大学本部硕士、博士中文学位论文，维护者为 [queekye](https://github.com/queekye)。感谢 Chu Yanshuo（dustincys）及上游贡献者。本分支将个人使用中积累的适配拆为独立选项，提供全部使用虚构信息的入门示例。

**推荐从 [Releases](https://github.com/queekye/hithesis/releases) 下载学生完整包**；其中已经包含由官方源码生成的运行文件。源码分支基于上游 `master` 固定提交 [04963b5](https://github.com/hithesis/hithesis/commit/04963b5157f62f0aa634978500744f0b3293da18)，保留 `hithesis.dtx`、`hithesis.ins` 和官方 `examples/`。本分支没有学校认证，具体提交要求以学校、学院与图书馆当前通知为准。

## 开始使用

需要已有的 XeLaTeX、BibTeX（例如 TeX Live 或 MiKTeX）。Windows 完整包解压后：

```powershell
.\scripts\build-student-windows.cmd
```

源码下载或克隆后，先运行一次：

```powershell
.\scripts\prepare-student-windows.cmd
.\scripts\build-student-windows.cmd
```

Linux/macOS：源码先运行 `bash scripts/prepare-student.sh`，完整包可跳过；再在 `student/` 执行 `xelatex thesis.tex → bibtex thesis → xelatex thesis.tex → xelatex thesis.tex`。上传到在线 LaTeX 编辑器时使用完整包中的 `student/`，主文件选 `thesis.tex`，编译器选 XeLaTeX。

修改 `student/front/cover.tex`、`student/body/`、`student/reference.bib` 和 `student/back/`。示例默认使用开源 Fandol 字体；Windows 正式提交可改为 `fontset=windows` 并核验所需字体。2025 预设会优先使用 Times New Roman，缺失时警告并回退；回退字体不能当作已经满足指定字体要求。匿名模式需核查全文身份线索。

## 修改了什么

| 功能 | 使用方式 | 默认 |
|---|---|---|
| 2025 指南适配、封面长字段换行、行业导师、创新性成果、现行原创性声明含 AI 标注句 | `guide2025=true` | 派生类关闭；入门示例开启 |
| 学术或专业学位类别及英文封面标签 | `degreecategory=academic` / `professional` | `legacy`；2025 预设自动选学术 |
| 目录章条目缩进修正 | `tocfix=true` | 派生类关闭；入门示例开启 |
| C 版面：150 × 229 mm 正文及 19.55 bp 行距 | `layout=c` | 关闭；属于可选项目版面 |
| 浮动体页面布局 | `floatlayout=true` | 关闭 |
| 匿名封面及 PDF author，示例排除身份相关后置页 | `anonymous=true` + `\hitanonymousTF` | 关闭 |
| 白字占位替换，避免 PDF 文本提取污染 | `fixhidden=true` | 本部硕博开启，可关闭 |
| 原生决议和可续页无框委员会名单 | `hitstudent-backmatter` 的 `mode=guide` | 入门示例使用 |
| 历史 Word 固定表兼容、成果列表、流式声明 | `mode=word`，替换相应 `back/*-word.tex` | 关闭 |
| 独立 AI 工具披露页 | `aideclaration` | 可删除示例输入 |
| 全角文献样式（沿用官方已有的完整会议输出） | `gbt7714-numerical-quanjiao.bst` | 入门示例使用，可换回 `hithesis` |
| 删除 PDF 页面链接，保留书签和原文件 | 构建加 `-NoPageLinks` | 关闭；需要 Python + `pypdf>=6,<7` |

2025 适配覆盖列出的具体条目，不表示指南所有条款自动合规。目录空行 `tocblank`、文献跨页 `splitbibitem`、双语题注、三线表及数字分组本来就是上游能力；本分支沿用，未将其作为新增功能。

详见 [选项与迁移](OPTIONS.md)、[规范与上游 issue 对照](FORK-NOTES.md)、[修改清单](CHANGES.md)、[验证](VALIDATION.md) 和 [上传前独立审核](REVIEW.md)。历史开发分支 `codex/hit-2025-compliance` 保留；当前学生发布分支为 `codex/hit-student-template`，不会覆盖历史分支。

## 来源与许可

上游原始说明保存在 [UPSTREAM-README.md](UPSTREAM-README.md)。保留上游版权、LPPL 1.3a+ 以及 README 的 CC BY-NC 4.0 非商业许可声明；全角 BST 另保留 Zeping Lee 的 LPPL 1.3c+ 来源。没有改为 MIT，也不授予商业使用许可。完整说明见 [LICENSE](LICENSE)。

反馈本分支扩展请在 [本仓库 Issues](https://github.com/queekye/hithesis/issues) 提出；上游问题请附可复现的官方模板示例，勿上传本人论文、签字页或送审材料。
