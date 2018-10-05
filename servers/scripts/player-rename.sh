#!/bin/sh
echo "update record_race set Name = \"$2\" where Name = \"$1\"; update record_teamrace set Name = \"$2\" where Name = \"$1\";"
