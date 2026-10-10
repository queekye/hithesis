# 来源、规范与关联 issue

审计日：2026-10-09。上游指 hithesis 维护团队的版本，不等同于学校官方认证模板。

## 分支关系

- 官方来源：[hithesis/hithesis](https://github.com/hithesis/hithesis)，原 dustincys/hithesis。
- 当前基线：[master 04963b5157f62f0aa634978500744f0b3293da18](https://github.com/hithesis/hithesis/commit/04963b5157f62f0aa634978500744f0b3293da18)，生成类版本标识 v3.1e；不同于上游的模块化 dev / v3.2a。
- 本仓库历史 `codex/hit-2025-compliance` 为早先模块化开发适配，保留历史。
- 本学生分支从上述 master 直接增加派生类、可选包与合成示例，未修改官方 `hithesis.dtx` 或 `hithesis.ins`，不将旧 dev 的重构提交混入。
- 新功能独立维护，未声明已合入上游或关闭其 issue；没有向上游或 CTAN 自动发布。

## 规范来源

| 可核验来源 | 本分支对应内容 |
|---|---|
| [2025-03-31《研究生学位论文或者实践成果写作指南》](https://hitgs.hit.edu.cn/2025/0331/c17461a365618/page.htm)，§3.1、§3.3.1/3.3.2 | 英文 Times New Roman；学位类别、行业导师封面标签 |
| 同指南 §1.6、§2.17 | 创新性成果后置标题 |
| 同指南 §1.7 | 评阅/答辩名单无框线，匿名评阅信息可不列；默认原生无框名单 |
| 同指南 §3.8 | 含页眉、页脚版芯及约 33 行的要求；C 方案是个人实现选择，150 × 229 mm 正文不是指南唯一规定 |
| 同指南附录 1（审计日官网附件） | 现行原创性声明、使用权限，保留 AI 工具标注句及论文题目 |
| [学校 AI 工具使用指南转载](https://hitgs.hit.edu.cn/2026/0519/c18904a392023/page.htm) | 可选详细披露页，需作者如实填写 |
| [历史理工类 Word 范例下载页](https://hitgs.hit.edu.cn/2021/0513/c17461a318415/page.htm) | 显式开启的固定表兼容；与新指南无框要求区分 |
| [图书馆提交要求](https://lib.hit.edu.cn/_upload/article/files/e1/62/1f4a89f5428cb26b7b8808f8614f/30a68897-8864-4ee5-b8c1-3f879f1843cf.pdf)，PDF 第 5 页“四” | 电子论文无空白页、无超链接、保留书签；声明含题目和签名，博士决议。PDF 工具仅负责删除页面链接 |

[官网指南附件](https://hitgs.hit.edu.cn/_upload/article/files/9d/52/c937ab6d47bd85bb5cdb44910f27/b3fa1757-140b-412c-b315-3ea9cbb7d779.doc)在审计日下载的 SHA-256：
`7701c89d36531437b778709f48266ffb1559125b3432975ffea7342d16876e27`。
公告日期不代表附件以后未更新；当前声明包含 AI 标注句，较早本地副本缺少该句。不能根据下载时间推定学校修订日期。本仓库不转载学校完整附件，读者应从官网核验最新文本。

## 上游 issue / PR 对照

状态只对应上述审计日。关联表示主题或缺陷对应，不等于本分支全面解决该 issue。

| 上游链接 | 关联和本分支处理 |
|---|---|
| [#248](https://github.com/hithesis/hithesis/issues/248)、[#298](https://github.com/hithesis/hithesis/issues/298) | 新规范及专业学位；2025 预设/类别选项涵盖列出的标签与声明，未实现全部专业实践成果格式 |
| [#290](https://github.com/hithesis/hithesis/issues/290) | 版芯讨论，上游 dev 已有调整；本分支可选 C 方案，不把其数值称为唯一规范 |
| [#247](https://github.com/hithesis/hithesis/issues/247) | 目录缩进，上游 dev 有相关修正；本 master 派生类提供独立 tocfix |
| [#238](https://github.com/hithesis/hithesis/issues/238) | PDF 文本中的占位污染；fixhidden 在本部硕博把白字占位换为 phantom |
| [#260](https://github.com/hithesis/hithesis/issues/260) | 博士答辩决议；扫描接口已在 master，新增原生内容和旧 Word 兼容 |
| [PR #289](https://github.com/hithesis/hithesis/pull/289) | 新指南声明适配，审计日仍未合入；本分支另保留官网当前 AI 句 |
| [#225](https://github.com/hithesis/hithesis/issues/225)、[#145](https://github.com/hithesis/hithesis/issues/145) | 目录空行，官方已有 tocblank；示例设置 false |
| [#104](https://github.com/hithesis/hithesis/issues/104) | 文献断页，官方已有 splitbibitem；示例设置 true |
| [#215](https://github.com/hithesis/hithesis/issues/215)、[#211](https://github.com/hithesis/hithesis/issues/211) | 文献全角风格及编号对齐，沿用官方能力；当前官方会议字段已经完整，不重复个人旧版补丁 |
| [#296](https://github.com/hithesis/hithesis/issues/296) | biblatex 支持，未由此 BibTeX 样式解决 |

浮动比例、C 行距、封面段落列宽、Word 安全测量与匿名条件是独立实现决策。多位数字分组、双语题注、booktabs 三线表、目录空行/参考文献断页选项已经存在于官方模板。

## 维护与许可

新增类使用 `hitthesis-student` 名称，日志明确标识非官方维护；包亦独立命名。官方原文件和可再生成源码保留，维护修改及原项目网址明确列出。沿用上游 LPPL 1.3a+ 和 CC BY-NC 4.0 通知，不扩大许可；全角文献样式另追溯 [Zeping Lee / gbt7714-bibtex-style](https://github.com/zepinglee/gbt7714-bibtex-style) v2.1.5、LPPL 1.3c+。详见 LICENSE 和各文件头。

继承的官方 CI 自动发布流水线仅允许 `hithesis/hithesis` 仓库运行，避免本 fork 以原项目名向 CTAN 发送发布。学生 CI 只有读取权限，仅编译/测试，不自动发布。
