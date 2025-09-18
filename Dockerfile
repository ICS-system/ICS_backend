# Janus Gateway 1.3.2 from meetecho official source
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    pkg-config \
    gengetopt \
    libtool \
    automake \
    libmicrohttpd-dev \
    libjansson-dev \
    libssl-dev \
    libglib2.0-dev \
    libconfig-dev \
    libnice-dev \
    libsrtp2-dev \
    libusrsctp-dev \
    libwebsockets-dev \
    libcurl4-openssl-dev \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    libogg-dev \
    libopus-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone and build Janus Gateway
WORKDIR /usr/src
RUN git clone https://github.com/meetecho/janus-gateway.git
WORKDIR /usr/src/janus-gateway

# Checkout v1.3.2
RUN git checkout v1.3.2

# Configure and build
RUN ./autogen.sh
RUN ./configure \
    --prefix=/usr/local \
    --disable-rabbitmq \
    --disable-mqtt \
    --enable-websockets \
    --disable-post-processing

RUN make && make install && make configs

# Create janus user
RUN useradd -r -s /bin/false janus

# Set ownership
RUN chown -R janus:janus /usr/local/etc/janus
RUN chown -R janus:janus /usr/local/share/janus

# Expose ports
EXPOSE 8088 8188 8989

# Run as janus user
USER janus

# Start Janus
CMD ["/usr/local/bin/janus", "--nat-1-1=${JANUS_NAT_1_1}", "--stun-server=${JANUS_STUN_SERVER}"]