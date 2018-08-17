---
layout: default
permalink: /fullList.html
codename: FullList
title: Minden snippet listája
tags: snippets skipfromindex
authors: Csorba Kristóf
---

<div class="home">
  <h1 class="page-heading">Minden snippet</h1>
  {% assign skippedPageTag = 'skipfromindex' %}
  <table>
    <tr><th>Kód</th><th>Cím</th><th>Címkék</th><th>Szerzők</th></tr>
    {% assign sortedPages = site.pages | sort:"codename" %}    
    {% for page in sortedPages %}
    {% unless page.tags contains skippedPageTag %}
    <tr>
      <td><small>{{page.codename}}</small></td><td><a class="post-link" href="{{ page.url | prepend: site.baseurl }}">{{ page.title }}</a></td><td><small>{{page.tags}}</small></td><td><small>{{page.authors}}</small></td>
    </tr>
    {% endunless %}
    {% endfor %}
  </table>
</div>
