from el_internationalisation import normalise
import regex as re
from .transliteration_data import SUPPORTED_TRANSLITERATORS, TRANSLIT_DATA
from icu import Collator, Locale, Transliterator, UTransDirection
from collections import OrderedDict
from pathlib import Path
import sys

# TODO:
#  * add type hinting
#  * add DocStrings

DEFAULT_NF = "NFM"

def prep_string(s, dir, lang, b = "latin-only"):
    if dir.lower() == "reverse" and b.lower() != "both":
        s = s.lower()
    s = normalise(DEFAULT_NF, s)
    if lang == "lo" and dir.lower() == "reverse":
        s = s.replace("\u0327", "\u0328").replace("\u031C", "\u0328")
    return s

def el_transliterate(bib_data, lang, dir = "forward", nf = DEFAULT_NF):
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

###############################################
#
# Athinkra Translit functions
#
###############################################

# Available transforms
def available_transforms(term = None):
    available = list(Transliterator.getAvailableIDs())
    if term is None:
        return available
    return [x for x in available if term.lower() in x.lower()]

# transliterate from inbuilt ICU transform
def translit_icu(text, transform):
    if transform not in available_transforms():
        print("Unsupported transformation. Not available in icu4c")
        sys.exit()
    transformer = Transliterator.createInstance(transform)
    return transformer.transliterate(text)

# READ transliteration rules from LDML file
def read_ldml_rules(ldml_file):
    import xml.etree.ElementTree as ET
    def get_ldml_rules(rules_file):
        rules = ''
        doc = ET.parse(rules_file)
        r = doc.find('./supplementalData/transforms/transform')
        if r is None:
            r = doc.find('./transforms/transform')
        if r is None:
            sys.stderr(f"Can't find transform in {rules_file}")
        pattern = re.compile(r'[ \t]{2,}|[ ]*#.+\n')
        rules = re.sub(pattern, '', r.find('./tRule').text)
        rules_name = r.attrib['alias'].split()[0]
        return (rules, rules_name)
    rules_tuple = get_ldml_rules(ldml_file)
    return rules_tuple

# Register transformer form LDML file
def register_ldml(ldml_file, direction = UTransDirection.FORWARD):
    ldml_rules = read_ldml_rules(ldml_file)
    ldml_transformer = Transliterator.createFromRules(ldml_rules[1], ldml_rules[0], direction)
    Transliterator.registerInstance(ldml_transformer)

# transform from custom rules
def translit_rules(text, rules, direction = UTransDirection.FORWARD, name = "Custom"):
    transformer = Transliterator.createFromRules(name, rules, direction)
    return transformer.transliterate(text)

# Resolve LDML file path
def set_ldml_file_path(raw_path):
    p = Path(raw_path)
    try:
        p = p.resolve(strict=True)
    except FileNotFoundError:
        print("LDML file not found.")
    if p.exists() and p.is_file():
        return str(p)
    else:
        print("LDML does not exist.")
