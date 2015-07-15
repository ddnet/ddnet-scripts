#!/usr/bin/env zsh
today=$(date +%Y%m%d)

cd /home/teeworlds/servers

if [ $today -eq 20150623 ]; then
  cp ddmax/1 types/ddmax/maps
  mv secret4/maps/{Hell\ 1\ V2.map,Heroic.map,HeyYa.map,Hook\ Fever.map,HearTcross.map} maps
  git add maps/{Hell\ 1\ V2.map,Heroic.map,HeyYa.map,Hook\ Fever.map,HearTcross.map}
  ./git-update.sh
elif [ $today -eq 20150624 ]; then
  cp ddmax/2 types/ddmax/maps
  mv secret4/maps/{Hope*map,Ice.map,Imagination3.map,Insane.map} maps
  git add maps/{Hope*map,Ice.map,Imagination3.map,Insane.map}
  ./git-update.sh
elif [ $today -eq 20150625 ]; then
  cp ddmax/3 types/ddmax/maps
  mv secret4/maps/{Icy\ Morning.map,Icy\ Mountain.map,illusion.map,Impulse_01.map,Insane\ 2.map} maps
  git add maps/{Icy\ Morning.map,Icy\ Mountain.map,illusion.map,Impulse_01.map,Insane\ 2.map}
  ./git-update.sh
elif [ $today -eq 20150626 ]; then
  cp ddmax/4 types/ddmax/maps
  mv secret4/maps/{Impulse_02.map,Impulse_03.map,JLI\ 1.map,Inspire.map} maps
  git add maps/{Impulse_02.map,Impulse_03.map,JLI\ 1.map,Inspire.map}
  ./git-update.sh
elif [ $today -eq 20150627 ]; then
  cp ddmax/5 types/ddmax/maps
  mv secret4/maps/{Jungle.map,JustMap.map,LATOM.map,Jajka.map,Lost\ Castle.map} maps
  git add maps/{Jungle.map,JustMap.map,LATOM.map,Jajka.map,Lost\ Castle.map}
  ./git-update.sh
elif [ $today -eq 20150629 ]; then
  cp ddmax/6 types/ddmax/maps
  mv secret4/maps/{lemonland.map,Love\ 0.6.map,lovely\ me.map,LowPossibility3.1.map,MicCore.map} maps
  git add maps/{lemonland.map,Love\ 0.6.map,lovely\ me.map,LowPossibility3.1.map,MicCore.map}
  ./git-update.sh
elif [ $today -eq 20150630 ]; then
  cp ddmax/7 types/ddmax/maps
  mv secret4/maps/{lovely\ me2.map,mario\(=D\).map,Maroon.map,MCPV.map,Multivitamin.map} maps
  git add maps/{lovely\ me2.map,mario\(=D\).map,Maroon.map,MCPV.map,Multivitamin.map}
  ./git-update.sh
elif [ $today -eq 20150701 ]; then
  cp ddmax/8 types/ddmax/maps
  mv secret4/maps/{Michler.map,Michler\ 2.map,Moon\ of\ the\ Jungle.map,Next.map,Natura.map} maps
  git add maps/{Michler.map,Michler\ 2.map,Moon\ of\ the\ Jungle.map,Next.map,Natura.map}
  ./git-update.sh
elif [ $today -eq 20150702 ]; then
  cp ddmax/9 types/ddmax/maps
  mv secret4/maps/{Next\ 2.map,o_O.map,Pandaland.map,Night\ Jungle.map,Notice\ 1.map} maps
  git add maps/{Next\ 2.map,o_O.map,Pandaland.map,Night\ Jungle.map,Notice\ 1.map}
  ./git-update.sh
elif [ $today -eq 20150703 ]; then
  cp ddmax/10 types/ddmax/maps
  mv secret4/maps/{Pandora.map,pepsi.map,R2D2.map,Outlet.map,Paik.map} maps
  git add maps/{Pandora.map,pepsi.map,R2D2.map,Outlet.map,Paik.map}
  ./git-update.sh
elif [ $today -eq 20150704 ]; then
  cp ddmax/11 types/ddmax/maps
  mv secret4/maps/{RageOne.map,Rainboom.map,Reach\ Pluto.map,Picklock.map,Poke.map} maps
  git add maps/{RageOne.map,Rainboom.map,Reach\ Pluto.map,Picklock.map,Poke.map}
  ./git-update.sh
elif [ $today -eq 20150705 ]; then
  cp ddmax/12 types/ddmax/maps
  mv secret4/maps/{Regret.map,Revolution.map,RockBlock\ 1.map,Rampage.map,Repeat.map} maps
  git add maps/{Regret.map,Revolution.map,RockBlock\ 1.map,Rampage.map,Repeat.map}
  ./git-update.sh
elif [ $today -eq 20150706 ]; then
  cp ddmax/13 types/ddmax/maps
  mv secret4/maps/{Rovo.map,run_the_cube.map,S-Race\ 1.map,Rockita.map,Scabrous\ 2.map} maps
  git add maps/{Rovo.map,run_the_cube.map,S-Race\ 1.map,Rockita.map,Scabrous\ 2.map}
  ./git-update.sh
elif [ $today -eq 20150707 ]; then
  cp ddmax/14 types/ddmax/maps
  mv secret4/maps/{S-Race\ 2.map,secreT.map,Shaxx.map,Skyfly.map,SkyIsland.map} maps
  git add maps/{S-Race\ 2.map,secreT.map,Shaxx.map,Skyfly.map,SkyIsland.map}
  ./git-update.sh
elif [ $today -eq 20150708 ]; then
  cp ddmax/15 types/ddmax/maps
  mv secret4/maps/{SilentNight.map,Sky\ line.map,Slim.map,slow.map} maps
  git add maps/{SilentNight.map,Sky\ line.map,Slim.map,slow.map}
  ./git-update.sh
elif [ $today -eq 20150709 ]; then
  cp ddmax/16 types/ddmax/maps
  mv secret4/maps/{smile.map,Snowy\ Sakura\ I.map,Spectrus\ I.map,Skyisland3.map,skynet\ compilation.map} maps
  git add maps/{smile.map,Snowy\ Sakura\ I.map,Spectrus\ I.map,Skyisland3.map,skynet\ compilation.map}
  ./git-update.sh
elif [ $today -eq 20150710 ]; then
  cp ddmax/17 types/ddmax/maps
  mv secret4/maps/{Stamina.map,Standby.map,Steff\ I\ beginning.map,Steff\ III\ peace.map,The\ Tower.map} maps
  git add maps/{Stamina.map,Standby.map,Steff\ I\ beginning.map,Steff\ III\ peace.map,The\ Tower.map}
  ./git-update.sh
elif [ $today -eq 20150711 ]; then
  cp ddmax/18 types/ddmax/maps
  mv secret4/maps/{StormzZ.map,The\ Captive\ Mind.map,Tribute\ 1.map,Therapy.map,Think\!\ 2.map} maps
  git add maps/{StormzZ.map,The\ Captive\ Mind.map,Tribute\ 1.map,Therapy.map,Think\!\ 2.map}
  ./git-update.sh
elif [ $today -eq 20150712 ]; then
  cp ddmax/19 types/ddmax/maps
  mv secret4/maps/{Tribute\ 2.map,TsinmaS.map,Tylost.map,Veni\ Vidi\ Vici.map,Volcano.map} maps
  git add maps/{Tribute\ 2.map,TsinmaS.map,Tylost.map,Veni\ Vidi\ Vici.map,Volcano.map}
  ./git-update.sh
elif [ $today -eq 20150713 ]; then
  cp ddmax/20 types/ddmax/maps
  mv secret4/maps/{Tylost\ 2.map,valentees.map,VeryLow1.map,VeryLow2.map,whatever.map} maps
  git add maps/{Tylost\ 2.map,valentees.map,VeryLow1.map,VeryLow2.map,whatever.map}
  ./git-update.sh
elif [ $today -eq 20150714 ]; then
  cp ddmax/21 types/ddmax/maps
  mv secret4/maps/{Violet.map,WinterMine.map,X-Cross.map,Woader.map} maps
  git add maps/{Violet.map,WinterMine.map,X-Cross.map,Woader.map}
  ./git-update.sh
elif [ $today -eq 20150715 ]; then
  cp ddmax/22 types/ddmax/maps
  mv secret4/maps/{Xeno\ Race\ \#1.map,Yin\&Yang.map,World\ of\ Magic.map} maps
  git add maps/{Xeno\ Race\ \#1.map,Yin\&Yang.map,World\ of\ Magic.map}
  ./git-update.sh
fi
