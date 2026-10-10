# 学生模板工具回归

这里仅使用虚构文献和运行时生成的合成 PDF，不包含实际论文或个人信息。

使用已有 Python（安装 `pypdf>=6,<7`）运行：

```powershell
python scripts/test_remove_pdf_page_links.py -v
python tests/student-tools/test_bst.py -v
```

PDF 回归验证内部及外部 `/Link` 移除，正文流、字体和图像资源、中文批注、书签及其坐标、命名目标、页标签、元数据、文档 ID 和原文件保留；覆盖中文及空格路径、重复处理、输出保护、失败清理、加密与签名字段拒绝。

BST 回归调用 PATH 中已有 `bibtex`，验证会议论文与 `conference` 别名的文献类型、会议集标题、版次、出版地、出版者、年份、页码、URL、访问日期和 DOI；验证三项显示开关可单独调整，以及普通期刊条目与上游一致。未安装 BibTeX 时该组测试显示 skip，不能视作通过。
