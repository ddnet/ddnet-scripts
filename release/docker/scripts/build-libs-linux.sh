#!/bin/bash
set -ex

# Builds DDNet dependency libraries for Linux
# Required env vars:
#   PLATFORM - x86_64 or x86
# Output goes to /output/ which should be a mounted volume

: "${PLATFORM:?PLATFORM must be x86_64 or x86}"
OUTPUT=/output

# Library versions
# SDL main snapshot, the 3.4 releases lack the per-device mice on macOS
SDL3_COMMIT=d4410b9a7ccbc05f6b235b411226b01ebb91fe51
CURL_VERSION=8.8.0
LIBOGG_VERSION=1.3.5
OPUS_VERSION=1.3.1
OPUSFILE_VERSION=0.12
SQLITE_VERSION=3460000
FFMPEG_VERSION=7.0.1
LWS_VERSION=4.3-stable
LIBPNG_VERSION=1.6.43
WAVPACK_VERSION=5.9.0

if [ "$PLATFORM" = "x86" ]; then
  ARCH_FLAGS="-m32"
  ARCH_FPIC=""
  HOST_FLAG="--host=i686-linux"
  X264_HOST="--host=i686-linux"
  FFMPEG_ARCH="--cpu=i686"
  LIB_SUFFIX="lib32"
  # SDL3's cmake build must see the i386 .pc files, the amd64 glibconfig.h
  # otherwise breaks the ibus build
  SDL_PKG_CONFIG_ENV="PKG_CONFIG_LIBDIR=/usr/lib/i386-linux-gnu/pkgconfig:/usr/share/pkgconfig"
else
  ARCH_FLAGS=""
  ARCH_FPIC="-fPIC"
  HOST_FLAG=""
  X264_HOST=""
  FFMPEG_ARCH=""
  LIB_SUFFIX="lib64"
  SDL_PKG_CONFIG_ENV=""
fi

COMMON_CFLAGS="${ARCH_FLAGS} ${ARCH_FPIC}"

# Download all sources
cd /build
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 -O "SDL3-${SDL3_COMMIT}.tar.gz" "https://github.com/libsdl-org/SDL/archive/${SDL3_COMMIT}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://curl.haxx.se/download/curl-${CURL_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "http://downloads.xiph.org/releases/ogg/libogg-${LIBOGG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://archive.mozilla.org/pub/opus/opus-${OPUS_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://downloads.xiph.org/releases/opus/opusfile-${OPUSFILE_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://www.sqlite.org/2024/sqlite-autoconf-${SQLITE_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://code.videolan.org/videolan/x264/-/archive/master/x264-master.tar.bz2"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://github.com/warmcat/libwebsockets/archive/v${LWS_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://download.sourceforge.net/libpng/libpng-${LIBPNG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://github.com/dbry/WavPack/releases/download/${WAVPACK_VERSION}/wavpack-${WAVPACK_VERSION}.tar.xz"

mkdir src && cd src
tar xf "../SDL3-${SDL3_COMMIT}.tar.gz"
tar xf "../curl-${CURL_VERSION}.tar.gz"
tar xf "../libogg-${LIBOGG_VERSION}.tar.gz"
tar xf "../opus-${OPUS_VERSION}.tar.gz"
tar xf "../opusfile-${OPUSFILE_VERSION}.tar.gz"
tar xf "../sqlite-autoconf-${SQLITE_VERSION}.tar.gz"
tar xf ../x264-master.tar.bz2
tar xf "../ffmpeg-${FFMPEG_VERSION}.tar.gz"
tar xf "../v${LWS_VERSION}.tar.gz"
tar xf "../libpng-${LIBPNG_VERSION}.tar.gz"
tar xf "../wavpack-${WAVPACK_VERSION}.tar.xz"

CURL_CONFIGURE_OPTIONS=(
  --disable-ftp --disable-file --disable-ldap --disable-rtsp
  --disable-dict --disable-telnet --disable-tftp --disable-pop3
  --disable-imap --disable-smb --disable-smtp --disable-gopher --disable-mqtt
)

WAVPACK_CMAKE_OPTIONS=(
  -DCMAKE_BUILD_TYPE=Release
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
  -DBUILD_TESTING=OFF
  -DWAVPACK_BUILD_PROGRAMS=OFF
  -DWAVPACK_ENABLE_THREADS=OFF
  -DWAVPACK_INSTALL_CMAKE_MODULE=OFF
  -DWAVPACK_INSTALL_DOCS=OFF
  -DWAVPACK_INSTALL_PKGCONFIG_MODULE=OFF
)

# --- curl ---
cd /build/src/curl-${CURL_VERSION}
CFLAGS="$COMMON_CFLAGS" LDFLAGS="$ARCH_FLAGS" \
  ./configure --with-openssl --enable-static --disable-shared "${CURL_CONFIGURE_OPTIONS[@]}"
CFLAGS="$COMMON_CFLAGS" LDFLAGS="$ARCH_FLAGS" make -j"$(nproc)"
cp lib/.libs/libcurl.a /build/src/

# --- libogg ---
cd /build/src/libogg-${LIBOGG_VERSION}
CFLAGS="$COMMON_CFLAGS" LDFLAGS="$ARCH_FLAGS" ./configure $HOST_FLAG
CFLAGS="$COMMON_CFLAGS" LDFLAGS="$ARCH_FLAGS" make -j"$(nproc)"
cp src/.libs/libogg.a /build/src/

# --- opus ---
cd /build/src/opus-${OPUS_VERSION}
CFLAGS="$COMMON_CFLAGS" LDFLAGS="$ARCH_FLAGS" ./configure $HOST_FLAG
CFLAGS="$COMMON_CFLAGS" LDFLAGS="$ARCH_FLAGS" make -j"$(nproc)"
cp .libs/libopus.a /build/src/

# --- opusfile ---
cd /build/src/opusfile-${OPUSFILE_VERSION}
CFLAGS="$COMMON_CFLAGS" LDFLAGS="$ARCH_FLAGS" \
  DEPS_LIBS="-lopus -logg -L/build/src/opus-${OPUS_VERSION}/.libs/ -L/build/src/libogg-${LIBOGG_VERSION}/src/.libs/" \
  DEPS_CFLAGS="${ARCH_FLAGS} -I/build/src/opus-${OPUS_VERSION}/include -I/build/src/libogg-${LIBOGG_VERSION}/include" \
  ./configure --disable-http $HOST_FLAG
CFLAGS="$COMMON_CFLAGS" LDFLAGS="$ARCH_FLAGS" make -j"$(nproc)"
cp .libs/libopusfile.a /build/src/

# --- SDL3 ---
cd /build/src/SDL-${SDL3_COMMIT}
env $SDL_PKG_CONFIG_ENV cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="$ARCH_FLAGS" -DCMAKE_CXX_FLAGS="$ARCH_FLAGS" \
  -DCMAKE_SHARED_LINKER_FLAGS="$ARCH_FLAGS" -DCMAKE_EXE_LINKER_FLAGS="$ARCH_FLAGS" \
  -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF \
  -DSDL_WAYLAND=OFF -DSDL_RPATH=OFF
cmake --build build -j"$(nproc)"
cp build/libSDL3.so.0.*.* /build/src/libSDL3.so.0
strip -s /build/src/libSDL3.so.0

# --- sqlite ---
cd /build/src/sqlite-autoconf-${SQLITE_VERSION}
./configure CFLAGS="${COMMON_CFLAGS} -DSQLITE_OMIT_LOAD_EXTENSION" $HOST_FLAG
make -j"$(nproc)"
cp .libs/libsqlite3.a /build/src/

# --- x264 ---
cd /build/src/x264-master
AS=nasm CFLAGS="${ARCH_FLAGS} -O2 -fno-fast-math" LDFLAGS="$ARCH_FLAGS" \
  ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale \
  --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced \
  --enable-pic $X264_HOST
CFLAGS="${ARCH_FLAGS} -O2 -fno-fast-math" LDFLAGS="$ARCH_FLAGS" make -j"$(nproc)"
cp libx264.a /build/src/

# --- ffmpeg ---
cd /build/src/ffmpeg-${FFMPEG_VERSION}
PKG_CONFIG_PATH=/build/src/x264-master/ \
  ./configure --disable-all --disable-vdpau --disable-vaapi --disable-libdrm --disable-alsa \
  --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes \
  --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat \
  --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file \
  --enable-libx264 --enable-swresample --enable-swscale --enable-gpl \
  --extra-cflags="${COMMON_CFLAGS} -I/build/src/x264-master" \
  --extra-cxxflags="${COMMON_CFLAGS} -I/build/src/x264-master" \
  --extra-ldflags="${ARCH_FLAGS} -L/build/src/x264-master -ldl" \
  ${FFMPEG_ARCH} --extra-libs="-lpthread -lm" --pkg-config-flags="--static"
make -j"$(nproc)"
cp libavcodec/*.a libavformat/*.a libavutil/*.a libswresample/*.a libswscale/*.a /build/src/

# --- libwebsockets ---
cd /build/src/libwebsockets-${LWS_VERSION}
CXXFLAGS="$COMMON_CFLAGS" CFLAGS="$COMMON_CFLAGS" LDFLAGS="$COMMON_CFLAGS" \
  cmake -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j"$(nproc)"
cp lib/libwebsockets.a /build/src/
cp lws_config.h /build/src/

# --- libpng ---
cd /build/src/libpng-${LIBPNG_VERSION}
./configure CFLAGS="$COMMON_CFLAGS" $HOST_FLAG
make -j"$(nproc)"
cp .libs/libpng16.a /build/src/

# --- wavpack ---
cd /build/src/wavpack-${WAVPACK_VERSION}
# CMAKE_ASM_FLAGS has to repeat -m32 or wavpack's x86 assembly is still
# assembled as 64 bit
cmake -S . -B build "${WAVPACK_CMAKE_OPTIONS[@]}" -DBUILD_SHARED_LIBS=OFF \
  -DCMAKE_C_FLAGS="$COMMON_CFLAGS" -DCMAKE_ASM_FLAGS="$ARCH_FLAGS"
cmake --build build -j"$(nproc)"
cp build/libwavpack.a /build/src/

# --- Distribute to ddnet-libs layout ---
cd /build/src

mkdir -p "$OUTPUT/curl/linux/${LIB_SUFFIX}"
cp libcurl.a "$OUTPUT/curl/linux/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/opus/linux/${LIB_SUFFIX}"
cp libogg.a libopus.a libopusfile.a "$OUTPUT/opus/linux/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/sdl/linux/${LIB_SUFFIX}"
cp libSDL3.so.0 "$OUTPUT/sdl/linux/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/sqlite3/linux/${LIB_SUFFIX}"
cp libsqlite3.a "$OUTPUT/sqlite3/linux/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/ffmpeg/linux/${LIB_SUFFIX}"
cp libavcodec.a libavformat.a libavutil.a libswresample.a libswscale.a libx264.a "$OUTPUT/ffmpeg/linux/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/websockets/linux/${LIB_SUFFIX}"
cp libwebsockets.a "$OUTPUT/websockets/linux/${LIB_SUFFIX}/"
cp lws_config.h "$OUTPUT/websockets/linux/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/png/linux/${LIB_SUFFIX}"
cp libpng16.a "$OUTPUT/png/linux/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/wavpack/linux/${LIB_SUFFIX}"
cp libwavpack.a "$OUTPUT/wavpack/linux/${LIB_SUFFIX}/"

echo "Linux ${PLATFORM} library build complete."
