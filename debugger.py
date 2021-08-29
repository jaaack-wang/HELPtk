'''
- Author: Zhengxiang (Jack) Wang 
- Date: 2021-08-26 created, 08-27 modified 
- GitHub: https://github.com/jaaack-wang 
- About: A set of debuggers for the Historical English Language Processing Toolkit (HELPtk),

including:
    - debugging the config folder files' formats;
    - debugging the transformation rules as stored in the config folder;
    - debugging whether the normalized xml files has flawless words alignments;
    - debugging the words misalignments that prevents the re-making of the xml files.

Moreover, print_attr_diff_in_xml_word_nodes method can be used for post hoc analysis:
    - (1), check whether every word node has the attributes we plug in;
    - (2) the differences between two interested attributes (e.g., historical vs. normalized spellings).
'''
from utils import *
from xmlHandler import *
from textPreprocessor import *
from textNormalizer import *
from os.path import exists
from os import mkdir


config_path = "./config/"
if not exists(config_path):
    config_path = None


def _file_format_debugger(filepath, items_per_line_min, delimiter="\t",
                          skip_header=True, print_msg=True):
    '''File format checker.'''
    count, err = 0, 0
    f = open(filepath, 'r')
    if skip_header: 
        next(f)
        count = 1
    for line in f:
        count += 1
        line = line.split(delimiter)
        l_n = len(line)
        if l_n < items_per_line_min:
            err += 1
            if print_msg:
                print(f"\033[31mFileFormatErro\033[0m\n{filepath}, line {count}," \
                      " {items_per_line_min} items expected, {l_n} items found: {str(line)}")
    if print_msg:
        if err:
            print(f"\033[4m\nA total of {err} formatting errors found for {filepath}.\033[0m\n")
        else:
            print(f"\n{filepath} passes the format debugging test!\n")
    
    return err


def config_file_formats_debugger(config_path=config_path, delimiter="\t", print_msg=True):
    '''Checks whether the files in the config folder all have the correct formatting. 
    
    Args:
        - config_path(str): path to the config folder. Defaults to "./config/".
        - delimiter(str): delimiter used in the config files. Defaults to "\t".
        - print_msg(bool): whether to print debugging messages. Defaults to True. 
    
    Return(int):
        The total number of errors identifed for the 4 config files. 
    '''
    assert config_path != None, "No config_path given."
    p = config_path + "/" if config_path[-1] != "/" else config_path
    err = []
    files = ["common_verbs.txt", "normalizing_rules.txt", "preprocessing_rules.txt", "test_sample.txt"]
    err.append(_file_format_debugger(p + files[0], 3, delimiter, print_msg=print_msg))
    err.append(_file_format_debugger(p + files[1], 2, delimiter, skip_header=False, print_msg=print_msg))
    err.append(_file_format_debugger(p + files[2], 2, delimiter, skip_header=False, print_msg=print_msg))
    err.append(_file_format_debugger(p + files[3], 3, delimiter, print_msg=print_msg))
    
    if print_msg:
        if sum(err) == 0:
            print("\nThe 4 config files all passed the format debugging test!")
        else:
            for i in range(len(err)):
                if err[i] == 0:
                    print(files[i] + " passed the format debugging test!\n")
                else:
                    print("\033[31m" + files[i] + " failed the format debugging test!\033[0m") 
    return sum(err)


def print_test_sample_file(filepath="config/test_sample.txt", delimiter="\t", print_err_msg=False, 
                         num_lines_to_show=None):
    '''Print the test sample file.'''
    
    try:
        f = open(filepath, "r")
    except:
        raise NameError("No filepath given or wrong filepath given. Current filepath: {filepath}")
    
    e = _file_format_debugger(filepath, 3, delimiter, True, print_err_msg)
    assert e == 0, "Test sample file fails in the file format debugging test." \
           " Please run this method again with print_err_msg=True."
    
    next(f)
    f = f.readlines()
    print(f"{len(f)} examples found, showing {len(f[:num_lines_to_show])} examples below.\n\n")
    
    tmp = "{0:20}{1:20}{2:20}"
    print(tmp.format("Raw Text", "Expected Preprocessed Text", "Expected Normalized Text\n"))
    for line in f[:num_lines_to_show]:
        line = line.split(delimiter)
        print(tmp.format(line[0], line[1], line[2].strip()))

        
def _word_debuger(obj_name, ori, expected, real, print_msg=True):
    '''Word debugger, checking whether a func converts a word into the expected form.'''
    
    if expected != real:
        if print_msg:
            print(f"\033[31m- {obj_name} error. Expected: [{expected}], but [{real}] was given for [{ori}].\033[0m")
        return True
    return False
    

def trans_rules_debugger(config_path=config_path, delimiter="\t"):
    '''Tranformation rules debugger.'''
    
    e = config_file_formats_debugger(config_path, delimiter, False)
    assert e == 0, "Config files fails in the file format debugging tests!" \
           " Please run config_file_formats_debugger() to debug." 
    
    test_sample = open(config_path + "test_sample.txt", 'r')
    next(test_sample)
    err = 0
    for line in test_sample:
        example, preprocessed, normalized = line.split('\t')
        normalized = normalized.strip()
        prep = textPreprocessing(example, apply_prep_rules=True)
        if _word_debuger("Preprocessing", example, preprocessed, prep):
            err += 1
            
        norm = textNormalizing(prep)
        if _word_debuger("Normalizing", example, normalized, norm):
            err += 1
            
    if err:
        print(f"\033[4m\n{err} erros identified during the transformation rules debugging test!\033[0m")
    else:
        print("\033[1mCongratulations!\033[0m The transformation rules pass the debugging test.")
    
    
def words_alignment_debugger(filepath, word_node="w", check_num=10, err_threshold=0.1, print_msg=True):
    '''Check whether the given restructured xml file aligns the original words with the normalized words correctly.
    
    Args:
        - filepath(str): path to the file.
        - check_num(int): Number of beginning and ending words to check, defaults to 10. The assumption here is simple,
                        if both the beginning words and the ending words are well aligned, that means the file is
                        correctly restructured and remade. 
        - err_threshold: the potential err rates that can be tolerated, defaults to 0.1, among every 10 words checked,
                        there can be no more than 1 potential error identified.
    '''
    
    words = get_nodes(filepath, word_node)
    to_check = words[:check_num] + words[-check_num:]
    potential_err = 0.
    for w in to_check:
        ori = w['Original']
        expected = textNormalizing(ori.lower())
        real = w['Normalized'].lower()
        if _word_debuger("Word alignment", ori, expected, real, print_msg):
            potential_err += 1
    
    print(f"\033[32m{potential_err} potential word misalignments for {filepath}\033[0m")
    err_rate = potential_err / (2 * check_num) 
    if err_rate > err_threshold:
        print(file_path + "needs manual check.")
    
    print(f"The potential error rate is {err_rate} < preset err threshold: {err_threshold}.")
    print(f"\033[1mGood! {filepath} passed the word alignment test!\033[0m")


def attr_diff_in_xml_word_nodes(filepath, word_node="w", attr_one="Original", attr_two="Normalized", 
                                num_of_dif_to_print=0):
    
    '''Returns the differences in a xml's word nodes between two chosen attributes, which
    can either be differences due to text processing (e.g., raw text versus normalized text, 
    lemma versus non-lemma etc.), or differences due to mislignments.
    
    Args:
        - filepath(str): filepath.
        - word_node(str): the keyword represents word nodes in the xml, defaults to "w".
        - attr_one(str): attribute one.
        - attr_two(str): attribute two.
        - num_of_dif_to_print(int): number of differences to print, defaults to 100. When set 0, 
                                    show all differences. 
    
    Return(list):
        A list of different related attributes of the word nodes stored in a tuple along with the 
        correponding word indices. 
    '''
    words = get_nodes(filepath, word_node)
    diffs = []
    for i in range(len(words)):
        w1, w2 = words[i][attr_one], words[i][attr_two]
        if w1 != w2:
            diffs.append((i, w1, w2))
            num_of_dif_to_print -= 1
            if not num_of_dif_to_print:
                break
    return diffs


def print_attr_diff_in_xml_word_nodes(filepath, word_node="w", attr_one="Original", attr_two="Normalized", 
                                      num_of_dif_to_print=0):
    '''Prints the differences in a xml's word nodes between two chosen attributes.'''
    diffs = attr_diff_in_xml_word_nodes(filepath, word_node, 
                                        attr_one, attr_two, num_of_dif_to_print)
    if num_of_dif_to_print == 0:
        print(f"A total of {len(diffs)} differences found in {filepath}, showing them all below:\n")
    
    elif len(diffs) < num_of_dif_to_print: 
        print(f"Only {len(diffs)} differences found, showing them all below:\n")
    
    else:
        print(f"Showing {num_of_dif_to_print} identified differences from {filepath} below:\n")
    
    print(("Word index", attr_one, attr_two), end="\n\n")
    for d in diffs:
        print(d)

        
def words_misalignments_logger(filepath, tokenized_lst, normalized_lst):
    '''Log the words misalignments between the tokenized_lst and normalized_lst, 
    which are not unequally long. All the words misalignments will be logged only if 
    normalized_lst or tokenized_lst constantly has extra tokens than the other. The log
    file will be saved in a auto-created word misalignment logger folder in the current
    working directory where the debugger.py is placed.'''
    
    filename = filepath.split("/")[-1] + ".txt"
    t_len, n_len = len(tokenized_lst), len(normalized_lst)
    
    if not exists("./word misalignment logger/"):
        mkdir("./word misalignment logger/")
        print("./word misalignment logger/ directory has been created!")
        
    if exists(f"./word misalignment logger/{filename}"):
        print(f"The word misalignment in ./word misalignment logger/{filename} has been logged already. Do remember check!")
        return
    
    fw = open(f"./word misalignment logger/{filename}", "w")
    fw.write(f"Original filepath: {filepath}, tokenized token numbers: {t_len}, normalized token numbers: {n_len}\n\n")
    temp = "{0:20}{1:20}{2:20}\n"
    fw.write(temp.format("Word Index", "Preprocessed", "Normalized"))

    # make two copies of the tokenized_lst and the normalized_lst
    tk_lst = tokenized_lst.copy()
    norm_lst = normalized_lst.copy()
    
    total_gap = abs(n_len - t_len)
    pre_mis_idx = 0
    misalign_idx = []
    min_len = min(t_len, n_len)
    for i in range(min_len):
        if tokenized_lst[i] != normalized_lst[i]:
            cur_mid_idx = i
            if cur_mid_idx - pre_mis_idx == 1:
                misalign_idx.append(pre_mis_idx)
                total_gap -= 1
                if total_gap == 0:
                    break
                if tokenized_lst[cur_mid_idx] == normalized_lst[cur_mid_idx+1]:
                    del normalized_lst[cur_mid_idx+1]
                elif tokenized_lst[cur_mid_idx+1] == normalized_lst[cur_mid_idx]:
                    del tokenized_lst[cur_mid_idx+1] 
            
            pre_mis_idx = cur_mid_idx
                    
    for idx in misalign_idx:
        if idx - 1 >= 0:
            fw.write(temp.format(idx - 1, tk_lst[idx - 1], norm_lst[idx - 1]))
        fw.write(temp.format(idx, tk_lst[idx], normalized_lst[idx]))
        if idx + 1 < min_len:
            fw.write(temp.format(idx + 1, tk_lst[idx + 1], norm_lst[idx + 1]))
        fw.write("\n")
        
    fw.close()
    print(f"\033[1mThe word misalignment in ./word misalignment logger/{filename} has been logged! Please check it out!\033[0m")
