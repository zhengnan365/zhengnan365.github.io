# 个人学术网站技术维护文档

## 1. 系统概览

网站是一个单页 Jekyll 站点，发布到 GitHub Pages。页面由以下部分组成：

- index.md：按导航配置调用各栏目模板
- _layouts/homepage.html：HTML 外壳、标题、图标、样式和脚本引用
- _includes/：论文、导航等可复用模板
- _data/：所有栏目数据、论文和期刊指标
- _includes/sections/：各栏目的 Liquid 渲染模板
- assets/css/：基础主题和本站覆盖样式
- assets/js/：导航、明暗模式、语言切换、返回顶部等交互
- scripts/：OpenAlex 论文同步脚本

页面是单页结构。导航栏通过锚点跳转到栏目模板中的 section id，例如 #projects 对应 section id="projects"。

## 2. 正式源码和本地预览

正式源码目录：

    D:\\00Keyan\\WorkSpace\\zhengnan365.github.io

本地预览应直接在正式源码目录运行 `bundle exec jekyll serve --livereload`，浏览 `http://localhost:4000/`。不要另行维护静态 HTML 副本；源码中的 Liquid 模板和 `_data` 数据需要由 Jekyll 构建。

## 3. 页面内容维护

index.md 现在只负责遍历 _data/navigation.yml 并按 template 字段调用栏目模板。可编辑文字集中在 _data 中，栏目模板集中在 _includes/sections/ 中。Jekyll 的 _data 目录使用 YAML、JSON 或 CSV；本项目统一使用 YAML，文件扩展名是 .yml。不会自动加载 _data 下的 .md 文件。

每个数据文件开头有字段说明；全部栏目的可复制示例见 [内容填写指南](CONTENT_GUIDE.md)。日常只需编辑数据，无需修改 HTML 或 index.md。

### 3.1 栏目数据文件

| 栏目 | 数据文件 | 模板 |
| --- | --- | --- |
| 个人简介 | _data/profile.yml | _includes/sections/about.html |
| 研究方向 | _data/research.yml | _includes/sections/research.html |
| 项目承担 | _data/projects.yml | _includes/sections/projects.html |
| 论文 | _data/publications.yml 和 _data/overrides.yml | _includes/publications.md |
| 专利 | _data/patents.yml | _includes/sections/patents.html |
| 获奖 | _data/awards.yml | _includes/sections/awards.html |
| 教学 | _data/teaching.yml | _includes/sections/teaching.html |
| 指导学生、竞赛 | _data/students.yml | _includes/sections/students.html |
| 新闻动态 | _data/news.yml | _includes/sections/news.html |
| 开源软件 | _data/opensource.yml | _includes/sections/opensource.html |
| 联系 | _data/contact.yml 和 _config.yml | _includes/sections/contact.html |

这些区域的中文和英文通常由 i18n-zh、i18n-en 两个 span 控制。新增内容时保持两种语言成对出现。

### 3.2 通过 YAML 数据渲染的内容

以下栏目由 _data 目录中的 YAML 文件渲染：

- 项目承担：_data/projects.yml
- 专利：_data/patents.yml
- 个人荣誉：_data/awards.yml
- 开源软件：_data/opensource.yml
- 导航栏和栏目开关：_data/navigation.yml

YAML 对缩进敏感。每一项以短横线开始，字段使用两个空格缩进，冒号后留一个空格。中文字段和英文字段都应填写。

专利页面会先按 display_date 倒序排列，只显示前五项；其余条目放在 details.older-patents 折叠区域中。修改专利状态时，保持 patent_type、status、display_number、display_date 及其中文英文标签的一致性。

### 3.3 显示或隐藏栏目

_data/navigation.yml 是栏目注册表。每项包含 key、template、title_zh、title_en、url 和 enabled：

    - key: news
      template: news
      enabled: false
      title_zh: 新闻动态
      title_en: News
      url: "#news"

enabled 为 false 时，_includes/navigation.html 不输出该导航项，index.md 也不会调用对应模板；改为 true 后两处会同时恢复。必须使用不加引号的布尔值；新闻默认关闭。调整栏目顺序时直接调整 navigation.yml 中条目的顺序。新增栏目时，需要同时新增数据文件、_includes/sections/ 下的模板，以及 index.md 中对应的 case 分支。已有栏目启用或停用不需要修改模板。

## 4. 论文数据流

论文同步脚本使用 OpenAlex 作者 ID A5001145059，通过 API 获取论文、作者、年份、期刊、DOI 和引用次数。

数据处理流程：

1. scripts/sync_publications.py 获取 OpenAlex works。
2. scripts/publication_data.py 标准化 DOI、作者、期刊和 GB/T 7714 引用。
3. _data/overrides.yml 应用人工修正或排除项。
4. _data/journal_metrics.yml 添加影响因子、中科院分区和 JCR 分区。
5. 脚本同时写入 _data/publications.yml 和 assets/data/site-data.json。
6. Jekyll 模板或本地静态页面读取处理后的数据。

不要直接编辑 _data/publications.yml 或 assets/data/site-data.json。需要修正论文标题、作者顺序、通讯作者、排除项或链接时，在 _data/overrides.yml 中按 DOI 或 OpenAlex ID 添加覆盖。

指标记录以 ISSN-L 为键，metric_year 表示指标年份。期刊指标可能随年份更新，修改时同时更新来源链接。

## 5. 样式和交互

样式加载顺序为：

1. 基础字体和 Minimal Light 主题
2. pub.css：论文和标签样式
3. nav.css：顶部固定导航
4. site-overrides.css：本站最终覆盖规则

修改字号、行距、留白、颜色、列表对齐和竞赛字重时，优先编辑 assets/css/site-overrides.css。不要直接修改生成页面中的 style 属性，除非是内容模板确实需要。

主要交互：

- _includes/topnav.html：导航栏和移动端菜单
- assets/js/site-controls.mjs：中英文和明暗模式
- assets/js/back-to-top.js：返回顶部按钮
- assets/js/favicon-switcher.js：按系统主题切换浏览器标签图标

浏览器标签图标位于 assets/img/favicon.svg 和 favicon-dark.svg，路径在 _config.yml 中配置。

## 6. GitHub Pages 发布链

推送 main 分支后，.github/workflows/pages.yml 会：

1. 检出仓库。
2. 使用 actions/jekyll-build-pages 构建 _site。
3. 上传 Pages artifact。
4. 部署到 GitHub Pages。

.github/workflows/sync-publications.yml 每周一运行论文同步；也支持在 Actions 页面手动触发。只有论文生成数据发生变化时，工作流才会提交更新。

仓库 Settings → Pages → Build and deployment 的来源应设置为 GitHub Actions。

同一个 Pages 工作流还会把 `_site` 上传为 `jekyll-site` artifact。当仓库变量 `ENABLE_SERVER_DEPLOY` 为 `true` 时，`deploy-server` 任务下载该 artifact，并使用 SSH 与 `rsync --delete` 同步到个人服务器。使用小皮面板时，建议目标目录为 `/xp/www/zn.znup.top`，由面板负责站点 Web 服务和 HTTPS。服务器连接信息只保存在 Actions Secrets 中，不写入仓库。配置项目和操作步骤见 README 的“同步到个人服务器”。

## 7. 本地检查

建议在提交前运行：

    bundle exec jekyll build

重点检查：

- 页面是否能正常构建
- 中英文切换是否都显示完整
- 明暗模式下文字和图标是否有足够对比度
- 专利“更多”是否能展开
- 论文 DOI、引用按钮和 OpenAlex 说明是否正常
- 移动端导航是否能打开和关闭

## 8. 常见故障

### 页面文字改了但网站没有变化

确认修改的是 WorkSpace 源码目录，而不是 8765 静态预览目录；确认文件已提交并推送到 main；再查看 Pages 工作流日志。

### 论文没有更新

确认 OpenAlex 作者 ID、网络请求和 _data/overrides.yml 格式；运行同步脚本后检查 _data/publications.yml 和 assets/data/site-data.json 是否同时变化。

### Jekyll 构建失败

先检查 YAML 缩进、Liquid 标签是否成对、HTML 标签是否闭合，再运行 bundle exec jekyll build --trace。

### 本地预览仍是旧样式

强制刷新浏览器；确认修改位于正式源码目录，必要时重新启动 `bundle exec jekyll serve --livereload`。

### 导航跳转不正确

检查 _data/navigation.yml 中的 url 是否与 index.md 的 section id 一一对应，例如 #patents 对应 id="patents"。

## 9. 文件管理规则

图片放在 assets/img/，简历和可下载文件放在 assets/files/。不要提交 _site、.jekyll-cache、__pycache__、临时截图或本地预览生成物。docs/ 用于维护文档，不参与网站页面展示。
