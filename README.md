## Authentication

This set up goes into the proxy not locally.

Basic Authentication Support
In order to be able to secure your virtual host, you have to create a file named as its equivalent VIRTUAL_HOST variable on directory /etc/nginx/htpasswd/$VIRTUAL_HOST

$ docker run -d -p 80:80 -p 443:443 \
    -v /path/to/htpasswd:/etc/nginx/htpasswd \
    -v /path/to/certs:/etc/nginx/certs \
    -v /var/run/docker.sock:/tmp/docker.sock:ro \
    jwilder/nginx-proxy