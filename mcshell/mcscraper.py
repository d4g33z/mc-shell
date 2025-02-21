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
    #_cmds = _cmd_table[0].find_all('code')

    #_code_elements = _soup_data.select('code')
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

if __name__ == '__main__':
    docs_dict = make_docs()
