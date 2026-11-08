<h2 class="pub-section-title"><span class="i18n-zh">论文</span><span class="i18n-en">Publications</span>{% if site.google_scholar %} <span class="pub-ext-links"><a href="{{ site.google_scholar }}" target="_blank" rel="noopener">Google Scholar</a></span>{% endif %}</h2>
<p class="section-note"><span class="i18n-zh">论文数据由 OpenAlex 定期同步，完整列表持续更新。</span><span class="i18n-en">Publication data is synced regularly from OpenAlex. The full list is updated on an ongoing basis.</span></p>

<div class="publications">
{% assign publications_by_year = site.data.publications.main | group_by: "year" | sort: "name" | reverse %}
{% for year_group in publications_by_year %}
  <h2 class="year">{{ year_group.name }}</h2>
  <ol class="bibliography">
  {% for link in year_group.items %}
    {% include publication-item.html link=link %}
  {% endfor %}
  </ol>
{% endfor %}
</div>
