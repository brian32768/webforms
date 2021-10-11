# Webforms

This is a web form for COVID data entry. 
It runs as a flask app in a Docker.

Output goes into Portal feature classes.

After each update of the 'cases' database,
it triggers an export to CSV so that my D3 chart
gets the latest data.

## Testing

The runtime environment is LINUX in Docker.
I test locally in WINDOWS
so I use Python 3.6.10 because DLLs won't load properly in Python 3.8
There should be a really simple upgrade/fix for this but I don't know it yet.

That's why I install python 3.6.10 in the environment for local testing

    conda create --name=flask_covid
    conda activate flask_covid
    conda install --file=requirements.txt

## Data dumper

This lets me see what's already in the "cases" feature class.

    conda activate flask_covid
    python data_dumper.py

## Authentication

This set up goes into the proxy not locally.

Basic Authentication Support
In order to be able to secure your virtual host, you have to create a file named as its equivalent VIRTUAL_HOST variable on directory /etc/nginx/htpasswd/$VIRTUAL_HOST

$ docker run -d -p 80:80 -p 443:443 \
    -v /path/to/htpasswd:/etc/nginx/htpasswd \
    -v /path/to/certs:/etc/nginx/certs \
    -v /var/run/docker.sock:/tmp/docker.sock:ro \
    jwilder/nginx-proxy

## Deploy

This won't work yet, because of the container name problem in the proxy nginx.

    docker stack deploy -c docker-compose.yml webforms

so do the old fashioned thing

    docker-compose up -d

## Updates

If you change files here in this folder, you have to redeploy to get them into the running image.
This works for me.

```bash
docker-compose build
docker-compose restart
```
