from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List, Callable, Union, Dict, Optional
from collections import OrderedDict

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
    pronun_list_func: Optional[Callable[[str, List[str], RawDictionary], Union[bool, EntryType]]] = None,
    pronun_dict_func: Optional[Callable[[str, OrderedDict[str, str], RawDictionary], Union[bool, EntryType]]] = None,
    save_deleted_words: Optional[Path] = None,
    save_result: bool = False,
    only_first_file: bool = False,
):
    deleted_words: RawDictionary = OrderedDict()
    num_removed = 0
    base_path = Path("..") / "entries"
    for yaml_file in YAML_FILES:
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
            else: # pronun_list_func is None
                if isinstance(value, list):
                    pronun_list = value
                elif isinstance(value, OrderedDict):
                    pronun_list = list(value.values())
                else:
                    raise ValueError(f"Unexpected type {type(value)}")

                # take the result of just looking at the first pronunciation
                result = single_pronun_func(word, pronun_list[0], dictionary)

            if isinstance(result, bool):
                if not result:  # delete word
                    deleted_words[word] = value
                    del yaml_dict[word]
                    num_removed += 1
            else:
                yaml_dict[word] = result
        print(f"removed {num_removed} entries in {yaml_file}")
        if save_result:
            yaml_path.open("w").write(dump(yaml_dict))
        if only_first_file:
            break
    if save_deleted_words is not None:
        write_to_yaml(save_deleted_words, deleted_words)


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
