# Using a Debian 10 chroot, mingw and osxcross (with compiler-rt built)
# DO NOT COPY libogg, extract directly... Changing timestamps breaks the build and requires autotools (or cp -a)

cd debian11/root
rm -rf *
wget -O SDL3-d4410b9a.tar.gz https://github.com/libsdl-org/SDL/archive/d4410b9a7ccbc05f6b235b411226b01ebb91fe51.tar.gz
wget https://curl.haxx.se/download/curl-8.8.0.tar.gz
wget https://download.savannah.gnu.org/releases/freetype/freetype-2.13.2.tar.gz
wget http://downloads.xiph.org/releases/ogg/libogg-1.3.5.tar.gz
wget https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz
wget https://downloads.xiph.org/releases/opus/opusfile-0.12.tar.gz
wget https://sqlite.org/2024/sqlite-autoconf-3460000.tar.gz
wget https://code.videolan.org/videolan/x264/-/archive/master/x264-master.tar.bz2
wget https://ffmpeg.org/releases/ffmpeg-7.0.1.tar.gz
wget https://github.com/warmcat/libwebsockets/archive/v4.3-stable.tar.gz
wget https://download.sourceforge.net/libpng/libpng-1.6.43.tar.gz
wget https://github.com/dbry/WavPack/releases/download/5.9.0/wavpack-5.9.0.tar.xz

# Causes issues, see https://github.com/ddnet/ddnet/pull/5475
#git clone --recurse-submodules https://github.com/jrfonseca/drmingw
#cd drmingw
#git checkout 0.9.5
#wget https://github.com/Jupeyy/drmingw/commit/08ab91c4897c04b5919d14fc2d7c21.diff
#wget https://github.com/Jupeyy/drmingw/commit/c04387280fa3c33e70cc083ff664ed.diff
## Disable wine stuff in ci/build.sh, set -DPOSIX_THREADS=ON
#patch -p1 < 08ab91c4897c04b5919d14fc2d7c21.diff
#patch -p1 < c04387280fa3c33e70cc083ff664ed.diff
#ci/build.sh
#for i in build/mingw64/bin/*.dll; do x86_64-w64-mingw32-strip -s $i; done
#for i in build/mingw32/bin/*.dll; do i686-w64-mingw32-strip -s $i; done

CURL_CONFIGURE_OPTIONS=(
	--disable-ftp
	--disable-file
	--disable-ipfs
	--disable-ldap
	--disable-rtsp
	--disable-dict
	--disable-telnet
	--disable-tftp
	--disable-pop3
	--disable-imap
	--disable-smb
	--disable-smtp
	--disable-gopher
	--disable-mqtt
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

rustup target add x86_64-pc-windows-gnu i686-pc-windows-gnu x86_64-apple-darwin aarch64-apple-darwin
mkdir -p zlib-rs-shim/src
cd zlib-rs-shim
cat > Cargo.toml <<'EOF'
[package]
name = "zlib-rs-shim"
version = "0.0.1"
edition = "2021"
publish = false

[lib]
crate-type = ["staticlib"]
path = "src/lib.rs"

[dependencies]
libz-rs-sys = { version = "=0.6.7", default-features = false, features = ["export-symbols", "c-allocator"] }

[profile.release]
opt-level = 3
panic = "abort"
strip = true
EOF
# no_std, so that nothing but the zlib API and libc ends up in libpng: with
# default features the Rust std pulls its whole windows platform layer
# (sockets, ntdll, ...) into the DLL.
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
for target in x86_64-pc-windows-gnu i686-pc-windows-gnu x86_64-apple-darwin aarch64-apple-darwin; do
	cargo build --release --target $target
	mkdir -p ../zlib-rs/$target/lib ../zlib-rs/$target/include
	cp target/$target/release/libzlib_rs_shim.a ../zlib-rs/$target/lib/libz.a
	cp ~/.cargo/registry/src/*/libz-rs-sys-0.6.7/include/zlib.h ~/.cargo/registry/src/*/libz-rs-sys-0.6.7/include/zconf.h ../zlib-rs/$target/include/
done
cd ..

cd ../..
chroot debian11 bash
cd

mkdir x86-64
cd x86-64
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL3-d4410b9a.tar.gz
tar xvf ../sqlite-autoconf-3460000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz
tar xvf ../wavpack-5.9.0.tar.xz

cd curl-8.8.0
./configure --with-openssl --enable-shared "${CURL_CONFIGURE_OPTIONS[@]}"
make -j4
cp lib/.libs/libcurl.so ..

cd ../libogg-1.3.5
./configure CFLAGS=-fPIC
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS=-fPIC
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
DEPS_LIBS="-lopus -logg -L/root/x86-64/opus-1.3.1/.libs/ -L/root/x86-64/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-I/root/x86-64/opus-1.3.1/include -I/root/x86-64/libogg-1.3.5/include"  ./configure --disable-http CFLAGS=-fPIC
make -j4
cp .libs/libopusfile.a ..

cd ../SDL-d4410b9a7ccbc05f6b235b411226b01ebb91fe51
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF -DSDL_WAYLAND=OFF -DSDL_RPATH=OFF
cmake --build build -j4
cp build/libSDL3.so.0.*.* ../libSDL3.so.0
strip -s ../libSDL3.so.0

cd ../sqlite-autoconf-3460000
./configure CFLAGS="-fPIC -DSQLITE_OMIT_LOAD_EXTENSION"
make -j4
cp .libs/libsqlite3.a ..

cd ../x264-master
CFLAGS="-O2 -fno-fast-math" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --enable-pic
CFLAGS="-O2 -fno-fast-math" make -j4
cp libx264.a ..

cd ../ffmpeg-7.0.1
PKG_CONFIG_PATH=/root/x86-64/x264-master/ ./configure --disable-all --disable-vdpau --disable-vaapi --disable-libdrm --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-fPIC -I/root/x86-64/x264-master" --extra-cxxflags="-fPIC -I/root/x86-64/x264-master" --extra-ldflags="-L/root/x86-64/x264-master -ldl" --extra-libs="-lpthread -lm" --pkg-config-flags="--static"
make -j4
cp */*.a ..

cd ../libwebsockets-4.3-stable
CXXFLAGS=-fPIC CFLAGS=-fPIC LDFLAGS=-fPIC cmake -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.a ..
cp lws_config.h ..

cd ../libpng-1.6.43
./configure CFLAGS=-FPIC
make -j4
cp .libs/libpng16.a ..

cd ../wavpack-5.9.0
cmake -S . -B build "${WAVPACK_CMAKE_OPTIONS[@]}" -DBUILD_SHARED_LIBS=OFF -DCMAKE_C_FLAGS=-fPIC
cmake --build build -j4
cp build/libwavpack.a ..

cd ../..

mkdir x86
cd x86
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL3-d4410b9a.tar.gz
tar xvf ../sqlite-autoconf-3460000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz
tar xvf ../wavpack-5.9.0.tar.xz

cd curl-8.8.0
CFLAGS=-m32 LDFLAGS=-m32 ./configure --with-openssl --enable-shared "${CURL_CONFIGURE_OPTIONS[@]}"
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp lib/.libs/libcurl.so ..

cd ../libogg-1.3.5
CFLAGS=-m32 LDFLAGS=-m32 ./configure
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
CFLAGS=-m32 LDFLAGS=-m32 ./configure
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
CFLAGS=-m32 LDFLAGS=-m32 DEPS_LIBS="-lopus -logg -L/root/x86/opus-1.3.1/.libs/ -L/root/x86/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-m32 -I/root/x86/opus-1.3.1/include -I/root/x86/libogg-1.3.5/include"  ./configure --disable-http
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp .libs/libopusfile.a ..

# The i386 variants of the dev packages are needed here, and pkg-config must be
# pointed at them, otherwise the amd64 glibconfig.h breaks the ibus build
cd ../SDL-d4410b9a7ccbc05f6b235b411226b01ebb91fe51
PKG_CONFIG_LIBDIR=/usr/lib/i386-linux-gnu/pkgconfig:/usr/share/pkgconfig cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS=-m32 -DCMAKE_CXX_FLAGS=-m32 -DCMAKE_SHARED_LINKER_FLAGS=-m32 -DCMAKE_EXE_LINKER_FLAGS=-m32 -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF -DSDL_WAYLAND=OFF -DSDL_RPATH=OFF
cmake --build build -j4
cp build/libSDL3.so.0.*.* ../libSDL3.so.0
strip -s ../libSDL3.so.0

cd ../sqlite-autoconf-3460000
./configure CFLAGS="-fPIC -m32 -DSQLITE_OMIT_LOAD_EXTENSION"
make -j4
cp .libs/libsqlite3.a ..

cd ../x264-master
AS=nasm CFLAGS="-m32 -O2 -fno-fast-math" LDFLAGS=-m32 ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --enable-pic --host=i686-linux
CFLAGS="-m32 -O2 -fno-fast-math" LDFLAGS=-m32 make -j4
cp libx264.a ..

cd ../ffmpeg-7.0.1
PKG_CONFIG_PATH=/root/x86/x264-master ./configure --disable-all --disable-vdpau --disable-vaapi --disable-libdrm --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-m32 -fPIC -I/root/x86/x264-master" --extra-cxxflags="-m32 -fPIC -I/root/x86/x264-master" --extra-ldflags="-m32 -L/root/x86/x264-master -ldl" --cpu=i686 --extra-libs="-lpthread -lm" --pkg-config-flags="--static"
make -j4
cp */*.a ..

cd ../libwebsockets-4.3-stable
CXXFLAGS="-m32 -fPIC" CFLAGS="-m32 -fPIC" LDFLAGS="-m32 -fPIC" cmake -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.a ..
cp lws_config.h ..

cd ../libpng-1.6.43
./configure CFLAGS="-m32 -FPIC" --host=i686-linux
make -j4
cp .libs/libpng16.a ..

# wavpack detects the target CPU by compiling a probe, so -m32 already selects
# its x86 assembly; CMAKE_ASM_FLAGS has to repeat it or those files are still
# assembled as 64 bit
cd ../wavpack-5.9.0
cmake -S . -B build "${WAVPACK_CMAKE_OPTIONS[@]}" -DBUILD_SHARED_LIBS=OFF -DCMAKE_C_FLAGS="-m32 -fPIC" -DCMAKE_ASM_FLAGS=-m32
cmake --build build -j4
cp build/libwavpack.a ..

cd ../..
[exit chroot]
mkdir win64
cd win64
tar xvf ../SDL3-d4410b9a.tar.gz
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../freetype-2.13.2.tar.gz
tar xvf ../sqlite-autoconf-3460000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz
tar xvf ../wavpack-5.9.0.tar.xz

cd SDL-d4410b9a7ccbc05f6b235b411226b01ebb91fe51
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_C_COMPILER=x86_64-w64-mingw32-gcc -DCMAKE_CXX_COMPILER=x86_64-w64-mingw32-g++ -DCMAKE_RC_COMPILER=x86_64-w64-mingw32-windres -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF
cmake --build build -j4
cp build/SDL3.dll build/libSDL3.dll.a ..
# import lib for MSVC; gendef is not packaged, mkdef.py is in ddnet-scripts
x86_64-w64-mingw32-objdump -p build/SDL3.dll | python3 mkdef.py SDL3.dll > SDL3.def
x86_64-w64-mingw32-dlltool -d SDL3.def -D SDL3.dll -l ../SDL3.lib

cd ../curl-8.8.0
./configure --host=x86_64-w64-mingw32 --with-schannel --enable-shared "${CURL_CONFIGURE_OPTIONS[@]}"
make -j4 V=1
rm lib/.libs/libcurl-4.dll
cd lib
# Long command from make with fixed dll name
cd ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libcurl.dll -l ../curl.lib lib/.libs/*.o
cp lib/.libs/libcurl.dll ../libcurl.dll

cd ../libogg-1.3.5
./configure --host=x86_64-w64-mingw32
make -j4
rm src/.libs/libogg-0.dll
x86_64-w64-mingw32-gcc -shared  src/.libs/framing.o src/.libs/bitwise.o    -O20 -O2   -o src/.libs/libogg.dll -Wl,--enable-auto-image-base -Xlinker --out-implib -Xlinker src/.libs/libogg.dll.a
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libogg.dll -l ../ogg.lib src/.libs/*.o
cp src/.libs/libogg.dll ../libogg.dll

cd ../opus-1.3.1
./configure --host=x86_64-w64-mingw32 CFLAGS=-D_FORTIFY_SOURCE=0
make -j4 V=1
rm .libs/libopus-0.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libopus.dll -l ../opus.lib src/*.o
cp .libs/libopus.dll ../libopus.dll

cd ../opusfile-0.12
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian11/root/win64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian11/root/win64/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian11/root/win64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian11/root/win64/libogg-1.3.5/include" ./configure --host=x86_64-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.13.2
./configure --host=x86_64-w64-mingw32 --prefix=/usr/x86_64-w64-mingw32 CPPFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/x86_64-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
rm objs/.libs/libfreetype-6.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

cd ../sqlite-autoconf-3460000
./configure --host=x86_64-w64-mingw32 CFLAGS=-DSQLITE_OMIT_LOAD_EXTENSION
make -j4
cp .libs/libsqlite3-0.dll ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols  -D sqlite3.dll -l ../sqlite3.lib .libs/*.o

cd ../x264-master
AS=nasm CFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=x86_64-mingw32 --prefix=/usr/x86_64-w64-mingw32 --cross-prefix=x86_64-w64-mingw32-
make -j4

cd ../ffmpeg-7.0.1
# Need to switch configure to use pkg-config instead of $pkg_config
PKG_CONFIG_PATH=/home/deen/isos/ddnet/debian11/root/win64/x264-master PKG_CONFIG_LIBDIR=/usr/x86_64-w64-mingw32/lib/pkgconfig ./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-I/home/deen/isos/ddnet/debian11/root/win64/x264-master" --extra-cxxflags="-I/home/deen/isos/ddnet/debian11/root/win64/x264-master" --extra-ldflags="-L/home/deen/isos/ddnet/debian11/root/win64/x264-master" --arch=x86_64 --target_os=mingw32 --cross-prefix=x86_64-w64-mingw32- --disable-static --enable-shared --extra-libs="-lpthread -lm" --pkg-config-flags="--static"
make -j4
cp libavcodec/avcodec-61.dll libavformat/avformat-61.dll libavutil/avutil-59.dll libswresample/swresample-5.dll libswscale/swscale-8.dll libavcodec/avcodec.lib libavformat/avformat.lib libavutil/avutil.lib libswresample/swresample.lib libswscale/swscale.lib ..

cd ../libwebsockets-4.3-stable
# v4.3-stable tip uses vpt in pollfd.c with a guard narrower than its declaration
# (broken for Windows, fixed on lws main); no-op once the branch is fixed
sed -i 's/^#if !defined(LWS_WITH_EVENT_LIBS)$/#if !defined(LWS_WITH_EVENT_LIBS) \&\& !defined(WIN32) \&\& !defined(_WIN32)/' lib/core-net/pollfd.c
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-w64.cmake -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp bin/libwebsockets.dll ..
cp lws_config.h ..
# import lib for MSVC; gendef is not packaged, mkdef.py is in ddnet-scripts
x86_64-w64-mingw32-objdump -p bin/libwebsockets.dll | python3 mkdef.py libwebsockets.dll > libwebsockets.def
x86_64-w64-mingw32-dlltool -d libwebsockets.def -D libwebsockets.dll -l ../websockets.lib

cd ../libpng-1.6.43
CPPFLAGS="-I/root/zlib-rs/x86_64-pc-windows-gnu/include" LDFLAGS="-L/root/zlib-rs/x86_64-pc-windows-gnu/lib" ./configure --host=x86_64-w64-mingw32
make -j4
cp .libs/libpng16-16.dll ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libpng16-16.dll -l ../libpng16-16.lib **/*.o

cd ../wavpack-5.9.0
cmake -S . -B build "${WAVPACK_CMAKE_OPTIONS[@]}" -DBUILD_SHARED_LIBS=ON -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_C_COMPILER=x86_64-w64-mingw32-gcc -DCMAKE_CXX_COMPILER=x86_64-w64-mingw32-g++ -DCMAKE_RC_COMPILER=x86_64-w64-mingw32-windres -DCMAKE_SHARED_LINKER_FLAGS=-static-libgcc
cmake --build build -j4
cp build/libwavpack-1.dll ..
# import lib for MSVC; gendef is not packaged, mkdef.py is in ddnet-scripts
x86_64-w64-mingw32-objdump -p build/libwavpack-1.dll | python3 mkdef.py libwavpack-1.dll > wavpack.def
x86_64-w64-mingw32-dlltool -d wavpack.def -D libwavpack-1.dll -l ../wavpack.lib

cd ..
for i in *.dll; do x86_64-w64-mingw32-strip -s $i; done

cd ../..

mkdir win32
cd win32
tar xvf ../SDL3-d4410b9a.tar.gz
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../freetype-2.13.2.tar.gz
tar xvf ../sqlite-autoconf-3460000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz
tar xvf ../wavpack-5.9.0.tar.xz

cd SDL-d4410b9a7ccbc05f6b235b411226b01ebb91fe51
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_C_COMPILER=i686-w64-mingw32-gcc -DCMAKE_CXX_COMPILER=i686-w64-mingw32-g++ -DCMAKE_RC_COMPILER=i686-w64-mingw32-windres -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF
cmake --build build -j4
cp build/SDL3.dll build/libSDL3.dll.a ..
# import lib for MSVC; gendef is not packaged, mkdef.py is in ddnet-scripts
i686-w64-mingw32-objdump -p build/SDL3.dll | python3 mkdef.py SDL3.dll > SDL3.def
i686-w64-mingw32-dlltool -d SDL3.def -D SDL3.dll -l ../SDL3.lib

cd ../curl-8.8.0
./configure --host=i686-w64-mingw32 --with-schannel --enable-shared "${CURL_CONFIGURE_OPTIONS[@]}"
make -j4 V=1
rm lib/.libs/libcurl-4.dll
cd lib
# Long command from make with fixed dll name
cd ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D libcurl.dll -l ../curl.lib lib/.libs/*.o
cp lib/.libs/libcurl.dll ../libcurl.dll

cd ../libogg-1.3.5
./configure --host=i686-w64-mingw32
make -j4
rm src/.libs/libogg-0.dll
i686-w64-mingw32-gcc -shared  src/.libs/framing.o src/.libs/bitwise.o    -O20 -O2   -o src/.libs/libogg.dll -Wl,--enable-auto-image-base -Xlinker --out-implib -Xlinker src/.libs/libogg.dll.a
i686-w64-mingw32-dlltool -v --export-all-symbols -D libogg.dll -l ../ogg.lib src/.libs/*.o
cp src/.libs/libogg.dll ../libogg.dll

cd ../opus-1.3.1
./configure --host=i686-w64-mingw32 CFLAGS=-D_FORTIFY_SOURCE=0
make -j4 V=1
rm .libs/libopus-0.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libopus.dll -l ../opus.lib src/*.o
cp .libs/libopus.dll ../libopus.dll

cd ../opusfile-0.12
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian11/root/win32/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian11/root/win32/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian11/root/win32/opus-1.3.1/include -I/home/deen/isos/ddnet/debian11/root/win32/libogg-1.3.5/include" ./configure --host=i686-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.13.2
./configure --host=i686-w64-mingw32 --prefix=/usr/i686-w64-mingw32 CPPFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/i686-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

cd ../sqlite-autoconf-3460000
./configure --host=i686-w64-mingw32 CFLAGS=-DSQLITE_OMIT_LOAD_EXTENSION
make -j4
cp .libs/libsqlite3-0.dll ..
i686-w64-mingw32-dlltool -v --export-all-symbols  -D sqlite3.dll -l ../sqlite3.lib .libs/*.o

cd ../x264-master
AS=nasm CFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=i686-mingw32 --prefix=/usr/i686-w64-mingw32 --cross-prefix=i686-w64-mingw32-
make -j4

cd ../ffmpeg-7.0.1
# Need to switch configure to use pkg-config instead of $pkg_config
PKG_CONFIG_PATH=/home/deen/isos/ddnet/debian11/root/win32/x264-master PKG_CONFIG_LIBDIR=/usr/i686-w64-mingw32/lib/pkgconfig ./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-I/home/deen/isos/ddnet/debian11/root/win32/x264-master" --extra-cxxflags="-I/home/deen/isos/ddnet/debian11/root/win32/x264-master" --extra-ldflags="-L/home/deen/isos/ddnet/debian11/root/win32/x264-master" --arch=i686 --target_os=mingw32 --cross-prefix=i686-w64-mingw32- --disable-static --enable-shared --pkg-config-flags="--static --with-path=/home/deen/isos/ddnet/debian11/root/win32/x264-master"
make -j4
cp libavcodec/avcodec-61.dll libavformat/avformat-61.dll libavutil/avutil-59.dll libswresample/swresample-5.dll libswscale/swscale-8.dll libavcodec/avcodec.lib libavformat/avformat.lib libavutil/avutil.lib libswresample/swresample.lib libswscale/swscale.lib ..

cd ../libwebsockets-4.3-stable
# v4.3-stable tip uses vpt in pollfd.c with a guard narrower than its declaration
# (broken for Windows, fixed on lws main); no-op once the branch is fixed
sed -i 's/^#if !defined(LWS_WITH_EVENT_LIBS)$/#if !defined(LWS_WITH_EVENT_LIBS) \&\& !defined(WIN32) \&\& !defined(_WIN32)/' lib/core-net/pollfd.c
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-w32.cmake -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp bin/libwebsockets.dll ..
cp lws_config.h ..
# import lib for MSVC; gendef is not packaged, mkdef.py is in ddnet-scripts
i686-w64-mingw32-objdump -p bin/libwebsockets.dll | python3 mkdef.py libwebsockets.dll > libwebsockets.def
i686-w64-mingw32-dlltool -d libwebsockets.def -D libwebsockets.dll -l ../websockets.lib

cd ../libpng-1.6.43
CPPFLAGS="-I/root/zlib-rs/i686-pc-windows-gnu/include" LDFLAGS="-L/root/zlib-rs/i686-pc-windows-gnu/lib" ./configure --host=i686-w64-mingw32
make -j4
cp .libs/libpng16-16.dll ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D libpng16-16.dll -l ../libpng16-16.lib **/*.o

cd ../wavpack-5.9.0
cmake -S . -B build "${WAVPACK_CMAKE_OPTIONS[@]}" -DBUILD_SHARED_LIBS=ON -DCMAKE_SYSTEM_NAME=Windows -DCMAKE_C_COMPILER=i686-w64-mingw32-gcc -DCMAKE_CXX_COMPILER=i686-w64-mingw32-g++ -DCMAKE_RC_COMPILER=i686-w64-mingw32-windres -DCMAKE_SHARED_LINKER_FLAGS=-static-libgcc
cmake --build build -j4
cp build/libwavpack-1.dll ..
# import lib for MSVC; gendef is not packaged, mkdef.py is in ddnet-scripts
i686-w64-mingw32-objdump -p build/libwavpack-1.dll | python3 mkdef.py libwavpack-1.dll > wavpack.def
i686-w64-mingw32-dlltool -d wavpack.def -D libwavpack-1.dll -l ../wavpack.lib

cd ..
for i in *.dll; do i686-w64-mingw32-strip -s $i; done

cd ../..

mkdir mac64
cd mac64
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL3-d4410b9a.tar.gz
tar xvf ../freetype-2.13.2.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz
tar xvf ../wavpack-5.9.0.tar.xz

export PATH=/home/deen/git/osxcross/target/bin/:$PATH
export CC=o64-clang
export CXX=o64-clang++
eval `osxcross-conf`
# If build fails, it's probably due to LLVM upgrade, rebuild osxcross:
# cd ~/git/osxcross
# rm -rf build
# ./build.sh
# ./build_compiler_rt.sh

cd curl-8.8.0
# Set cross_compiling=yes in configure
CFLAGS="-mmacosx-version-min=10.9" ./configure --host=x86_64-apple-darwin20.1 --with-secure-transport --enable-static --enable-shared "${CURL_CONFIGURE_OPTIONS[@]}"
make -j4
cp lib/.libs/libcurl.a ..

cd ../libogg-1.3.5
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin20.1
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin20.1
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
PKG_CONFIG=/usr/sbin/pkg-config DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian11/root/mac64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian11/root/mac64/libogg-1.3.5/src/.libs/" ./configure CFLAGS="-mmacosx-version-min=10.9 -I/home/deen/isos/ddnet/debian11/root/mac64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian11/root/mac64/libogg-1.3.5/include" CPPFLAGS="-I/home/deen/isos/ddnet/debian11/root/mac64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian11/root/mac64/libogg-1.3.5/include" --host=x86_64-apple-darwin20.1 --disable-http
make -j4
cp .libs/libopusfile.a ..

# SDL3's GameController code needs a newer SDK than the MacOSX11.0 one osxcross
# defaults to, so point both the wrapper and cmake at MacOSX15.4.sdk. Its
# @available checks lower to ___isPlatformVersionAtLeast from compiler-rt, which
# is not installed in the system clang resource dir; CMAKE_C_STANDARD_LIBRARIES
# appends it after the objects, where ld64 can actually resolve it.
# own cross-macos-x86_64.cmake, copied into the source dir
export OSXCROSS_SDK=/home/deen/git/osxcross/target/SDK/MacOSX15.4.sdk
export OSXCROSS_SDKROOT=$OSXCROSS_SDK
export OSXCROSS_SDK_VERSION=15.4
cd ../SDL-d4410b9a7ccbc05f6b235b411226b01ebb91fe51
# Name GCMouse devices after the product instead of "Mouse", not upstream yet
sed -i 's/SDL_AddMouse(mouseID, NULL);/SDL_AddMouse(mouseID, mouse.vendorName ? [mouse.vendorName UTF8String] : NULL);/' src/video/cocoa/SDL_cocoamouse.m
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=cross-macos-x86_64.cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-mmacosx-version-min=10.15" -DCMAKE_SHARED_LINKER_FLAGS="-mmacosx-version-min=10.15" -DCMAKE_C_STANDARD_LIBRARIES="-L/home/deen/git/osxcross/build/compiler-rt/compiler-rt/build_x86_64/lib/darwin -lclang_rt.osx" -DSDL_FRAMEWORK=ON -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF -DSDL_HIDAPI_LIBUSB=OFF
cmake --build build -j4
cp -a build/SDL3.framework ..

cd ../freetype-2.13.2
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin20.1 --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4
cp objs/.libs/libfreetype.6.dylib ..

cd ../x264-master
AS=nasm CFLAGS="-mmacosx-version-min=10.9 -I/usr/x86_64-apple-darwin20.1/include" LDFLAGS="-L/usr/x86_64-apple-darwin20.1/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=x86_64-apple-darwin20.1 --prefix=/usr/x86_64-apple-darwin20.1 --cross-prefix=x86_64-apple-darwin20.1-
make -j4

cd ../ffmpeg-7.0.1
# Need to switch configure to use pkg-config instead of $pkg_config
PKG_CONFIG_PATH=/home/deen/isos/ddnet/debian11/root/mac64/x264-master ./configure --disable-all --disable-appkit --disable-bzlib --disable-avfoundation --disable-coreimage --disable-securetransport --disable-audiotoolbox --disable-cuda-llvm --disable-videotoolbox --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-cxxflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-ldflags="-L../x264-master" --arch=x86_64 --target_os=darwin --cross-prefix=x86_64-apple-darwin20.1- --disable-static --enable-shared --cc=$CC --cxx=$CXX
make -j4
cp libavcodec/libavcodec.61.dylib libavformat/libavformat.61.dylib libavutil/libavutil.59.dylib libswresample/libswresample.5.dylib libswscale/libswscale.8.dylib ..

cd ../libwebsockets-4.3-stable
# own contrib/cross-macos-x86_64.cmake
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-macos-x86_64.cmake -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.19.dylib ..
cp lws_config.h ..

cd ../libpng-1.6.43
# CC= because libpng's configure only probes $host-gcc, which osxcross does not
# ship, and then silently falls back to the host gcc
CC=x86_64-apple-darwin20.1-cc CPPFLAGS="-I/root/zlib-rs/x86_64-apple-darwin/include" LDFLAGS="-L/root/zlib-rs/x86_64-apple-darwin/lib" ./configure --host=x86_64-apple-darwin20.1
make -j4
cp .libs/libpng16.16.dylib ..

cd ../wavpack-5.9.0
# own cross-macos-x86_64.cmake, copied into the source dir. CMAKE_AR/CMAKE_RANLIB
# because the toolchain file does not set them and cmake would otherwise archive
# with the host GNU ar, which Apple's linker cannot read.
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=cross-macos-x86_64.cmake "${WAVPACK_CMAKE_OPTIONS[@]}" -DBUILD_SHARED_LIBS=OFF -DCMAKE_AR=$(which x86_64-apple-darwin20.1-ar) -DCMAKE_RANLIB=$(which x86_64-apple-darwin20.1-ranlib) -DCMAKE_C_FLAGS="-mmacosx-version-min=10.9"
cmake --build build -j4
cp build/libwavpack.a ..

# Requires osxcross with SDK >= 12.0 for oa64-clang
mkdir macarm64
cd macarm64
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL3-d4410b9a.tar.gz
tar xvf ../freetype-2.13.2.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz
tar xvf ../wavpack-5.9.0.tar.xz

export PATH=/home/deen/git/osxcross/target/bin/:$PATH
export CC=oa64-clang
export CXX=oa64-clang++
eval `osxcross-conf`

cd curl-8.8.0
# Set cross_compiling=yes in configure
CFLAGS="-mmacosx-version-min=10.9" ./configure --host=aarch64-apple-darwin20.1 --with-secure-transport --enable-static --enable-shared "${CURL_CONFIGURE_OPTIONS[@]}"
make -j4
cp lib/.libs/libcurl.a ..

cd ../libogg-1.3.5
./configure CFLAGS="-mmacosx-version-min=10.9" --host=aarch64-apple-darwin20.1
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS="-mmacosx-version-min=10.9" --host=aarch64-apple-darwin20.1
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
PKG_CONFIG=/usr/sbin/pkg-config DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian11/root/macarm64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian11/root/macarm64/libogg-1.3.5/src/.libs/" ./configure CFLAGS="-mmacosx-version-min=10.9 -I/home/deen/isos/ddnet/debian11/root/macarm64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian11/root/macarm64/libogg-1.3.5/include" CPPFLAGS="-I/home/deen/isos/ddnet/debian11/root/macarm64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian11/root/macarm64/libogg-1.3.5/include" --host=aarch64-apple-darwin20.1 --disable-http
make -j4
cp .libs/libopusfile.a ..

# own cross-macos-arm64.cmake, copied into the source dir; see the x86_64 SDL3 notes
export OSXCROSS_SDK=/home/deen/git/osxcross/target/SDK/MacOSX15.4.sdk
export OSXCROSS_SDKROOT=$OSXCROSS_SDK
export OSXCROSS_SDK_VERSION=15.4
cd ../SDL-d4410b9a7ccbc05f6b235b411226b01ebb91fe51
sed -i 's/SDL_AddMouse(mouseID, NULL);/SDL_AddMouse(mouseID, mouse.vendorName ? [mouse.vendorName UTF8String] : NULL);/' src/video/cocoa/SDL_cocoamouse.m
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=cross-macos-arm64.cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-mmacosx-version-min=10.15" -DCMAKE_SHARED_LINKER_FLAGS="-mmacosx-version-min=10.15" -DCMAKE_C_STANDARD_LIBRARIES="-L/home/deen/git/osxcross/build/compiler-rt/compiler-rt/build_arm64/lib/darwin -lclang_rt.osx" -DSDL_FRAMEWORK=ON -DSDL_SHARED=ON -DSDL_STATIC=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF -DSDL_HIDAPI_LIBUSB=OFF
cmake --build build -j4
cp -a build/SDL3.framework ..

cd ../freetype-2.13.2
./configure CFLAGS="-mmacosx-version-min=10.9" --host=aarch64-apple-darwin20.1 --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4
cp objs/.libs/libfreetype.6.dylib ..

cd ../x264-master
CFLAGS="-mmacosx-version-min=10.9 -I/usr/aarch64-apple-darwin20.1/include" LDFLAGS="-L/usr/aarch64-apple-darwin20.1/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=aarch64-apple-darwin20.1 --prefix=/usr/aarch64-apple-darwin20.1 --cross-prefix=aarch64-apple-darwin20.1-
make -j4

cd ../ffmpeg-7.0.1
# Need to switch configure to use pkg-config instead of $pkg_config
PKG_CONFIG_PATH=/home/deen/isos/ddnet/debian11/root/macarm64/x264-master ./configure --disable-all --disable-appkit --disable-bzlib --disable-avfoundation --disable-coreimage --disable-securetransport --disable-audiotoolbox --disable-cuda-llvm --disable-videotoolbox --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-cxxflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-ldflags="-L../x264-master" --arch=aarch64 --target_os=darwin --cross-prefix=aarch64-apple-darwin20.1- --disable-static --enable-shared --cc=$CC --cxx=$CXX
make -j4
cp libavcodec/libavcodec.61.dylib libavformat/libavformat.61.dylib libavutil/libavutil.59.dylib libswresample/libswresample.5.dylib libswscale/libswscale.8.dylib ..

cd ../libwebsockets-4.3-stable
# own contrib/cross-macos-arm64.cmake
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-macos-arm64.cmake -DLWS_IPV6=ON -DLWS_WITHOUT_TESTAPPS=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.19.dylib ..
cp lws_config.h ..

cd ../libpng-1.6.43
CC=aarch64-apple-darwin20.1-cc CPPFLAGS="-I/root/zlib-rs/aarch64-apple-darwin/include" LDFLAGS="-L/root/zlib-rs/aarch64-apple-darwin/lib" ./configure --host=aarch64-apple-darwin20.1
make -j4
cp .libs/libpng16.16.dylib ..

cd ../wavpack-5.9.0
# own cross-macos-arm64.cmake, copied into the source dir; see the x86_64 lane
cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=cross-macos-arm64.cmake "${WAVPACK_CMAKE_OPTIONS[@]}" -DBUILD_SHARED_LIBS=OFF -DCMAKE_AR=$(which aarch64-apple-darwin20.1-ar) -DCMAKE_RANLIB=$(which aarch64-apple-darwin20.1-ranlib) -DCMAKE_C_FLAGS="-mmacosx-version-min=10.9"
cmake --build build -j4
cp build/libwavpack.a ..

# The public wavpack.h in ddnet-libs/wavpack/include is the one from the source
# tarball (include/wavpack.h); it is identical for every platform.

# fix output paths in shared libs on macOS:
# (SDL3's cmake framework build already sets @rpath/SDL3.framework/Versions/A/SDL3)
otool -L $i
install_name_tool -id @rpath/libpng16.16.dylib libpng16.16.dylib
install_name_tool -id @rpath/libwebsockets.19.dylib libwebsockets.19.dylib
install_name_tool -id @rpath/libfreetype.6.dylib libfreetype.6.dylib
install_name_tool -id @rpath/libswscale.8.dylib libswscale.8.dylib
install_name_tool -change /usr/local/lib/libavutil.59.dylib @rpath/libavutil.59.dylib libswscale.8.dylib
install_name_tool -id @rpath/libswresample.5.dylib libswresample.5.dylib
install_name_tool -change /usr/local/lib/libavutil.59.dylib @rpath/libavutil.59.dylib libswresample.5.dylib
install_name_tool -id @rpath/libavutil.59.dylib libavutil.59.dylib
install_name_tool -id @rpath/libavformat.61.dylib libavformat.61.dylib
install_name_tool -change /usr/local/lib/libavcodec.61.dylib @rpath/libavcodec.61.dylib libavformat.61.dylib
install_name_tool -change /usr/local/lib/libavutil.59.dylib @rpath/libavutil.59.dylib libavformat.61.dylib
install_name_tool -id @rpath/libavcodec.61.dylib libavcodec.61.dylib
install_name_tool -change /usr/local/lib/libavutil.59.dylib @rpath/libavutil.59.dylib libavcodec.61.dylib
# TODO: Can this be done automatically by setting --prefix=@rpath?

# create fat binaries for mac
rm -rf libfat; mkdir libfat; for i in lib64/*.dylib; do lipo -create $i libarm64/${i:t} -output libfat/${i:t}; done
mkdir libfat; for i in lib64/*.a; do lipo -create $i libarm64/${i:t} -output libfat/${i:t}; done
cd sdl/mac; rm -rf libfat/SDL3.framework; cp -a lib64/SDL3.framework libfat/SDL3.framework; rm libfat/SDL3.framework/Versions/A/SDL3; lipo -create lib64/SDL3.framework/Versions/A/SDL3 libarm64/SDL3.framework/Versions/A/SDL3 -output libfat/SDL3.framework/Versions/A/SDL3

# sign all arm64 and fat dylibs using codesign on macOS (until https://github.com/thefloweringash/sigtool/issues/8 is fixed, then we can automate it on Linux)
for i in **/libarm64/*.dylib **/libfat/*.dylib sdl/mac/libarm64/SDL3.framework sdl/mac/libfat/SDL3.framework; do codesign -s - $i; done

# The SDL3 headers in ddnet-libs (sdl/include/<platform>/SDL3/) are just the
# SDL3-x.y.z/include/ tree, the same one gen_libs.sh copies for android/webasm.
# ddnet-libs/sdl/webasm and sdl/android (and sdl/java) come from that script.

# The lws_config.h files collected above go into the per-platform ddnet-libs
# include dirs (websockets/include/{windows,mac,linux}/lws_config.h, next to the
# lws headers); lws only generates it per build. The windows file combines the
# x86/x64 and arm64 configs behind an architecture #if.

# Windows arm64 is not built above; it uses the llvm-mingw docker lane from
# ddnet#8800, now release/docker in this repo. It builds the same zlib-rs shim,
# so its libpng uses zlib-rs too:
#   cd release/docker
#   docker build --platform linux/amd64 -f Dockerfile.libs-winarm64 -t ddnet-libs-winarm64 .
#   docker run --rm --platform linux/amd64 -v ./output:/output ddnet-libs-winarm64
# Dockerfile.libs-windows (PLATFORM=64/32) and Dockerfile.libs-linux are docker
# equivalents of the chroot sections above.
