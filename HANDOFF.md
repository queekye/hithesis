# 学生模板交接

## 项目定位与维护分支

这是 hithesis/hithesis 的非官方本部硕博学生模板派生，不代表学校认证。开发默认分支为 `codex/hit-student-template`；上游master及其他历史分支仍保留。学生公开基准为 `student-v1.0.0` 发行，后续交接文档不改写旧tag/发行包。

先读 README、OPTIONS、FORK-NOTES、CHANGES 和 LICENSE。模板功能和正式提交条件以当前学校/学院/图书馆要求为准；样例采用虚构信息，不提交个人论文、签字页或隐私材料到公共仓。

## 安装、构建与路径

需要可用 XeLaTeX 和 BibTeX（TeX Live 或 MiKTeX）；这些工具不随源码打包。首次使用源码克隆，在Windows根目录运行：

```powershell
.\scripts\prepare-student-windows.cmd
.\scripts\build-student-windows.cmd
```

发行压缩包已生成必要类文件，按README使用构建脚本。Linux/macOS源码先 `bash scripts/prepare-student.sh`，再在 `student/` 顺序执行 `xelatex thesis.tex`、`bibtex thesis`、`xelatex thesis.tex`、`xelatex thesis.tex`。云编辑器使用学生发行目录，主文件thesis.tex，编译器XeLaTeX。

正文/封面/参考文献/后置材料分别位于 `student/body/`、`student/front/cover.tex`、`student/reference.bib`、`student/back/`。默认Fandol便于跨机器构建；正式Windows字体或Times New Roman需接手人按许可自行安装并核对，不能从可编译推断指定字体已满足。

只有可选PDF去页码链接流程需Python及 `scripts/requirements-pdf.txt` 中的pypdf依赖，可通过构建脚本的NoPageLinks选项启用；见README和OPTIONS。没有模型、数据集、API key或个人服务器路径要求。

## 验证、许可与后续维护

已有验证/审查证据在 VALIDATION、VALIDATION-RESULTS、REVIEW、REVIEW-MANIFEST；本次仅补交接文档，没有重新验收学校全部提交要求。改动排版、字体或PDF处理后应重新构建并提取/逐页核对PDF，不以CI或样例构建替代用户实际论文审查。

保留上游版权：源码LPPL1.3a+，原README的CC BY-NC4.0及全角BST的LPPL1.3c+按LICENSE划分；不改成统一MIT。后续围绕独立可选学生适配、规范来源证据、合成样例及复现问题维护；不并入私人论文源码。修复先建立可复现匿名例子，源码/发行内容与许可核对后再发新版。旧student-v1.0.0不重新打包或覆盖。
