# 选项与迁移

## 两个入口

继续使用 `\documentclass{hithesisbook}` 时，官方类和示例保持原样。使用 `\documentclass{hitthesis-student}` 时加载同一官方类，再选择学生扩展。自定义包不覆盖官方 `hithesis.sty`；禁止用个人旧版生成类替换此基线。

派生类默认 `guide2025=false,degreecategory=legacy,anonymous=false,tocfix=false,floatlayout=false,layout=upstream,fixhidden=true`。要复现官方行为，额外设 `fixhidden=false`。入门示例显式启用 2025 预设和目录修正，与派生类默认值不同。
入门示例还显式设 `library=true`，采用官方电子版模式避免章前空白页。打印装订需按要求选择 `library=false,openright=true` 等官方选项。

## 学位和版面

```latex
\documentclass[fontset=windows,type=master,campus=harbin,
  guide2025=true,degreecategory=professional,layout=upstream]{hitthesis-student}
```

学术学位设 `degreecategory=academic`；专业学位设 `professional`，将 `csubject/esubject` 填为本人专业学位类别，`cxueke/exueke` 填为所授学位领域。是否存在行业导师取决于本人，不需填时留空。新增核心实质选项限定本部硕博；深圳、威海、本科、博后继续走官方入口。

`layout=upstream` 沿用官方 `newgeometry` 及行距设置。若选择 `layout=c`，C 包覆盖正文几何与基础行距，仅支持本部中文硕博正式论文。该方案从个人版面调整提炼，不是学校规定的唯一尺寸。不要同时叠加自己的 geometry 补丁后声称选项仍有效。

`tocfix` 每次写章目录条目前重设悬挂宽度，避免被节条目改写共享长度。`floatlayout` 独立设 top/bottom/text/float-page 比例为 0.92/0.80/0.05/0.85；这些数值是项目排版选择。

## 匿名送审

加 `anonymous=true`，封面作者、导师、学号及 PDF author 清空。用：

```latex
\hitanonymousTF{匿名版内容}{含身份的正式版内容}
```

入门文件已把成果、决议、授权、致谢等置于正式版分支。该功能不扫描正文、图片、文献自引、附件、PDF 其他元数据或 Git 历史；必须按送审要求手动核查。公开模板只含虚构数据，自己的论文宜在独立私有目录维护。

## 决议、声明和 AI 页

推荐 `\usepackage[mode=guide]{hitstudent-backmatter}`，配合 `back/resolution-guide.tex`（无框名单，可续页）、`back/authorization-guide.tex`（类维护的声明）。

需要旧 Word 框线表时，显式改为 `mode=word`，并把输入换为 `resolution-word` 和 `authorization-word`。Word 表是约 154 mm 宽的历史固定坐标，不跟随 C 正文宽度；栏目字调整为 10.5 bp。超长决议、单元格宽高超限、重复固定行或非 A4 时编译失败，不会裁切成表面成功的 PDF。需要更长内容请选择原生模式。旧表行数不可随意扩增。
固定决议表仅支持本部中文博士（表中包含博士学位授予建议），硕士使用原生模式；Word 成果列表和流式声明接口可单独使用。

Word 成果列表可在 `publication` 环境内使用（须加载 `mode=word`）：

```latex
\hitwordpubheading{一、学术论文}
\begin{wordpublist}
  \item 本人的真实、已核验成果条目。
\end{wordpublist}
```

保留上游 `\resolution[scan.pdf]` / `\resolution*[scan.pdf]` 及 `\authorization[scan.pdf]` / 带星号版本。扫描件和签字由本人准备。原生模式适合编辑草稿，正式版以当前学校表单及签字要求为准。

2025 预设的原创性声明保留当前官网附录 1 的 AI 工具标注句；`aideclaration` 只是独立的详细披露页，不代替声明。未使用或无需附页时删去 `\input{back/ai-tools}`。

## 参考文献

`\bibliographystyle{gbt7714-numerical-quanjiao}` 沿用官方全角风格。当前官方基线已能完整输出会议集、编辑者、出版信息、年份、页码等，本发布版不再重复个人旧版本的会议字段补丁。URL、DOI 和访问日期默认显示，三个 `show.*` 可在 BST 的 `load.config` 内独立改为 `#0`；隐藏属于个人选择，不是本分支认定的规范要求。该风格有自身配置，官方类 `bibmaxauthor/bibauthorupper/biblabelalign` 仅对官方 BST 生效。换回 `\bibliographystyle{hithesis}` 使用官方样式。

## 无页面链接 PDF

安装 `pypdf>=6,<7` 后：

```powershell
.\scripts\build-student-windows.cmd -NoPageLinks
# Python 不在 PATH 时
.\scripts\build-student-windows.cmd -NoPageLinks -PythonExe "C:\path\python.exe"
```

生成 `thesis_no_links.pdf`，保留 `thesis.pdf`。移除内部/外部页面 `/Link` 批注，保留目录书签、目标、文本、字体/图像及其他批注。PDF 数字签名/认证签名和加密文件会被拒绝；请在签名或正式归档之前处理。只删除页面链接不会自动清除空白页或补全签字，不代表通过图书馆全部审核。

## 更新上游

此分支固定源码基线，生成类来自同一 `hithesis.ins`。升级上游时须重新生成类、运行测试并独立审查；核心补丁找不到目标宏会报错。不要仅替换部分 `.cls/.cfg/.sty`。
