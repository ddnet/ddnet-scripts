# Using a Debian 6 chroot, mingw and osxcross (with compiler-rt built)
# DO NOT COPY libogg, extract directly... Changing timestamps breaks the build and requires autotools (or cp -a)

wget http://libsdl.org/release/SDL2-2.0.18.tar.gz
wget https://patch-diff.githubusercontent.com/raw/libsdl-org/SDL/pull/4306.diff
wget https://patch-diff.githubusercontent.com/raw/libsdl-org/SDL/pull/4683.diff
wget https://curl.haxx.se/download/curl-7.79.0.tar.gz
wget https://download.savannah.gnu.org/releases/freetype/freetype-2.11.0.tar.gz
wget http://downloads.xiph.org/releases/ogg/libogg-1.3.5.tar.gz
wget https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz
wget https://downloads.xiph.org/releases/opus/opusfile-0.12.tar.gz
wget https://www.sqlite.org/2021/sqlite-autoconf-3360000.tar.gz
wget https://code.videolan.org/videolan/x264/-/archive/master/x264-master.tar.bz2
wget https://ffmpeg.org/releases/ffmpeg-4.4.tar.gz
wget https://github.com/warmcat/libwebsockets/archive/v4.2-stable.tar.gz
wget https://download.sourceforge.net/libpng/libpng-1.6.37.tar.gz

chroot debian6 bash
cat /etc/apt/sources.list
deb http://archive.debian.org/debian squeeze main contrib non-free
/root/x86-64/libogg-1.3.5/missingcd

mkdir x86-64
cd x86-64
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL2-2.0.18.tar.gz
tar xvf ../sqlite-autoconf-3360000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-4.4.tar.gz
tar xvf ../v4.2-stable.tar.gz
tar xvf ../libpng-1.6.37.tar.gz

cd libogg-1.3.5
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

cd ../SDL2-2.0.18
patch -p1 < ../../4306.diff
patch -p1 < ../../4683.diff
./configure --enable-ime CFLAGS=-fPIC --disable-video-wayland
CFLAGS=-fPIC make -j4
cp build/.libs/libSDL2-2.0.so.0.*.0 ../libSDL2-2.0.so.0
strip -s ../libSDL2-2.0.so.0

cd ../sqlite-autoconf-3360000
./configure CFLAGS="-fPIC -DSQLITE_OMIT_LOAD_EXTENSION"
make -j4
cp .libs/libsqlite3.a ..

cd ../x264-master
CFLAGS="-O2 -fno-fast-math" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --enable-pic
CFLAGS="-O2 -fno-fast-math" make -j4
cp libx264.a ..

cd ../ffmpeg-4.4
./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-fPIC -I../x264-master" --extra-cxxflags="-fPIC -I../x264-master" --extra-ldflags="-L../x264-master -ldl"
make -j4
cp */*.a ..

cd ../libwebsockets-4.2-stable
CFLAGS=-fPIC LDFLAGS=-fPIC cmake -DLWS_UNIX_SOCK=OFF -DLWS_WITH_SSL=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.a ..

cd ../libpng-1.6.37
./configure CFLAGS=-FPIC
make -j4
cp .libs/libpng16.a ..

cd ../..

mkdir x86
cd x86
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL2-2.0.18.tar.gz
tar xvf ../sqlite-autoconf-3360000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-4.4.tar.gz
tar xvf ../v4.2-stable.tar.gz
tar xvf ../libpng-1.6.37.tar.gz

cd libogg-1.3.5
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

cd ../SDL2-2.0.18
patch -p1 < ../../4306.diff
patch -p1 < ../../4683.diff
./configure --enable-ime CFLAGS="-fPIC -m32" LDFLAGS=-m32 --disable-video-wayland
LDFLAGS=-m32 CFLAGS="-fPIC -m32" make -j4
cp build/.libs/libSDL2-2.0.so.0.*.0 ../libSDL2-2.0.so.0
strip -s ../libSDL2-2.0.so.0

cd ../sqlite-autoconf-3360000
./configure CFLAGS="-fPIC -m32 -DSQLITE_OMIT_LOAD_EXTENSION"
make -j4
cp .libs/libsqlite3.a ..

cd ../x264-master
AS=nasm CFLAGS="-m32 -O2 -fno-fast-math" LDFLAGS=-m32 ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --enable-pic --host=i686-linux
CFLAGS="-m32 -O2 -fno-fast-math" LDFLAGS=-m32 make -j4
cp libx264.a ..

cd ../ffmpeg-4.4
./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-m32 -fPIC -I../x264-master" --extra-cxxflags="-m32 -fPIC -I../x264-master" --extra-ldflags="-m32 -L../x264-master -ldl" --cpu=i686
make -j4
cp */*.a ..

cd ../libwebsockets-4.2-stable
CFLAGS="-m32 -fPIC" LDFLAGS="-m32 -fPIC" cmake -DLWS_UNIX_SOCK=OFF -DLWS_WITH_SSL=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.a ..

cd ../libpng-1.6.37
./configure CFLAGS="-m32 -FPIC" --host=i686-linux
make -j4
cp .libs/libpng16.a ..

cd ../..

mkdir win64
cd win64
tar xvf ../SDL2-2.0.18.tar.gz
tar xvf ../curl-7.79.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../freetype-2.11.0.tar.gz
tar xvf ../sqlite-autoconf-3360000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-4.4.tar.gz
tar xvf ../v4.2-stable.tar.gz
tar xvf ../libpng-1.6.37.tar.gz

cd SDL2-2.0.18
patch -p1 < ../../4306.diff
patch -p1 < ../../4683.diff
./configure --host=x86_64-w64-mingw32 --enable-ime
echo "--- foo.c	2020-09-22 16:07:25.358951807 +0200
+++ src/video/windows/SDL_windowskeyboard.c	2020-09-22 16:07:50.365763770 +0200
@@ -370,7 +370,6 @@
     videodata->ime_available = SDL_TRUE;
     IME_UpdateInputLocale(videodata);
     IME_SetupAPI(videodata);
-    videodata->ime_uiless = UILess_SetupSinks(videodata);
     IME_UpdateInputLocale(videodata);
     IME_Disable(videodata, hwnd);
 }
@@ -878,9 +877,6 @@
     case WM_INPUTLANGCHANGE:
         IME_InputLangChanged(videodata);
         break;
-    case WM_IME_SETCONTEXT:
-        *lParam = 0;
-        break;
     case WM_IME_STARTCOMPOSITION:
         trap = SDL_TRUE;
         break;
" | patch src/video/windows/SDL_windowskeyboard.c
make -j4
cp build/.libs/SDL2.dll build/.libs/libSDL2.dll.a ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D SDL2.dll -l ../SDL2.lib build/.libs/*.o

cd ../curl-7.79.0
./configure --host=x86_64-w64-mingw32 --with-schannel --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
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
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian6/root/win64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian6/root/win64/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian6/root/win64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian6/root/win64/libogg-1.3.5/include" ./configure --host=x86_64-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.11.0
./configure --host=x86_64-w64-mingw32 --prefix=/usr/x86_64-w64-mingw32 CPPFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/x86_64-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
rm objs/.libs/libfreetype-6.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

cd ../sqlite-autoconf-3360000
./configure --host=x86_64-w64-mingw32 CFLAGS=-DSQLITE_OMIT_LOAD_EXTENSION
make -j4
cp .libs/libsqlite3-0.dll ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols  -D sqlite3.dll -l ../sqlite3.lib .libs/*.o

cd ../x264-master
AS=nasm CFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=x86_64-mingw32 --prefix=/usr/x86_64-w64-mingw32 --cross-prefix=x86_64-w64-mingw32-
make -j4

cd ../ffmpeg-4.4
./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-I../x264-master" --extra-cxxflags="-I../x264-master" --extra-ldflags="-L../x264-master" --arch=x86_64 --target_os=mingw32 --cross-prefix=x86_64-w64-mingw32- --disable-static --enable-shared
make -j4
cp libavcodec/avcodec-58.dll libavformat/avformat-58.dll libavutil/avutil-56.dll libswresample/swresample-3.dll libswscale/swscale-5.dll libavcodec/avcodec.lib libavformat/avformat.lib libavutil/avutil.lib libswresample/swresample.lib libswscale/swscale.lib ..

cd ../libwebsockets-4.2-stable
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-w64.cmake -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp bin/libwebsockets.dll ..

cd ../libpng-1.6.37
CFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" ./configure --host=x86_64-w64-mingw32
make -j4
cp .libs/libpng16-16.dll ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libpng16-16.dll -l ../libpng16-16.lib **/*.o

cd ..
for i in *.dll; do x86_64-w64-mingw32-strip -s $i; done

cd ../..

mkdir win32
cd win32
tar xvf ../SDL2-2.0.18.tar.gz
tar xvf ../curl-7.79.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../freetype-2.11.0.tar.gz
tar xvf ../sqlite-autoconf-3360000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-4.4.tar.gz
tar xvf ../v4.2-stable.tar.gz
tar xvf ../libpng-1.6.37.tar.gz

cd SDL2-2.0.18
patch -p1 < ../../4306.diff
patch -p1 < ../../4683.diff
./configure --host=i686-w64-mingw32 --enable-ime
echo "--- foo.c	2020-09-22 16:07:25.358951807 +0200
+++ src/video/windows/SDL_windowskeyboard.c	2020-09-22 16:07:50.365763770 +0200
@@ -370,7 +370,6 @@
     videodata->ime_available = SDL_TRUE;
     IME_UpdateInputLocale(videodata);
     IME_SetupAPI(videodata);
-    videodata->ime_uiless = UILess_SetupSinks(videodata);
     IME_UpdateInputLocale(videodata);
     IME_Disable(videodata, hwnd);
 }
@@ -878,9 +877,6 @@
     case WM_INPUTLANGCHANGE:
         IME_InputLangChanged(videodata);
         break;
-    case WM_IME_SETCONTEXT:
-        *lParam = 0;
-        break;
     case WM_IME_STARTCOMPOSITION:
         trap = SDL_TRUE;
         break;
" | patch src/video/windows/SDL_windowskeyboard.c
make -j4
cp build/.libs/SDL2.dll build/.libs/libSDL2.dll.a ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D SDL2.dll -l ../SDL2.lib build/.libs/*.o

cd ../curl-7.79.0
./configure --host=i686-w64-mingw32 --with-schannel --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
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
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian6/root/win32/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian6/root/win32/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian6/root/win32/opus-1.3.1/include -I/home/deen/isos/ddnet/debian6/root/win32/libogg-1.3.5/include" ./configure --host=i686-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.11.0
./configure --host=i686-w64-mingw32 --prefix=/usr/i686-w64-mingw32 CPPFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/i686-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

cd ../sqlite-autoconf-3360000
./configure --host=i686-w64-mingw32 CFLAGS=-DSQLITE_OMIT_LOAD_EXTENSION
make -j4
cp .libs/libsqlite3-0.dll ..
i686-w64-mingw32-dlltool -v --export-all-symbols  -D sqlite3.dll -l ../sqlite3.lib .libs/*.o

cd ../x264-master
AS=nasm CFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=i686-mingw32 --prefix=/usr/i686-w64-mingw32 --cross-prefix=i686-w64-mingw32-
make -j4

cd ../ffmpeg-4.4
./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-I../x264-master" --extra-cxxflags="-I../x264-master" --extra-ldflags="-L../x264-master" --arch=i686 --target_os=mingw32 --cross-prefix=i686-w64-mingw32- --disable-static --enable-shared
make -j4
cp libavcodec/avcodec-58.dll libavformat/avformat-58.dll libavutil/avutil-56.dll libswresample/swresample-3.dll libswscale/swscale-5.dll libavcodec/avcodec.lib libavformat/avformat.lib libavutil/avutil.lib libswresample/swresample.lib libswscale/swscale.lib ..

cd ../libwebsockets-4.2-stable
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-w32.cmake -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp bin/libwebsockets.dll ..

cd ../libpng-1.6.37
CFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" ./configure --host=i686-w64-mingw32
make -j4
cp .libs/libpng16-16.dll ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D libpng16-16.dll -l ../libpng16-16.lib **/*.o

cd ..
for i in *.dll; do i686-w64-mingw32-strip -s $i; done

cd ../..

mkdir mac64
cd mac64
tar xvf ../curl-7.79.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL2-2.0.18.tar.gz
tar xvf ../11.0.tar.gz
tar xvf ../sqlite-autoconf-3360000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-4.4.tar.gz
tar xvf ../v4.2-stable.tar.gz
tar xvf ../libpng-1.6.37.tar.gz

export PATH=/home/deen/git/osxcross/target/bin/:$PATH
export CC=o64-clang
export CXX=o64-clang++
eval `osxcross-conf`

cd curl-7.79.0
CFLAGS="-mmacosx-version-min=10.9" ./configure --host=x86_64-apple-darwin17 --without-ssl --with-secure-transport --enable-static --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cp lib/.libs/libcurl.a ..

cd ../libogg-1.3.5
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin17
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin17
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
PKG_CONFIG=/usr/sbin/pkg-config DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian6/root/mac64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian6/root/mac64/libogg-1.3.5/src/.libs/" ./configure CFLAGS="-mmacosx-version-min=10.9 -I/home/deen/isos/ddnet/debian6/root/mac64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian6/root/mac64/libogg-1.3.5/include" CPPFLAGS="-I/home/deen/isos/ddnet/debian6/root/mac64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian6/root/mac64/libogg-1.3.5/include" --host=x86_64-apple-darwin17 --disable-http
make -j4
cp .libs/libopusfile.a ..

cd ../SDL2-2.0.18
patch -p1 < ../../4306.diff
patch -p1 < ../../4683.diff
./configure --enable-ime CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin17
CFLAGS="-mmacosx-version-min=10.9" make -j4
cp build/.libs/libSDL2-2.0.0.dylib ../SDL2

cd ../11.0
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin17 --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4
cp objs/.libs/libfreetype.6.dylib ..

cd ../sqlite-autoconf-3360000
./configure --host=x86_64-apple-darwin17 CFLAGS="-fPIC -DSQLITE_OMIT_LOAD_EXTENSION"
make -j4
cp .libs/libsqlite3.0.dylib ..

cd ../x264-master
AS=nasm CFLAGS="-mmacosx-version-min=10.9 -I/usr/x86_64-apple-darwin17/include" LDFLAGS="-L/usr/x86_64-apple-darwin17/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=x86_64-apple-darwin17 --prefix=/usr/x86_64-apple-darwin17 --cross-prefix=x86_64-apple-darwin17-
make -j4

cd ../ffmpeg-4.4
./configure --disable-all --disable-appkit --disable-bzlib --disable-avfoundation --disable-coreimage --disable-securetransport --disable-audiotoolbox --disable-cuda-llvm --disable-videotoolbox --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-cxxflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-ldflags="-L../x264-master" --arch=x86_64 --target_os=darwin --cross-prefix=x86_64-apple-darwin17- --disable-static --enable-shared --cc=$CC --cxx=$CXX
make -j4
cp libavcodec/libavcodec.58.dylib libavformat/libavformat.58.dylib libavutil/libavutil.56.dylib libswresample/libswresample.3.dylib libswscale/libswscale.5.dylib ..

cd ../libwebsockets-4.2-stable
# own cross-osx.cmake
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-osx.cmake -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.18.dylib ..

cd ../libpng-1.6.37
./configure --host=x86_64-apple-darwin17
make -j4
cp .libs/libpng16.16.dylib ..
