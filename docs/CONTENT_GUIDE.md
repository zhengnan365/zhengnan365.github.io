# 栏目内容填写指南

日常只改 `_data` 中的 `.yml` 文件。Jekyll 读取这些结构化数据，由 `_includes/sections/` 的模板排版。`index.md` 只调用已启用的栏目，不保存栏目正文。不要把数据文件改名为 `.md`，否则 Jekyll 不会将其加载到 `site.data`。

## 栏目开关和顺序

在 `_data/navigation.yml` 找到已有栏目，修改 `enabled`：

```yaml
- key: news
  template: news
  enabled: true
  title_zh: 新闻动态
  title_en: News
  url: "#news"
```

`true` 同时显示正文与导航；`false` 同时隐藏，两者都不加引号。关闭时保留数据文件，之后可随时恢复。将整个条目移动到列表的其他位置即可调整正文与导航顺序。`key`、`template` 和 `url` 是模板关联字段，更新文字时保持原值。`title_zh/title_en` 控制导航名称，栏目正文标题目前由相应模板定义。

## 通用填写规则

使用 UTF-8，空格缩进，不使用 Tab。`-` 表示新记录，复制完整记录后再改文字。日期写成带引号的字符串，例如 `'2026-11-09'`。带英文冒号和空格的文字应加引号。下面的示例仅供复制，不会自动添加到网站。

### 个人简介：profile.yml

在 `paragraphs` 下按段添加：

```yaml
paragraphs:
  - text_zh: >-
      这里填写中文简介。
      这些换行会合并为同一段文字。
    text_en: >-
      Write the English profile here.
```

### 研究方向：research.yml

```yaml
- title_zh: 研究方向名称
  title_en: Research topic
  description_zh: 研究内容介绍
  description_en: Research description
```

### 项目：projects.yml

```yaml
- period: 2026.01–2028.12
  title_zh: 项目名称
  title_en: Project title
  role_zh: 主持
  role_en: Principal investigator
  amount_zh: 30 万元
  amount_en: CNY 300,000
```

目前正文展示项目名称、金额和角色；`period` 保留为项目元数据。

### 专利：patents.yml

新增已受理记录可复制以下模板，并替换示例编号与内容：

```yaml
- title_zh: 发明名称
  title_en: Invention title
  application_number: CN202610000000.0
  application_date: '2026-11-09'
  inventors:
    - 郑楠
    - 其他发明人
  patent_type_zh: 发明专利
  patent_type_en: Invention patent
  status_key: accepted
  status_zh: 已受理
  status_en: Application accepted
  display_number_label_zh: 申请号
  display_number_label_en: Application no.
  display_number: CN202610000000.0
  display_date_label_zh: 申请日
  display_date_label_en: Filed
  display_date: '2026-11-09'
```

按通知书保留发明人顺序；页面会突出郑楠。后续状态变化时同步修改以下字段：

| 阶段 | 状态字段 | 编号和日期 |
| --- | --- | --- |
| 受理 | `accepted` / 已受理 / Application accepted | 申请号、申请日 |
| 公开 | `published` / 已公开 / Published | 增加 `publication_number`、`publication_date`，显示标签改为公开号/Publication no.、公开日/Published |
| 授权 | `granted` / 已授权 / Granted | 增加 `grant_number`、`grant_date`，显示标签改为授权公告号/Grant no.、授权日/Granted |

`display_number` 和 `display_date` 分别填写该阶段对应的真实编号和日期。页面自动按显示日期倒序排列，前五条以外的记录进入“更多”。可添加 `source_url` 保存来源，`verification` 和 `verified_on` 保存核对方式与日期。

### 奖励：awards.yml

```yaml
- year: 2026
  title_zh: 奖励名称
  title_en: Award title
```

### 新闻：news.yml

```yaml
- date: '2026-11-09'
  text_zh: 新闻内容
  text_en: News text
```

新闻默认隐藏。内容填写后，再把 `navigation.yml` 中 `news` 的 `enabled` 改为 `true`。奖励、新闻、项目与软件按数据文件顺序显示，建议新记录放在前面。

### 教学：teaching.yml

```yaml
semesters:
  - name_zh: 第五学期
    name_en: Semester 5
    courses:
      - name_zh: 课程名称
        name_en: Course title
```

### 人才培养：students.yml

`competition_awards` 维护竞赛获奖，`students` 按学生维护培养成果。`count` 大于 1 时，页面自动显示“×数量”：

```yaml
competition_awards:
  - year: 2026
    title_zh: 竞赛奖项
    title_en: Competition award

students:
  - grade_zh: 2026级
    grade_en: Class of 2026
    level_zh: 本科生
    level_en: Undergraduate
    name_zh: 学生姓名
    name_en: Student name
    achievements:
      - text_zh: 培养成果
        text_en: Student achievement
      - text_zh: 同类成果
        text_en: Repeated achievement
        count: 2
```

新增学生时复制一个完整的 `students` 条目；新增成果时在该学生的 `achievements` 下追加一项。

### 开源软件：opensource.yml

```yaml
- name: 软件名称
  url: https://github.com/用户名/项目名
  description_zh: 软件介绍
  description_en: Software description
```

### 联系方式：contact.yml

```yaml
address_zh: 中文地址
address_en: English address
office_zh: 中文办公室
office_en: English office
```

邮箱、姓名、职称、单位及个人链接仍在 `_config.yml` 中统一维护，侧栏和联系方式会共用邮箱。

### 论文：overrides.yml 与 journal_metrics.yml

`publications.yml` 是自动生成文件，不直接手改。更正已有论文时在 `overrides.yml` 按小写 DOI（不含 `https://doi.org/`）填写，例如：

```yaml
"10.1234/example":
  title: Corrected paper title
  exclude: false
```

`exclude: true` 可排除误收的论文；覆盖项只作用于 OpenAlex 已收录的作品。保存后运行 `python scripts/sync_publications.py`，或者等待/手动触发 Sync publications 工作流，才会写入页面读取的生成文件。期刊指标按 ISSN 在 `journal_metrics.yml` 中维护，也需重新同步。

## 更新后生效

本地 Jekyll 预览：保存后等待重新构建；改 `_config.yml` 后重启预览服务。线上：保存、提交、推送到 `main`，等待 Actions 中 Pages 工作流成功。独立的静态预览副本需要重新生成，不会自动读取源目录的数据变化。
