<div class="publications"><ol class="bibliography">
{% for link in site.data.publications.main %}
{% if forloop.index == 9 %}<details class="older-publications"><summary>Show older publications</summary>{% endif %}
<li><div class="pub-row"><div class="pub-year">{{ link.year }}</div><div class="pub-content"><div class="title"><a href="{{ link.url }}" target="_blank" rel="noopener">{{ link.title }}</a></div><div class="author">{{ link.authors }}</div><div class="periodical"><em>{{ link.venue }}{% if link.year %}, {{ link.year }}{% endif %}</em></div><div class="links">{% if link.pdf %}<a href="{{ link.pdf }}" target="_blank" rel="noopener">PDF</a>{% endif %}{% if link.doi %}<a href="{{ link.doi }}" target="_blank" rel="noopener">DOI</a>{% endif %}{% if link.open_access %}<span class="oa-label">Open access</span>{% endif %}</div></div></div></li>
{% endfor %}
{% if site.data.publications.main.size > 8 %}</details>{% endif %}
</ol></div>
