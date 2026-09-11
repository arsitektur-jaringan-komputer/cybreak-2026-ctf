FROM debian:trixie
RUN apt-get update && apt-get install -y socat util-linux && rm -rf /var/lib/apt/lists/*
RUN useradd -m ctf
WORKDIR /home/ctf
COPY chall /home/ctf/chall
COPY entrypoint.sh /entrypoint.sh
RUN mkdir -p /run/ctf && ln -s /run/ctf/flag.txt /home/ctf/flag.txt && \
    chown -R root:root /home/ctf && chmod 755 /home/ctf /home/ctf/chall /entrypoint.sh
EXPOSE 4282
ENTRYPOINT ["/entrypoint.sh"]
CMD ["socat", "TCP-LISTEN:4282,reuseaddr,fork", "EXEC:/home/ctf/chall,stderr"]
