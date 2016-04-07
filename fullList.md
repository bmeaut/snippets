---
layout: default
permalink: /fullList.html
---

<div class="home">
  <h1 class="page-heading">Minden snippet</h1>
  <ul class="post-list">
    {% for page in site.pages %}
      <li>
        <h2>
          <a class="post-link" href="{{ page.url | prepend: site.baseurl }}">{{ page.title }} (author: {{page.authors}}, tags: {{page.tags}})</a>
        </h2>
      </li>
    {% endfor %}
  </ul>
  <p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | prepend: site.baseurl }}">via RSS</a></p>
</div>
