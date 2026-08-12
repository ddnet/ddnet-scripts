#!/bin/bash
set -ex

# Builds DDNet dependency libraries for Windows (MinGW cross-compilation)
# Required env vars:
#   PLATFORM - 64 or 32
# Output goes to /output/ which should be a mounted volume

: "${PLATFORM:?PLATFORM must be 64 or 32}"
OUTPUT=/output

# Library versions
SDL3_VERSION=3.4.14
CURL_VERSION=8.8.0
FREETYPE_VERSION=2.13.2
LIBOGG_VERSION=1.3.5
OPUS_VERSION=1.3.1
OPUSFILE_VERSION=0.12
SQLITE_VERSION=3460000
FFMPEG_VERSION=7.0.1
LWS_VERSION=4.3-stable
LIBPNG_VERSION=1.6.43
WAVPACK_VERSION=5.9.0
ZLIB_VERSION=1.3.1
ZLIB_RS_VERSION=0.6.7

if [ "$PLATFORM" = "64" ]; then
  HOST=x86_64-w64-mingw32
  LIB_SUFFIX="lib64"
  FFMPEG_ARCH="--arch=x86_64"
  PREFIX=/usr/x86_64-w64-mingw32
  LWS_TOOLCHAIN=contrib/cross-w64.cmake
  RUST_TARGET=x86_64-pc-windows-gnu
else
  HOST=i686-w64-mingw32
  LIB_SUFFIX="lib32"
  FFMPEG_ARCH="--arch=i686"
  PREFIX=/usr/i686-w64-mingw32
  LWS_TOOLCHAIN=contrib/cross-w32.cmake
  RUST_TARGET=i686-pc-windows-gnu
fi

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

# Download all sources
cd /build
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://libsdl.org/release/SDL3-${SDL3_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://curl.haxx.se/download/curl-${CURL_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "http://downloads.xiph.org/releases/ogg/libogg-${LIBOGG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://archive.mozilla.org/pub/opus/opus-${OPUS_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://downloads.xiph.org/releases/opus/opusfile-${OPUSFILE_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://downloads.sourceforge.net/freetype/freetype-${FREETYPE_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://www.sqlite.org/2024/sqlite-autoconf-${SQLITE_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://code.videolan.org/videolan/x264/-/archive/master/x264-master.tar.bz2"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://github.com/warmcat/libwebsockets/archive/v${LWS_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://download.sourceforge.net/libpng/libpng-${LIBPNG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://github.com/dbry/WavPack/releases/download/${WAVPACK_VERSION}/wavpack-${WAVPACK_VERSION}.tar.xz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://github.com/madler/zlib/releases/download/v${ZLIB_VERSION}/zlib-${ZLIB_VERSION}.tar.gz"

mkdir src && cd src
tar xf "../zlib-${ZLIB_VERSION}.tar.gz"
tar xf "../SDL3-${SDL3_VERSION}.tar.gz"
tar xf "../curl-${CURL_VERSION}.tar.gz"
tar xf "../libogg-${LIBOGG_VERSION}.tar.gz"
tar xf "../opus-${OPUS_VERSION}.tar.gz"
tar xf "../opusfile-${OPUSFILE_VERSION}.tar.gz"
tar xf "../freetype-${FREETYPE_VERSION}.tar.gz"
tar xf "../sqlite-autoconf-${SQLITE_VERSION}.tar.gz"
tar xf ../x264-master.tar.bz2
tar xf "../ffmpeg-${FFMPEG_VERSION}.tar.gz"
tar xf "../v${LWS_VERSION}.tar.gz"
tar xf "../libpng-${LIBPNG_VERSION}.tar.gz"
tar xf "../wavpack-${WAVPACK_VERSION}.tar.xz"

# --- SDL3 ---
cd /build/src/SDL3-${SDL3_VERSION}
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_NAME=Windows \
  -DCMAKE_C_COMPILER=${HOST}-gcc -DCMAKE_CXX_COMPILER=${HOST}-g++ \
  -DCMAKE_RC_COMPILER=${HOST}-windres \
  -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF
cmake --build build -j"$(nproc)"
cp build/SDL3.dll build/libSDL3.dll.a /build/src/
# import lib for MSVC, from the DLL's export table
(cd /build/src && gendef SDL3.dll && ${HOST}-dlltool -d SDL3.def -D SDL3.dll -l /build/src/SDL3.lib)

# --- curl ---
cd /build/src/curl-${CURL_VERSION}
./configure --host=$HOST --with-schannel --enable-shared "${CURL_CONFIGURE_OPTIONS[@]}"
make -j"$(nproc)" V=1
# libtool names the DLL libcurl-4.dll; the import lib below references
# libcurl.dll, so ship it under that name
${HOST}-dlltool -v --export-all-symbols -D libcurl.dll -l /build/src/curl.lib lib/.libs/*.o
cp lib/.libs/libcurl-4.dll /build/src/libcurl.dll

# --- libogg ---
cd /build/src/libogg-${LIBOGG_VERSION}
./configure --host=$HOST
make -j"$(nproc)"
rm -f src/.libs/libogg-0.dll
${HOST}-gcc -shared src/.libs/framing.o src/.libs/bitwise.o -O2 \
  -o src/.libs/libogg.dll -Wl,--enable-auto-image-base -Xlinker --out-implib -Xlinker src/.libs/libogg.dll.a
${HOST}-dlltool -v --export-all-symbols -D libogg.dll -l /build/src/ogg.lib src/.libs/*.o
cp src/.libs/libogg.dll /build/src/libogg.dll

# --- opus ---
cd /build/src/opus-${OPUS_VERSION}
./configure --host=$HOST CFLAGS=-D_FORTIFY_SOURCE=0
make -j"$(nproc)" V=1
${HOST}-dlltool -v --export-all-symbols -D libopus.dll -l /build/src/opus.lib src/*.o
cp .libs/libopus-0.dll /build/src/libopus.dll

# --- opusfile ---
cd /build/src/opusfile-${OPUSFILE_VERSION}
DEPS_LIBS="-lopus -logg -L/build/src/opus-${OPUS_VERSION}/.libs/ -L/build/src/libogg-${LIBOGG_VERSION}/src/.libs/" \
  DEPS_CFLAGS="-I/build/src/opus-${OPUS_VERSION}/include -I/build/src/libogg-${LIBOGG_VERSION}/include" \
  ./configure --host=$HOST --disable-http
make -j"$(nproc)" V=1
${HOST}-dlltool -v --export-all-symbols -D libopusfile.dll -l /build/src/opusfile.lib src/*.o
cp .libs/libopusfile-0.dll /build/src/libopusfile.dll

# --- freetype ---
cd /build/src/freetype-${FREETYPE_VERSION}
./configure --host=$HOST --prefix=$PREFIX \
  CPPFLAGS="-I${PREFIX}/include" LDFLAGS="-L${PREFIX}/lib" \
  PKG_CONFIG_LIBDIR=${PREFIX}/lib/pkgconfig \
  --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j"$(nproc)" V=1
${HOST}-dlltool -v --export-all-symbols -D libfreetype.dll -l /build/src/freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype-6.dll /build/src/libfreetype.dll

# --- sqlite ---
cd /build/src/sqlite-autoconf-${SQLITE_VERSION}
./configure --host=$HOST CFLAGS=-DSQLITE_OMIT_LOAD_EXTENSION
make -j"$(nproc)"
cp .libs/libsqlite3-0.dll /build/src/
${HOST}-dlltool -v --export-all-symbols -D sqlite3.dll -l /build/src/sqlite3.lib .libs/*.o

# --- x264 ---
cd /build/src/x264-master
AS=nasm CFLAGS="-I${PREFIX}/include" LDFLAGS="-L${PREFIX}/lib" \
  ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale \
  --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced \
  --host=${HOST%%-w64*}-mingw32 --prefix=$PREFIX --cross-prefix=${HOST}-
make -j"$(nproc)"

# --- ffmpeg ---
cd /build/src/ffmpeg-${FFMPEG_VERSION}
PKG_CONFIG_PATH=/build/src/x264-master PKG_CONFIG_LIBDIR=${PREFIX}/lib/pkgconfig \
  ./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb \
  --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib \
  --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac \
  --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample \
  --enable-swscale --enable-gpl \
  --extra-cflags="-I/build/src/x264-master" \
  --extra-cxxflags="-I/build/src/x264-master" \
  --extra-ldflags="-L/build/src/x264-master" \
  $FFMPEG_ARCH --target_os=mingw32 --cross-prefix=${HOST}- \
  --disable-static --enable-shared --extra-libs="-lpthread -lm" --pkg-config-flags="--static"
make -j"$(nproc)"
cp libavcodec/avcodec-61.dll libavformat/avformat-61.dll libavutil/avutil-59.dll \
   libswresample/swresample-5.dll libswscale/swscale-8.dll \
   libavcodec/avcodec.lib libavformat/avformat.lib libavutil/avutil.lib \
   libswresample/swresample.lib libswscale/swscale.lib /build/src/

# --- libwebsockets ---
cd /build/src/libwebsockets-${LWS_VERSION}
# v4.3-stable tip uses vpt in pollfd.c with a guard narrower than its declaration
# (broken for Windows, fixed on lws main); no-op once the branch is fixed
sed -i 's/^#if !defined(LWS_WITH_EVENT_LIBS)$/#if !defined(LWS_WITH_EVENT_LIBS) \&\& !defined(WIN32) \&\& !defined(_WIN32)/' lib/core-net/pollfd.c
cmake -DCMAKE_TOOLCHAIN_FILE=$LWS_TOOLCHAIN \
  -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF \
  -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j"$(nproc)"
cp bin/libwebsockets.dll /build/src/
cp lws_config.h /build/src/
gendef /build/src/libwebsockets.dll
${HOST}-dlltool -d libwebsockets.def -D libwebsockets.dll -l /build/src/websockets.lib

# --- zlib (static, into the mingw sysroot; needed by libpng) ---
cd /build/src/zlib-${ZLIB_VERSION}
cmake -S . -B build -DCMAKE_SYSTEM_NAME=Windows \
  -DCMAKE_C_COMPILER=${HOST}-gcc \
  -DCMAKE_RC_COMPILER=${HOST}-windres \
  -DCMAKE_AR=/usr/bin/${HOST}-ar \
  -DCMAKE_RANLIB=/usr/bin/${HOST}-ranlib \
  -DCMAKE_C_FLAGS=-w -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
cp build/libzlibstatic.a ${PREFIX}/lib/libz.a
cp zlib.h build/zconf.h ${PREFIX}/include/

# --- zlib-rs (static, for libpng only) ---
# libpng links this instead of the C zlib above, so it decompresses with
# zlib-rs like the rest of DDNet does. The C zlib stays in the sysroot for the
# other consumers. no_std, or Rust's std pulls its whole windows platform layer
# (sockets, ntdll, ...) into libpng.
mkdir -p /build/zlib-rs-shim/src
cd /build/zlib-rs-shim
cat > Cargo.toml <<EOF
[package]
name = "zlib-rs-shim"
version = "0.0.1"
edition = "2021"
publish = false

[lib]
crate-type = ["staticlib"]
path = "src/lib.rs"

[dependencies]
libz-rs-sys = { version = "=${ZLIB_RS_VERSION}", default-features = false, features = ["export-symbols", "c-allocator"] }

[profile.release]
opt-level = 3
panic = "abort"
strip = true
EOF
cat > src/lib.rs <<'EOF'
//! Static archive exporting the zlib C API, implemented by zlib-rs.
#![no_std]

use core::alloc::{GlobalAlloc, Layout};

use libz_rs_sys as _;

unsafe extern "C" {
    fn abort() -> !;
}

/// zlib-rs links the `alloc` crate, so a global allocator has to exist, but it
/// never allocates through it: the `c-allocator` feature routes zlib-rs's own
/// allocations to `malloc`, and libpng installs its own `zalloc`/`zfree` on
/// every stream regardless. Abort instead of pretending to allocate.
struct Unused;

unsafe impl GlobalAlloc for Unused {
    unsafe fn alloc(&self, _layout: Layout) -> *mut u8 {
        unsafe { abort() }
    }

    unsafe fn dealloc(&self, _ptr: *mut u8, _layout: Layout) {
        unsafe { abort() }
    }
}

#[global_allocator]
static ALLOCATOR: Unused = Unused;

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    unsafe { abort() }
}

/// The precompiled `core` rlib is built with `panic=unwind`, so its unwind
/// tables reference this. We abort on panic, so it is never called.
#[no_mangle]
extern "C" fn rust_eh_personality() {}
EOF
cargo build --release --target ${RUST_TARGET}
mkdir -p /build/zlib-rs/lib /build/zlib-rs/include
cp target/${RUST_TARGET}/release/libzlib_rs_shim.a /build/zlib-rs/lib/libz.a
cp "$HOME"/.cargo/registry/src/*/libz-rs-sys-${ZLIB_RS_VERSION}/include/zlib.h \
   "$HOME"/.cargo/registry/src/*/libz-rs-sys-${ZLIB_RS_VERSION}/include/zconf.h \
   /build/zlib-rs/include/

# --- libpng ---
cd /build/src/libpng-${LIBPNG_VERSION}
CPPFLAGS="-I/build/zlib-rs/include" LDFLAGS="-L/build/zlib-rs/lib" ./configure --host=$HOST
make -j"$(nproc)"
cp .libs/libpng16-16.dll /build/src/
${HOST}-dlltool -v --export-all-symbols -D libpng16-16.dll -l /build/src/libpng16-16.lib .libs/*.o

# --- Strip all DLLs ---
cd /build/src
for i in *.dll; do ${HOST}-strip -s "$i"; done

# --- wavpack ---
cd /build/src/wavpack-${WAVPACK_VERSION}
cmake -S . -B build "${WAVPACK_CMAKE_OPTIONS[@]}" -DBUILD_SHARED_LIBS=ON \
  -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_C_COMPILER=${HOST}-gcc -DCMAKE_CXX_COMPILER=${HOST}-g++ \
  -DCMAKE_RC_COMPILER=${HOST}-windres -DCMAKE_SHARED_LINKER_FLAGS=-static-libgcc
cmake --build build -j"$(nproc)"
cp build/libwavpack-1.dll /build/src/
(cd /build/src && gendef libwavpack-1.dll && ${HOST}-dlltool -d libwavpack-1.def -D libwavpack-1.dll -l /build/src/wavpack.lib)

# --- Distribute to ddnet-libs layout ---
mkdir -p "$OUTPUT/sdl/windows/${LIB_SUFFIX}"
cp SDL3.dll SDL3.lib libSDL3.dll.a "$OUTPUT/sdl/windows/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/curl/windows/${LIB_SUFFIX}"
cp libcurl.dll curl.lib "$OUTPUT/curl/windows/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/opus/windows/${LIB_SUFFIX}"
cp libogg.dll ogg.lib libopus.dll opus.lib libopusfile.dll opusfile.lib "$OUTPUT/opus/windows/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/freetype/windows/${LIB_SUFFIX}"
cp libfreetype.dll freetype.lib "$OUTPUT/freetype/windows/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/sqlite3/windows/${LIB_SUFFIX}"
cp libsqlite3-0.dll sqlite3.lib "$OUTPUT/sqlite3/windows/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/ffmpeg/windows/${LIB_SUFFIX}"
cp avcodec-61.dll avformat-61.dll avutil-59.dll swresample-5.dll swscale-8.dll \
   avcodec.lib avformat.lib avutil.lib swresample.lib swscale.lib "$OUTPUT/ffmpeg/windows/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/websockets/windows/${LIB_SUFFIX}"
cp libwebsockets.dll websockets.lib lws_config.h "$OUTPUT/websockets/windows/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/png/windows/${LIB_SUFFIX}"
cp libpng16-16.dll libpng16-16.lib "$OUTPUT/png/windows/${LIB_SUFFIX}/"

mkdir -p "$OUTPUT/wavpack/windows/${LIB_SUFFIX}"
cp libwavpack-1.dll wavpack.lib "$OUTPUT/wavpack/windows/${LIB_SUFFIX}/"

echo "Windows win${PLATFORM} library build complete."
