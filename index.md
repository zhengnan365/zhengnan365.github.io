---
layout: homepage
---

<div class="hero-intro" id="about">
  <p class="eyebrow"><span class="i18n-zh">低碳能源系统 · 综合能源 · 智能调控</span><span class="i18n-en">LOW-CARBON ENERGY SYSTEMS · INTEGRATED ENERGY · INTELLIGENT CONTROL</span></p>
  <h2><span class="i18n-zh">个人简介</span><span class="i18n-en">Profile</span></h2>
  <div class="i18n-zh">
    <p>郑楠，男，工学博士，讲师，硕士生导师，现任扬州大学电气与能源动力工程学院教师。2024 年 6 月毕业于华北电力大学动力工程及工程热物理专业（硕博连读），2023 年 8 月至 2024 年 8 月在意大利比萨大学联合培养。</p>
    <p>主要从事多能互补综合能源系统设计与集成、低碳能源系统优化运行与智能调控研究，围绕风光地热、氢氨醇、冷热电和多元储能协同，开展燃料电池、ORC、sCO₂ 循环、电解槽等能源转换单元建模、系统集成设计、协同运行及多目标优化研究。主持或参与多项国家级和省部级科研项目，已发表学术论文 50 余篇，其中以第一作者或通讯作者发表 SCI、EI 等论文 20 余篇，申请或授权专利 12 项。</p>
  </div>
  <div class="i18n-en">
    <p>Nan Zheng is a lecturer and master's supervisor at the College of Electrical, Energy and Power Engineering, Yangzhou University. He received his Ph.D. in Power Engineering and Engineering Thermophysics from North China Electric Power University in June 2024 and completed joint doctoral training at the University of Pisa from August 2023 to August 2024.</p>
    <p>His research focuses on integrated multi-energy system design and low-carbon energy system optimization and intelligent control. His work covers the coordination of wind, solar, geothermal, hydrogen, ammonia, methanol, cooling, heating, power, and multi-type energy storage, including modeling of fuel cells, ORC, supercritical CO₂ cycles, and electrolyzers, system integration, coordinated operation, and multi-objective optimization. He has led or participated in national and provincial research projects, published more than 50 academic papers including over 20 SCI/EI papers as first or corresponding author, and applied for or been granted 12 patents.</p>
  </div>
</div>

<section id="research">
  <h2><span class="i18n-zh">研究方向</span><span class="i18n-en">Research Interests</span></h2>
  <div class="topic-grid">
    <article class="topic-card">
      <span class="topic-number">01</span>
      <h3><span class="i18n-zh">多能互补综合能源系统</span><span class="i18n-en">Integrated Multi-Energy Systems</span></h3>
      <p class="i18n-zh">围绕风光地热、氢氨醇、冷热电和多元储能协同，开展系统建模、集成设计与协同运行策略研究</p>
      <p class="i18n-en">System modeling, integrated design, and coordinated operation of wind, solar, and geothermal energy; hydrogen, ammonia, and methanol; combined cooling, heating, and power; and energy storage</p>
    </article>
    <article class="topic-card">
      <span class="topic-number">02</span>
      <h3><span class="i18n-zh">低碳能源系统优化运行与智能调控</span><span class="i18n-en">Low-Carbon Optimization and Intelligent Control</span></h3>
      <p class="i18n-zh">针对可再生能源出力波动及复杂运行条件，开展多目标优化、不确定性分析、随机与鲁棒优化以及智能调控研究</p>
      <p class="i18n-en">Multi-objective optimization, uncertainty analysis, stochastic and robust optimization, and intelligent control for fluctuating renewable energy and complex operating conditions</p>
    </article>
  </div>
</section>

<section id="projects">
  <h2><span class="i18n-zh">项目承担</span><span class="i18n-en">Projects</span></h2>
  <div class="timeline-list">{% for item in site.data.projects %}
    <article class="timeline-item">
      <h3><span class="i18n-zh">{{ item.title_zh }}</span><span class="i18n-en">{{ item.title_en }}</span></h3>
      <p><span class="i18n-zh">· {{ item.amount_zh }} · {{ item.role_zh }}</span><span class="i18n-en">· {{ item.amount_en }} · {{ item.role_en }}</span></p>
    </article>
  {% endfor %}</div>
</section>

<section id="publications" class="publication-section">{% include publications.md %}</section>

<section id="patents" class="patent-section-divider">
  <h2><span class="i18n-zh">专利</span><span class="i18n-en">Patents</span><small class="pub-total"><span class="i18n-zh">（共{{ site.data.patents.size }}项）</span><span class="i18n-en">({{ site.data.patents.size }} total)</span></small></h2>
  {% assign sorted_patents = site.data.patents | sort: "display_date" | reverse %}
  <div class="patent-list compact-list">{% for item in sorted_patents %}
    <article class="patent-item">
      <h3 class="title"><span class="i18n-zh">{{ item.title_zh }}</span><span class="i18n-en">{{ item.title_en }}</span></h3>
      <div class="publication-badges"><span class="pub-badge"><span class="i18n-zh">{{ item.patent_type_zh }}</span><span class="i18n-en">{{ item.patent_type_en }}</span></span><span class="pub-badge"><span class="i18n-zh">{{ item.status_zh }}</span><span class="i18n-en">{{ item.status_en }}</span></span><span class="pub-badge"><span class="i18n-zh">{{ item.display_number_label_zh }} {{ item.display_number }}</span><span class="i18n-en">{{ item.display_number_label_en }} {{ item.display_number }}</span></span></div>
      <p class="author patent-inventors"><span class="i18n-zh">发明人：{% for inventor in item.inventors %}{% unless forloop.first %}、{% endunless %}{% if inventor == "郑楠" %}<strong>{{ inventor }}</strong>{% else %}{{ inventor }}{% endif %}{% endfor %}</span><span class="i18n-en">Inventors: {% for inventor in item.inventors %}{% unless forloop.first %}, {% endunless %}{% if inventor == "郑楠" %}<strong>Nan Zheng</strong>{% else %}{{ inventor }}{% endif %}{% endfor %}</span></p>
      <p class="patent-key-meta"><span class="i18n-zh">{{ item.display_date_label_zh }}：{{ item.display_date }}</span><span class="i18n-en">{{ item.display_date_label_en }}: {{ item.display_date }}</span></p>
    </article>
  {% endfor %}</div>
</section>

<section id="awards" class="section-divider">
  <h2><span class="i18n-zh">奖励荣誉</span><span class="i18n-en">Awards</span></h2>
  <ul class="award-list">{% for item in site.data.awards %}
    <li><span>{{ item.year }}</span><div class="i18n-zh" style="display:inline">{{ item.title_zh }}</div><div class="i18n-en" style="display:inline">{{ item.title_en }}</div></li>
  {% endfor %}</ul>
</section>

<section id="teaching">
  <h2><span class="i18n-zh">教学</span><span class="i18n-en">Teaching</span></h2>
  <div class="teaching-semester">
    <h3><span class="i18n-zh">第五学期</span><span class="i18n-en">Semester 5</span></h3>
    <ul>
      <li><span class="i18n-zh">计算机辅助设计</span><span class="i18n-en">Computer-Aided Design</span></li>
      <li><span class="i18n-zh">综合能源高效利用技术</span><span class="i18n-en">Efficient Utilization of Integrated Energy</span></li>
    </ul>
  </div>
  <div class="teaching-semester">
    <h3><span class="i18n-zh">第六学期</span><span class="i18n-en">Semester 6</span></h3>
    <ul>
      <li><span class="i18n-zh">光伏系统设计</span><span class="i18n-en">Photovoltaic System Design</span></li>
      <li><span class="i18n-zh">能源互联网技术与应用-人工智能+</span><span class="i18n-en">Energy Internet Technology and Applications: AI+</span></li>
      <li><span class="i18n-zh">新能源综合项目创新实践</span><span class="i18n-en">Innovative Practice in Integrated New Energy Projects</span></li>
    </ul>
  </div>
</section>

<section id="students">
  <h2><span class="i18n-zh">指导学生</span><span class="i18n-en">Students</span></h2>
  <div class="student-subsection">
    <h3><span class="i18n-zh">竞赛</span><span class="i18n-en">Competitions</span></h3>
    <ul class="award-list student-award-list">
      <li><span>2026</span><span class="i18n-zh">江苏省大学生节能减排社会实践与科技竞赛特等奖</span><span class="i18n-en">Grand Prize, Jiangsu College Students Energy Conservation and Emission Reduction Competition</span></li>
      <li><span>2026</span><span class="i18n-zh">江苏省大学生节能减排社会实践与科技竞赛一等奖</span><span class="i18n-en">First Prize, Jiangsu College Students Energy Conservation and Emission Reduction Competition</span></li>
      <li><span>2026</span><span class="i18n-zh">全国大学生节能减排社会实践与科技竞赛三等奖</span><span class="i18n-en">Third Prize, National College Students Energy Conservation and Emission Reduction Competition</span></li>
      <li><span>2026</span><span class="i18n-zh">全国大学生节能减排社会实践与科技竞赛三等奖</span><span class="i18n-en">Third Prize, National College Students Energy Conservation and Emission Reduction Competition</span></li>
      <li><span>2025</span><span class="i18n-zh">中国研究生能源装备创新设计大赛三等奖</span><span class="i18n-en">Third Prize, China Graduate Energy Equipment Innovation Design Competition</span></li>
      <li><span>2025</span><span class="i18n-zh">国家级大学生创新训练计划（国家级大创）并结项</span><span class="i18n-en">Completion of the National College Students Innovation and Entrepreneurship Training Program (National Innovation Training Program)</span></li>
    </ul>
  </div>
  <div class="student-subsection">
    <h3><span class="i18n-zh">学生</span><span class="i18n-en">Students</span></h3>
    <div class="student-group">
      <h4><span class="i18n-zh">研究生</span><span class="i18n-en">Graduate Students</span></h4>
      <p class="i18n-zh">欢迎新能源科学与工程、能源与动力工程及相关学科的硕士研究生加入课题组，围绕综合能源系统、储能系统和低碳能源技术开展科研</p>
      <p class="i18n-en">Master's students in New Energy Science and Engineering, Energy and Power Engineering, and related fields are welcome to join the group and work on integrated energy systems, energy storage, and low-carbon energy technologies</p>
    </div>
    <div class="student-group">
      <h4><span class="i18n-zh">本科生</span><span class="i18n-en">Undergraduate Students</span></h4>
      <div class="student-grade">
        <h5><span class="i18n-zh">2023 级</span><span class="i18n-en">Class of 2023</span></h5>
        <ul class="student-profile-list">
          <li class="student-profile"><strong><span class="i18n-zh">英笑</span><span class="i18n-en">Ying Xiao</span></strong><span class="i18n-zh">保研至河海大学</span><span class="i18n-en">Recommended for postgraduate study at Hohai University</span></li>
          <li class="student-profile"><strong><span class="i18n-zh">庄宇跃</span><span class="i18n-en">Zhuang Yuyue</span></strong><span class="i18n-zh">保研至中国科学院大学工程热物理研究所</span><span class="i18n-en">Recommended for postgraduate study at the Institute of Engineering Thermophysics, University of Chinese Academy of Sciences</span></li>
        </ul>
      </div>
      <div class="student-grade">
        <h5><span class="i18n-zh">2024 级</span><span class="i18n-en">Class of 2024</span></h5>
      </div>
      <div class="student-grade">
        <h5><span class="i18n-zh">2025 级</span><span class="i18n-en">Class of 2025</span></h5>
      </div>
    </div>
  </div>
</section>

<section id="opensource">
  <h2><span class="i18n-zh">开源软件</span><span class="i18n-en">Open Source</span></h2>
  <ul class="software-list">{% for item in site.data.opensource %}
    <li><a href="{{ item.url }}" target="_blank" rel="noopener"><i class="fab fa-github" aria-hidden="true"></i> {{ item.name }}</a><span class="i18n-zh">{{ item.description_zh }}</span><span class="i18n-en">{{ item.description_en }}</span></li>
  {% endfor %}</ul>
</section>

<section id="contact" class="contact-block">
  <h2><span class="i18n-zh">联系方式</span><span class="i18n-en">Contact</span></h2>
  <div class="contact-row"><i class="fa-solid fa-envelope" aria-hidden="true"></i><p><strong><span class="i18n-zh">邮箱：</span><span class="i18n-en">Email:</span></strong> <a href="mailto:{{ site.email }}">{{ site.email }}</a></p></div>
  <div class="contact-row"><i class="fa-solid fa-location-dot" aria-hidden="true"></i><p><strong><span class="i18n-zh">地址：</span><span class="i18n-en">Address:</span></strong> <span class="i18n-zh">中国江苏省扬州市邗江区华扬西路196号，扬州大学扬子津校区</span><span class="i18n-en">Yangzijin Campus, Yangzhou University, 196 Huayang West Road, Hanjiang District, Yangzhou, Jiangsu, China</span></p></div>
  <div class="contact-row"><i class="fa-solid fa-building" aria-hidden="true"></i><p><strong><span class="i18n-zh">办公室：</span><span class="i18n-en">Office:</span></strong> <span class="i18n-zh">知行楼 S529</span><span class="i18n-en">Room S529, Zhixing Building</span></p></div>
</section>
