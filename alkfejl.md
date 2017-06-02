---
layout: default
permalink: /alkfejl.html
codename: AlkFejlSnippetek
title: Alkalmazásfejlesztés snippetek
tags: snippets skipfromindex
authors: Csorba Kristóf
---

<div class="home">
  {% assign tagToFilterFor = 'alkfejl' %}
  {% assign skippedTags = 'skipfromindex' %}

  <h1 class="page-heading">Alkalmazásfejlesztés snippetek címkék szerint</h1>
  {% assign skippedPageTag = 'skipfromindex' %}
  <table>
    <tr><th>Kód</th><th>Cím</th><th>Címkék</th><th>Szerzők</th></tr>
    {% assign sortedPages = site.pages | sort:"codename" %}    
    {% for page in sortedPages %}
    {% if page.tags contains tagToFilterFor %}
    {% unless page.tags contains skippedPageTag %}
    <tr>
      <td><small>{{page.codename}}</small></td><td><a class="post-link" href="{{ page.url | prepend: site.baseurl }}">{{ page.title }}</a></td><td><small>{{page.tags}}</small></td><td><small>{{page.authors}}</small></td>
    </tr>
    {% endunless %}
    {% endif %}
    {% endfor %}
  </table>




{% for tag in allTagsArray %}
  <h2 id="{{tag}}">{{tag}}</h2><br/>
  <ul>
  {% for page in site.pages %}
    {% if page.tags contains tag and page.tags contains "alkfejl" %}
    {% unless page.tags contains skippedTags %}
    <li>
      <a href="{{ page.url | prepend: site.baseurl }}">{{ page.title }}</a> <small>{{page.tags}} ({{page.authors}})</small>
    </li>
    {% endunless %}
    {% endif %}
  {% endfor %}
  </ul>
{% endfor %}

  <p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | prepend: site.baseurl }}">via RSS</a></p>

</div>
