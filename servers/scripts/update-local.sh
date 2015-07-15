#!/bin/bash

cd /home/teeworlds/servers

types=`cat all-types`

for i in $types; do
  scripts/create-votes.py $i > types/$i/votes.$$.tmp
  mv types/$i/votes.$$.tmp types/$i/votes.cfg
  split -l 40 types/$i/votes.cfg types/$i/votes.cfg
done

(for i in test/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/test/votes.$$.tmp
mv types/test/votes.$$.tmp types/test/votes.cfg

(for i in secret/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/secret/votes.$$.tmp
mv types/secret/votes.$$.tmp types/secret/votes.cfg

#(for i in secret2/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/secret2/votes.$$.tmp
#mv types/secret2/votes.$$.tmp types/secret2/votes.cfg

(for i in secret3/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/secret3/votes.$$.tmp
mv types/secret3/votes.$$.tmp types/secret3/votes.cfg

(for i in secret4/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/secret4/votes.$$.tmp
mv types/secret4/votes.$$.tmp types/secret4/votes.cfg

(for i in secret5/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/secret5/votes.$$.tmp
mv types/secret5/votes.$$.tmp types/secret5/votes.cfg

(for i in secret6/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/secret6/votes.$$.tmp
mv types/secret6/votes.$$.tmp types/secret6/votes.cfg

(for i in secret7/maps/*.map; do b=$(basename "$i" .map); echo "add_vote \"$b\" \"change_map \\\"$b\\\"\""; done) > types/secret7/votes.$$.tmp
mv types/secret7/votes.$$.tmp types/secret7/votes.cfg

#scripts/update-servers.sh # TODO: Should we? I think it makes the players lag for a moment. We can probably add sleeps inbetween the add_votes to stop the lags
