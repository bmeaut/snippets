---
layout: default
permalink: /alkfejlmerged.html
codename: alkfejl
title: Alkalmazásfejlesztés snippetek összeolvasztva
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
  {% for page in site.pages %}
    {% if page.tags contains tag and page.tags contains "alkfejl" %}
      {{page.content | markdownify}}
    {% endif %}
  {% endfor %}
  </table>
{% endfor %}

  <p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | prepend: site.baseurl }}">via RSS</a></p>

</div>
