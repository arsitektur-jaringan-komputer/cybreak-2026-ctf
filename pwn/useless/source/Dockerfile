FROM ubuntu:26.04@sha256:513c074113a871b51a8d16ab445c88779d6452d937a164fb5cc479f32668a41d
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages for building and running the application
RUN apt-get update -y && \
    apt-get install -y socat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root mirai
RUN useradd -u 1337 -d /home/mirai -s /bin/bash mirai

# Set the working directory
WORKDIR /home/mirai

# Copy the binary
COPY entrypoint.sh /entrypoint.sh
COPY chall /home/mirai/

# Copy the flag
COPY flag.txt /home/mirai/flag.txt

# Set permissions to make necessary files read-only
RUN chmod +x /entrypoint.sh
RUN chmod 111 /home/mirai/chall
RUN chmod 444 /home/mirai/flag.txt
RUN chmod -R 555 /home/mirai

# Expose port
EXPOSE 1337
CMD ["/entrypoint.sh"]
