#!/usr/bin/env bash
shopt -s globstar
DIR="${0%/*}"

echo '== Map Settings =='
cat src/**/{config_variables,variables}.h | "$DIR/settings.py" CFGFLAG_GAME
cat src/**/{console,netban,server,gamecontext,engine}.cpp | grep "Register(" | grep CFGFLAG_GAME | grep -v "\\/\\/" | "$DIR/commands.py" CFGFLAG_GAME

echo '== Server Settings =='
cat ./**/{config_variables,variables}.h | "$DIR/settings.py" CFGFLAG_SERVER

echo '== Econ Settings =='
cat ./**/{config_variables,variables}.h | "$DIR/settings.py" CFGFLAG_ECON

echo '== Server Commands =='
(cat src/**/{console,netban,server,gamecontext,engine}.cpp | grep "Register(" | grep CFGFLAG_SERVER | grep -v "\\/\\/"; cat src/**/ddracecommands.h) | "$DIR/commands.py" CFGFLAG_SERVER

echo '== Chat Commands =='
cat src/**/{ddracechat,ddracecommands}.h | "$DIR/commands.py" CFGFLAG_CHAT

echo '== Client Settings =='
cat src/**/{variables,config_variables}.h | "$DIR/settings.py" CFGFLAG_CLIENT

echo '== Client Commands =='
cat src/**/{console,netban,voting,emoticon,spectator,camera,chat,controls,friends,gameclient,client,gamecontext}.cpp | grep "Register(" | grep CFGFLAG_CLIENT | grep -v "\\/\\/" | "$DIR/commands.py" CFGFLAG_CLIENT

echo '== Tunings =='
grep MACRO_TUNING src/game/tuning.h | "$DIR/tunings.py"

echo "[[Category:Mapping]]"
echo "[[Category:Settings]]"
