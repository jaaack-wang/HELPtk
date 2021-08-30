'''
- Author: Zhengxiang (Jack) Wang 
- Date: 2021-08-25
- GitHub: https://github.com/jaaack-wang 
- About: A small text preprocessing toolkit that contains two pre-defined 
tokenizers and a general method for further text preprocessing using 
preprocessing rules written in target-replacement regular expression pairs. 
The preprocessing rules are mostly relevant for early modern English texts. 
'''
from utils import *
from corenlpToolbox import stanfordTokenizer


try:
    prep_rules = preprocessing_rules()
except: 
    prep_rules = None  

try:
    stTK = stanfordTokenizer()
    stTokenizer = stTK.tokenize
except:
    stTokenizer = None


def whiteSpaceTokenizer(text, list_out=True):
    '''Tokenize text by whitespaces. Return a list of
    whitespace separated tokens by default. If list_out,
    return string.'''
    if list_out: return text.split()
    else: return text 

    
def textPreprocessing(text, tokenizer=stTokenizer, prep_rules=prep_rules, 
                      apply_prep_rules=False, final_trim=True, list_out=False):
    '''Preprocessing text given pre-defined tokenizer and/or preprocessing rules.
    The preprocessing rules will only be applied when apply_prep_rules=True. The
    builtin preprocessing rules are mostly relevant for early modern English texts.
    The default tokenizer is stanfordTokenizer() imported from corenlpToolbox.py if
    none is given. This script also provides whiteSpaceTokenizer. The function returns
    preprocessed string. If list_out=True, a list of tokens will be returned.
    
    Args:
        - text(str): raw_text to preprocess.
        - tokenizer(method): a tokenizer method that takes text as input and returns a
                            list of tokens, defaults to the builtin stanfordTokenizer()
                            from corenlpToolbox.py.
        - prep_rules(list/tuple): a list/tuple of preprocessing rules, each of which is
                                a target-replacement pair written in Pythond readable regular
                            expression. Defaults to the builtin preprocessing rules from utils.py.
        - apply_prep_rules(bool): whether to apply the preprocessing rules. Defaults to True.
                                  If set False, will only tokenize the text using the tokenizer. 
        - final_trim(bool): defaults to True. If False, the preprocessed text will not be trimmed.
        - list_out(bool): defaults to False. If True, will return a list of preprocessed tokens.'''

    assert tokenizer != None, "No tokenizer given. You can use two tokenizers builtin here: " \
           "whiteSpaceTokenizer (method) and stanfordTokenizer's (class) tokenize (method), " \
           "or any other tokenizer as you please. The tokenizer should return a list of tokens as output."

    if "%" in text:
        text = re.sub("%", " was_percent_sign", text) 
        text = ' '.join(tokenizer(text))
    else:
        text = ' '.join(tokenizer(text))
    
    if apply_prep_rules:
        
        assert prep_rules != None, "No prep_rules given. Please use preprocessing_rules(filepath) " \
                                    "from utils to get prep_rules and input it here."
        
        text = apply_trans_rules(prep_rules, text, final_trim)
        
    if list_out: return text.split()
    else: return text 
