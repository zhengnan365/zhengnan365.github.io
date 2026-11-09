# 郑楠个人学术主页

这是郑楠的个人学术主页，基于 Jekyll 和 GitHub Pages 构建。网站默认中文，支持中英文切换、浅色/深色模式、论文自动同步、专利、项目、获奖、教学、指导学生、开源软件和联系方式展示。

## 网站地址

- GitHub Pages：[https://zhengnan365.github.io/](https://zhengnan365.github.io/)
- 自定义域名：[https://scholar.znup.top/](https://scholar.znup.top/)
- 自定义域名由根目录的 CNAME 文件管理。

## 修改文字应该编辑哪里

请优先修改正式源码目录：

    D:\\00Keyan\\WorkSpace\\zhengnan365.github.io

D:\\00Keyan\\18-课题组\\个人网站 是当前的本地静态预览副本。直接修改其中的 index.html 只会改变本地预览，不会更新 GitHub Pages。

| 要修改的内容 | 编辑文件 | 备注 |
| --- | --- | --- |
| 姓名、职称、学校、学院、邮箱、各类主页链接 | _config.yml | 中英文站点信息和链接集中在这里 |
| 个人简介 | _data/profile.yml | 修改 paragraphs 中的 text_zh/text_en |
| 研究方向 | _data/research.yml | 修改每个方向的标题和介绍 |
| 项目承担 | _data/projects.yml | 每个项目同时填写中文和英文 |
| 论文 | OpenAlex 自动同步 | 不要直接修改生成的论文数据 |
| 论文作者、排除某篇论文 | _data/overrides.yml | 按 DOI 或 OpenAlex ID 添加人工修正 |
| 期刊影响因子、分区、TOP | _data/journal_metrics.yml | 按 ISSN-L 维护指标 |
| 专利 | _data/patents.yml | 修改标题、发明人、类型、状态、编号和日期 |
| 个人荣誉 | _data/awards.yml | 按年份增加或调整奖项 |
| 教学课程 | _data/teaching.yml | 修改学期和 courses |
| 指导学生和竞赛 | _data/students.yml | 修改 competitions、graduate、undergraduate |
| 开源软件 | _data/opensource.yml | 修改项目名称、链接和中英文介绍 |
| 新闻动态 | _data/news.yml | 修改 date、text_zh、text_en；默认隐藏 |
| 联系方式中的地址、办公室 | _data/contact.yml | 修改地址和办公室的中英文内容 |
| 导航栏名称、顺序、显示状态 | _data/navigation.yml | 修改 title、url、enabled；enabled 为 false 时同时隐藏导航和正文 |
| 页面颜色、字号、间距 | assets/css/site-overrides.css | 本站覆盖样式集中在这里 |
| 头像、浏览器标签图标 | assets/img/ 和 _config.yml | 图片放入 assets/img 后更新配置路径 |

## 双语文字的写法

日常维护只需修改数据文件中的 `text_zh/text_en`、`title_zh/title_en` 等成对字段，不必编辑 HTML。每个栏目数据文件开头都有字段说明，可复制现有记录后修改文字。

**数据文件保持 `.yml` 扩展名**。Jekyll 原生不会把 `_data/news.md` 或 `_data/new.md` 读取为栏目数据；新闻文件是 `_data/news.yml`。各栏目的可复制模板见 [内容填写指南](docs/CONTENT_GUIDE.md)。

## 常见修改示例

### 增加一个项目

在 _data/projects.yml 末尾增加一组字段：

    - period: 2026.01–2028.12
      title_zh: 项目中文名称
      title_en: English project title
      role_zh: 主持
      role_en: Principal investigator
      amount_zh: 30 万元
      amount_en: CNY 300,000

### 增加一个奖项

在 _data/awards.yml 中增加：

    - year: 2026
      title_zh: 奖项中文名称
      title_en: English award title

### 更新专利状态

在 _data/patents.yml 中修改对应条目的 patent_type、status、display_number、display_date 及其中文和英文标签。专利会按 display_date 从新到旧排列，页面默认显示前五项，其余放在“更多”中。

### 显示或隐藏栏目

在 _data/navigation.yml 中找到对应栏目，将 enabled 设置为 false 即可同时隐藏导航项和页面栏目；改回 true 即可恢复。例如：

    - key: news
      template: news
      enabled: false
      title_zh: 新闻动态
      title_en: News
      url: "#news"

栏目模板位于 _includes/sections/，一般不需要修改模板，只需更新对应的 _data 文件。

`enabled` 使用不加引号的 `true` 或 `false`。关闭不会删除数据；重新打开会恢复内容。移动整个栏目条目会同时调整正文与导航的顺序。修改保存并经 Jekyll 重新构建后生效；线上还需提交、推送并等待 Pages 部署完成。

## 论文自动同步

论文数据来自 OpenAlex 作者记录 A5001145059。同步脚本会更新：

- _data/publications.yml
- assets/data/site-data.json

网站不会从 ResearchGate、Scopus 或 Google Scholar 自动抓取论文。需要人工修正时使用 _data/overrides.yml；影响因子和分区使用 _data/journal_metrics.yml。

同步方式：

    python scripts/sync_publications.py

GitHub Actions 每周一自动运行，也可以在仓库 Actions 页面手动运行 Sync publications。

## 本地预览

正式 Jekyll 预览需要 Ruby、Bundler 和 Python：

    bundle install
    bundle exec jekyll serve --livereload

然后打开 http://localhost:4000/。

当前任务中使用的静态预览地址是：

    http://127.0.0.1:8765/

修改源码后，需要重新构建或让我同步静态预览副本；不要把 8765 目录中的 index.html 当作 GitHub Pages 的源码。

## 提交前检查

    python -m unittest discover -s tests -p "test_*.py" -v
    node --test tests/site-controls.test.mjs
    bundle exec jekyll build

确认本地页面正常后，再提交并推送 main 分支。GitHub Pages 工作流成功后，检查中英文切换、明暗模式、移动端导航、论文数据和折叠栏目。

## 目录结构

    _config.yml                 站点信息和链接
    index.md                    按导航配置调用各栏目模板
    _layouts/                   页面布局
    _includes/                  可复用模板
    _data/                      所有栏目数据和论文指标
    _includes/sections/         各栏目的 Liquid 渲染模板
    assets/css/                 样式文件
    assets/js/                  交互脚本
    assets/img/                 头像和图标
    assets/files/               可下载文件
    scripts/                    OpenAlex 同步脚本
    tests/                      自动化测试
    .github/workflows/          Pages 部署和论文同步
    docs/CONTENT_GUIDE.md       内容填写指南
    docs/TECHNICAL.md           技术维护文档

## 许可

源码沿用 CC0 1.0 Universal。个人资料、简历和学术数据请按其原始来源和授权使用。
