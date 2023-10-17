FROM nginx:1.25
# Install certbot
RUN apk add --no-cache certbot

# Copy renew cron script
COPY infra/nginx/renew /etc/periodic/daily/renew
RUN chmod +x /etc/periodic/daily/renew

RUN mkdir /var/lib/certbot

# Copy entrypoint
COPY infra/nginx/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# nginx config
COPY dockerization/nginx/default.conf /etc/nginx/conf.d/default.conf

ENTRYPOINT [ "../entrypoint.sh" ]