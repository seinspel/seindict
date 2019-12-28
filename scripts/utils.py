"""Useful functions for writing scripts that change the dicionary"""
from __future__ import annotations

import re
from pathlib import Path
from collections import OrderedDict
from typing import TYPE_CHECKING, List, Callable, Union, Dict, Optional, Iterator, Tuple, NamedTuple
from typing_extensions import Literal

from strictyaml import as_document, load, MapPattern, Str, Seq
from strictyaml.dumper import StrictYAMLDumper
import ruamel

SCHEMA = MapPattern(Str(), Str() | MapPattern(Str(), Str()) | Seq(Str()))

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
if TYPE_CHECKING:
    RawDictionary = OrderedDict[str, Union[str, List[str], OrderedDict[str, str]]]


def read_yaml_file(fpath: Path):
    """Load the content of a YAML file as an ordered dictionary"""
    raw_data = fpath.open().read()
    return load(raw_data, SCHEMA)


def apply(
    single_pronun_func: Callable[[str, str, RawDictionary], Union[bool, EntryType]],
    pronun_list_func: Optional[
        Callable[[str, List[str], RawDictionary], Union[bool, EntryType]]
    ] = None,
    pronun_dict_func: Optional[
        Callable[[str, OrderedDict[str, str], RawDictionary], Union[bool, EntryType]]
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
    deleted_words: RawDictionary = OrderedDict()
    base_path = Path("..") / "entries"
    for yaml_file in YAML_FILES:
        num_removed = 0
        num_changed = 0
        yaml_path = base_path / yaml_file
        yaml_dict = read_yaml_file(yaml_path)
        dictionary: RawDictionary = yaml_dict.data
        for word, value in dictionary.items():
            result: Union[bool, EntryType]
            if isinstance(value, str):
                result = single_pronun_func(word, value, dictionary)
            elif isinstance(value, OrderedDict) and pronun_dict_func is not None:
                pronun_dict: OrderedDict[str, str] = value
                result = pronun_dict_func(word, pronun_dict, dictionary)
            elif pronun_list_func is not None:
                if isinstance(value, list):
                    pronun_list: List[str] = value
                    result = pronun_list_func(word, pronun_list, dictionary)
                elif isinstance(value, OrderedDict):  # pronun_dict_func must be None
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
                    elif isinstance(value, OrderedDict):
                        pronun_list = list(value.values())
                    else:
                        raise ValueError(f"Unexpected type {type(value)}")
                    # take the result of just looking at the first pronunciation
                    result = single_pronun_func(word, pronun_list[0], dictionary)
                elif mode == "transform":
                    # iterate over the pronunciations and transform them one-by-one
                    new_pronuns: Union[OrderedDict[str, str], List[str]]
                    entries: Union[Iterator[Tuple[str, str]], Iterator[Tuple[int, str]]]
                    if isinstance(value, list):
                        pronun_list = value
                        new_pronuns = [p for p in pronun_list]  # copy list
                        entries = enumerate(pronun_list)
                    elif isinstance(value, OrderedDict):
                        pronun_dict = value
                        new_pronuns = OrderedDict()
                        entries = pronun_dict.items()
                    else:
                        raise ValueError(f"Unexpected type {type(value)}")

                    result = _iterate_over_subentries(
                        new_pronuns, entries, single_pronun_func, word, dictionary
                    )

            if isinstance(result, bool):
                if not result:  # delete word
                    deleted_words[word] = value
                    del yaml_dict[word]
                    num_removed += 1
            else:
                yaml_dict[word] = result
                num_changed += 1
        if num_removed:
            print(f"removed {num_removed} entries in {yaml_file}")
        elif num_changed:
            print(f"changed {num_changed} entries in {yaml_file}")
        else:
            print(f"nothing changed or removed in {yaml_file}")
        if save_result:
            yaml_path.open("w").write(dump(yaml_dict))
        if only_first_file:
            break
    if save_deleted_words is not None:
        write_to_yaml(save_deleted_words, deleted_words)


def _iterate_over_subentries(
    container: Union[OrderedDict[str, str], List[str]],
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


def write_to_yaml(fpath: Path, content: OrderedDict) -> None:
    """Write an ordered dictionary as YAML to a file"""
    if not content:
        return
    yaml = as_document(content)
    fpath.open("w").write(dump(yaml))


def dump(yaml_dict):
    """Render the YAML node and subnodes as string."""
    return ruamel.yaml.dump(
        yaml_dict.as_marked_up(), Dumper=StrictYAMLDumper, allow_unicode=True, width=1000
    )


REPLACEMENTS = {
    "SH": "ʃ",
    "TH": "θ",
    "WH": "ʍ",
    "CH": "ʒ",
    "AU": "a",
    "NN": "n",
    "LL": "l",
    "TT": "t",
    "OU": "u",
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

    pattern: str
    source: str
    target: str


class VowelReplacement:
    """Class for changing vowels"""

    def __init__(
        self,
        spelling_patterns: List[str],
        phoneme_patterns: List[Replacement],
        overrides: Optional[Dict[str, str]] = None,
        exclude: str = "",
    ):
        self.spelling_patterns = spelling_patterns
        self.phoneme_patterns = phoneme_patterns

        self.overrides: Dict[str, str] = overrides if overrides is not None else {}

        self.exclude: List[str] = exclude.split()

        self.is_active = False

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
            if re.search(rep.pattern, pronun) is not None:
                present_stresses.append((rep.source, rep.target))
        if not present_stresses:
            return True

        leeway = 1

        changed_anything = False
        new_pronun = pronun
        for source, target in present_stresses:
            new_pronun_split = new_pronun.split()
            source_split = source.split()
            # find index where `source` begins
            phoneme_index = new_pronun_split.index(source_split[0])
            if (
                min(abs(pattern_index - phoneme_index) for pattern_index in pattern_indices)
                > leeway
            ):
                print(
                    f"probably no candiate '{word}', letter indices: {pattern_indices}, sound index: {phoneme_index}"
                )
                continue
            new_pronun = new_pronun.replace(source, target)
            changed_anything = True
        if not changed_anything:
            return True
        print(f"change '{word}', new pronun: '{new_pronun.replace(target, target.lower())}'")
        if self.is_active:
            return new_pronun
        return True
