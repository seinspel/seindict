"""Useful functions for writing scripts that change the dicionary"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Callable, Union, Dict, Optional, Iterator, Tuple, NamedTuple
from typing_extensions import Final, Literal

from ruamel.yaml import YAML

YAML_FILES: List[str] = [
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
]

EntryType = Union[str, List[str], Dict[str, str]]
RawDictionary = Dict[str, Union[str, List[str], Dict[str, str]]]


def read_yaml_file(fpath: Path) -> Tuple[YAML, RawDictionary]:
    """Load the content of a YAML file as an ordered dictionary"""
    yaml_obj = YAML(typ="rt")
    with  fpath.open() as fp:
        dictionary = yaml_obj.load(fp)
    return yaml_obj, dictionary


def apply(
    single_pronun_func: Callable[[str, str, RawDictionary], Union[bool, EntryType]],
    pronun_list_func: Optional[
        Callable[[str, List[str], RawDictionary], Union[bool, EntryType]]
    ] = None,
    pronun_dict_func: Optional[
        Callable[[str, Dict[str, str], RawDictionary], Union[bool, EntryType]]
    ] = None,
    save_deleted_words: Optional[Path] = None,
    save_result: bool = False,
    only_first_file: bool = False,
    mode: Literal["filter", "transform"] = "filter",
):
    """This function is ugly so that your code doesn't have to be.

    This function takes three functions and applies them to entries in a dictionary depending on
    what the type of the entry is.
    """

    assert mode in ("filter", "transform")
    deleted_words: RawDictionary = {}
    base_path = Path("..") / "entries"
    for yaml_file in YAML_FILES:
        num_removed = 0
        num_changed = 0
        yaml_path = base_path / yaml_file
        yaml_obj, dictionary = read_yaml_file(yaml_path)
        for word, value in dictionary.items():
            assert isinstance(word, str)
            result: Union[bool, EntryType]
            if isinstance(value, str):
                result = single_pronun_func(word, value, dictionary)
            elif isinstance(value, dict) and pronun_dict_func is not None:
                pronun_dict: Dict[str, str] = value
                result = pronun_dict_func(word, pronun_dict, dictionary)
            elif pronun_list_func is not None:
                if isinstance(value, list):
                    pronun_list: List[str] = value
                    result = pronun_list_func(word, pronun_list, dictionary)
                elif isinstance(value, dict):  # pronun_dict_func must be None
                    pronun_dict = value
                    result = pronun_list_func(word, list(pronun_dict.values()), dictionary)
                else:
                    raise ValueError(f"Unexpected type {type(value)}")
            else:
                # At this point, `pronun_list_func` is None and `pronun_dict_func` is also None if
                # `value` is an OrderedDict.

                # what we do now, depends on the mode
                if mode == "filter":
                    if isinstance(value, list):
                        pronun_list = value
                    elif isinstance(value, dict):
                        pronun_list = list(value.values())
                    else:
                        raise ValueError(f"Unexpected type {type(value)}")
                    # take the result of just looking at the first pronunciation
                    result = single_pronun_func(word, pronun_list[0], dictionary)
                elif mode == "transform":
                    # iterate over the pronunciations and transform them one-by-one
                    new_pronuns: Union[Dict[str, str], List[str]]
                    entries: Union[Iterator[Tuple[str, str]], Iterator[Tuple[int, str]]]
                    if isinstance(value, list):
                        pronun_list = value
                        new_pronuns = [p for p in pronun_list]  # copy list
                        entries = enumerate(pronun_list)
                    elif isinstance(value, dict):
                        pronun_dict = value
                        new_pronuns = {}
                        entries = pronun_dict.items()
                    else:
                        raise ValueError(f"Unexpected type {type(value)}")

                    result = _iterate_over_subentries(
                        new_pronuns, entries, single_pronun_func, word, dictionary
                    )

            if isinstance(result, bool):
                if not result:  # delete word
                    deleted_words[word] = value
                    #del dictionary[word]
                    num_removed += 1
            else:
                dictionary[word] = result
                num_changed += 1
        if num_removed:
            print(f"found {num_removed} entries in {yaml_file}")
        elif num_changed:
            print(f"changed {num_changed} entries in {yaml_file}")
        else:
            print(f"nothing changed or removed in {yaml_file}")
        if save_result:
            write_to_yaml(yaml_path, yaml_obj, dictionary)
        if only_first_file:
            break
    print(f"{len(deleted_words)} deleted in total")
    print("\n".join(f"{k}: {v}" for k, v, in deleted_words.items()))
    if save_deleted_words is not None:
        raise NotImplementedError()
        # write_to_yaml(save_deleted_words, yaml_obj, deleted_words)


def _iterate_over_subentries(
    container: Union[Dict[str, str], List[str]],
    entries: Union[Iterator[Tuple[str, str]], Iterator[Tuple[int, str]]],
    single_pronun_func: Callable[[str, str, RawDictionary], Union[bool, EntryType]],
    word: str,
    dictionary: RawDictionary,
) -> Union[bool, EntryType]:
    was_one_entry_changed = False
    for k, pronun in entries:
        new_pronun = single_pronun_func(word, pronun, dictionary)
        if isinstance(new_pronun, bool):  # True means 'keep the entry', False means 'delete it'
            assert new_pronun is True, "can't filter words in 'transform' mode"
            container[k] = pronun
            continue
        assert isinstance(new_pronun, str), "can't return more than one pronun in 'transform' mode"
        was_one_entry_changed = True
        container[k] = new_pronun
    if not was_one_entry_changed:
        return True
    return container


def write_to_yaml(fpath: Path, yaml_obj: YAML, dictionary: RawDictionary) -> None:
    """Write an ordered dictionary as YAML to a file"""
    if not dictionary:
        return
    yaml_obj.allow_unicode = True
    yaml_obj.width = 1000
    with fpath.open("w") as fp:
        yaml_obj.dump(dictionary, stream=fp)


REPLACEMENTS = {
    "AI": "i",
    "AU": "a",
    "CH": "ʒ",
    "EE": "e",
    "FF": "f",
    "LL": "l",
    "MM": "m",
    "NN": "n",
    "OU": "u",
    "SH": "ʃ",
    "SS": "s",
    "TH": "θ",
    "TT": "t",
    "WH": "ʍ",
    "EA": "ɛ",
    # "ER": "r",  # causes problems
}


def replace_digraphs(word: str) -> str:
    """Replace common digraphs with a single letter"""
    for digraph, replacement in REPLACEMENTS.items():
        word = word.replace(digraph, replacement)
    return word


def find_indices(word: str, pattern_list: List[str]) -> List[int]:
    """Find indices where the given pattern occur"""
    word_with_better_letters = replace_digraphs(word)
    indices: List[int] = []
    for pattern in pattern_list:
        indices += [m.start() for m in re.finditer(pattern, word_with_better_letters)]
    return indices


class Replacement(NamedTuple):
    """A tuple that specifies a replacement"""

    guard: str
    source: str
    target: str


class FindAndReplace:
    """Class for changing vowels"""

    def __init__(
        self,
        spelling_patterns: List[str],
        phoneme_patterns: List[Replacement],
        overrides: Optional[Dict[str, str]] = None,
        exclude: str = "",
        leeway: int = 1,
    ):
        self.spelling_patterns = spelling_patterns
        self.phoneme_patterns = phoneme_patterns
        self.overrides: Dict[str, str] = overrides if overrides is not None else {}
        self.exclude: List[str] = exclude.split()
        self.is_active = False
        self.leeway = leeway

    def __call__(self, word: str, pronun: str, dictionary):
        if word in self.overrides:
            return self.overrides[word]

        if word in self.exclude:
            return True

        pattern_indices = find_indices(word, self.spelling_patterns)

        if not pattern_indices:  # no suitable letters found
            return True

        present_stresses: List[Tuple[str, str]] = []
        for rep in self.phoneme_patterns:
            if re.search(rep.guard, pronun) is not None:
                present_stresses.append((rep.source, rep.target))
        if not present_stresses:
            return True

        changed_anything = False
        new_pronun = pronun
        for source, target in present_stresses:
            new_pronun_split = new_pronun.split()
            source_split = source.split()
            # find indices where `source` begins
            phoneme_indices = [i for i, d in enumerate(new_pronun_split) if d == source_split[0]]
            for phoneme_index in phoneme_indices:
                if (
                    min(abs(pattern_index - phoneme_index) for pattern_index in pattern_indices)
                    > self.leeway
                ):
                    continue
                new_pronun = new_pronun.replace(source, target)
                changed_anything = True
            if not changed_anything:
                print(
                    f"probably no candiate '{word}', letter indices: {pattern_indices}, sound index: {phoneme_indices}"
                )
        if not changed_anything:
            return True
        print(f"change '{word}', new pronun: '{new_pronun.replace(target, target.lower())}'")
        if self.is_active:
            return new_pronun
        return True


VOWELS: Final = [
    "A",
    "AH",
    "AHY",
    "AR",
    "AW",
    "EE",
    "EH",
    "EIR",
    "EL",
    "EW",
    "EWR",
    "EY",
    "IA",
    "IER",
    "IH",
    "IRE",
    "O",
    "OA",
    "OH",
    "OHR",
    "OIR",
    "OO",
    "OOR",
    "OR",
    "OW",
    "OWR",
    "OY",
    "U",
    "UH",
    "UR",
    "ə",
    "əR",
]

def is_vowel(phon: str):
    return phon[0:-1] in VOWELS or phon in ("EL", "ə", "əR")
