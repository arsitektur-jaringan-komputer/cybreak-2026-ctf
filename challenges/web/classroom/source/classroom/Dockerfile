FROM node:18-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    make \
    gcc \
    g++ \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --production && npm cache clean --force

RUN apt-get remove -y python3 make gcc g++ libxml2-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN rm -f /app/flag.txt

RUN mkdir -p /app/public/uploads /app/modules /app/backup

COPY flag.txt /root/flag.txt
RUN chown root:root /root/flag.txt && chmod 400 /root/flag.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN chown -R node:node /app

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (r) => {process.exit(r.statusCode === 302 ? 0 : 1)})"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["node", "server.js"]
