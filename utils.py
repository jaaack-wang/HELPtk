'''
Author: Zhengxiang (Jack) Wang 
Date: 2021-08-25 
GitHub: https://github.com/jaaack-wang 
About: Helper functions for the Historical English Language Processing Toolkit (HELPtk).
'''
from os import listdir, walk
from os.path import isfile, join
import re
import json
import random  

        
def get_filenames_from_dir(file_dir, include_sub_dir=False, file_format=None, shuffle=False):
    '''Return a list of filenames given a file directory and some conditions.
    
    Args:
        - file_dir(str): file_dir.
        - include_sub_dir(bool): whether to include all files within the sub_dir, defaults to False. 
                                 When set True, the returned filenames will be prefixed with the sub_dir. 
        - file_format(str or tuple or list or None): When set, only return files in the chosen format(s).
        - shuffle(bool): shuffle the filenames if set True. Otherwise, return a sorted list of filenames.
        
    Return(list): a list of filenames.'''
    
    if include_sub_dir:
        filenames = []
        for root, _, files in walk(file_dir, topdown=False):
            for f in files:
                filenames.append(join(root, f).replace(file_dir + "/", ""))
    else:
        filenames = [f for f in listdir(file_dir) if isfile(join(file_dir, f))]
        
    if file_format:
        if not isinstance(file_format, (str, list, tuple)):
            raise TypeError("file_format must be str, list or tuple.")
        file_format = tuple(file_format) if isinstance(file_format, list) else file_format
        format_checker = lambda f: f.endswith(file_format)
        filenames = list(filter(format_checker, filenames))

    if shuffle:
        random.shuffle(filenames)
    else:
        filenames.sort()
        
    return filenames


def _get_trans_rules(filepath, delimiter="\t"):
    '''Reads preprocessing_rules.txt and normalizing_rules.txt stored in config folder
    and returns a tuple of rules that contain the target pattern and replacement pattern pairs.'''
    
    f = open(filepath, 'r')
    targets, replaces = [], []
    for line in f:
        line = line.split(delimiter)
        targets.append(line[0])
        replaces.append(line[1] if not line[1].endswith('\n') else line[1].rstrip())
    
    return tuple(zip(targets, replaces))


def apply_trans_rules(rules, text, final_trim=True):
    '''Apply tranformation rules to the input text. The rules should be a list/tuple of 
    tranformation rules that contain the target pattern and replacement pattern pairs.'''
    
    for target, replace in rules:
        if "(\w)" in target or "(\S)" in target:
            text = re.sub(fr"{target}", fr"{replace}", text, flags=re.IGNORECASE)
        else:
            text = re.sub(fr"\b{target}\b", fr"{replace}", text, flags=re.IGNORECASE)
        
    if final_trim: return re.sub(r"\s+", " ", text).strip()
    else: return text

    
def normalizing_rules(filepath='config/normalizing_rules.txt', delimiter="\t"):
    '''Retrieve the normalizing_rules stored in the config folder by default，
    used for spelling normalization.'''
    return _get_trans_rules(filepath, delimiter)

        
def preprocessing_rules(filepath='config/preprocessing_rules.txt', delimiter="\t"):
    '''Retrieve the preprocessing_rules stored in the config folder, used for re-tokenization.'''
    return _get_trans_rules(filepath, delimiter)


def get_common_verbs(filepath='config/common_verbs.txt', delimiter="\t"):
    '''Retrieve the common verbs along with their third person singular and 
    simple past tense inflections (verified) stored in the config folder.'''

    # base verb (vb), third person singular (vbz) and simple past tense (vbd)
    vb, vbz, vbd = [], [], []
    verbs = open(filepath, 'r')
    next(verbs)
    for verb in verbs:
        verb = verb.split(delimiter)
        vb.append(verb[0])
        vbz.append(verb[1])
        vbd.append(verb[2].strip())
    return vb, vbz, vbd


def get_irreg_v_past_inflect_dict(filepath="config/irregular_v_past_inflections.json"):
    '''Retrieve the irregular verb past tense inflections dictionary. The dictionary is based 
    on data scraped from https://www.englishpage.com/irregularverbs/irregularverbs2.html'''
    return json.load(open(filepath, "r"))
