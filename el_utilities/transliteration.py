from el_internationalisation import normalise
import regex as re
from .transliteration_data import SUPPORTED_TRANSLITERATORS, TRANSLIT_DATA
from icu import Collator, Locale
from collections import OrderedDict
from typing import Final

# TODO:
#  * add type hinting
#  * add DocStrings

DEFAULT_NF: Final[str] = "NFM"

def prep_string(s: str, dir: str, lang: str, b: str = "latin-only") -> str:
    if dir.lower() == "reverse" and b.lower() != "both":
        s = s.lower()
    s = normalise(DEFAULT_NF, s)
    if lang == "lo" and dir.lower() == "reverse":
        s = s.replace("\u0327", "\u0328").replace("\u031C", "\u0328")
    return s

def el_transliterate(bib_data: str, lang: str, dir: str = "forward", nf: str = DEFAULT_NF) -> str:
    lang = lang.replace("-", "_").split('_')[0]
    dir = dir.lower()
    if dir != "reverse":
        dir = "forward"
    if SUPPORTED_TRANSLITERATORS[lang]:
        translit_table = SUPPORTED_TRANSLITERATORS[lang]
        nf = nf.upper() if nf.upper() in ["NFC", "NFKC", "NFKC_CF", "NFD", "NFKD", "NFM"] else DEFAULT_NF
        bib_data = prep_string(bib_data, dir, lang, translit_table[1])
        if dir == "forward":
            collator = Collator.createInstance(Locale.getRoot())
        else:
            collator = Collator.createInstance(Locale(lang))
        if dir == "reverse" and lang in list(Collator.getAvailableLocales().keys()):
            collator = Collator.createInstance(Locale(lang))
        else:
            collator = Collator.createInstance(Locale.getRoot())
        word_dict = OrderedDict(sorted(TRANSLIT_DATA[translit_table[0]]['translit_dict'][dir].items(), reverse=True, key=lambda x: collator.getSortKey(x[0])))
        word_dict = {normalise(DEFAULT_NF, k): normalise(DEFAULT_NF, v) for k, v in word_dict.items()}
        label = translit_table[2]
        if dir == "reverse":
            bib_data_split = re.split('(\W+?)', bib_data)
            res = "".join(word_dict.get(ele, ele) for ele in bib_data_split)
        else:
            from functools import reduce
            res = reduce(lambda x, y: x.replace(y, word_dict[y]), word_dict, bib_data)
    else:
        res = bib_data
    if nf != DEFAULT_NF:
        res = normalise(nf, res)
    return res
