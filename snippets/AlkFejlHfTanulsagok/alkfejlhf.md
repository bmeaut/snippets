---
layout: default
permalink: /alkfejl.html
codename: alkFejlHfTanulsagok
title: Alkalmazásfejlesztés házi feladatok tanulságai (hallgatók)
tags: alkfejl
authors: Csorba Kristóf
---

<div class="home">
  <h1 class="page-heading">Az alkalmazásfejlesztés házi feladatok tanulságai</h1>
  (Az alábbi leírásokat mind hallgatói csapatok készítették.)

{% for tag in allTagsArray %}
  <h2 id="{{tag}}">{{tag}}</h2><br/>
  <ul>
  {% for page in site.pages %}
    {% if page.tags contains tag and page.tags contains 'afhf' %}
    <li>
      <a href="{{ page.url | prepend: site.baseurl }}">{{ page.title }}</a> <small>{{page.tags}} ({{page.authors}})</small>
    </li>
    {% endif %}
  {% endfor %}
  </ul>
{% endfor %}

  <p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | prepend: site.baseurl }}">via RSS</a></p>

</div>
