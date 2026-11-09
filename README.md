# Nan Zheng academic homepage

这是郑楠的个人学术主页，使用 Jekyll + GitHub Pages 构建，支持中英文切换、浅色/深色模式、响应式布局、论文自动同步、项目/专利/奖励/教学/开源软件和联系方式展示。

## 在线地址

- <https://zhengnan365.github.io/>
- 自定义域名由根目录的 `CNAME` 管理。

## 目录说明

```text
_config.yml                 站点信息与 Jekyll 配置
index.md                    首页内容与各个 section
_layouts/                   页面布局
_includes/                  可复用模板
_data/                      YAML 数据源
assets/css/                 样式
assets/js/                  交互脚本
assets/img/                 图片与图标
assets/files/               可下载文件
scripts/                    OpenAlex 论文同步脚本
tests/                      Python 与 Node.js 测试
.github/workflows/          Pages 部署和论文同步工作流
docs/TECHNICAL.md           技术说明与维护手册
```

## GitHub Pages 发布

进入 **Settings → Pages → Build and deployment**，将来源设置为 **GitHub Actions**。推送到 `main` 后，`pages.yml` 会构建并部署首页；自定义域名保持在仓库根目录的 `CNAME` 中。仓库只维护 Jekyll 源码，不提交 `_site` 构建结果。

## 本地预览

安装 Ruby、Bundler 和 Python 3.12+ 后运行：

```bash
bundle install
bundle exec jekyll serve --livereload
```

浏览 <http://localhost:4000/>。测试依赖安装与执行：

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -p "test_*.py" -v
node --test tests/site-controls.test.mjs
```

## 手动更新信息

日常更新只需编辑对应文件，保存后提交并推送：

| 内容 | 文件 |
| --- | --- |
| 姓名、职称、单位、邮箱、个人链接、头像 | `_config.yml` |
| 简介、研究方向、教学、学生、联系方式 | `index.md` |
| 项目 / 专利 / 奖励 / 新闻 / 开源软件 | `_data/projects.yml`、`_data/patents.yml`、`_data/awards.yml`、`_data/news.yml`、`_data/opensource.yml` |
| 导航名称和顺序 | `_data/navigation.yml` |
| 论文人工修正 | `_data/overrides.yml` |
| 期刊指标 | `_data/journal_metrics.yml` |
| 简历文件 | `assets/files/`，并更新 `_config.yml` 的 `cv_link` |

论文数据不要直接手改 `_data/publications.yml` 或 `assets/data/site-data.json`。运行 `python scripts/sync_publications.py` 或在 Actions 中手动运行 **Sync publications**；需要排除论文或修正标题、作者、链接时，在 `_data/overrides.yml` 中按 DOI 或 OpenAlex ID 添加覆盖项。

## 提交前检查

```bash
python -m unittest discover -s tests -p "test_*.py" -v
node --test tests/site-controls.test.mjs
bundle exec jekyll build
```

推送到 `main` 后，在 **Actions** 页面确认 Pages 工作流成功，再检查网站移动端、中英文切换和新数据。

## 许可证

源码沿用 CC0 1.0 Universal。个人资料、简历和学术数据请按其原始来源与授权使用。
