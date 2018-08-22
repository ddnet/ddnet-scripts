#!/usr/bin/env zsh
DIR=${0:h}
echo '<div class="block">'
echo '<h2 id="map-settings">Map Settings</h2>'
cat **/{config_variables,variables}.h | $DIR/settings.py CFGFLAG_GAME
cat src/**/{console,netban,server,gamecontext,engine}.cpp | grep "Register(" | grep CFGFLAG_GAME | grep -v "\/\/" | $DIR/commands.py CFGFLAG_GAME
echo '</div>'

echo '<div class="block">'
echo '<h2 id="server-settings">Server Settings</h2>'
cat **/{config_variables,variables}.h | $DIR/settings.py CFGFLAG_SERVER
echo '</div>'

echo '<div class="block">'
echo '<h2 id="server-commands">Server Commands</h2>'
cat src/**/{console,netban,server,gamecontext,engine}.cpp | grep "Register(" | grep CFGFLAG_SERVER | grep -v "\/\/" | $DIR/commands.py CFGFLAG_SERVER
echo '</div>'

echo '<div class="block">'
echo '<h2 id="chat-commands">Chat Commands</h2>'
cat **/ddracechat.h | $DIR/commands.py CFGFLAG_CHAT
echo '</div>'

echo '<div class="block">'
echo '<h2 id="client-settings">Client Settings</h2>'
cat **/variables.h **/config_variables.h | $DIR/settings.py CFGFLAG_CLIENT
echo '</div>'

echo '<div class="block">'
echo '<h2 id="client-commands">Client Commands</h2>'
cat src/**/{console,netban,voting,emoticon,spectator,camera,chat,controls,friends,gameclient,client,gamecontext}.cpp | grep "Register(" | grep CFGFLAG_CLIENT | grep -v "\/\/" | $DIR/commands.py CFGFLAG_CLIENT
echo '</div>'

echo '<div class="block">'
echo '<h2 id="tunings">Tunings</h2>'
cat src/game/tuning.h | grep MACRO_TUNING | $DIR/tunings.py
echo '</div>'
