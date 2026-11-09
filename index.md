---
layout: homepage
---

{% comment %}Sections and navigation are controlled by _data/navigation.yml.{% endcomment %}
{% for item in site.data.navigation.main %}
{% if item.enabled != false %}
{% case item.template %}
{% when "about" %}{% include sections/about.html %}
{% when "research" %}{% include sections/research.html %}
{% when "projects" %}{% include sections/projects.html %}
{% when "publications" %}{% include sections/publications.html %}
{% when "patents" %}{% include sections/patents.html %}
{% when "awards" %}{% include sections/awards.html %}
{% when "teaching" %}{% include sections/teaching.html %}
{% when "students" %}{% include sections/students.html %}
{% when "news" %}{% include sections/news.html %}
{% when "opensource" %}{% include sections/opensource.html %}
{% when "contact" %}{% include sections/contact.html %}
{% endcase %}
{% endif %}
{% endfor %}
