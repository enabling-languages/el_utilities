def list_to_string(items: list, sep: str = ', ', drop_bool: bool = True) -> str:
    """Convert list to string

    Converts:
       ['one', 'two', 'three']
    to:
       'one, two, three'

    Args:   
        items (list): _description_
        sep (str, optional): _description_. Defaults to ', '.

    Returns:
       str: _description_
    """
    # return sep.join([item for item in items if item])
    if not drop_bool:
        return sep.join(f'{item}' for item in items)
    return sep.join(f'{item}' for item in items if item)

def string_to_list(items: str, sep: str = ', ') -> list:
    """Convert string to list

    Converts:
       'one, two, three'
    to:
       ['one', 'two', 'three']

    Args:
        items (str): _description_
        sep (str, optional): _description_. Defaults to ', '.

    Returns:
        list: _description_
    """
    # return [item.strip() for item in items.split(sep) if item.strip()]
    return [item for i in items.split(sep) if (item := i.strip())]

def print_list(l: list, sep: str = "\n", drop_bool: bool = True) -> None:
    """Print list to STDOUT

    Print list to STDOUT, using specified separator between list items, defaulting 
    to a new line.

    Args:
        l (list): _description_
        sep (str, optional): _description_. Defaults to "\n".
    """
    if sep == "\u0020":
        print(list_to_string(l, sep=sep, drop_bool=drop_bool))
    else:
        print(*l, sep=sep)

pl = print_list

def search_dict_values(dictionary: dict, searchString: str) -> list:
    """Retrieve dictionary keys for matching values

    Args:
        dictionary (dict): _description_
        searchString (str): _description_

    Returns:
        list: _description_
    """
    return [key for key,val in dictionary.items() if any(searchString in s for s in val)]

def search_dict_keys(dictionary: dict, searchString: str) -> list:
    """Retrieve dictionary values for matching keys

    Args:
        dictionary (dict): _description_
        searchString (str): _description_

    Returns:
        list: _description_
    """
    return dictionary[searchString] if dictionary.get(searchString) != None else None
