'''
- Author: Zhengxiang (Jack) Wang 
- Date: 2021-08-25
- GitHub: https://github.com/jaaack-wang 
- About: Ruled-based functions for normalizing English text，including base verb
to third person singular conversion, base verb to the simple past tense conversion,
as well as normalizing rules that are relevant to historical English texts. With
normalizing rules modified in the config/normalizing_rules.txt tailored for one's
specific needs, this textNormalizer can also serve as a general framework for
rule-based English text normalization. 
'''
from utils import *
import re


vowels = ["a", "e", "i", "o", "u"]
try: 
    norm_rules = normalizing_rules()
except: 
    norm_rules == None
try: 
    verbs = get_common_verbs()
except: 
    verbs == None
try: 
    irreg_v_dict = get_irreg_v_past_inflect_dict()
except: 
    irreg_v_dict == None


def v_third_present(verb):
    '''Converts a verb into its third person singular present form. 
    Ref: https://dictionary.cambridge.org/grammar/british-grammar/present-simple-i-work'''
    
    if verb.endswith(("ss", "zz", "x", "sh", "ch")):
        return verb + "es"
    if verb.endswith(('go', 'do',)):
        return verb + "es"    
    if verb.endswith(("s", "z", )) and verb[-2] in vowel:
        return verb + verb[-1] + "es"
    if verb[-1] == "y" and verb[-2] not in vowels:
        return verb[:-1] + "ies"
    if verb == "have":
        return "has"
    
    return verb + "s"


def v_past_tense(verb, irreg_v_dict=irreg_v_dict, rand_idx=0):
    '''Converts a verb into its past tense. This method cannot model perfectly whether 
    it should double a costant-ending verb's final constant as that is not totally ruled-based. 
    
    Args:
        verb(str): a verb.
        irreg_v_dict(dict): a built-in dict that contains a list of verbs, each of which has irregular 
                            inflections for the simple past tense and past particle. Please note that, as 
                            some verbs can have two inflections, to preserve them, all the inflections have 
                            been stored in a list. The past tense ("VBD") and past particle ("VBN") are stored 
                            as another dict. To get a verb's past tense inflection if it is in the dict, 
                            use: irreg_v_dict[verb]["VBD"][0]. The final index [0] can also be [-1], which will
                            return a different version of inflections if there are two inflections available.
        rand_idx(int): must be either 0 or -1.'''
    
    assert irreg_v_dict != None, "No irreg_v_dict given. Please use get_irreg_v_past_inflect_dict(filepath) to get norm_rules and input it here."
    if irreg_v_dict.get(verb):
        return irreg_v_dict[verb]['VBD'][rand_idx]
    if verb[-1] == "e":
        return verb + "d"
    if verb[-1] == "y" and verb[-2] not in vowels:
        return verb[:-1] + "ied"
    if len(verb) <= 2:
        return verb + "ed"
    if verb[-1] not in vowels + ['y', 'x', 'w'] and verb[-2] in vowels:
        if verb[-3] not in vowels and len(verb) <= 5:
            return verb + verb[-1] + "ed"
    
    return verb + "ed"
    

def textNormalizing(text, norm_rules=norm_rules, verbs=verbs):
    '''The main function for text spelling Normalization. This function is a general one,
    but the imported norm_rules and verbs to convert are very specific to Early Modern English texts.
    If these rules are not relevant, you should choose not not normalize your texts using this function.'''
    
    assert norm_rules != None, "No norm_rules given. Please use normalizing_rules(filepath)" \
                               " from utils.py to get norm_rules and input it here."
    assert verbs != None, "No verbs given. Please use get_common_verbs(filepath) from utils.py" \
                           " to get verbs and input it here."
    
    text = re.sub("ſ", "s", text)
    text = apply_trans_rules(norm_rules, text)
    
    vb, vbz, vbd = verbs
    # 嗨 is a Chinese word for "hi", used as a marker to locate past tense verbs to convert. 
    # Simply changing 'd ---> ed should be much less accurate than looking at them case by case. 
    # As 嗨'd is a very unlikely sequence to appear in any text I can think of, hence the use
    marked_vs = re.findall(r"\b\S+嗨'd\b", text)
    for marked_v in marked_vs:
        v = marked_v[:-3] # get the base verb
        if v in vb: # if the base verb is in the common verb list we have, look up its past tense there
            idx = vb.index(v)
            text = re.sub(fr"\b{marked_v}\b", vbd[idx], text, flags=re.IGNORECASE)
            
        else: # otherwise, use the v_past_tense function above
            text = re.sub(fr"\b{marked_v}\b", v_past_tense(v), text, flags=re.IGNORECASE)
        
    for i in range(len(vb)):
        # for third person singular
        text = re.sub(fr"\b{vb[i]}e?th\b", vbz[i], text, flags=re.IGNORECASE)
        # for second person singular
        text = re.sub(fr"\b{vb[i]}'?e?st\b", vb[i], text, flags=re.IGNORECASE)
    
    return text
