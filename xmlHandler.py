'''
- Author: Zhengxiang (Jack) Wang 
- Date: 2021-08-25
- GitHub: https://github.com/jaaack-wang 
- About: Some handy wrapper functions for handling xml files.
'''
from bs4 import BeautifulSoup as bs
from lxml import etree
from os.path import join


def readXML(filepath):
    ''''Reads XML files as bs4.BeautifulSoup type.'''
    return bs(open(filepath, "rb"), "xml")
    
    
def _get_node(soup, filepath, node_name, as_str=False):
    '''An abstract implementation for get_node.'''
    node = soup.find(node_name)
    if node:
        if as_str: 
            return node.prettify()
        return node
    else:
        print(f"\033[32mNodeNotFound\033[0m: \"{node_name}\" not found in {filepath}." \
              " Return empty string instead.")
        return ""


def get_node(filepath, node_name, as_str=False):
    '''Returns the first node given a xml's filepath and the node_name. 
    If as_str set True, returns formatted str. Otherwise, bs4.element.Tag.
    If the node_name is not found, returns an empty string.'''
    return _get_node(readXML(filepath), filepath, node_name, as_str)


def get_nodes(filepath, node_name):
    '''Returns all bs4.element.Tags in a given xml file related to the queried node_name 
    if any. Otherwise, Return NoneType.'''
    nodes = readXML(filepath).find_all(node_name)
    if nodes:
        return nodes
    else:
        print(f"\033[32mNodeNotFound\033[0m: \"{node_name}\" not found in {filepath}. Return None.")
        return 


def get_header(filepath, head_node, as_str=False):
    '''Return the header of a xml file.'''
    return get_node(filepath, head_node, as_str)


def get_body(filepath, body_node, as_str=False):
    '''Return the body part of a xml file.'''
    return get_node(filepath, body_node, as_str)
    

def get_header_body_as_str(filepath, head_node, body_node):
    '''Return formatted header and body parts of a xml file as str.
    If a node name is not found, return an empty string'''
    
    soup = readXML(filepath)
    header = _get_node(soup, filepath, head_node, as_str=True)
    body = _get_node(soup, filepath, body_node, as_str=True)
    return header, body


def createXmlFileFromStr(filename=None, root_name="TEI.2", header="", 
                         body="", dst_dir="./", save=True):
    '''Creates a XML file given a set of xml-formatted strings. 
    Args:
        - filename(str): filename for the new xml file, defaults to None.  
        - root_name(str): the name of the first super node for the xml file, defaults to "TEI.2". 
                          The root name is loosely used. Does not refer to the real conceptual root.
        - header(str): xml-like string, header part, defaults to empty str.
        - body(str): xml-like string, body part, defaults to empty str.
        - dst_dir(str): path-like string. If not given, defaults to the current dir.
        - save(bool): whether to save, defaluts to True. 
        
    Return:
        - if save set False, return lxml.etree._ElementTree. Otherwise, no returns. 
    '''
    if not filename:
        save = False
    else:
        filename = filename if filename.endswith('.xml') else filename + '.xml'
    content = f'<{root_name}>' + header + body + f'</{root_name}>'
    content = bs(content, 'xml').prettify()
    content = content.replace('<?xml version="1.0" encoding="utf-8"?>\n', '')
    parser = etree.XMLParser(recover=True)
    try:
        root = etree.fromstring(content, parser=parser)
        tree = etree.ElementTree(root)
        if save:
            filepath = join(dst_dir, filename)
            tree.write(filepath)
            print(filepath + " has been created!")
        else:
            return tree
            
    except Exception as e:
        print(f"\033[1m\033[31mA problem creating {join(dst_dir, filename)} as follows: \033[0m{e}\n")
