# Pronunciation dictionary for Seinspel

This dictionary is loosely based on [cmudict](https://en.wikipedia.org/wiki/CMU_Pronouncing_Dictionary).
The entries can be found in `entries/` separated by the first letter of the words.

The pronunciations in the dictionary don't follow any real spoken accent;
rather they represent an amalgamation of the North American and British pronunciations.
Using John Wells' lexical sets, it has the following mergers:

 *  TRAP-BATH
 *  FLEECE-HAPPY
 *  KIT-EXPLORE

## Symbols

The dictionary uses [Wikipedia's respelling][wiki-respell] symbols to indicate pronunciation:

| Symbol  | IPA | Example     | Lexical set |
|---------|-----|-------------|-------------|
| A       | æ   | b**a**t     | TRAP        |
| AH      | ɑ   | b**al**m    | PALM        |
| AHY     | ɑɪ  | b**i**te    | PRICE       |
| AR      | ɑɚ  | b**ar**     | START       |
| AW      | ɔ   | b**ough**t  | THOUGHT     |
| EE      | i   | b**ea**t    | FLEECE      |
| EH      | ɛ   | b**e**t     | DRESS       |
| EW      | ju  | b**eau**ty  | (CUTE\*)    |
| EY      | eɪ  | b**ai**t    | FACE        |
| IA      | iə  | b**ea**trix | (IAN\*)     |
| IH      | ɪ   | b**i**t     | KIT         |
| O       | ɒ   | b**o**t     | LOT         |
| OH      | oʊ  | b**oa**t    | GOAT        |
| OO      | u   | b**oo**t    | GOOSE       |
| OR      | ɔɚ  | b**or**t    | NORTH       |
| OW      | aʊ  | b**ou**t    | MOUTH       |
| OY      | ɔɪ  | b**oy**     | CHOICE      |
| U       | ʊ   | b**oo**k    | FOOT        |
| UH      | ʌ   | b**u**tt    | STRUT       |
| UR      | ɝ   | b**ir**d    | NURSE       |
| ə       | ə   | comm**a**   | commA       |
| əR      | ɚ   | lett**er**  | lettER      |
| B       | b   | **b**uy |  |
| CH      | tʃ  | **Ch**ina |  |
| D       | d   | **d**ie |  |
| DH      | ð   | **th**y |  |
| EL      | l̩   | bott**le** |  |
| EM      | m̩   | rhyth**m** |  |
| EN      | n̩   | butt**on** |  |
| F       | f   | **f**ight |  |
| G       | g   | **g**uy |  |
| HH      | h   | **h**igh |  |
| J       | dʒ  | **j**ive |  |
| K       | k   | **k**ite |  |
| L       | l   | **l**ie |  |
| M       | m   | **m**y |  |
| N       | n   | **n**igh |  |
| NG      | ŋ   | si**ng** |  |
| P       | p   | **p**ie |  |
| RR      | ɹ   | **r**ye |  |
| S       | s   | **s**igh |  |
| SH      | ʃ   | **sh**y |  |
| T       | t   | **t**ie |  |
| TH      | θ   | **th**igh |  |
| V       | v   | **v**ie |  |
| W       | w   | **w**ise |  |
| WH      | ʍ   | **wh**y |  |
| Y       | j   | **y**acht |  |
| Z       | z   | **z**oo |  |
| ZH      | ʒ   | plea**s**ure |  |

\* non-standard lexical set

## Context tags

The context tags are defined in the `cainteoir.ttl` file of the
[pos-tags](https://github.com/rhdunn/pos-tags) project.

## License

Copyright (C) 1993-2015 Carnegie Mellon University. All rights reserved.  
Copyright (C) 2016-2018 Reece H. Dunn (Cainteoir Technologies). All rights reserved.

The American English Pronunciation Dictionary is released under a
[2-clause BSD](COPYING) license.

[wiki-respell]: https://en.wikipedia.org/wiki/Help:Pronunciation_respelling_key
