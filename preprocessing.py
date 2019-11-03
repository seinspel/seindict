"""Pre-process the dictionry"""

from pathlib import Path
from collections import OrderedDict
import json
from typing import Union, List
from strictyaml import load, MapPattern, Str, Seq


def main() -> None:
    raw_data = (Path(".") / "dictionary" / "a.yaml").open().read()
    schema = MapPattern(Str(), Str() | MapPattern(Str(), Str()) | Seq(Str()))
    dictionary: OrderedDict[str, Union[str, List[str], OrderedDict[str, str]]]
    dictionary = load(raw_data, schema).data
    print(type(dictionary))
    i = 0
    for word, pronunciations in dictionary.items():
        if isinstance(pronunciations, str):
            i += 1
        elif isinstance(pronunciations, list):
            print(pronunciations)
        elif isinstance(pronunciations, OrderedDict):
            print(pronunciations)
        else:
            raise ValueError("unexpected type: {type(pronunciations)}")
    print("words: ", i)


if __name__ == "__main__":
    main()
