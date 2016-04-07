---
layout: default
permalink: /alkfejl.html
codename: alkfejl
title: Alkalmazásfejlesztés snippetek
tags: snippets
authors: Csorba Kristóf
---

<div class="home">
  {% assign tagToFilterFor = 'alkfejl' %}

  {% capture allTags %}
    {% for p in site.pages %}
      {% if p.tags contains tagToFilterFor %}
        {% for t in p.tags %} {{t}} {% endfor %}
      {% endif %}
    {% endfor %}
  {% endcapture %}
  {% assign allTagsArrayWithDuplicates = allTags | split : ' ' | sort %}

  {% assign prev = "" %}
  {% capture allTags %}
  {% for t in allTagsArrayWithDuplicates %}
    {% if prev != t and t != tagToFilterFor %} {{t}} {% endif %}
    {% assign prev = t %}
  {% endfor %}
  {% endcapture %}
  {% assign allTagsArray = allTags | split : ' ' | sort | %}

  <h1 class="page-heading">Alkalmazásfejlesztés snippetek címkék szerint</h1>

{% for tag in allTagsArray %}
  <h2 id="{{tag}}">{{tag}}</h2><br/>
  <ul>
  {% for page in site.pages %}
    {% if page.tags contains tag and page.tags contains "alkfejl" %}
    <li>
      <a href="{{ page.url | prepend: site.baseurl }}">{{ page.title }}</a> <small>{{page.tags}} ({{page.authors}})</small>
    </li>
    {% endif %}
  {% endfor %}
  </ul>
{% endfor %}

  <p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | prepend: site.baseurl }}">via RSS</a></p>

</div>
