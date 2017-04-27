FROM zookeeper

RUN apk add --no-cache python3

ENV ZOO_SERVER_COUNT=1

ADD lookup.py /usr/local/bin/lookup.py

COPY docker-entrypoint-override.sh /
ENTRYPOINT ["/docker-entrypoint-override.sh"]
CMD ["zkServer.sh", "start-foreground"]
