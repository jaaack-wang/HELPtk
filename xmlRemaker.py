'''
- Author: Zhengxiang (Jack) Wang 
- Date: 2021-08-27
- GitHub: https://github.com/jaaack-wang 
- About: A set of handy methods and a general framework for remakng a xml file 
with just a few lines of code.

Usage includes:

    - tokenizing or preprocessing a xml file,
    - normalizing its spellings ,
    - pos tagging the tokens,
    - lemmatizing the tokens, 
    - and the combination of these four.
    
which will yield 8 different remade xml formats if not including the differences between
the tokenized and preprocessed remade files.

In principle, this can be useful for any xml file if the header part node and body part node
are given correctly. The usage applies for both a single xml file and a corpus/folder of 
xml files. Can also be useful for modern English texts with the preprocessing and normalizing rules
turned off, who are originally written for processing early modern English text. The default wrapped
up StanfordCoreNLP software is the state-of-the-art English processing toolkit.

Even if you are not fluent in feature engeering or regular expressions, changing the config files
in a word-to-word pair manner can also help you utilize this framework to the fullest and make it
more specific to your text processing needs.  
'''
from corenlpToolbox import stanfordAnnotator as STA
from debugger import * 
from threading import Thread
# besides its only functionalities, importing debugger saves us from importing the following: 
# from utils import *
# from xmlHandler import *
# from textPreprocessor import *
# from textNormalizer import *
# from os.path import exists, join etc.
# from os import mkdir etc.

# The path_to_corenlp must be set up in corenlpToolbox.py, before running this script. 
# In the future release of HELPtk, I may include more portable as the alternative 
# Tokenizer and Annotator. 
sta = STA()


def _make_attr_pair(key, value):
    '''Create a xml node attritube given key and value.'''
    if value != "\"":
        return f'{key}="{value}"'
    return f"{key}='{value}'"

def _make_attr_pairs(keys, values):
    '''Create a list of xml node attritubes given keys and values.'''
    return ' '.join([_make_attr_pair(k, v) for (k, v) in zip(keys, values)])


def _make_node(node_name, text, attrs):
    '''Create a xml node given the node name, text and the node attritubes.'''
    return f"<{node_name}{attrs}>{text}</{node_name}>"


def _make_word_node(text, attrs, node_name='w'):
    '''Create a xml word node for every word tokenized.'''
    return _make_node(node_name, text, attrs)


def _lst_as_func(lst):
    '''Turn a list into a function. If an empty list is given, the 
    converted lst_func will return an empty list no matter what is being inputted. 
    Whereas when a single-layer list is inputted, the converted lst_func will turn every 
    element into a list; and when a multiple layers list is given, the lst_func will zip 
    them together so that they can be retrived row by row (elements in corresponding position).'''
    def empty_lst(*arg):
        return []
    def norm_lst(idx):
        return lst[idx]
    if lst:
        if not isinstance(lst[0], (list, tuple)):
            lst = [[l] for l in lst]
        else:
            lst = [list(l) for l in zip(*lst)]
        return norm_lst   
    return empty_lst


def _build_new_body(filepath, tokenized, normalized, tags,
                    annotation_keys=[], annotation_values=[]):
    '''Build a new body for a xml file to be remade.
    
    Args:
        - tokenized(str): xml-like tokenized body text, or preprocessed text.
        
        - normalized(str or NoneType): when normalized is NoneType, the text is 
        not normalized. The normalized text will also be xml-like.
        
        - tags(list): original tags in the old body text. These tags are conveniently
        extracted and replaced with because it turns out that StanfordCoreNLP will
        perfectly igonre them all as ADD. Conversely, if the original tags were kept,
        StanfordCoreNLP occassionally will mis-annotate them.
        
        - annotation_keys(list): a list of names for the annotations performed. Possible names: 
        ['pos'], ['lemma'], and ['pos', 'lemma']. When empty list is given, that means no
        annotations were performed.
                                
        - annotation_values(list): the list of annotations corresponding to the annotation_keys. 
        When empty list is given, that means no annotations were performed. 
    
    Return(str):
        The remade xml-like body text with word nodes (with or without attributes).
    '''
    new_body =[]
    tag_idx = 0
    
    # convert the tokenized into a list of tokens based tags and whitespaces 
    tokenized = re.findall(r"(</?[^>]+>|\S+)", tokenized)
    annotated = _lst_as_func(annotation_values) # this turns the annotation_values into a "list_func", see above.
    # if normalized text was made
    if normalized:
        keys = ['Original', 'Normalized'] + annotation_keys
        normalized = re.findall(r"(</?[^>]+>|\S+)", normalized)
        
        # aligning tags and words one by one.
        try:
            for i in range(len(tokenized)):
                if tokenized[i][0] == "<" and tokenized[i][-1] == ">":
                    new_body.append(tags[tag_idx])
                    tag_idx += 1
                else:
                    # the will be always [] if no annotation_values was given and a corresponding list if it is not empty. 
                    values = [tokenized[i], normalized[i]] + annotated(i) 
                    attr = _make_attr_pairs(keys, values) # make the word attributes.
                    new_body.append(_make_word_node(tokenized[i], " " + attr))
                    
        except Exception as e:
            print(f"\033[32mWordMisalignmentError: \033[0m for {filepath}", e)
            
    # if no normalized text was made
    else:
        try:
            if len(annotation_keys) >= 1:
                keys = ['Original'] + annotation_keys
                for i in range(len(tokenized)):
                    if tokenized[i][0] == "<" and tokenized[i][-1] == ">":
                        new_body.append(tags[tag_idx])
                        tag_idx += 1
                    else:
                        values = [tokenized[i]] + annotated(i)
                        attr = _make_attr_pairs(keys, values)
                        new_body.append(_make_word_node(tokenized[i], " " + attr))
            else:
                for i in range(len(tokenized)):
                    if tokenized[i][0] == "<" and tokenized[i][-1] == ">":
                        new_body.append(tags[tag_idx])
                        tag_idx += 1
                    else:
                        new_body.append(_make_word_node(tokenized[i], ""))
                        
        except Exception as e:
            print(f"\033[32mWordMisalignmentError: \033[0m for {filepath}", e)
            
    return ' '.join(new_body)


def _debug(file_dir, filename, spell_norm, word_alignment_debug):
    '''Debug whether the remade xml file has the desired level of words alignments. This debugger is
    only on when the spelling normalization has been performed. Althogh it is also feasible to compare
    words and lemma, but lemma will require a normalized text in order for it to look good on histoical
    English text. Nevertheless, lemma-based words alignments are not provided for convenience. To compare
    differences between original texts and lemma or any word node attributes, use attr_diff_in_xml_word_nodes()
    or print_attr_diff_in_xml_word_nodes() from debugger.py intead.'''
    
    if not spell_norm and word_alignment_debug:
        print("word_alignment_debug is for spelling normalized text only.")
        return
    if not word_alignment_debug:
        return 
    
    filepath = join(file_dir, filename)
    words_alignment_debugger(filepath)

        
def _skip_exists(filepath, skip_exists):
    '''When skip_exists set True, return True when the file already exists. Otherwise, False.'''
    if skip_exists:
        if exists(filepath):
            print(f"\033[33m{filepath} also exists. If you want to overwrite this file, do skip_exists=False.\033[0m")
            return True
    return False
    

def _text_len_check(text, low=0, high=1000000):
    '''Check whether the given text falls into the desired range.'''
    if high == None:
        return 0
    if not isinstance(high, int):
        raise TypeError("The upper limit for the text must be an integer or None.")
    if len(text) > low and len(text) <= high:
        return 0
    if len(text) < low:
        return -1
    return 1
    
    
def _tokenize_xml(filepath, head_node, body_node, apply_prep_rules=False, spell_norm=False,
                  text_lower_len=0, text_upper_len=1000000):
    
    '''Tokenize/preprocess and/or normalize the body text of a given xml filepath. 
    
    Args:
        - filepath(str): filepath.
        
        - head_node(str): the name of the header node, such as "header", "teiheader" etc.
        
        - body_node(str): the name of the body node, such as "text", "doc". Ideally, the head_node part
        and body_node part can make up the entire xml.
        
        - apply_prep_rules(bool): Defaults to False. If set True, the program will perform the text
        preprocessing rules that are mostly relevant for early modern English texts. Without
        apply_prep_rules=True, the xmlRamaker is suitable for the contemporary English texts as
        it is based on the state-of-the-art Stanford CoreNLP software.
        
        - spell_norm(bool): whether to apply spelling normalization rules. Likewise, as the rules are mostly 
        relevant for non-early modern English texts, turning it off can speed up the program. Thus, defaults to False.
        
        - text_lower_len(int): the lower limit for the text to be remade (counted by characters). Defaults to 0.
        
        - text_upper_len(int): the upper limit for the text to be remade (counted by characters). 
        Defaults to 1000000, which empirically will gaurantee a fast processing of the algorithms even
        when the richest text annotations are turned on. If none is given, there will be no body text length limit.
        
    Returns:
        - header(str): xml-like header text, including all the tags. 
        - body(str): xml-like body text, re-tokenized (so that the tokens are separated by whitespcaes) or preprocessed
        (if apply_prep_rules=True), with the original tags temporarily replaced by <tag> to improve the accuracy of the StanfordCoreNLP software.
        
        - body_norm(str or None): if spell_norm=True, body_norm = xml-like normalized body text; otherwise, None.
        
        - tags(list): the original tags in the body text.'''
    
    header, body = get_header_body_as_str(filepath, head_node, body_node)
    
    # performing the body text length test to see whether the body text falls in the desired length range.
    len_ch = _text_len_check(body, text_lower_len, text_upper_len)
    if len_ch == 1:
        print(f"\033[34mSkipping {filepath}: body text {len(body)} chars, exceeds the preset upper text limit: {text_upper_len}.")
        print("\033[0mYou can either reset the upper text limit or turn it off by setting text_upper_len=None.")
        return 
    if len_ch == -1:
        print(f"\033[34mSkipping {filepath}: body text {len(body)} chars, below the preset text_lower_len: {text_lower_len} chars.")
        print("\033[0mYou can either reset the lower text limit or turn it off by setting text_lower_len=0.")
        return 
    
    tags = re.findall(r"<[^>]+>", body)
    body = re.sub(r"<[^>]+>", "<tag>", body)
    body = textPreprocessing(body, apply_prep_rules=apply_prep_rules)
    if spell_norm:
        body_norm = textNormalizing(body)
        # 嗨 is a marker to locate past tense verb ending with 'd, now change it back 
        # to where it should be after the text has been normalized.
        # the reason to spell 嗨'd all out is to make sure that the original 嗨 if any is not changed
        body = re.sub(r"嗨'd", "'d", body) 
        if len(body_norm.split()) != len(body.split()):
            print(f"\033[31mLength not equal. Filepath: {filepath}\033[0m")
            # log the words misalignments. This is automatic, unless the code is removed.
            words_misalignments_logger(filepath, body.split(), body_norm.split())
            return 
        return header, body, body_norm, tags
    
    # if no spell norm is performed, also need to change the 嗨'd back to 'd
    body = re.sub(r"嗨'd", "'d", body)
    return header, body, None, tags
    

def _execute(file_dir, filename, head_node, body_node, root_name='TEI.2', dst_dir='./',
             apply_prep_rules=False, spell_norm=False, word_alignment_debug=False, skip_exists=True,
             text_lower_len=0, text_upper_len=1000000, annotation_keys=[], annotation_func=None):
    ''''The abstract func to execute: tokenization/preprocessing, normalization, pos tagging, 
    lemmatization and all of their combinations.
    
    Args:
        - file_dir(str): file_dir.
        - filename(str): filename.
        - head_node(str): the name of the header node.
        - body_node(str): the name of the body node.
        - root_name(str): the name of the first super node for the xml file, defaults to "TEI.2".
                        In principle, the root refers to the entire Document. The root here is just for
                        easy understanding.
        
        - dst_dir(str): path-like str. Directory to save the remade xml file.
        
        - apply_prep_rules(bool): Whether to apply preprocessing rules to the text. Defaults to False, meaning only the Standard
                                Stanford Tokenizer (with hyphensplit turned off) will be performed.
                                
        - spell_norm(bool): whether to apply spelling normalization rules. Defaults to False.
        
        - word_alignment_debug(bool): whether to perform word alignment debugging test for the remade xml file.
        
        - skip_exists(bool): whether to not overwrite a remade xml file if it already exists. Defaults to True.
        
        - text_lower_len(int): the lower limit for the text to be remade (counted by characters). Defaults to 0.
        
        - text_upper_len(int): the upper limit for the text to be remade (counted by characters).
                            Defaults to 1000000. If None is given, there will be no body text length limit.
                            
        - annotation_keys(list): the annotation_keys if any, defaults to an empty list, which equals to only executing
                                the tokenization or preprocessing of the xml file. See _build_new_body method above.
                                 
        - annotation_func(method or None): the correponding annotation_func that can get the annotation_values to 
                                         build the new body for the xml file to be remade.
                                         '''
    
    filepath_in = join(file_dir, filename)
    fn_out = filename if "/" not in filename else filename.split("/")[-1]
    if _skip_exists(join(dst_dir, fn_out), skip_exists):
        return
    
    res = _tokenize_xml(filepath_in, head_node, body_node, 
                        apply_prep_rules, spell_norm, text_lower_len, text_upper_len)
    
    # if res == None, either the body text length test fails (either the file too small or to big), 
    # or there are words misalignments between the normalized body (if any) and the tokenized/preprocessed body.
    if res == None:
        return

    header, body, body_norm, tags = res
    
    if not annotation_keys:
        annotation_values = []
    else:
        if spell_norm:
            annotation_values = annotation_func(body_norm)
        else:
            annotation_values = annotation_func(body)

    new_body = _build_new_body(filepath_in, body, body_norm, tags, annotation_keys, annotation_values)
    createXmlFileFromStr(fn_out, root_name, header, new_body, dst_dir)
    _debug(dst_dir, fn_out, spell_norm, word_alignment_debug)


def tokenize_xml_body(file_dir, filename, head_node, body_node, root_name='TEI.2', dst_dir='./',
                      apply_prep_rules=False, spell_norm=False, word_alignment_debug=False, skip_exists=True,
                      text_lower_len=0, text_upper_len=1000000):
    '''Function to tokenize a single xml file's body with further preprocessing and spelling normalization optional.
    More about the args, please do print(xmlRemaker._execute.__doc__) to check it out.'''
    
    _execute(file_dir, filename, head_node, body_node, root_name, dst_dir, apply_prep_rules, spell_norm,
             word_alignment_debug, skip_exists, text_lower_len, text_upper_len, annotation_keys=[], annotation_func=None)
        

def pos_tag_xml_body(file_dir, filename, head_node, body_node, root_name='TEI.2', dst_dir='./',
                       apply_prep_rules=False, spell_norm=False, word_alignment_debug=False, skip_exists=True,
                       text_lower_len=0, text_upper_len=1000000):
    ''''Function to pos tag a single xml file's body with further preprocessing and spelling normalization optional.
    More about the args, please do print(xmlRemaker._execute.__doc__) to check it out.'''
    
    _execute(file_dir, filename, head_node, body_node, root_name, dst_dir, apply_prep_rules, spell_norm,
             word_alignment_debug, skip_exists, text_lower_len, text_upper_len, annotation_keys=['pos'], annotation_func=sta.get_pos_tags)
    

def lemmatize_xml_body(file_dir, filename, head_node, body_node, root_name='TEI.2', dst_dir='./',
                       apply_prep_rules=False, spell_norm=False, word_alignment_debug=False, skip_exists=True,
                       text_lower_len=0, text_upper_len=1000000):
    ''''Function to lemmatize a single xml file's body with further preprocessing and spelling normalization optional.
    More about the args, please do print(xmlRemaker._execute.__doc__) to check it out.'''
    
    _execute(file_dir, filename, head_node, body_node, root_name, dst_dir, apply_prep_rules, spell_norm,
             word_alignment_debug, skip_exists, text_lower_len, text_upper_len, annotation_keys=['lemma'], annotation_func=sta.get_lemma)
    

def xml_body_with_pos_lemma(file_dir, filename, head_node, body_node, root_name='TEI.2', dst_dir='./',
                            apply_prep_rules=False, spell_norm=False, word_alignment_debug=False, skip_exists=True,
                            text_lower_len=0, text_upper_len=1000000):
    '''Function to pos tag and lemmatize a single xml file's body with further preprocessing and spelling normalization optional.
    More about the args, please do print(xmlRemaker._execute.__doc__) to check it out.'''
    
    _execute(file_dir, filename, head_node, body_node, root_name, dst_dir, apply_prep_rules, spell_norm,
             word_alignment_debug, skip_exists, text_lower_len, text_upper_len, ['pos', 'lemma'], sta.get_pos_and_lemma)
        

class xmlCorpusRemaker:
    '''Class method for remaking a corpus of xml files, partial or entire. 
    
    Args (initialization): 
        - corpus_dir(str): corpus directory. 
        - head_node(str): head_node name.
        - body_node(str): body_node name.
        - root_name(str): the name of the first super node for the xml file, defaults to "TEI.2".
        
        - dst_dir(str): the directory to hold the remade xml files. If not given, a dst_dir named after
        the original corpus_dir with "_remade" in the end will appear in the same directory of the corpus_dir.
        
        - include_sub_dir(bool): defaults to False. When set True, return all the filenames with the
        corpus_dir, including those from the sub_dir. Filenames from the sub_dir will also be prefixed
        with the sub_dir, but the original sub_dir will not be kept in the remade xml corpus directory.
        
        - shuffle(bool): defaults to False. When set True, the filenames will be shuffled. Another way to shuffle
        the filenames is to use the function shuffle_filename() included in the class method. Check the bottom line of this doc.
    
    ##############
    Example usage:
    ##############
    
    >>> remaker = xmlCorpusRemaker(corpus_dir, head_node, body_node,...)
    
    # tokenize/preprocess the whole or part of the corpus:
    >>> remaker.tokenize_the_corpus()
    
    # pos tag the_corpus (including tokenization/preprocessing)
    >>> remaker.pos_tag_the_corpus()
    
    # lemmatize the corpus (including tokenization/preprocessing)
    >>> remaker.lemmatize_the_corpus()
    
    # pos tag and lemmatize the corpus (including tokenization/preprocessing)
    >>> remaker.corpus_with_pos_lemma()
    
    **************************************************************************************************************
    * All these four methods inlcude the same set of parameters:                                                   
    *                                                                                                              
    * - apply_prep_rules(bool): whether to appply preprocessing rules that are more relevant to                    
    * early modern English text. Defaults to False.
    *
    * - spell_norm(bool): whether to appply spelling normalization rules that are more relevant to                 
    * early modern English text. Defaults to False.
    *
    * - num_or_ratio(int or float or None): the number of files in the corpus to be processed on when given int;   
    * the ratio of the corpus to be processed when given float; otherwise, defaults to None, which will process
    * the entire coorpus.
    *
    * - word_alignment_debug(bool): whether to perform word alignment debugging tests for remade xml files.        
    * Defaults to False. Not recommeded to turn on if the num of files to process is large. Recommeded only
    * for testing the program on the selected corpus.     
    *                                                                                                              
    * - skip_exists(bool): whether to skip already extant remade xml files. Defaults to True.
    *
    * - text_lower_len(int): the lower limit for the text to be remade (counted by characters). Defaults to 0.
    *
    * - text_upper_len(int or None): the upper limit for the text to be remade (counted by characters).            
    * Defaults to 1000000. If None is given, there will be no body text length limit.
    *
    * - multitasking(bool): whether to do multithreading, defaults to False.
    *
    * - threads_num(int): number of threads occuring at the runtime, defaults to 10.                               
    **************************************************************************************************************
    
    # Besides, the class also provide handy method to show the corpus files by
    >>> remaker.show_filenames()
    # Or to randomize the filenames, which will be important while playing around the corpus.
    >>> remaker.shuffle_filename()
    '''
    def __init__(self, corpus_dir, head_node, body_node, root_name='TEI.2', dst_dir=None,
                 include_sub_dir=False, shuffle=False):
        
        self._corpus_dir = corpus_dir  + "/" if not corpus_dir.endswith("/") else corpus_dir
        self._filenames = get_filenames_from_dir(corpus_dir, include_sub_dir, ".xml", shuffle)
        self._head_node = head_node
        self._body_node = body_node
        if not get_node(join(corpus_dir, self._filenames[0]), head_node):
            print("Test run. head_node not found. Please double check and/or recall this class.")
        if not get_node(join(corpus_dir, self._filenames[0]), body_node):
            print("Test run. body_node not found. Please double check and/or recall this class.")
        
        if dst_dir:
            self._dst_dir = dst_dir
        else:
            if not corpus_dir.endswith("/"):
                self._dst_dir = corpus_dir + "_remade/"
            else:
                self._dst_dir = "/".join(corpus_dir.split("/")) + "_remade/"
        if not exists(self._dst_dir):
            mkdir(self._dst_dir)
            print(self._dst_dir + " has been created.")
        
        self._root_name = root_name    
    
    def show_filenames(self, num_to_show=None):
        return self._filenames
    
    def shuffle_filename(self):
        random.shuffle(self._filenames)

    def get_remade_xml_filepaths(self):
        filenames = get_filenames_from_dir(self._dst_dir, False, ".xml")
        return [join(self._dst_dir, f) for f in filenames]
    
    def _get_part(self, num_or_ratio):
        if num_or_ratio is None:
            return None
        elif isinstance(num_or_ratio, int):
            return num_or_ratio
        elif num_or_ratio>0. and num_or_ratio<1.:
            return len(self._filenames) * num_or_ratio
        else:
            raise TypeError("num_or_ratio must be either int, float in (0, 1), or not given (None).")
    
    def _run(self, func, apply_prep_rules, spell_norm, num_or_ratio, word_alignment_debug,
             skip_exists, text_lower_len, text_upper_len, multitasking, threads_num):
        
        part = self._get_part(num_or_ratio)
        if not multitasking:
            for filename in self._filenames[:part]:
                func(self._corpus_dir, filename, self._head_node, self._body_node, 
                             self._root_name, self._dst_dir, apply_prep_rules, spell_norm,   
                              word_alignment_debug, skip_exists, text_lower_len, text_upper_len)
        else:
            end = len(self._filenames[:part])
            for i in range(0, end, threads_num):
                threads = []
                for filename in self._filenames[:part][i: i + threads_num if i + threads_num <= end else end]:
                    
                    t = Thread(target=func, args=(self._corpus_dir, filename, self._head_node, self._body_node, 
                                                  self._root_name, self._dst_dir, apply_prep_rules, spell_norm,   
                                                  word_alignment_debug, skip_exists, text_lower_len, text_upper_len,))
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
    
    def tokenize_the_corpus(self, apply_prep_rules=False, spell_norm=False, num_or_ratio=None,
                            word_alignment_debug=False, skip_exists=True,
                            text_lower_len=0, text_upper_len=1000000,
                            multitasking=False, threads_num=10):
        
        self._run(tokenize_xml_body, apply_prep_rules, spell_norm, num_or_ratio, word_alignment_debug, 
                  skip_exists, text_lower_len, text_upper_len, multitasking, threads_num)
                
    def pos_tag_the_corpus(self, apply_prep_rules=False, spell_norm=False, num_or_ratio=None,
                           word_alignment_debug=False, skip_exists=True,
                           text_lower_len=0, text_upper_len=1000000,
                           multitasking=False, threads_num=10):
        
        self._run(pos_tag_xml_body, apply_prep_rules, spell_norm, num_or_ratio, word_alignment_debug, 
                  skip_exists, text_lower_len, text_upper_len, multitasking, threads_num)
    
    def lemmatize_the_corpus(self, apply_prep_rules=False, spell_norm=False, num_or_ratio=None,
                             word_alignment_debug=False, skip_exists=True,
                             text_lower_len=0, text_upper_len=1000000,
                             multitasking=False, threads_num=10):
        
        self._run(lemmatize_xml_body, apply_prep_rules, spell_norm, num_or_ratio, word_alignment_debug, 
                  skip_exists, text_lower_len, text_upper_len, multitasking, threads_num)
    
    def corpus_with_pos_lemma(self, apply_prep_rules=False, spell_norm=False, num_or_ratio=None,
                              word_alignment_debug=False, skip_exists=True,
                              text_lower_len=0, text_upper_len=1000000,
                              multitasking=False, threads_num=10):
        
        self._run(xml_body_with_pos_lemma, apply_prep_rules, spell_norm, num_or_ratio, word_alignment_debug, 
                  skip_exists, text_lower_len, text_upper_len, multitasking, threads_num)

    def debug_remade_corpus(self, num_or_ratio=None, check_num=10, err_threshold=0.1, print_msg=True):
        part = self._get_part(num_or_ratio)
        filepaths = self.get_remade_xml_filepaths()
        try:
            for f in filepaths:
                words_alignment_debugger(f, "w", check_num, err_threshold, print_msg)
        except:
            print("\033[32mCorpus Not Normalized.\033[0m words_alignment_debugger method" \
                  " is for Normalized remade xml files only. To compare differences between" \
                  "attributes, call attr_diff_in_xml_word_nodes or print_attr_diff_in_xml_word_nodes" \
                  "from debugger.py instead.")
