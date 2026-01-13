I want to test the github pages static website generated from this repository using a locally running docker container.

There is an official docker container available for this in Docker Hub:
jekyll/jekyll:pages
It is tailored for GitHub Pages, preconfigured with the github-pages gem.

A minimal docker-compose.yml:
```
services:
  jekyll:
    image: jekyll/jekyll:pages
    command: jekyll serve --watch --incremental --host 0.0.0.0
    ports:
      - "4000:4000"
    volumes:
      - .:/srv/jekyll
```

Further preferences:

- If the docker image is not present, try to download it. If it fails, build it using a dockerfile. (Please create that dockerfile for me as well.)
- The site should be served from inside the container and available on the host via the default port 4000.
- The container should run interactively so I can stop it from the console when not using it anymore.
- Use the default system browser to open the site.
- Put the generated .cmd file into the root of the repository. Call it "local_test_with_docker.cmd".
