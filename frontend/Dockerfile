FROM nginx:1.27-alpine

RUN rm -rf /usr/share/nginx/html/* \
    && mkdir -p /var/cache/nginx /var/run /usr/share/nginx/html \
    && chown -R nginx:nginx /var/cache/nginx /var/run /usr/share/nginx/html /etc/nginx/conf.d

COPY index.html /usr/share/nginx/html/index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

USER nginx

CMD ["nginx", "-g", "daemon off;"]
