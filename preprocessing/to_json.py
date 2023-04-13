"""Pre-process the dictionry"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Final, Literal, TypeAlias, TypeVar

from ruamel.yaml import YAML

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

VOWELS: Final = {
    "A",
    "AH",
    "AHY",
    "AR",
    "AW",
    "EE",
    "EH",
    "EL",
    "EW",
    "EY",
    "IA",
    "IH",
    "O",
    "OA",
    "OH",
    "OO",
    "OR",
    "OW",
    "OY",
    "U",
    "UH",
    "UR",
    "ə",
    "əR",
}

UNAMBIGUOUS_BEFORE_LMN: Final = {
    "B",
    "CH",
    "D",
    "DH",
    "F",
    "G",
    "J",
    "K",
    "P",
    "S",
    "SH",
    "T",
    "TH",
    "V",
    "Z",
    "ZH",
}
UNAMBIGUOUS_BEFORE_L: Final = UNAMBIGUOUS_BEFORE_LMN
UNAMBIGUOUS_BEFORE_M: Final = UNAMBIGUOUS_BEFORE_LMN
UNAMBIGUOUS_BEFORE_N: Final = UNAMBIGUOUS_BEFORE_LMN

Identifier: TypeAlias = Literal[
    "adj", "adv", "conj", "det", "intj", "noun", "num", "prep", "pron", "verb", "verb@past"
]
SHORT_IDENTIFIERS: dict[Identifier, str] = {
    "adj": "j",  # adjective
    "adv": "a",  # adverb
    "conj": "c",  # conjuction
    "det": "d",  # determiner
    "intj": "i",  # interjection
    "noun": "n",  # noun
    "num": "u",  # number
    "prep": "p",  # preposition
    "pron": "o",  # pronoun
    "verb": "v",  # verb
    "verb@past": "s",  # past form of a verb
}

# fmt: off
ENGLISH_LETTERS: Final = {"'", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
    "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "Ç",
    "É", "Ë", "Ï", "Ñ", "Ö", "Ü"}
# fmt: on


class Pronunciation(list[str]):
    """Wrapper around list of strings that is used to have meaningful type information"""


T = TypeVar("T")
U = TypeVar("U")
Entry: TypeAlias = dict[U, T] | list[T] | T
RawDictionary = dict[str, Entry[str, str]]
Dictionary: TypeAlias = dict[str, Entry[Identifier, Pronunciation]]


def main() -> None:
    base_path = Path("..") / "entries"
    dictionary: RawDictionary = {}
    for yaml_file in YAML_FILES:
        dictionary.update(read_yaml_file(base_path / yaml_file))
        print(f"Parsed {yaml_file}")
    print("Convert all...")
    converted: Dictionary = {}
    for word, value in dictionary.items():
        converted[word] = convert_any(word, value)
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
    """Load the content of a YAML file as an ordered dictionary."""
    yaml = YAML(typ="safe")
    with fpath.open() as fp:
        dictionary = yaml.load(fp)
    return dictionary


def convert_any(word: str, value: Entry[str, str]) -> Entry[Identifier, Pronunciation]:
    assert all(letter in ENGLISH_LETTERS for letter in word), word
    match value:
        case str() as raw_pronun:
            return convert(raw_pronun, word)
        case list() as raw_pronun_list:
            return [convert(raw_pronun, word) for raw_pronun in raw_pronun_list]
        case dict() as raw_pronun_dict:
            return {
                ensure_ident(ident, word): convert(
                    raw_pronun, word, is_interjection=ident == "intj"
                )
                for ident, raw_pronun in raw_pronun_dict.items()
            }
        case _:
            raise ValueError(f"unexpected type: {type(value)}")


def ensure_ident(ident: str, word: str) -> Identifier:
    match ident:
        case (
            "adj"
            | "adv"
            | "conj"
            | "det"
            | "intj"
            | "noun"
            | "num"
            | "prep"
            | "pron"
            | "verb"
            | "verb@past"
        ):
            return ident
        case _:
            raise ValueError(f"incorrect identifier '{ident}' in word '{word}'")


def convert(raw_pronun: str, word: str, is_interjection: bool = False) -> Pronunciation:
    """
    Convert pronunciation symbols according to spelling rules

    :param raw_pronun: The raw pronunciation string
    :returns: converted pronunciation symbols
    """
    assert isinstance(word, str), f"all entry keys must be strings ({word}: {raw_pronun})"
    assert isinstance(raw_pronun, str), f"all pronunciations must be strings ({word}: {raw_pronun})"
    out = Pronunciation([])
    symbols = raw_pronun.strip().split(" ")
    symbol_iterator = enumerate(symbols)
    for i, symbol in symbol_iterator:
        has_stress = symbol[-1] in ("0", "1", "2")
        symbol_no_s = symbol[0:-1] if has_stress else symbol
        stress = symbol[-1] if has_stress else ""
        ahead1: str | None = symbols[i + 1] if len(symbols) > i + 1 else None

        # whether or not the next phoneme is intervocalic
        ahead2: str | None = symbols[i + 2] if len(symbols) > i + 2 else None
        # ignore apostrophes when determining whether the next phoneme is intervocalic
        if ahead2 == "'":
            ahead2 = symbols[i + 3] if len(symbols) > i + 3 else None
        next_intervocalic = count_vowels([ahead2]) != 0
        next_vowel = count_vowels([ahead1 if ahead1 != "'" else ahead2])

        behind1: str | None = symbols[i - 1] if i > 0 else None

        # ================================ handle special cases ===================================
        match symbol_no_s:
            case "ə":
                if not next_intervocalic:
                    # ignore apostrophes for this
                    if behind1 == "'":
                        behind1 = symbols[i - 2] if i > 1 else None
                    # syllablic consonants
                    match ahead1:
                        case "L" if behind1 in UNAMBIGUOUS_BEFORE_L:
                            out.append("EL")
                            next(symbol_iterator)  # skip the next symbol
                            continue
                        case "M" if behind1 in UNAMBIGUOUS_BEFORE_M:
                            out.append("EM")
                            next(symbol_iterator)  # skip the next symbol
                            continue
                        case "N" if behind1 in UNAMBIGUOUS_BEFORE_N:
                            out.append("EN")
                            next(symbol_iterator)  # skip the next symbol
                            continue
                        case _:
                            pass
            case "EE":
                if ahead1 is None and stress == "0":
                    out.append("II")
                    continue
            case "OA":
                cloth_environ = ahead1 in ("F", "G", "K", "N", "NG", "S", "SH", "TH")
                assert cloth_environ, f"{word}: OA only before F, G, K, N, NG, S, SH, TH"
            case "A" | "EH" | "IH" | "O" | "U" | "UH":
                is_checked = (ahead1 is not None and not next_vowel) or is_interjection
                assert (
                    is_checked
                ), f"{word}: checked vowels only before consonants (or be interjection)"
            case "RR":
                is_prevocalic = next_vowel or ahead1 == "W" or behind1 == "'"
                assert (
                    is_prevocalic
                ), f"{word}: RR must be followed by a vowel or W, or preceded by '"
            case _:
                pass

        out.append(symbol)  # do nothing
    return out


def count_vowels(phons: list[str | None]) -> int:
    """Returns the number of vowels in the given pronunciation"""
    num_vowels = 0
    for phon in phons:
        if phon is None:
            continue
        if phon[0:-1] in VOWELS or phon in ("EL", "ə", "əR"):
            num_vowels += 1
    return num_vowels


def dictionary_improvement(dictionary: Dictionary) -> None:
    """Iteration over the dictionary entries"""
    for word, pronun_or_list in dictionary.items():
        if isinstance(pronun_or_list, Pronunciation):
            pronun: Pronunciation = pronun_or_list
            dictionary[word] = fix_unstressed_vowels(word, pronun)
        elif isinstance(pronun_or_list, dict):
            pronun_dict: dict[Identifier, Pronunciation] = pronun_or_list
            dictionary[word] = {
                ident: fix_unstressed_vowels(word, pronun) for ident, pronun in pronun_dict.items()
            }
        else:
            pronun_list: list[Pronunciation] = pronun_or_list
            new_list = maybe_discard_variants(pronun_list)
            for i, pronun in enumerate(new_list):
                new_list[i] = fix_unstressed_vowels(word, pronun)
            dictionary[word] = new_list


def fix_unstressed_vowels(word: str, pronun: Pronunciation) -> Pronunciation:
    """Fix inconsistencies with AH0, EH0, IH0"""
    assert isinstance(pronun, Pronunciation)
    # words that start with EN- should always have IH0 at the beginning
    if word[0:2] == "EN" and (pronun[0] == "EH0" or pronun[0] == "EH2"):
        pronun[0] = "IH0"
    # AA0 doesn't exist (AA2 does exist though, e.g. "botox")
    pronun = Pronunciation(["ə" if phon == "AH0" else phon for phon in pronun])
    return pronun


def maybe_discard_variants(pronun_list: list[Pronunciation]) -> list[Pronunciation]:
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
            # preference for weak vowels: IH0 > ə > EH0
            # preference for syllabic consonants: prefer them over the alternative
            score_for_switching = 0  # the score for switching out the `currentBest`
            for current_symbol, new_symbol in diffs:
                change = f"{current_symbol} -> {new_symbol}"
                if change in (
                    "EH0 -> IH0",
                    "ə -> IH0",
                    "ə -> A0",
                    "L -> EL",
                    "N -> EN",
                    "M -> EM",
                    "U1 -> OO1",
                ):
                    score_for_switching += 1
                    continue
                elif change in (
                    "IH0 -> EH0",
                    "IH0 -> ə",
                    "A0 -> ə",
                    "EL -> L",
                    "EN -> N",
                    "EM -> M",
                    "OO1 -> U1",
                ):
                    score_for_switching -= 1
                    continue
                # prefer ə over other weak vowels
                if current_symbol == "ə" and len(new_symbol) > 2 and new_symbol[2] == "0":
                    score_for_switching -= 1
                elif len(current_symbol) > 2 and current_symbol[2] == "0" and new_symbol == "ə":
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


def get_differences(pronun1: Pronunciation, pronun2: Pronunciation) -> list[tuple[str, str]]:
    """Given two pronunciations, return a list of tuples that contain the differences"""
    diffs: list[tuple[str, str]] = []
    total_len = max(len(pronun1), len(pronun2))
    for i in range(total_len):
        symbol1 = pronun1[i] if len(pronun1) > i else ""
        symbol2 = pronun2[i] if len(pronun2) > i else ""
        if symbol1 != symbol2:
            diffs.append((symbol1, symbol2))
    return diffs


def minimize_all(
    dictionary: Dictionary,
) -> RawDictionary:
    """Convert the symbols based on two letters to one-letter symbols"""
    minimized_dict: RawDictionary = {}

    for word, pronun_or_list in dictionary.items():
        if isinstance(pronun_or_list, Pronunciation):  # only a single pronunciations
            pronun = pronun_or_list
            minimized_dict[word] = minimize(pronun)
        elif isinstance(pronun_or_list, dict):
            pronun_dict: dict[Identifier, Pronunciation] = pronun_or_list
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
