#!/usr/bin/env zsh
today=$(date +%Y%m%d)

cd /home/teeworlds/servers

if [ $today -eq 20150908 ]; then
  cp race/01 types/race/maps
  mv secret/maps/{Aufnahmetest_AE.map,run_alkohol.map} maps
  git add maps/{Aufnahmetest_AE.map,run_alkohol.map}
  ./git-update.sh
elif [ $today -eq 20150909 ]; then
  cp race/02 types/race/maps
  mv secret/maps/{run_spring.map,run_4popi.map} maps
  git add maps/{run_spring.map,run_4popi.map}
  ./git-update.sh
elif [ $today -eq 20150910 ]; then
  cp race/03 types/race/maps
  mv secret/maps/{run_glowing_ice.map,run_skizz_loop1200.map} maps
  git add maps/{run_glowing_ice.map,run_skizz_loop1200.map}
  ./git-update.sh
elif [ $today -eq 20150911 ]; then
  cp race/04 types/race/maps
  mv secret/maps/{run_redbull.map,run_shutter.map} maps
  git add maps/{run_redbull.map,run_shutter.map}
  ./git-update.sh
elif [ $today -eq 20150912 ]; then
  cp race/05 types/race/maps
  mv secret/maps/{run_black_jack.map,run_4lollipop.map} maps
  git add maps/{run_black_jack.map,run_4lollipop.map}
  ./git-update.sh
# Tournament on 2015-09-13
elif [ $today -eq 20150914 ]; then
  cp race/06 types/race/maps
  mv secret/maps/{run_cave_grass.map,run_ankii.map} maps
  git add maps/{run_cave_grass.map,run_ankii.map}
  ./git-update.sh
elif [ $today -eq 20150915 ]; then
  cp race/07 types/race/maps
  mv secret/maps/{run_yellow.map,run_harder_than_hard.map} maps
  git add maps/{run_yellow.map,run_harder_than_hard.map}
  ./git-update.sh
elif [ $today -eq 20150916 ]; then
  cp race/08 types/race/maps
  mv secret/maps/{run_pinky.map,run_yellow_hell.map} maps
  git add maps/{run_pinky.map,run_yellow_hell.map}
  ./git-update.sh
elif [ $today -eq 20150917 ]; then
  cp race/09 types/race/maps
  mv secret/maps/{run_neonlight.map,run_frosty.map} maps
  git add maps/{run_neonlight.map,run_frosty.map}
  ./git-update.sh
elif [ $today -eq 20150918 ]; then
  cp race/10 types/race/maps
  mv secret/maps/{run_4tzoy.map,run_4xerhul.map} maps
  git add maps/{run_4tzoy.map,run_4xerhul.map}
  ./git-update.sh
elif [ $today -eq 20150919 ]; then
  cp race/11 types/race/maps
  mv secret/maps/{run_4xerhul2.map,run_alboni.map} maps
  git add maps/{run_4xerhul2.map,run_alboni.map}
  ./git-update.sh
# Tournament on 2015-09-20
elif [ $today -eq 20150921 ]; then
  cp race/12 types/race/maps
  mv secret/maps/{frustrainleave.map,pocramruinrun.map} maps
  git add maps/{frustrainleave.map,pocramruinrun.map}
  ./git-update.sh
elif [ $today -eq 20150922 ]; then
  cp race/13 types/race/maps
  mv secret/maps/{run_2rocketstwo.map,run_4mystery.map} maps
  git add maps/{run_2rocketstwo.map,run_4mystery.map}
  ./git-update.sh
elif [ $today -eq 20150923 ]; then
  cp race/14 types/race/maps
  mv secret/maps/{run_antibuguse.map,run_asr.map} maps
  git add maps/{run_antibuguse.map,run_asr.map}
  ./git-update.sh
elif [ $today -eq 20150924 ]; then
  cp race/15 types/race/maps
  mv secret/maps/{run_blue.map,run_brown.map} maps
  git add maps/{run_blue.map,run_brown.map}
  ./git-update.sh
elif [ $today -eq 20150925 ]; then
  cp race/16 types/race/maps
  mv secret/maps/{run_dfc.map,run_firestorm.map} maps
  git add maps/{run_dfc.map,run_firestorm.map}
  ./git-update.sh
elif [ $today -eq 20150926 ]; then
  cp race/17 types/race/maps
  mv secret/maps/{run_dragon.map,run_dude.map} maps
  git add maps/{run_dragon.map,run_dude.map}
  ./git-update.sh
# Tournament on 2015-09-27
elif [ $today -eq 20150928 ]; then
  cp race/18 types/race/maps
  mv secret/maps/{run_for_ghost.map,run_for_onkelz.map} maps
  git add maps/{run_for_ghost.map,run_for_onkelz.map}
  ./git-update.sh
elif [ $today -eq 20150929 ]; then
  cp race/19 types/race/maps
  mv secret/maps/{run_g6.map,run_galaxy.map} maps
  git add maps/{run_g6.map,run_galaxy.map}
  ./git-update.sh
elif [ $today -eq 20150930 ]; then
  cp race/20 types/race/maps
  mv secret/maps/{run_golden_toilet.map,run_miniatur.map} maps
  git add maps/{run_golden_toilet.map,run_miniatur.map}
  ./git-update.sh
elif [ $today -eq 20151001 ]; then
  cp race/21 types/race/maps
  mv secret/maps/{run_grass_hell.map,run_groove.map} maps
  git add maps/{run_grass_hell.map,run_groove.map}
  ./git-update.sh
elif [ $today -eq 20151002 ]; then
  cp race/22 types/race/maps
  mv secret/maps/{run_inset_into_the_heavy_jungle.map,run_longWAR.map} maps
  git add maps/{run_inset_into_the_heavy_jungle.map,run_longWAR.map}
  ./git-update.sh
elif [ $today -eq 20151003 ]; then
  cp race/23 types/race/maps
  mv secret/maps/{run_not_short.map,run_orange.map} maps
  git add maps/{run_not_short.map,run_orange.map}
  ./git-update.sh
# Tournament on 2015-10-04
elif [ $today -eq 20151005 ]; then
  cp race/24 types/race/maps
  mv secret/maps/{run_out_jungle.map,run_painted.map} maps
  git add maps/{run_out_jungle.map,run_painted.map}
  ./git-update.sh
elif [ $today -eq 20151006 ]; then
  cp race/25 types/race/maps
  mv secret/maps/{run_pencil.map,run_radioactive.map} maps
  git add maps/{run_pencil.map,run_radioactive.map}
  ./git-update.sh
elif [ $today -eq 20151007 ]; then
  cp race/26 types/race/maps
  mv secret/maps/{run_shadow.map,run_away.map} maps
  git add maps/{run_shadow.map,run_away.map}
  ./git-update.sh
elif [ $today -eq 20151008 ]; then
  cp race/27 types/race/maps
  mv secret/maps/{run_skizz_keres.map,run_hot_or_not.map} maps
  git add maps/{run_skizz_keres.map,run_hot_or_not.map}
  ./git-update.sh
elif [ $today -eq 20151009 ]; then
  cp race/28 types/race/maps
  mv secret/maps/{run_stoned.map,run_sunsetcave.map} maps
  git add maps/{run_stoned.map,run_sunsetcave.map}
  ./git-update.sh
elif [ $today -eq 20151010 ]; then
  cp race/29 types/race/maps
  mv secret/maps/{run_three.map,run_unschaffbar.map} maps
  git add maps/{run_three.map,run_unschaffbar.map}
  ./git-update.sh
# Tournament on 2015-10-11
elif [ $today -eq 20151012 ]; then
  cp race/30 types/race/maps
  mv secret/maps/{run_WARmoepopo.map,run_skizzrettex.map} maps
  git add maps/{run_WARmoepopo.map,run_skizzrettex.map}
  ./git-update.sh
elif [ $today -eq 20151013 ]; then
  cp race/31 types/race/maps
  mv secret/maps/{yoshiloop.map,climate-crisis.map} maps
  git add maps/{yoshiloop.map,climate-crisis.map}
  ./git-update.sh
fi
