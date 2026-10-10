# 验证记录

日期：2026-10-09。执行环境：Windows、Python 3.12.14、MiKTeX 26.5 / XeTeX 4.18、BibTeX、Poppler、pypdf 6.10.0。TeX 环境未安装、修复或替换。本轮没有编译或发布个人论文，只构建合成模板。

## 已完成

| 验证组 | 结果 |
|---|---|
| 集成模板测试 | 24/24，通过明细见 [VALIDATION-RESULTS.json](VALIDATION-RESULTS.json) |
| 核心配置 | 4 个正常配置各三遍 XeLaTeX；3 个非法选项/校区正确拒绝 |
| 完整入门项目 | 8 种学位、匿名、C、Word 组合，均三遍 XeLaTeX + BibTeX；博士 14 页、硕士 13 页、匿名 9 页 |
| Word 边界 | 单元格宽/高、决议宽/高、重复行、非 A4、硕士误用固定博士表，共 7 例均在预期错误处拒绝 |
| 原生续页 | 8 页，80 行委员和 320 句决议全部保留；续页表头和末尾标记完整 |
| 默认兼容 | 关闭全部扩展含 fixhidden，与相同元信息的官方父类比较；14 页在 100 dpi 下逐页像素字节一致 |
| PDF 工具回归 | 16/16，无 skip；原文件、书签、目标、文本流、资源、页标签、元信息、其他批注保留，签名/加密输入拒绝 |
| BibTeX 回归 | 3/3，无 skip；含 editor 的完整 .bbl 与官方全角样式一致，显示开关可独立调整 |
| Windows 构建 | 官方 docstrip 生成成功、主项目完整构建、参数失败退出及 runtime 检测通过 |
| 最终无链接入口 | 14 页，55 个页面 Link → 0，17 个书签和 50 个命名目标保留，原 PDF 保留 |
| 版面人工检查 | Word 示例全页缩略图及固定表/声明大图、C 无框名单、关键封面及正文页；未见裁切、越框或重叠 |
| 独立审核 | 模板与工具通过；完整发布包另经 [REVIEW.md](REVIEW.md) 所记录的发布审核 |

测试运行时发现并修复数字布尔名解析、含段落的补丁 helper、C 未定义条件、Word 维度解析/行宽保护及验证记录误判。全文使用虚构数据。独立审查未以实现者自测代替上传前审核。

## 复现

以下回归命令在**完整源码仓库**根目录执行；学生完整 ZIP 只包含写论文所需内容，不携带 tests：

```powershell
.\scripts\prepare-student-windows.cmd
python -m pip install -r scripts/requirements-pdf.txt
python scripts/test_remove_pdf_page_links.py -v
python tests/student-tools/test_bst.py -v
python tests/validate_student.py
.\scripts\build-student-windows.cmd -NoPageLinks
python scripts/package-student.py
```

缺失 XeLaTeX、BibTeX、Poppler 或 pypdf 时集成测试失败，不视为通过。默认模式的像素对照由 pdftoppm 执行；可用 `--pdftoppm` 提供其路径。测试产物进入忽略的 `_work/student-validation/`。

## 验证范围

这次检查对象是新增本部中文硕博扩展及其合成示例；不是上游一校三区所有 42 变体、l3build、所有 TeX 版本或全部字体的全面认证。官方 dtx/ins/examples 未改写。Times New Roman 或指定中文字体缺失时的回退警告不能证明符合最终字体要求。不同论文长度、实际签字、学校新要求仍需作者验收。

GitHub 学生 CI 配置只读权限，在干净 Linux / TeX Live 环境执行测试。这里记录的是上传前本地实测；远程 CI 的当前结果以 Actions 页面为准。
