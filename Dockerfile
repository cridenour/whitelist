FROM python:3.6-alpine3.9

MAINTAINER Chris Ridenour <chrisridenour@gmail.com>

# update pip
RUN pip3 install --no-cache-dir --upgrade pip

# set python
ENV PYTHONUNBUFFERED 1

# create needed folder
RUN mkdir /app
WORKDIR /app

ADD ./requirements.txt /app/

# Include libraries for our packages
RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
    freetype-dev \
	gcc \
	g++ \
	git \
	musl-dev \
	make \
	jpeg-dev \
	lcms2-dev \
	libffi-dev \
	libpng-dev \
	libpq \
	libwebp-dev \
	openjpeg-dev \
	openssl-dev \
	postgresql-dev \
	tiff-dev \
	zlib-dev \
	linux-headers && \
	apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
	libressl2.7-libcrypto \
    gdal-dev \
	geos && \
	CFLAGS="$CFLAGS -L/lib" pip3 install --no-cache-dir -r /app/requirements.txt && \
	apk del --no-cache \
	gcc \
	g++ \
	make \
	musl-dev \
	postgresql-dev

# add ca-certs
RUN apk add --no-cache ca-certificates

ADD . /app/

# Build the project
#RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
#    yarn && \
#    yarn && \
#    yarn run build && \
#    apk del --no-cache \
#    yarn && \
#    rm -rf node_modules

# Collect static files
RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]