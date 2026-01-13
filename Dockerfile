FROM jekyll/jekyll:pages

# Ensure build tools and dev headers are available so native gems can compile
USER root
RUN apk add --no-cache \
	build-base \
	ruby-dev \
	musl-dev \
	zlib-dev \
	openssl-dev \
	libffi-dev \
	make \
	gcc \
	g++

WORKDIR /srv/jekyll

ENV JEKYLL_ENV=development

CMD ["jekyll", "serve", "--watch", "--incremental", "--host", "0.0.0.0"]
