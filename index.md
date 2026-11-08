---
layout: homepage
---

<div class="hero-intro" id="about">
  <p class="eyebrow"><span class="i18n-zh">低碳能源系统 · 综合能源 · 智能调控</span><span class="i18n-en">LOW-CARBON ENERGY SYSTEMS · INTEGRATED ENERGY · INTELLIGENT CONTROL</span></p>
  <h2><span class="i18n-zh">个人经历</span><span class="i18n-en">About Me</span></h2>
  <div class="i18n-zh">
    <p>郑楠，工学博士，讲师，硕士生导师，现任职于扬州大学电气与能源动力工程学院。2024 年毕业于华北电力大学动力工程及工程热物理专业（硕博连读），曾于比萨大学联合培养。</p>
    <p>我的研究围绕低碳能源系统的设计、运行与控制展开，重点关注多能互补综合能源系统、可再生能源与多元储能协同，以及复杂运行环境下的低碳优化和智能调控。</p>
  </div>
  <div class="i18n-en">
    <p>Nan Zheng is a lecturer and master's supervisor at the College of Electrical, Energy and Power Engineering, Yangzhou University. He received his Ph.D. in Power Engineering and Engineering Thermophysics from North China Electric Power University in 2024 and completed joint doctoral training at the University of Pisa.</p>
    <p>His research focuses on the design, operation, and control of low-carbon energy systems, including integrated systems that combine multiple energy sources, renewable energy and storage coordination, and intelligent optimization under complex operating conditions.</p>
  </div>
</div>

<section id="research">
  <h2><span class="i18n-zh">研究方向</span><span class="i18n-en">Research Interests</span></h2>
  <div class="topic-grid">
    <article class="topic-card">
      <span class="topic-number">01</span>
      <h3><span class="i18n-zh">多能互补综合能源系统</span><span class="i18n-en">Integrated Multi-Energy Systems</span></h3>
      <p class="i18n-zh">围绕风光地热、氢氨醇、冷热电和多元储能协同，开展系统建模、集成设计与协同运行策略研究。</p>
      <p class="i18n-en">System modeling, integrated design, and coordinated operation of wind, solar, and geothermal energy; hydrogen, ammonia, and methanol; combined cooling, heating, and power; and energy storage.</p>
    </article>
    <article class="topic-card">
      <span class="topic-number">02</span>
      <h3><span class="i18n-zh">低碳能源系统优化运行与智能调控</span><span class="i18n-en">Low-Carbon Optimization and Intelligent Control</span></h3>
      <p class="i18n-zh">面向可再生能源波动和复杂运行环境，研究多目标优化、不确定性分析、随机优化、鲁棒优化与智能调控。</p>
      <p class="i18n-en">Multi-objective optimization, uncertainty analysis, stochastic and robust optimization, and intelligent control for fluctuating renewable energy and complex operating conditions.</p>
    </article>
  </div>
</section>

<section id="publications" class="publication-section">{% include publications.md %}</section>

<section id="patents">
  <h2><span class="i18n-zh">专利</span><span class="i18n-en">Patents</span></h2>
  <ol class="compact-list">{% for item in site.data.patents %}
    <li><span class="i18n-zh">{{ item.text_zh }}</span><span class="i18n-en">{{ item.text_en }}</span></li>
  {% endfor %}</ol>
</section>

<section id="projects">
  <h2><span class="i18n-zh">科研项目</span><span class="i18n-en">Projects</span></h2>
  <div class="timeline-list">{% for item in site.data.projects %}
    <article class="timeline-item">
      <div class="timeline-year">{{ item.period }}</div>
      <div>
        <h3><span class="i18n-zh">{{ item.title_zh }}</span><span class="i18n-en">{{ item.title_en }}</span></h3>
        <p><span class="i18n-zh">{{ item.role_zh }} · {{ item.amount_zh }}</span><span class="i18n-en">{{ item.role_en }} · {{ item.amount_en }}</span></p>
      </div>
    </article>
  {% endfor %}</div>
</section>

<section id="students">
  <h2><span class="i18n-zh">学生培养</span><span class="i18n-en">Students</span></h2>
  <p class="i18n-zh">欢迎新能源科学与工程、能源与动力工程及相关学科学生保研、考研，欢迎各年级本科生参与竞赛与科研。欢迎对综合能源系统、储能系统和低碳能源技术感兴趣的同学联系我。</p>
  <p class="i18n-en">Prospective graduate students in New Energy Science and Engineering, Energy and Power Engineering, and related fields are welcome to get in touch. Undergraduates at any stage are also welcome to join research projects and competitions, especially those interested in integrated energy systems, energy storage, and low-carbon energy technologies.</p>
</section>

<section id="awards">
  <h2><span class="i18n-zh">奖励荣誉</span><span class="i18n-en">Awards</span></h2>
  <ul class="award-list">{% for item in site.data.awards %}
    <li><span>{{ item.year }}</span><div class="i18n-zh" style="display:inline">{{ item.title_zh }}</div><div class="i18n-en" style="display:inline">{{ item.title_en }}</div></li>
  {% endfor %}</ul>
</section>

<section id="news">
  <h2><span class="i18n-zh">最新动态</span><span class="i18n-en">News</span></h2>
  <ul class="news-list">{% for item in site.data.news %}
    <li><span>{{ item.date }}</span><div class="i18n-zh" style="display:inline">{{ item.text_zh }}</div><div class="i18n-en" style="display:inline">{{ item.text_en }}</div></li>
  {% endfor %}</ul>
</section>

<section id="contact" class="contact-block">
  <h2><span class="i18n-zh">联系方式</span><span class="i18n-en">Contact</span></h2>
  <p><strong><span class="i18n-zh">邮箱：</span><span class="i18n-en">Email:</span></strong> <a href="mailto:{{ site.email }}">{{ site.email }}</a></p>
  <p><strong><span class="i18n-zh">简历：</span><span class="i18n-en">CV:</span></strong> <a href="{{ site.cv_link }}"><span class="i18n-zh">下载个人简历</span><span class="i18n-en">Download curriculum vitae</span></a></p>
</section>
