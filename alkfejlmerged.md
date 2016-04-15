---
layout: default
permalink: /alkfejlmerged.html
codename: AlkFejlMerged
title: Alkalmazásfejlesztés snippetek összeolvasztva
tags: snippets skipfromindex
authors: Csorba Kristóf
---

<div class="home">
  <h1 class="page-heading">Alkalmazásfejlesztés snippetek összefűzve</h1>
  {% for page in site.pages %}
    {% if page.tags contains "alkfejl" %}
    <div id="{{page.url}}" style="width: auto; height: auto">
      <script type="text/javascript"> document.getElementById("{{page.url}}").innerHTML='<object type="text/html" data="{{ page.url | prepend: site.baseurl }}/index.html" ></object>'; </script>
    </div>
    {% endif %}
  {% endfor %}

  <p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | prepend: site.baseurl }}">via RSS</a></p>

</div>
