#!/usr/bin/env zsh

setopt sh_word_split
unsetopt nomatch
cd /home/teeworlds/servers

for i in `cat all-types` PermaNovice Multimap SunnyLand; do
  scripts/create-votes.py $i > types/${i:l}/votes.$$.tmp &&
  mv types/${i:l}/votes.$$.tmp types/${i:l}/votes.cfg &&
  #split -l 40 types/${i:l}/votes.cfg types/${i:l}/votes.cfg
done

echo "add_vote \"reload map\" \"reload\"" >> types/test/votes.$$.tmp
echo "add_vote \"─── TESTING MAPS ───\" \"info\"" >> types/test/votes.$$.tmp
(for i in test/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) >> types/test/votes.$$.tmp
mv types/test/votes.$$.tmp types/test/votes.cfg

cp types/moderate/votes.cfg types/secret/votes.cfg
#for server in secret secret2 secret3 secret4 secret5 secret6 secret7; do
for server in secret2 secret3 secret4 secret5 secret6 secret7; do
  (for i in ~/testing/$server/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/$server/votes.$$.tmp
  mv types/$server/votes.$$.tmp types/$server/votes.cfg
done

tar cfz votes.$$.tmp.tar.gz types/*/votes.cfg maps/*.map.cfg maps/.*.map.cfg
mv votes.$$.tmp.tar.gz votes.tar.gz

for i in `cat all-locations`; do
  ssh -q $i.ddnet.tw "cd servers; tar xfz - --warning=no-timestamp" < votes.tar.gz &
done

#scripts/update-servers.sh # Should we? I think it makes the players lag for a moment. We can probably add sleeps inbetween the add_votes to stop the lags
