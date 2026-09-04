#!/bin/bash
set -ex

# Builds DDNet dependency libraries for Windows ARM64
# Based on ddnet-arm/Dockerfile
# Output goes to /output/ which should be a mounted volume

OUTPUT=/output
mkdir -p "$OUTPUT" /dist

# Library versions
# SDL main snapshot, the 3.4 releases lack the per-device mice on macOS
SDL3_COMMIT=d4410b9a7ccbc05f6b235b411226b01ebb91fe51
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
VULKAN_VERSION=1.3.290.0

# Dockerfile.libs-winarm64 provides these via ENV; the defaults match its
# x86_64-hosted llvm-mingw toolchain
TOOLCHAIN_DIR=${TOOLCHAIN_DIR:-/opt/llvm-mingw-20240619-ucrt-ubuntu-20.04-x86_64}
SYSROOT=${SYSROOT:-${TOOLCHAIN_DIR}/aarch64-w64-mingw32}

# Download all sources
cd /build
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 -O "SDL3-${SDL3_COMMIT}.tar.gz" "https://github.com/libsdl-org/SDL/archive/${SDL3_COMMIT}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://curl.haxx.se/download/curl-${CURL_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://downloads.sourceforge.net/freetype/freetype-${FREETYPE_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "http://downloads.xiph.org/releases/ogg/libogg-${LIBOGG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://archive.mozilla.org/pub/opus/opus-${OPUS_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://downloads.xiph.org/releases/opus/opusfile-${OPUSFILE_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://www.sqlite.org/2024/sqlite-autoconf-${SQLITE_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://code.videolan.org/videolan/x264/-/archive/master/x264-master.tar.bz2"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://ffmpeg.org/releases/ffmpeg-${FFMPEG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://github.com/warmcat/libwebsockets/archive/v${LWS_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://download.sourceforge.net/libpng/libpng-${LIBPNG_VERSION}.tar.gz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://github.com/dbry/WavPack/releases/download/${WAVPACK_VERSION}/wavpack-${WAVPACK_VERSION}.tar.xz"
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://github.com/madler/zlib/releases/download/v${ZLIB_VERSION}/zlib-${ZLIB_VERSION}.tar.gz"

mkdir src && cd src
tar xf "../SDL3-${SDL3_COMMIT}.tar.gz"
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
tar xf "../zlib-${ZLIB_VERSION}.tar.gz"

# --- zlib (static, needed by libpng and others) ---
cd /build/src/zlib-${ZLIB_VERSION}
cmake -G Ninja -S . -B build -DCMAKE_SYSTEM_NAME=Windows \
  -DCMAKE_SYSROOT=${SYSROOT} \
  -DCMAKE_C_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-clang \
  -DCMAKE_RC_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-windres \
  -DCMAKE_AR=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-ar \
  -DCMAKE_RANLIB=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-ranlib \
  -DCMAKE_C_FLAGS="-w" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER \
  -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY
cmake --build build --parallel
cp build/libzlibstatic.a ${SYSROOT}/lib/libz.a
cp *.h build/*.h ${SYSROOT}/include

# --- SDL3 ---
cd /build/src/SDL-${SDL3_COMMIT}
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
  -DCMAKE_C_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-clang \
  -DCMAKE_CXX_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-clang++ \
  -DCMAKE_RC_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-windres \
  -DCMAKE_AR=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-ar \
  -DCMAKE_RANLIB=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-ranlib \
  -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF
cmake --build build -j"$(nproc)"
cp build/SDL3.dll /dist
gendef /dist/SDL3.dll
aarch64-w64-mingw32-dlltool -d SDL3.def -l /dist/SDL3.lib -D /dist/SDL3.dll

# --- curl ---
cd /build/src/curl-${CURL_VERSION}
lt_cv_deplibs_check_method='pass_all' \
  ./configure --host=aarch64-w64-mingw32 --with-schannel \
  --enable-shared --disable-dict --disable-gopher \
  --disable-imap --disable-pop3 --disable-rtsp \
  --disable-smtp --disable-telnet --disable-tftp \
  --disable-smb --disable-ldap --enable-file --disable-static
make -j"$(nproc)"
cp lib/.libs/libcurl-4.dll /dist
gendef /dist/libcurl-4.dll
aarch64-w64-mingw32-dlltool -d libcurl-4.def -l /dist/curl.lib -D /dist/libcurl-4.dll

# --- libogg ---
cd /build/src/libogg-${LIBOGG_VERSION}
./configure --host=aarch64-w64-mingw32
make -j"$(nproc)"
cp src/.libs/libogg-0.dll /dist
gendef /dist/libogg-0.dll
aarch64-w64-mingw32-dlltool -d libogg-0.def -l /dist/ogg.lib -D /dist/libogg-0.dll

# --- opus ---
cd /build/src/opus-${OPUS_VERSION}
./configure --host=aarch64-w64-mingw32 CFLAGS=-D_FORTIFY_SOURCE=0
make -j"$(nproc)"
cp .libs/libopus-0.dll /dist
gendef /dist/libopus-0.dll
aarch64-w64-mingw32-dlltool -d libopus-0.def -l /dist/opus.lib -D /dist/libopus-0.dll

# --- opusfile ---
cd /build/src/opusfile-${OPUSFILE_VERSION}
DEPS_LIBS="-lopus -logg -L/dist" \
  DEPS_CFLAGS="-I/build/src/opus-${OPUS_VERSION}/include -I/build/src/libogg-${LIBOGG_VERSION}/include" \
  ./configure --host=aarch64-w64-mingw32 --disable-http
make -j"$(nproc)"
cp .libs/libopusfile-0.dll /dist
gendef /dist/libopusfile-0.dll
aarch64-w64-mingw32-dlltool -d libopusfile-0.def -l /dist/opusfile.lib -D /dist/libopusfile-0.dll

# --- freetype ---
cd /build/src/freetype-${FREETYPE_VERSION}
./configure --host=aarch64-w64-mingw32 \
  --prefix=${SYSROOT} \
  CPPFLAGS="-I${SYSROOT}/include" \
  LDFLAGS="-L${SYSROOT}/lib" \
  --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j"$(nproc)"
cp objs/.libs/libfreetype-6.dll /dist
gendef /dist/libfreetype-6.dll
aarch64-w64-mingw32-dlltool -d libfreetype-6.def -l /dist/freetype.lib -D /dist/libfreetype-6.dll

# --- sqlite ---
cd /build/src/sqlite-autoconf-${SQLITE_VERSION}
./configure --host=aarch64-w64-mingw32 CFLAGS=-DSQLITE_OMIT_LOAD_EXTENSION
make -j"$(nproc)"
cp .libs/libsqlite3-0.dll /dist
gendef /dist/libsqlite3-0.dll
aarch64-w64-mingw32-dlltool -d libsqlite3-0.def -l /dist/sqlite3.lib -D /dist/libsqlite3-0.dll

# --- x264 (static, for ffmpeg) ---
cd /build/src/x264-master
AS=aarch64-w64-mingw32-as \
  CFLAGS="-I${SYSROOT}/include" \
  LDFLAGS="-L${SYSROOT}/lib" \
  ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale \
  --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced \
  --host=aarch64-mingw32 --prefix=${SYSROOT} --cross-prefix=aarch64-w64-mingw32-
make -j"$(nproc)"

# --- ffmpeg ---
cd /build/src/ffmpeg-${FFMPEG_VERSION}
PKG_CONFIG_PATH=/build/src/x264-master \
  ./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb \
  --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib \
  --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac \
  --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample \
  --enable-swscale --enable-gpl --extra-cflags="-I/build/src/x264-master" \
  --extra-cxxflags="-I/build/src/x264-master" \
  --extra-ldflags="-L/build/src/x264-master" \
  --arch=aarch64 --target_os=mingw32 --cross-prefix=aarch64-w64-mingw32- \
  --disable-static --enable-shared --extra-libs="-lpthread -lm" --pkg-config-flags="--static" \
  --pkg-config=pkg-config
make -j"$(nproc)"
cp libavcodec/*.dll libavformat/*.dll libavutil/*.dll libswresample/*.dll libswscale/*.dll /dist/
cp libavcodec/*.lib libavformat/*.lib libavutil/*.lib libswresample/*.lib libswscale/*.lib /dist/

# --- libwebsockets ---
cd /build/src/libwebsockets-${LWS_VERSION}
# v4.3-stable tip uses vpt in pollfd.c with a guard narrower than its declaration
# (broken for Windows, fixed on lws main); no-op once the branch is fixed
sed -i 's/^#if !defined(LWS_WITH_EVENT_LIBS)$/#if !defined(LWS_WITH_EVENT_LIBS) \&\& !defined(WIN32) \&\& !defined(_WIN32)/' lib/core-net/pollfd.c
cmake -G Ninja -S . -B build -DCMAKE_SYSTEM_NAME=Windows \
  -DCMAKE_SYSROOT=${SYSROOT} \
  -DCMAKE_C_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-clang \
  -DCMAKE_CXX_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-clang++ \
  -DCMAKE_RC_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-windres \
  -DCMAKE_AR=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-ar \
  -DCMAKE_RANLIB=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-ranlib \
  -DCMAKE_C_FLAGS="-w" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER \
  -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY \
  -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF \
  -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF
cmake --build build --parallel
cp build/bin/libwebsockets.dll /dist
cp build/lws_config.h /dist
gendef /dist/libwebsockets.dll
aarch64-w64-mingw32-dlltool -d libwebsockets.def -l /dist/libwebsockets.lib -D /dist/libwebsockets.dll

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
cargo build --release --target aarch64-pc-windows-gnullvm
mkdir -p /build/zlib-rs/lib /build/zlib-rs/include
cp target/aarch64-pc-windows-gnullvm/release/libzlib_rs_shim.a /build/zlib-rs/lib/libz.a
cp "$HOME"/.cargo/registry/src/*/libz-rs-sys-${ZLIB_RS_VERSION}/include/zlib.h \
   "$HOME"/.cargo/registry/src/*/libz-rs-sys-${ZLIB_RS_VERSION}/include/zconf.h \
   /build/zlib-rs/include/

# --- libpng ---
cd /build/src/libpng-${LIBPNG_VERSION}
CPPFLAGS="-I/build/zlib-rs/include" LDFLAGS="-L/build/zlib-rs/lib" \
  ./configure --host=aarch64-w64-mingw32
make -j"$(nproc)"
cp .libs/libpng16-16.dll /dist
gendef /dist/libpng16-16.dll
aarch64-w64-mingw32-dlltool -d libpng16-16.def -l /dist/libpng16-16.lib -D /dist/libpng16-16.dll

# --- wavpack ---
cd /build/src/wavpack-${WAVPACK_VERSION}
cmake -G Ninja -S . -B build -DCMAKE_SYSTEM_NAME=Windows \
  -DCMAKE_SYSROOT=${SYSROOT} \
  -DCMAKE_C_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-clang \
  -DCMAKE_CXX_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-clang++ \
  -DCMAKE_RC_COMPILER=${TOOLCHAIN_DIR}/bin/aarch64-w64-mingw32-windres \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
  -DBUILD_SHARED_LIBS=ON \
  -DBUILD_TESTING=OFF \
  -DWAVPACK_BUILD_PROGRAMS=OFF \
  -DWAVPACK_ENABLE_THREADS=OFF \
  -DWAVPACK_INSTALL_CMAKE_MODULE=OFF \
  -DWAVPACK_INSTALL_DOCS=OFF \
  -DWAVPACK_INSTALL_PKGCONFIG_MODULE=OFF
cmake --build build -j"$(nproc)"
cp build/libwavpack-1.dll /dist
gendef /dist/libwavpack-1.dll
aarch64-w64-mingw32-dlltool -d libwavpack-1.def -l /dist/wavpack.lib -D /dist/libwavpack-1.dll

# --- Vulkan ---
cd /build
wget -q --tries=5 --timeout=60 --waitretry=10 --retry-on-http-error=429,500,502,503 "https://sdk.lunarg.com/sdk/download/${VULKAN_VERSION}/warm/VulkanRT-${VULKAN_VERSION}-Components.zip"
unzip -q "VulkanRT-${VULKAN_VERSION}-Components.zip"
cp "VulkanRT-${VULKAN_VERSION}-Components/vulkan-1."* /dist/
gendef /dist/vulkan-1.dll
aarch64-w64-mingw32-dlltool -d vulkan-1.def -l /dist/vulkan-1.lib -D /dist/vulkan-1.dll

# --- libwinpthread ---
cp ${TOOLCHAIN_DIR}/aarch64-w64-mingw32/bin/libwinpthread-1.dll /dist

# --- Strip all DLLs ---
for i in /dist/*.dll; do aarch64-w64-mingw32-strip "$i"; done

# --- Distribute to ddnet-libs layout ---
mkdir -p "$OUTPUT/curl/windows/libarm64"
cp /dist/libcurl-4.dll /dist/curl.lib "$OUTPUT/curl/windows/libarm64/"

mkdir -p "$OUTPUT/ffmpeg/windows/libarm64"
cp /dist/av*.dll /dist/sw*.dll /dist/av*.lib /dist/sw*.lib "$OUTPUT/ffmpeg/windows/libarm64/"

mkdir -p "$OUTPUT/freetype/windows/libarm64"
cp /dist/libfreetype-6.dll /dist/freetype.lib "$OUTPUT/freetype/windows/libarm64/"

mkdir -p "$OUTPUT/opus/windows/libarm64"
cp /dist/libogg-0.dll /dist/libopus-0.dll /dist/libopusfile-0.dll /dist/libwinpthread-1.dll \
   /dist/ogg.lib /dist/opus.lib /dist/opusfile.lib "$OUTPUT/opus/windows/libarm64/"

mkdir -p "$OUTPUT/png/windows/libarm64"
cp /dist/libpng16-16.dll /dist/libpng16-16.lib "$OUTPUT/png/windows/libarm64/"

mkdir -p "$OUTPUT/sdl/windows/libarm64"
cp /dist/SDL3.dll /dist/SDL3.lib "$OUTPUT/sdl/windows/libarm64/"

mkdir -p "$OUTPUT/sqlite3/windows/libarm64"
cp /dist/libsqlite3-0.dll /dist/sqlite3.lib "$OUTPUT/sqlite3/windows/libarm64/"

mkdir -p "$OUTPUT/websockets/windows/libarm64"
cp /dist/libwebsockets.dll /dist/libwebsockets.lib /dist/lws_config.h "$OUTPUT/websockets/windows/libarm64/"

mkdir -p "$OUTPUT/vulkan/windows/libarm64"
cp /dist/vulkan-1.* "$OUTPUT/vulkan/windows/libarm64/"

mkdir -p "$OUTPUT/wavpack/windows/libarm64"
cp /dist/libwavpack-1.dll /dist/wavpack.lib "$OUTPUT/wavpack/windows/libarm64/"

echo "Windows ARM64 library build complete."
