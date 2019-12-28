"""Pre-process the dictionry"""

from __future__ import annotations

from pathlib import Path
from collections import OrderedDict
import json
from typing import Union, List, Optional, Dict, TYPE_CHECKING, Tuple
from typing_extensions import Final, Literal

from strictyaml import load, MapPattern, Str, Seq

from asciicompression import ASCIICOMPRESSION

YAML_FILES: Final = (
    "A.yaml",
    "B.yaml",
    "C.yaml",
    "D.yaml",
    "E.yaml",
    "F.yaml",
    "G.yaml",
    "H.yaml",
    "I.yaml",
    "J.yaml",
    "K.yaml",
    "L.yaml",
    "M.yaml",
    "N.yaml",
    "O.yaml",
    "P.yaml",
    "Q.yaml",
    "R.yaml",
    "S.yaml",
    "T.yaml",
    "U.yaml",
    "V.yaml",
    "W.yaml",
    "X.yaml",
    "Y.yaml",
    "Z.yaml",
    "_other.yaml",
)

VOWELS: Final = (
    "AA",
    "AE",
    "AH",
    "AO",
    "AW",
    "AY",
    "AX",
    "AXR",
    "EH",
    "ER",
    "EY",
    "IH",
    "IW",
    "IY",
    "OH",
    "OO",
    "OW",
    "OY",
    "UH",
    "UW",
)

UNAMBIGUOUS_BEFORE_LMN: Final = (
    "B",
    "CH",
    "D",
    "DH",
    "F",
    "G",
    "JH",
    "K",
    "P",
    "S",
    "SH",
    "T",
    "TH",
    "V",
    "Z",
    "ZH",
)
UNAMBIGUOUS_BEFORE_L: Final = UNAMBIGUOUS_BEFORE_LMN
UNAMBIGUOUS_BEFORE_M: Final = UNAMBIGUOUS_BEFORE_LMN
UNAMBIGUOUS_BEFORE_N: Final = UNAMBIGUOUS_BEFORE_LMN

Identifier = Literal[
    "adj", "adv", "conj", "det", "intj", "noun", "num", "prep", "pron", "verb", "verb@past"
]
ENSURE_IDENT: Dict[str, Identifier] = {
    "adj": "adj",  # adjective
    "adv": "adv",  # adverb
    "conj": "conj",  # conjuction
    "det": "det",  # determiner
    "intj": "intj",  # interjection
    "noun": "noun",  # noun
    "num": "num",  # number
    "prep": "prep",  # preposition
    "pron": "pron",  # pronoun
    "verb": "verb",  # verb
    "verb@past": "verb@past",  # past form of a verb
}
SHORT_IDENTIFIERS: Dict[Identifier, str] = {
    "adj": "j",
    "adv": "a",
    "conj": "c",
    "det": "d",
    "intj": "i",
    "noun": "n",
    "num": "u",
    "prep": "p",
    "pron": "o",
    "verb": "v",
    "verb@past": "s",
}


class Pronunciation(List[str]):
    """Wrapper around list of strings that is used to have meaningful type information"""


if TYPE_CHECKING:
    RawDictionary = OrderedDict[str, Union[str, List[str], OrderedDict[str, str]]]
Dictionary = Dict[str, Union[Pronunciation, List[Pronunciation], Dict[Identifier, Pronunciation]]]


def main() -> None:
    base_path = Path("..") / "entries"
    dictionary: RawDictionary = OrderedDict()
    for yaml_file in YAML_FILES:
        dictionary.update(read_yaml_file(base_path / yaml_file))
        print(f"Parsed {yaml_file}")
    print("Convert all...")
    converted = convert_all(dictionary)
    print("Improve dictionary...")
    dictionary_improvement(converted)
    # print(converted)
    print("Minimize all...")
    minimized = minimize_all(converted)
    # print(minimized)
    with Path("dictionary.json").open("w") as fp:
        json.dump(minimized, fp, separators=(",", ":"), sort_keys=True)
    print("Done.")


def read_yaml_file(fpath: Path) -> RawDictionary:
    """Load the content of a YAML file as an ordered dictionary"""
    raw_data = fpath.open().read()
    schema = MapPattern(Str(), Str() | MapPattern(Str(), Str()) | Seq(Str()))
    dictionary: RawDictionary = load(raw_data, schema).data
    return dictionary


def convert_all(dictionary: RawDictionary) -> Dictionary:
    """Convert all entries in the raw dictionary from YAML file to our format"""
    converted: Dictionary = {}
    for word, value in dictionary.items():
        if isinstance(value, str):
            raw_pronun: str = value
            converted[word] = convert(raw_pronun)
        elif isinstance(value, list):
            raw_pronun_list: List[str] = value
            converted[word] = [convert(raw_pronun) for raw_pronun in raw_pronun_list]
        elif isinstance(value, OrderedDict):
            raw_pronun_dict: OrderedDict[str, str] = value
            converted[word] = {
                ENSURE_IDENT[ident]: convert(raw_pronun)
                for ident, raw_pronun in raw_pronun_dict.items()
            }
        else:
            raise ValueError(f"unexpected type: {type(value)}")
    return converted


def convert(raw_pronun: str) -> Pronunciation:
    """
    Convert pronunciation symbols according to spelling rules

    Args:
        raw_pronun: The raw pronunciation string

    Returns:
        converted pronunciation symbols
    """
    out = Pronunciation([])
    symbols = raw_pronun.strip().split(" ")
    symbol_iterator = iter(symbols)
    for i, symbol in enumerate(symbol_iterator):
        has_stress = symbol[0:-1] in VOWELS
        symbol_no_s = symbol[0:-1] if has_stress else symbol
        stress = symbol[-1] if has_stress else ""
        ahead1: Optional[str] = symbols[i + 1] if len(symbols) > i + 1 else None

        # whether or not the next phoneme is intervocalic
        ahead2: Optional[str] = symbols[i + 2] if len(symbols) > i + 2 else None
        # ignore apostrophes when determining whether the next phoneme is intervocalic
        if ahead2 == "'":
            ahead2 = symbols[i + 3] if len(symbols) > i + 3 else None
        next_intervocalic = count_vowels([ahead2]) != 0

        behind1: Optional[str] = symbols[i - 1] if i > 0 else None
        if behind1 == "'":
            behind1 = symbols[i - 2] if i > 1 else None

        # ================================== convert symbols ======================================
        if symbol_no_s == "AA":
            if ahead1 == "R":
                out.append("AR" + stress)
                next(symbol_iterator)  # skip the next symbol
                continue
        elif symbol_no_s == "AO":
            if ahead1 == "R":
                out.append("OR" + stress)
                next(symbol_iterator)  # skip the next symbol
                continue
        elif symbol_no_s == "AX":
            if not next_intervocalic:
                # syllablic consonants
                if ahead1 == "L" and behind1 in UNAMBIGUOUS_BEFORE_L:
                    out.append("EL")
                    next(symbol_iterator)  # skip the next symbol
                    continue
                elif ahead1 == "M" and behind1 in UNAMBIGUOUS_BEFORE_M:
                    out.append("EM")
                    next(symbol_iterator)  # skip the next symbol
                    continue
                elif ahead1 == "N" and behind1 in UNAMBIGUOUS_BEFORE_N:
                    out.append("EN")
                    next(symbol_iterator)  # skip the next symbol
                    continue
        elif symbol_no_s == "ER":
            out.append("YR" + stress)
            continue
        elif symbol_no_s == "EY":
            if ahead1 == "R":
                out.append("ER" + stress)
                next(symbol_iterator)  # skip the next symbol
                continue
        elif symbol_no_s == "IY":
            if ahead1 == "R":
                out.append("IR" + stress)
                next(symbol_iterator)  # skip the next symbol
                continue
            elif ahead1 is None and stress == "0":
                out.append("II")
                continue
        elif symbol_no_s == "OO":
            assert ahead1 != "R", "no OO before R, use AO or OH"
        elif symbol_no_s == "OW":
            if ahead1 == "R" and not next_intervocalic:
                out.append("OR" + stress)
                next(symbol_iterator)  # skip the next symbol
                continue
        elif symbol_no_s == "UH":
            assert ahead1 != "R", "no UH before R, use UW or IW"
        elif symbol_no_s == "UW":
            if ahead1 == "R":
                out.append("UR" + stress)
                next(symbol_iterator)  # skip the next symbol
                continue
        # TODO: handle `elif symbolNoS == 'R':` to turn `AW R` and `AY R` into `AW YR0` and `AY YR0`

        out.append(symbol)  # do nothing
    return out


def count_vowels(phons: List[Optional[str]]) -> int:
    """Returns the number of vowels in the given pronunciation"""
    num_vowels = 0
    for phon in phons:
        if phon is None:
            continue
        if phon[0:-1] in VOWELS or phon in ("AX", "AXR"):
            num_vowels += 1
    return num_vowels


def dictionary_improvement(dictionary: Dictionary) -> None:
    """Iteration over the dictionary entries"""
    for word, pronun_or_list in dictionary.items():
        if isinstance(pronun_or_list, Pronunciation):
            pronun: Pronunciation = pronun_or_list
            dictionary[word] = fix_unstressed_vowels(word, pronun)
        elif isinstance(pronun_or_list, dict):
            pronun_dict: Dict[Identifier, Pronunciation] = pronun_or_list
            dictionary[word] = {
                ident: fix_unstressed_vowels(word, pronun) for ident, pronun in pronun_dict.items()
            }
        else:
            pronun_list: List[Pronunciation] = pronun_or_list
            new_list = maybe_discard_variants(pronun_list)
            for i, pronun in enumerate(new_list):
                new_list[i] = fix_unstressed_vowels(word, pronun)
            dictionary[word] = new_list


def fix_unstressed_vowels(word: str, pronun: Pronunciation) -> Pronunciation:
    """Fix inconsistencies with AA0, EH0, IH0"""
    assert isinstance(pronun, Pronunciation)
    # words that start with EN- should always have IH0 at the beginning
    if word[0:2] == "EN" and (pronun[0] == "EH0" or pronun[0] == "EH2"):
        pronun[0] = "IH0"
    # AA0 doesn't exist (AA2 does exist though, e.g. "botox")
    pronun = Pronunciation(["AX" if phon == "AA0" else phon for phon in pronun])
    return pronun


def maybe_discard_variants(pronun_list: List[Pronunciation]) -> List[Pronunciation]:
    """
    If one word has multiple given pronunciations, then try to figure out which one is the best.
    """
    current_bests = [pronun_list[0]]
    # loop over the pronunciations to compare them with the current bests
    # start with i=1 because we already added the one for i=0 to `currentBests`
    for i in range(1, len(pronun_list)):
        add_to_bests = False
        candidate = pronun_list[i]
        # for each candidate, loop over the current bests and compare
        for j, current_best in enumerate(current_bests):
            diffs = get_differences(current_best, candidate)
            # number of differences that are expected because of length differences
            diffs_from_length = abs(len(current_best) - len(candidate))
            if (len(diffs) - diffs_from_length) > 2:
                # too many differences; the pronunciations are not comparable
                add_to_bests = True
                continue
            # preference for weak vowels: IH0 > AX > EH0
            # preference for syllabic consonants: prefer them over the alternative
            score_for_switching = 0  # the score for switching out the `currentBest`
            for current_symbol, new_symbol in diffs:
                change = f"{current_symbol} -> {new_symbol}"
                if change in (
                    "EH0 -> IH0",
                    "AX -> IH0",
                    "AX -> AE0",
                    "L -> EL",
                    "N -> EN",
                    "M -> EM",
                    "UH1 -> UW1",
                ):
                    score_for_switching += 1
                    continue
                elif change in (
                    "IH0 -> EH0",
                    "IH0 -> AX",
                    "AE0 -> AX",
                    "EL -> L",
                    "EN -> N",
                    "EM -> M",
                    "UW1 -> UH1",
                ):
                    score_for_switching -= 1
                    continue
                # prefer AX over other weak vowels
                if current_symbol == "AX" and len(new_symbol) > 2 and new_symbol[2] == "0":
                    score_for_switching -= 1
                elif len(current_symbol) > 2 and current_symbol[2] == "0" and new_symbol == "AX":
                    score_for_switching += 1
            if score_for_switching > 0:
                # this pronunciation is better -> replace the old one
                current_bests[j] = candidate
                add_to_bests = False  # no need to add it
                print(f"Discarded variant: {current_best}, rival: {candidate}")
                break  # we can stop comparing this candidate
            elif score_for_switching == 0:
                # they're equally good -> include both
                add_to_bests = True
            else:
                # score was less than current
                # we already have something better than this
                add_to_bests = False
                print(f"Discarded variant: {candidate}, rival: {current_best}")
                break  # we can stop comparing this candidate
        if add_to_bests:
            current_bests.append(candidate)
    return current_bests


def get_differences(pronun1: Pronunciation, pronun2: Pronunciation) -> List[Tuple[str, str]]:
    """Given two pronunciations, return a list of tuples that contain the differences"""
    diffs: List[Tuple[str, str]] = []
    total_len = max(len(pronun1), len(pronun2))
    for i in range(total_len):
        symbol1 = pronun1[i] if len(pronun1) > i else ""
        symbol2 = pronun2[i] if len(pronun2) > i else ""
        if symbol1 != symbol2:
            diffs.append((symbol1, symbol2))
    return diffs


def minimize_all(dictionary: Dictionary) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
    """Convert the symbols based on two letters to one-letter symbols"""
    minimized_dict: Dict[str, Union[str, List[str], Dict[str, str]]] = {}

    for word, pronun_or_list in dictionary.items():
        if isinstance(pronun_or_list, Pronunciation):  # only a single pronunciations
            pronun = pronun_or_list
            minimized_dict[word] = minimize(pronun)
        elif isinstance(pronun_or_list, dict):
            pronun_dict: Dict[Identifier, Pronunciation] = pronun_or_list
            minimized = {
                SHORT_IDENTIFIERS[ident]: minimize(pronun) for ident, pronun in pronun_dict.items()
            }
            if len(set(minimized.values())) == 1:  # if all the pronunciations are the same
                minimized_dict[word] = next(iter(minimized.values()))
            else:
                minimized_dict[word] = minimized
        else:
            # minimize them all and remove duplicates with `set()`
            deduplicated = list(set(minimize(pronun) for pronun in pronun_or_list))
            # if it's just one entry after de-duplication, then don't store it as a list
            minimized_dict[word] = deduplicated if len(deduplicated) > 1 else deduplicated[0]
    return minimized_dict


def minimize(pronun: Pronunciation) -> str:
    """Minimize the given pronunciation"""
    assert isinstance(pronun, Pronunciation)
    out: str = ""
    for symbol in pronun:
        # we don't really need to distinguish between no stress (0) and secondary stress (2)
        ascii_symbol = ASCIICOMPRESSION.get(symbol.replace("2", "0"))
        if ascii_symbol is None:
            raise ValueError(f'undefined ascii symbol for "{symbol}"')
        out += ascii_symbol
    return out


if __name__ == "__main__":
    main()
