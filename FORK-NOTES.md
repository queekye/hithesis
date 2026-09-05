# 哈尔滨校区研究生 2025 指南适配开发版

本目录是 [hithesis/hithesis](https://github.com/hithesis/hithesis) 的非官方修改版，基于 `dev` 提交 `50357f18f268ccf77e12a8aaad20fd03a1b610bf`（2026-08-04）。上游稳定版为 v3.1e，`master` 提交 `4a4b31148779e94eebbee4a175757551f94cab87`（2026-08-21）。日期不同源于稳定分支的发布合并，不代表开发分支已包含稳定分支全部提交。

原始作者与贡献者版权、README 中 LPPL 1.3a 或更新版本及 CC BY-NC 4.0 的许可声明全部保留。本分支修改由 queekye 维护；上游作者不承担本分支的支持责任。上游完整未修改源码可从上述仓库和固定提交获取。修改后的类文件会在编译日志中明确标识非官方修改版。模板与其示例应按原许可非商业分享；不重新标为 MIT，也不把模板作者替换成修改者。

## 规范依据与范围

- [2025-03-31 学校发布通知及理工类指南附件](https://hitgs.hit.edu.cn/2025/0331/c17461a365618/page.htm)：3.3.1 外封、3.3.2 内封、3.8 版心及附录 1 声明。
- 用户提供的《研究生学位论文书写范例》：中英文封面、创新性成果及声明版式；声明文字以较新的指南为准。
- [2026-05-19 人工智能工具使用指南](https://hitgs.hit.edu.cn/2026/0519/c18904a392023/page.htm)，已读取其嵌入的四页 PDF：第七条要求使用者主动出具人工智能使用声明，并披露工具名称、版本、网址、具体用途、环节、参数和验证过程。
- 适用范围：哈尔滨校区理工类硕士、博士学位论文。其他校区、学士、博士后及实践成果报告未纳入本次规范适配。

## 使用

```latex
\documentclass[fontset=windows,type=doctor,campus=harbin,
  guide2025=true,degreecategory=academic]{hithesisbook}
```

硕士使用 `type=master`；专业学位使用 `degreecategory=professional`。`guide2025` 默认 false；`degreecategory` 默认 legacy。仅启用 `guide2025` 时采用学术学位。旧文档不加新选项时保留原来的学位字段及版心默认值。

`degreecategory` 负责外封学位类型标记、内封“学科／类别”、申请学位和对应英文标签。专业学位中文申请学位为“专业学位博士／硕士”；英文具体学位名称仍由 `exueke` 等原有元数据表达，需按学校公布名称填写。

`guide2025` 负责版心默认选择 `newgeometry=no`（150 × 224 mm 正文区，加页眉页脚约 150 × 240 mm）、Times New Roman 字体、行业导师标签、长字段换行、英文内封留白调整、2025 年声明和创新性成果标题。显式指定 `newgeometry` 仍优先；若选其他值，应自行核对是否符合指南。缺少 Times New Roman 时会发出警告，回退字体不作为最终字体合规证明。字体文件不随仓库分发。

三处白色占位文字改为等尺寸 phantom，以消除 PDF 文本提取污染。此修复适用于全部原有变体，需单独进行跨变体回归。

示例全部使用虚构信息，不含个人论文正文、审稿意见、签名或学校原始 Word 附件。四个研究生示例用于封面、换行、版心和声明检查，不能替代完整论文所有表格、图件和参考文献的格式核验。

2026 年 AI 指南通过可选 `aideclaration` 环境支持，见 `ai-disclosure-example.tex`。该环境不推定用户是否使用 AI，也不替用户声称没有使用或已经完成核验。采用单独声明承载实际使用记录；没有将现有 PR #289 的新增概括句直接拼入 2025 原创性声明。格式位置仍应核对学院具体要求。

## 构建

遵循上游 CONTRIBUTING.md，编辑 `src/*.dtx`，生成的 cls、PDF 不进入源码提交。跨平台推荐 `l3build unpack`；本机该命令退出码为 1 且无输出，因此通过设置进程级 `TEXINPUTS=./src//;` 后执行 `latex -interaction=nonstopmode hithesis.ins` 完成 docstrip 生成。未安装或修复任何 TeX 环境。

示例使用 XeLaTeX、BibTeX、XeLaTeX、XeLaTeX 构建；本工作区通过项目 `compile-thesis-windows.cmd -Main <示例名> -WorkingDirectory <本目录>` 调用。

## PR 拆分建议

1. 封面学位类型单独 PR，关联 #298：只保留 degreecategory 选项、封面字段、文档、测试。建议标题 `feat(book): 支持本部研究生学术与专业学位封面`。
2. 版心和 2025 规范预设先在 #290 讨论默认策略；本分支以 opt-in 方式实现，不能把复合分支直接当作第一项 PR。
3. 声明文字与现有 Draft PR #289 协调；其 AI 使用声明需确认独立规范来源，本分支没有加入缺少指南依据的句子。
4. phantom、封面长字段及创新性成果标题分别提交小补丁。发布前运行上游 42 变体、l3build 和 TeX Live 2022–2026 CI。

建议先 fork 到 `queekye/hithesis`，保留 GitHub 的 fork 来源与历史，再推送开发分支。上游目标为 `dev`。发布操作与本地适配分别记录；没有远程链接时不视为已上传。
