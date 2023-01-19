import regex, icu, collections, pathlib, sys
import el_internationalisation as eli
from .transliteration_data import SUPPORTED_TRANSLITERATORS, TRANSLIT_DATA
import copy

# TODO:
#  * add type hinting
#  * add DocStrings

DEFAULT_NF = "NFM"

def toNFM(text, engine="ud"):
    if engine.lower() == "icu":
        return eli.normalise("NFM", text)
    return eli.normalise("NFM", text)

def prep_string(s, dir, lang, bicameral = "latin-only", nf = DEFAULT_NF):
    # If both scripts are not bicameral, only lower case string if dirction
    # of Script-Latin is reverse. Ie Latin lowercase for conversion to
    # unicameral script.
    if dir.lower() == "reverse" and bicameral.lower() != "both":
        s = s.lower()
    # notmalise string to required form
    s = eli.normalise(nf, s)
    # If converting from Latin to Lao (for ALALC), standarise 
    # interpretations of charcters used in ALALC Lao 2011 table.
    # LIkewise for Thai. Due to differences in interpretation due to
    # Removal of MARC-8 data during the 2011 revision of the 1997 tables.
    if (lang == "lo" or lang == "th") and dir.lower() == "reverse":
        s = s.replace("\u0327", "\u0328").replace("\u031C", "\u0328")
    return s

# def el_transliterate(source, lang, dir = "forward", nf = DEFAULT_NF):
#     lang = lang.replace("-", "_").split('_')[0]
#     dir = dir.lower()
#     if dir != "reverse":
#         dir = "forward"
#     if SUPPORTED_TRANSLITERATORS[lang]:
#         translit_table = SUPPORTED_TRANSLITERATORS[lang]
#         nf = nf.upper() if nf.upper() in ["NFC", "NFKC", "NFKC_CF", "NFD", "NFKD", "NFM"] else DEFAULT_NF
#         source = prep_string(source, dir, lang, translit_table[1])
#         if dir == "forward":
#             collator = icu.Collator.createInstance(icu.Locale.getRoot())
#         else:
#             collator = icu.Collator.createInstance(icu.Locale(lang))
#         if dir == "reverse" and lang in list(icu.Collator.getAvailableLocales().keys()):
#             collator = icu.Collator.createInstance(icu.Locale(lang))
#         else:
#             collator = icu.Collator.createInstance(icu.Locale.getRoot())
#         word_dict = collections.OrderedDict(sorted(TRANSLIT_DATA[translit_table[0]]['translit_dict'][dir].items(), reverse=True, key=lambda x: collator.getSortKey(x[0])))
#         word_dict = {eli.normalise(DEFAULT_NF, k): eli.normalise(DEFAULT_NF, v) for k, v in word_dict.items()}
#         label = translit_table[2]
#         if dir == "reverse":
#             source_split = regex.split('(\W+?)', source)
#             res = "".join(word_dict.get(ele, ele) for ele in source_split)
#         else:
#             from functools import reduce
#             res = reduce(lambda x, y: x.replace(y, word_dict[y]), word_dict, source)
#     else:
#         res = source
#     if nf != DEFAULT_NF:
#         res = eli.normalise(nf, res)
#     return res

###############################################
#
# Athinkra Translit functions
#
###############################################

# Available transforms
def available_transforms(term = None):
    available = list(icu.Transliterator.getAvailableIDs())
    if term is None:
        return available
    return [x for x in available if term.lower() in x.lower()]

# transliterate from inbuilt ICU transform
def translit_icu(source: str | list[str], transform: str) -> str | list[str] | None:
    if transform not in available_transforms():
        print(f'Unsupported transformation. Not available in icu4c {icu.ICU_VERSION}')
        return
    transformer = icu.Transliterator.createInstance(transform)
    if isinstance(source, list):
        return [transformer.transliterate(item) for item in source]
    return transformer.transliterate(source)

# READ transliteration rules from LDML file
def read_ldml_rules(ldml_file: str) -> tuple[str, str]:
    """Read transliteration rules from LDML file

    Args:
        ldml_file (str): LDML file containing transformation rules.

    Returns:
        tuple[str, str]: Tuple containing rules and label.
    """
    import xml.etree.ElementTree as ET
    def get_ldml_rules(rules_file):
        rules = ''
        doc = ET.parse(rules_file)
        r = doc.find('./supplementalData/transforms/transform')
        if r is None:
            r = doc.find('./transforms/transform')
        if r is None:
            sys.stderr(f"Can't find transform in {rules_file}")
        pattern = regex.compile(r'[ \t]{2,}|[ ]*#.+\n')
        rules = regex.sub(pattern, '', r.find('./tRule').text)
        rules = regex.sub('\n', '', rules)
        rules_name = r.attrib['alias'].split()[0]
        return (rules, rules_name)
    rules_tuple = get_ldml_rules(ldml_file)
    return rules_tuple

# Register transformer form LDML file
def register_ldml(ldml_file, direction = icu.UTransDirection.FORWARD):
    ldml_rules = read_ldml_rules(ldml_file)
    ldml_transformer = icu.Transliterator.createFromRules(ldml_rules[1], ldml_rules[0], direction)
    icu.Transliterator.registerInstance(ldml_transformer)

# transform from custom rules
def translit_rules(source: str | list[str], rules:str, direction: int = icu.UTransDirection.FORWARD, name: str = "Custom") -> str | list[str]:
    """Text transformation (transliteration) using custom rules or LDML files.

    Args:
        source (str | list[str]): String or List of strings to be transformed.
        rules (str): Rules to use for transformation.
        direction (int, optional): Direction of transformation (forward or reverse). Defaults to icu.UTransDirection.FORWARD.
        name (str, optional): Label for transformation. Defaults to "Custom".

    Returns:
        str | list[str]: Transformed string or list.
    """
    transformer = icu.Transliterator.createFromRules(name, rules, direction)
    if isinstance(source, list):
        return [transformer.transliterate(item) for item in source]
    return transformer.transliterate(source)

# Resolve LDML file path
def set_ldml_file_path(raw_path: str) -> str:
    """Resolve LDML file path.

    Args:
        raw_path (str): sting of relative or absolute path to LDML file.

    Returns:
        str: return a resolved path as a string.
    """
    p = pathlib.Path(raw_path)
    try:
        p = p.resolve(strict=True)
    except FileNotFoundError:
        print("LDML file not found.")
    if p.exists() and p.is_file():
        return str(p)
    else:
        print("LDML does not exist.")

# Get language subtag form a BCP-47 langauge tage or from a locale label
def get_lang_subtag(lang):
    subtags = lang.replace("-", "_").split('_')
    remainder = copy.deepcopy(subtags)
    lang_subtag = subtags[0]
    remainder.pop(0)
    script_subtag = ""
    country_subtag = ""
    # if len(subtags) > 1:
    if 1 < len(subtags):
        if bool(regex.match(r"^([A-Z][a-z]{3})$", subtags[1])):
            script_subtag = subtags[1]
            remainder.pop(0)
        elif bool(regex.match(r"^([A-Z]{2})$", subtags[1])):
            country_subtag = subtags[1]
            remainder.pop(0)
    if 2 < len(subtags):
        if bool(regex.match(r"^([A-Z]{2})$", subtags[2])):
            country_subtag = subtags[2]
            remainder.pop(0)
    remainder_str = "-".join(remainder) if len(remainder) > 0 else ""
    return (lang_subtag, script_subtag, country_subtag, remainder_str)

# transform using dictionary
def translit_dict(source, lang, dir = "forward", nf = DEFAULT_NF):
    lang = get_lang_subtag(lang)[0]
    dir = "forward" if dir.lower() != "reverse" else "reverse"
    if SUPPORTED_TRANSLITERATORS[lang]:
        translit_table = SUPPORTED_TRANSLITERATORS[lang]
        nf = nf.upper() if nf.upper() in ["NFC", "NFKC", "NFKC_CF", "NFD", "NFKD", "NFM"] else DEFAULT_NF
        # source = prep_string(source, dir, lang, translit_table[1])
        # if dir == "forward":
        #     collator = icu.Collator.createInstance(icu.Locale.getRoot())
        # else:
        #     collator = icu.Collator.createInstance(icu.Locale(lang))
        # if dir == "reverse" and lang in list(icu.Collator.getAvailableLocales().keys()):
        #     collator = icu.Collator.createInstance(icu.Locale(lang))
        # else:
        #     collator = icu.Collator.createInstance(icu.Locale.getRoot())
        if dir == "reverse" and lang in list(icu.Collator.getAvailableLocales().keys()):
            collator = icu.Collator.createInstance(icu.Locale(lang))
        else:
            collator = icu.Collator.createInstance(icu.Locale.getRoot())
        word_dict = collections.OrderedDict(sorted(TRANSLIT_DATA[translit_table[0]]['translit_dict'][dir].items(), reverse=True, key=lambda x: collator.getSortKey(x[0])))
        word_dict = {eli.normalise(DEFAULT_NF, k): eli.normalise(DEFAULT_NF, v) for k, v in word_dict.items()}
        label = translit_table[2]
        if dir == "reverse":
            source_split = regex.split('(\W+?)', source)
            res = "".join(word_dict.get(ele, ele) for ele in source_split)
        else:
            from functools import reduce
            res = reduce(lambda x, y: x.replace(y, word_dict[y]), word_dict, source)
    else:
        res = source
    if nf != DEFAULT_NF:
        res = eli.normalise(nf, res)
    return res

# el_transliterate = translit_dict

#
# 1. Use prep_string() or similar normalisation before transofrmations
# 2. 
#