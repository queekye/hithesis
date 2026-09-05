# feat(book): 支持本部研究生学术与专业学位封面

目标：`hithesis/hithesis:dev`。关联：#298。

2025 年理工类研究生学位论文写作指南 3.3.2 要求学术学位填写“学科”、专业学位填写“类别”。现有本部硕士封面直接输出“学科或类别”，博士封面固定输出“学科”；专业学位的外封标识和英文标签也需要对应选择。

建议新增 `degreecategory=legacy|academic|professional`。默认 legacy 保留既有行为；显式选择 academic/professional 后，仅对哈尔滨校区硕士、博士同步设置外封标识、中英文内封学位与类别标签。学习方式 `fulltime` 和其他校区保持独立。

例：`type=doctor,campus=harbin,degreecategory=professional` 应输出“（专业学位论文）”“申请学位：专业学位博士”“类别”，英文使用 Professional Degree Applied for / Professional Degree Category。academic 对应“（学术学位论文）”“学科”和 Academic Degree Applied for / Speciality。

规范来源：https://hitgs.hit.edu.cn/2025/0331/c17461a365618/page.htm

当前综合适配分支包含额外的 guide2025、声明、换行和占位文字修复，不应直接用作此 PR 的 head。提交前需要抽取上述最小差异，附合成封面示例及宏级测试，再补上上游 TeX Live 矩阵结果。

本地综合分支已验证四种本部硕博学位组合；这些结果不能替代最小 PR 分支的独立验证。本机 l3build 启动退出码为 1 且无输出，尚未完成上游宏级和 42 变体回归。建议先以 Draft PR 讨论接口，CI 通过后再转为 Ready for review。

声明更新与现有 #289 协调；版心预设与 #290 协调。fork 专用来源说明不必作为上游代码的一部分。
