#!/usr/bin/env bash
shopt -s globstar
DIR="${0%/*}"

echo '<languages/>'
echo '<translate>'
echo '== Map Settings == <!--T:1-->'
echo '</translate>'
cat src/**/{config_variables,variables}.h | "$DIR/settings.py" CFGFLAG_GAME 10000
cat src/**/{console,netban,server,gamecontext,engine}.cpp | grep "Register(" | grep CFGFLAG_GAME | grep -v "\\/\\/" | "$DIR/commands.py" CFGFLAG_GAME 20000

echo '<translate>'
echo '== Server Settings == <!--T:3-->'
echo '</translate>'
cat ./**/{config_variables,variables}.h | "$DIR/settings.py" CFGFLAG_SERVER 30000

echo '<translate>'
echo '== Econ Settings == <!--T:5-->'
echo '</translate>'
cat ./**/{config_variables,variables}.h | "$DIR/settings.py" CFGFLAG_ECON 40000

echo '<translate>'
echo '== Server Commands == <!--T:7-->'
echo '</translate>'
(cat src/**/{console,netban,server,gamecontext,engine}.cpp | grep "Register(" | grep CFGFLAG_SERVER | grep -v "\\/\\/"; cat src/**/ddracecommands.h) | "$DIR/commands.py" CFGFLAG_SERVER 50000

echo '<translate>'
echo '== Chat Commands == <!--T:9-->'
echo '</translate>'
cat src/**/{ddracechat,ddracecommands}.h | "$DIR/commands.py" CFGFLAG_CHAT 60000

echo '<translate>'
echo '== Client Settings == <!--T:11-->'
echo '</translate>'
cat src/**/{variables,config_variables}.h | "$DIR/settings.py" CFGFLAG_CLIENT 70000

echo '<translate>'
echo '== Client Commands == <!--T:13-->'
echo '</translate>'
cat src/**/{console,netban,voting,emoticon,spectator,camera,chat,controls,friends,gameclient,client,gamecontext}.cpp | grep "Register(" | grep CFGFLAG_CLIENT | grep -v "\\/\\/" | "$DIR/commands.py" CFGFLAG_CLIENT 80000

echo '<translate>'
echo '== Tunings == <!--T:15-->'
echo '</translate>'
grep MACRO_TUNING src/game/tuning.h | "$DIR/tunings.py" 90000

echo "[[Category:Mapping]]"
echo "[[Category:Settings]]"
