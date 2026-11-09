{% assign publications_by_year = site.data.publications.main | group_by: "year" | sort: "name" | reverse %}
{% assign newest_year = publications_by_year.first.name | plus: 0 %}
{% assign recent_cutoff = newest_year | minus: 2 %}
{% assign oldest_year = publications_by_year.last.name | plus: 0 %}
<h2 class="pub-section-title"><span class="i18n-zh">论文</span><span class="i18n-en">Publications</span><small class="pub-total"><span class="i18n-zh">（共{{ site.data.publications.main.size }}篇）</span><span class="i18n-en">({{ site.data.publications.main.size }} total)</span></small></h2>
<div class="publications">
{% for year_group in publications_by_year %}
  {% assign group_year = year_group.name | plus: 0 %}
  {% if group_year >= recent_cutoff %}
    <h3 class="year">{{ year_group.name }}</h3>
    <ol class="bibliography">{% for link in year_group.items %}{% include publication-item.html link=link %}{% endfor %}</ol>
  {% endif %}
{% endfor %}
{% if oldest_year < recent_cutoff %}
<details class="older-publications">
  <summary><span class="i18n-zh">更多</span><span class="i18n-en">More</span></summary>
  {% for year_group in publications_by_year %}
    {% assign group_year = year_group.name | plus: 0 %}
    {% if group_year < recent_cutoff %}
      <h3 class="year">{{ year_group.name }}</h3>
      <ol class="bibliography">{% for link in year_group.items %}{% include publication-item.html link=link %}{% endfor %}</ol>
    {% endif %}
  {% endfor %}
</details>
{% endif %}
</div>
<p class="section-note publication-source"><span class="i18n-zh">论文数据由 <a href="https://openalex.org/A5001145059" target="_blank" rel="noopener">OpenAlex</a> 定期同步。</span><span class="i18n-en">Publication data is synced regularly from <a href="https://openalex.org/A5001145059" target="_blank" rel="noopener">OpenAlex</a>.</span></p>
