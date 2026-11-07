---
layout: homepage
---

<div class="hero-intro" id="about">
  <p class="eyebrow">LOW-CARBON ENERGY SYSTEMS · INTEGRATED ENERGY · INTELLIGENT CONTROL</p>
  <h2>About Me</h2>
  <p>郑楠，工学博士，讲师，硕士生导师，现任职于扬州大学电气与能源动力工程学院。2024 年毕业于华北电力大学动力工程及工程热物理专业（硕博连读），曾于比萨大学联合培养。</p>
  <p>我的研究围绕低碳能源系统的设计、运行与控制展开，重点关注多能互补综合能源系统、可再生能源与多元储能协同，以及复杂运行环境下的低碳优化和智能调控。</p>
</div>

<section id="research">
  <h2>Research Interests</h2>
  <div class="topic-grid">
    <article class="topic-card"><span class="topic-number">01</span><h3>多能互补综合能源系统</h3><p>围绕风光地热、氢氨醇、冷热电和多元储能协同，开展系统建模、集成设计与协同运行策略研究。</p></article>
    <article class="topic-card"><span class="topic-number">02</span><h3>低碳能源系统优化运行与智能调控</h3><p>面向可再生能源波动和复杂运行环境，研究多目标优化、不确定性分析、随机优化、鲁棒优化与智能调控。</p></article>
  </div>
</section>

<section id="publications"><h2>Publications</h2><p class="section-note">论文数据由 OpenAlex 定期同步，完整列表持续更新。</p>{% include publications.md %}</section>

<section id="patents"><h2>Patents</h2><ol class="compact-list">{% for item in site.data.patents %}<li>{{ item.text }}</li>{% endfor %}</ol></section>

<section id="projects"><h2>Projects</h2><div class="timeline-list">{% for item in site.data.projects %}<article class="timeline-item"><div class="timeline-year">{{ item.period }}</div><div><h3>{{ item.title }}</h3><p>{{ item.role }} · {{ item.amount }}</p></div></article>{% endfor %}</div></section>

<section id="students"><h2>Students</h2><p>欢迎新能源科学与工程、能源与动力工程及相关学科学生保研、考研，欢迎各年级本科生参与竞赛与科研。欢迎对综合能源系统、储能系统和低碳能源技术感兴趣的同学联系我。</p></section>

<section id="awards"><h2>Awards</h2><ul class="award-list">{% for item in site.data.awards %}<li><span>{{ item.year }}</span>{{ item.title }}</li>{% endfor %}</ul></section>

<section id="news"><h2>News</h2><ul class="news-list">{% for item in site.data.news %}<li><span>{{ item.date }}</span>{{ item.text }}</li>{% endfor %}</ul></section>

<section id="contact" class="contact-block"><h2>Contact</h2><p><strong>Email:</strong> <a href="mailto:{{ site.email }}">{{ site.email }}</a></p><p><strong>CV:</strong> <a href="{{ site.cv_link }}">Download curriculum vitae</a></p></section>
