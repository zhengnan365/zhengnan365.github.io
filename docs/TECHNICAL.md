# 技术说明

## 架构

这是一个单页 Jekyll 站点。`index.md` 使用 `homepage` 布局，布局负责 HTML 外壳、图标字体、全局样式和脚本；页面内容通过 Liquid 从 `_data` 目录读取。论文模板将论文按年份分组，并提供可复制的 GB/T 7714 引用。

主题源码已在仓库内维护：`_sass/minimal-light-no-dark-mode.scss` 提供基础 Sass，`assets/css/style.scss` 负责导入，`site-overrides.css`、`nav.css` 和 `pub.css` 负责本站定制样式。构建不依赖远程主题，减少 Pages 构建时的外部依赖。

## GitHub Pages 构建链

`.github/workflows/pages.yml` 在 `main` 推送或手动触发时检出源码、配置 Pages、使用 `actions/jekyll-build-pages` 构建到 `_site`、上传 artifact，再由 `actions/deploy-pages` 发布。仓库 Settings 中必须选择 GitHub Actions 作为 Pages 来源。

`Gemfile` 使用 `github-pages` 依赖集合，方便本地 Bundler 环境与 GitHub Pages 兼容。`_config.yml` 的 `exclude` 排除了测试、脚本、文档和开发依赖；这些文件保留在源码仓库，但不会出现在生成站点中。

## 数据流

论文同步脚本从 OpenAlex 作者 ID `A5001145059` 分页获取作品，标准化 DOI、作者、期刊、年份、页码和引用次数，再合并 `_data/overrides.yml` 与 `_data/journal_metrics.yml`。脚本会校验数据、去重、排序，并以原子方式同时写入 `_data/publications.yml` 和 `assets/data/site-data.json`，避免只更新一份文件。

同步工作流每周一运行，也可以在 GitHub Actions 中选择 **Run workflow**。只有生成数据发生变化时才会提交；随后 Pages 构建使用最新的 `main` 分支。

## 内容维护规则

- YAML 文件使用 UTF-8 和合法 YAML，日期统一使用 `YYYY-MM-DD` 或项目现有格式。
- 双语字段以 `_zh` 和 `_en` 结尾；新增项目、专利和奖励时应同时填写两种语言。
- 论文生成文件由脚本管理，人工调整放入 `overrides.yml`，期刊指标放入 `journal_metrics.yml`。
- 图片放在 `assets/img/`，下载文件放在 `assets/files/`。
- 不要提交 `_site`、`.jekyll-cache`、`__pycache__` 或临时构建文件。

## 故障排查

1. 本地构建失败时先运行 `bundle install`，再执行 `bundle exec jekyll build --trace`。
2. Pages 失败时查看 workflow build 日志，重点检查 Liquid 语法、YAML 格式和资源路径。
3. 论文同步失败时不要删除现有生成文件。脚本在获取数据、校验分页或写入失败时会保留旧数据；修正网络、覆盖项或指标文件后重新运行。
4. 域名异常时检查根目录 `CNAME`、DNS 记录以及 Settings → Pages 中的自定义域名状态。
