import urllib.request
from bs4 import BeautifulSoup

from mcshell.constants import *

def fetch_html(url):
    _pkl_path = MC_DATA_DIR.joinpath(f"{url.name}.pkl")
    if _pkl_path.exists():
        print(f'loading from {_pkl_path}')
        _data = pickle.load(_pkl_path.open('rb'))
    else:
        # retrieve document from url
        print(f'fetching from {url}')
        try:
            with urllib.request.urlopen(str(url)) as response:
                _data = response.read()
        except Exception as e:
            print(e)
            return
        pickle.dump(_data,_pkl_path.open('wb'))
    return _data

def make_docs():
    # parse document and extract and interpret figure data
    _soup_data = BeautifulSoup(fetch_html(MC_DOC_URL), 'html.parser')

    _tables = _soup_data.find_all('table',attrs={'class':'stikitable'})
    _code_elements = _tables[0].select('code')

    _doc_dict = {}
    for _code_element in _code_elements:
        _cmd = _code_element.text[1:]
        _parent = _code_element.find_parent()
        _doc_line = _parent.find_next_siblings()[0].text.strip()
        try:
            _doc_url_stub = urlpath.URL(_code_element.find_all('a')[0].attrs['href'])
            _doc_url = MC_DOC_URL.joinpath(_doc_url_stub)
        except IndexError:
            continue

        _doc_soup_data = BeautifulSoup(fetch_html(_doc_url),'html.parser')
        try:
            _syntax_h2s = list(filter(lambda x:x is not None,map(lambda x:x.find('span',string='Syntax'),_doc_soup_data.find_all('h2'))))
            assert len(_syntax_h2s) == 1
            _doc_code_elements = list(filter(lambda x:x != [] and x is not None,map(lambda x:x.find('code'),_syntax_h2s.pop().parent.find_next_sibling('dl').find_all('dd'))))
            _doc_code_lines = list(filter(lambda x:x.split()[0] == _cmd,map(lambda x:x.text,_doc_code_elements)))
        except:
            continue

        _doc_dict[_cmd] = (_doc_line,str(_doc_url),_doc_code_lines)

    pickle.dump(_doc_dict,MC_DOC_PATH.open('wb'))

    return _doc_dict

def make_materials():

    _soup_data = BeautifulSoup(fetch_html(MC_MATERIAL_URL), 'html.parser')

    material_names = []

    enum_summary_section = _soup_data.find('section', id='enum-constant-summary')
    if not enum_summary_section:
        print(f"Error: Could not find the section with id 'enum-constant-summary' on the page {MC_MATERIAL_URL}")
        return material_names

    code_tags_in_section = enum_summary_section.select('code')
    for code_tag in code_tags_in_section:
        link_tags_in_code = code_tag.find_all('a')
        for link_tag in link_tags_in_code:
            text = link_tag.string
            if text.upper() == text:
                if text.strip() not in material_names: # Avoid duplicates from broader search
                     material_names.append(text.strip())

    pickle.dump(material_names,MC_MATERIALS_PATH.open('wb'))

    return sorted(list(set(material_names))) # Return sorted unique names

def make_entity_id_map() -> Optional[dict[str, int]]:
    """
    Fetches and parses the implemented Bukkit EntityType.java file to create a mapping
    from the Bukkit enum name string to its legacy numerical ID.

    Args:
        url: The URL to the raw Java source file.

    Returns:
        A dictionary mapping entity names to IDs, or None on error.
    """

    java_code = fetch_html(MC_ENTITY_TYPE_URL)
    # This regex is designed to capture the enum constant name and its ID.
    # It looks for:
    # 1. ^\s*([A-Z_]+)      - Start of line, optional whitespace, then captures the uppercase enum NAME.
    # 2. \(.*?             - Matches the opening parenthesis and non-greedily everything after.
    # 3. ,\s*(-?\d+)\s* - Looks for a comma, whitespace, and then captures the integer ID.
    # 4. .*?\),?           - Matches the rest of the arguments until the closing parenthesis and optional comma.
    # This pattern is robust for constructor signatures like (name, class, id) and (name, class, id, bool).
    pattern = re.compile(r"^\s*([A-Z_]+)\(.*?,\s*(-?\d+).*?\),?$")

    entity_id_map = {}
    lines = java_code.splitlines()
    is_deprecated = False

    for line in lines:
        stripped_line = line.strip()

        # Check for @Deprecated annotation on the line preceding the enum constant
        if stripped_line == "@Deprecated":
            is_deprecated = True
            continue

        match = pattern.match(str(stripped_line,'utf-8'))
        if match and not is_deprecated:
            enum_name = match.group(1)
            entity_id = int(match.group(2))

            # The enum constant 'UNKNOWN' has ID -1 and is not a spawnable entity.
            if enum_name != 'UNKNOWN' and entity_id != -1:
                entity_id_map[enum_name] = entity_id
        else:
            pass
            # print(stripped_line)
        # Reset the deprecated flag after processing the line
        is_deprecated = False

    pickle.dump(entity_id_map, MC_ENTITY_ID_MAP_PATH.open('wb'))
    return entity_id_map
