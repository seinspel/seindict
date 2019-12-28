#!/bin/bash

for vowel in "AA" "AE" "AH" "AO" "AW" "AY" "EH" "EY" "IH" "IY" "OH" "OO" "OW" "OY" "UH" "UW"
do
    combi="${vowel}[012] R"
    echo -ne "${combi}\t"
    # grep -o "${vowel}[012] AX" cmudict.yaml | wc -l
    grep -o "${combi}" cmudict.yaml | wc -l
done
