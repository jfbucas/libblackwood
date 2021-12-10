cat EternityII_Clueless.stats | while read s n a; do [ "$(($s % 16))" == "0" ] && echo "" ; echo -n "$n,";  done > EternityII_Clueless.stats.csv
