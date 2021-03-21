#!/usr/bin/env bash
shopt -s globstar
DIR="${0%/*}"

echo '<div class="block">'
echo '<h2 id="map-settings">Map Settings</h2>'
cat src/**/{config_variables,variables}.h | "$DIR/settings.py" CFGFLAG_GAME
cat src/**/{console,netban,server,gamecontext,engine}.cpp | grep "Register(" | grep CFGFLAG_GAME | grep -v "\\/\\/" | "$DIR/commands.py" CFGFLAG_GAME
echo '</div>'

echo '<div class="block">'
echo '<h2 id="server-settings">Server Settings</h2>'
cat ./**/{config_variables,variables}.h | "$DIR/settings.py" CFGFLAG_SERVER
echo '</div>'

echo '<div class="block">'
echo '<h2 id="econ-settings">Econ Settings</h2>'
cat ./**/{config_variables,variables}.h ./**/econ.cpp | "$DIR/settings.py" CFGFLAG_ECON
echo '</div>'

echo '<div class="block">'
echo '<h2 id="server-commands">Server Commands</h2>'
(cat src/**/{console,netban,server,gamecontext,engine}.cpp | grep "Register(" | grep CFGFLAG_SERVER | grep -v "\\/\\/"; cat src/**/ddracecommands.h) | "$DIR/commands.py" CFGFLAG_SERVER
echo '</div>'

echo '<div class="block">'
echo '<h2 id="chat-commands">Chat Commands</h2>'
cat src/**/{ddracechat,ddracecommands}.h | "$DIR/commands.py" CFGFLAG_CHAT
echo '</div>'

echo '<div class="block">'
echo '<h2 id="client-settings">Client Settings</h2>'
cat src/**/{variables,config_variables}.h | "$DIR/settings.py" CFGFLAG_CLIENT
echo '</div>'

echo '<div class="block">'
echo '<h2 id="client-commands">Client Commands</h2>'
cat src/**/{console,netban,voting,emoticon,spectator,camera,chat,controls,friends,gameclient,client,gamecontext}.cpp | grep "Register(" | grep CFGFLAG_CLIENT | grep -v "\\/\\/" | "$DIR/commands.py" CFGFLAG_CLIENT
echo '</div>'

echo '<div class="block">'
echo '<h2 id="tunings">Tunings</h2>'
grep MACRO_TUNING src/game/tuning.h | "$DIR/tunings.py"
echo '</div>'
