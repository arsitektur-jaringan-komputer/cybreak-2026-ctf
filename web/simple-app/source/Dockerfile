FROM golang:1.23-bookworm AS build

WORKDIR /src
COPY ./src/go.mod ./src/go.sum .
RUN go mod download
COPY ./src/*.go .
RUN go build -o /out/simple-app .

FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates sqlite3 && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r rootkids && useradd -r -g rootkids rootkids && \
    mkdir /app

COPY --from=build /out/simple-app /app/simple-app
COPY ./src/templates /app/templates/
COPY flag.txt /flag.txt
COPY init.sql /tmp/init.sql

RUN chmod 444 /flag.txt && \
    chmod -R 555 /app/templates && \
    chown rootkids:rootkids /app

USER rootkids

RUN sqlite3 /app/database.sqlite < /tmp/init.sql && \
    mkdir /app/uploads

WORKDIR /app
EXPOSE 5000

CMD ["/app/simple-app"]
