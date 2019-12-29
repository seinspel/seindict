#!/bin/bash

function replace {
    echo $1 -\> $2
    find ../entries/ -name  '*.yaml' -exec sed -i '' -e "s/${1}/${2}/g" {} \;
}

# first all involving AXR
replace " AY\([012]\) AXR" " IRE\1"
replace " OY\([012]\) AXR" " OIR\1"
replace " AW\([012]\) AXR" " OWR\1"

# then all involving R
replace " AA\([012]\) R" " AR\1"
replace " IY\([012]\) R" " IER\1"
replace " EY\([012]\) R" " EIR\1"
replace " IW\([012]\) R" " EWR\1"
replace " UW\([012]\) R" " OOR\1"
replace " AO\([012]\) R" " OR\1"

# then all that do NOT map onto existing symbols
replace " AE\([012]\)" " A\1"
replace " IY\([012]\)" " EE\1"
replace " IW\([012]\)" " EW\1"
replace " AY\([012]\)" " AHY\1"
replace " AX" " ə"
replace " AXR" " əR"
replace " OH\([012]\)" " O\1"
replace " OO\([012]\)" " OA\1"
replace " ER\([012]\)" " UR\1"
replace " UH\([012]\)" " U\1"

# finally those where we have to be VERY careful about the order
replace " AH\([012]\)" " UH\1"
replace " AA\([012]\)" " AH\1"
replace " UW\([012]\)" " OO\1"
replace " OW\([012]\)" " OH\1"
replace " AW\([012]\)" " OW\1"
replace " AO\([012]\)" " AW\1"

# consonants
replace " JH" " J"
replace " R" " RR"
