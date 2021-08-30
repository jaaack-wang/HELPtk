# General intro

## What is included
HELPtk (**H**istorical **E**nglish **L**anguage **P**rocessing Tool**tk**) is an efficient toolkit and a general framework for early modern & modern English Language Processing. It comes with: 

- A set of builtin preprocessing and normalizing rules that are relevant to the tokenization and normalization of early modern English (still under development. See: [config folder](https://github.com/jaaack-wang/HELPtk/tree/main/config)).
- A [corenlpToolbox](https://github.com/jaaack-wang/HELPtk/blob/main/corenlpToolbox.py) that provides a general method to enable Python to make the fullest use of [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) without text length restrictions imposed by the use of server. 
- A [xmlRemaker](https://github.com/jaaack-wang/HELPtk/blob/main/xmlRemaker.py) that make tokenizing, normalizing and annotating a XML file and corpus easy, fast, more accurate, more specified, and without losing the original annotated or textual information during the remaking of the original XML file(s). 
- A set of [debuggers](https://github.com/jaaack-wang/HELPtk/blob/main/debugger.py) that help debug and identify the potential errors in the configuration files' formatting, and check whether the [textPreprocessor](https://github.com/jaaack-wang/HELPtk/blob/main/textPreprocessor.py) and [textNormalizer](https://github.com/jaaack-wang/HELPtk/blob/main/textNormalizer.py) perform the transformation rules as desired. More importantly, the debuggers conduct automatic words alignments debugging to ensure the added normalizations and annotations well aligned with the original corresponding texts; and log the misaligned words automatically for post hoc error analysis.

## Why do this 

HELPtk is a product of playing around with the [Early Modern Multiloquent Authors (EMMA) Corpus](https://www.uantwerpen.be/en/projects/mind-bending-grammars/emma-corpus/), a large collection of 50 prolific London-based English writers born in the 17th century. However, it turns out HELPtk works well for modern English texts too either with or without the builtin preprocessing and normalizing rules turned on (as they are not very relevant and hence less harmful). In fact, it is interesting to apply those rules to modern English and use the functions in the [debuggers](https://github.com/jaaack-wang/HELPtk/blob/main/debugger.py) to see the differences between the normalized words and the original words, which can (1) either help you to learn the changes of English language; (2) and the potential improvements for the rules. 

## Reliability 

**In terms of just tokenizing and annotating XML files with good words alignments, [xmlRemaker](https://github.com/jaaack-wang/HELPtk/blob/main/xmlRemaker.py) should mostly work.** As of now, I have tested it on 13750 XML files from [EMMA](https://www.uantwerpen.be/en/projects/mind-bending-grammars/emma-corpus/) with a few erros fixed. It has also been applied to both [the British Academic Spoken English (BASE) Corpus](http://www.reading.ac.uk/acadepts/ll/base_corpus/) and the [Michigan Corpus of Academic Spoken English Corpus](https://quod.lib.umich.edu/m/micase/) smoothly and the results look good, thanks to Stanford CoreNLP. Additionally, applying the xmlRemaker to a variety of randomly selected historical English texts (i.e., Eighteenth Century Collections Online (ECCO) TCP, Early English Books Online (EEBO) TCP and Evans Early American Imprint Collection) as provided in this [historical-texts GitHub repository](https://github.com/Anterotesis/historical-texts) did not cause any obvious errors either in terms of formatting. 

## Effeciency 

Depending on the file size and the task performed, for a normal corpus, such as the BASE corpus where there are 197 files and a total of 1.6 million tokens, with `multisasking=True`, HELPtk can tokenize, pos tag, lemmatize and remake the entire corpus with just about 5 minutes for a single running window. HELPtk also tokenized, further preprocessed, normalized, pos tagged, lemmatized and remade <ins>13,100</ins> XML files of EMMA (all below 200KB) for a single running window with `multisasking=True` for about 3 hours and half.


# General usage

## Remake XML file(s)

[xmlRemaker](https://github.com/jaaack-wang/HELPtk/blob/main/xmlRemaker.py) contains highly wrapped up functions that enables the remaking of XML file(s) a matter of a few lines of code and a few minutes (for general cases).

- For a corpus of XML files
```python
# First import and then initialize the class method
>>> from xmlRemaker import xmlCorpusRemaker

# Only the corpus_dir, head_node, body_node are needed. root_name can also be important.
>>> remaker = xmlCorpusRemaker(corpus_dir,  #the corpus directory 
			 	head_node, # the header node name for the XML files
				body_node, # the body node name
				root_name='TEI.2', # the first node name visble, not the real "Document" node.			
				dst_dir=None, # directory to save. If not given, auto-create a dir within the same folder of corpus_dir
				include_sub_dir=False, # if True, includes XML files from sub-directories
				shuffle=False) # whether to shuffle the filenames

# As simple as the following
>>> remaker.tokenize_the_corpus()   # - Tokenize the corpus 
>>> remaker.pos_tag_the_corpus()    # - Pos tag the corpus
>>> remaker.lemmatize_the_corpus()  # Lemmatize the corpus
>>> remaker.corpus_with_pos_lemma() # Both pos tag and lemmatize the corpus
```

- For a single XML file
```python
# First import everything
>>> from xmlRemaker import *
# Simlarlily, required args: need file_dir, filename, head_node, body_node. May be relevant: root_name.
# As simple as the following
>>> tokenize_xml_body(file_dir, filename, head_node, body_node)     # - Tokenize the file 
>>> pos_tag_xml_body(file_dir, filename, head_node, body_node)      # - Pos tag the file
>>> lemmatize_xml_body(file_dir, filename, head_node, body_node)    # Lemmatize the file
>>> xml_body_with_pos_lemma(file_dir, filename, head_node, body_node) # Both pos tag and lemmatize the file
```

The effects may look like this:

- For modern English texts with the builtin rules turned off (BASE)

Before remaking            |  After remaking (the original header is preserved)
:-------------------------:|:-------------------------:
![](https://github.com/jaaack-wang/HELPtk/blob/main/images/BASE_ori.png)  |  ![](https://github.com/jaaack-wang/HELPtk/blob/main/images/BASE_new.png)

- For early modern English texts with the builtin rules applied (EMMA)

Before remaking            |  After remaking (the normalized words are provided) 
:-------------------------:|:-------------------------:
![](https://github.com/jaaack-wang/HELPtk/blob/main/images/EMMA_ori.png)  |  ![](https://github.com/jaaack-wang/HELPtk/blob/main/images/EMMA_new.png)


Of course, xmlRemaker comes with much more and much more nuanced functionalities than what have been shown above. Please read the source code or simply `print(xmlRemaker.xmlCorpusRemaker.__doc__)` to learn more. 

## Tokenizing, pos tagging and lemmatizing texts

Due to the use of server, the python wrappers to Stanford CoreNLP seem to all have a strict 100,000 character text length limit for all kinds of tasks Stanford CoreNLP can perform. If you use Java, there is no such restrictions. It also turns out that if your text string contain certain symbols, such as the percent sign "%", you will get `"Could not handle incoming annotation"` back, which again does not occur in the Java's implementation. 

While the "%" issue can be worked around by swapping it with other given symbols, such as "was_percent" (LOL), the text length restrictions need some more reliable solutions. The [corenlpToolbox](https://github.com/jaaack-wang/HELPtk/blob/main/corenlpToolbox.py) script included in the current release of HELPtk provides a general method of automatic text slicing that allow oversized text to be inputted a cluster of tokens by another cluster of tokens, which can be as simple as whitespace-based tokenization. Sentence-based segmentation may not be reliable: (1) not every text has punctuations; (2) can be fairly slow for a long text. 

Empirically, the average word length of English texts should be below 10, which means we may slice the oversized text into 10,000 tokens, then string them together, and input them to Stanford CoreNLP. The `corenlpToolbox` take a more conversative 5000 tokens slicing step when an oversized text is given, and then narrow down the slicing step if that does not work out. 

Made up test example:

```python
# import the package (cd to the same folder)
>>> from corenlpToolbox import stanfordTokenizer as stTokenizer
# all set up, no need to input anything
>>> st = stTokenizer()
# so this token is 176 character long. If there are 1000 reptitions 
# of it, we need a slicing step < 100,000/176 = 568 to get things working 
>>> text = " " + "a" * 175
>>> res = st.tokenize(text * 1000)
Output: # narrowing down the slicing by 1/4 a time if the previous step does not work out
TokenizingError:  Expecting value: line 1 column 1 (char 0)
Trying to re-do the process by narrowing the slicing steps by 500. Was: 5000. Now: 3750
TokenizingError:  Expecting value: line 1 column 1 (char 0)
Trying to re-do the process by narrowing the slicing steps by 500. Was: 3750. Now: 2812
TokenizingError:  Expecting value: line 1 column 1 (char 0)
Trying to re-do the process by narrowing the slicing steps by 500. Was: 2812. Now: 2109
TokenizingError:  Expecting value: line 1 column 1 (char 0)
Trying to re-do the process by narrowing the slicing steps by 500. Was: 2109. Now: 1581
TokenizingError:  Expecting value: line 1 column 1 (char 0)
Trying to re-do the process by narrowing the slicing steps by 500. Was: 1581. Now: 1185
TokenizingError:  Expecting value: line 1 column 1 (char 0)
Trying to re-do the process by narrowing the slicing steps by 500. Was: 1185. Now: 888
TokenizingError:  Expecting value: line 1 column 1 (char 0)
Trying to re-do the process by narrowing the slicing steps by 500. Was: 888. Now: 666
TokenizingError:  Expecting value: line 1 column 1 (char 0)
Trying to re-do the process by narrowing the slicing steps by 500. Was: 666. Now: 499
```

In general, this method can be applied for all the utilities included in the server version of the Stanford CoreNLP. The current has provided the code for the above method as parent class. The two children classes, stanfordTokenizer and stanfordAnnotator provide English tokenization, pos tagging and lemmatization for the current need of HELPtk, but it can be extended very easily. 

## Debugging

- Transformation rules

```python
>>> from debugger import *
>>> trans_rules_debugger() # check whether the transformation rules work or has errors
Congratulations! The transformation rules pass the debugging test. # if things works out

##############

# made up examples again (the test examples are all wrong, the transformation rules are right)
- Preprocessing error. Expected: [so it should not], but [There are made up examples] was given for [There are made up examples].
- Normalizing error. Expected: [work out], but [There are made up examples] was given for [There are made up examples].
- Preprocessing error. Expected: [are intentionally], but [The following] was given for [The following].
- Normalizing error. Expected: [modified rules], but [The following] was given for [The following].
- Normalizing error. Expected: [hanged], but [hung] was given for [hang'd].
- Normalizing error. Expected: [satisfys], but [satisfies] was given for [satisfyeth].
- Normalizing error. Expected: [atisfyed], but [satisfied] was given for [satisfy'd].

7 erros identified during the transformation rules debugging test!
>>>
```
`words_alignment_debugger` and `words_misalignments_logger` functions are automatically triggered when remaking XML file(s). Using `print_attr_diff_in_xml_word_nodes` we can compare the differences between different attributes of all the word nodes, useful for checking 
the differences caused by spelling normalization, differences between lemma and the original etc. [misalignments_logger_example.xml.txt](https://github.com/jaaack-wang/HELPtk/blob/main/misalignments_logger_example.xml.txt) shows a semi-real example of the `words_misalignments_logger` logging the word mislignments. 


# Dependencies

- [stanfordcorenlp](https://github.com/Lynten/stanford-corenlp), a python wrapper for Stanford CoreNLP.
- [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) and necessary Java installed.
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

The rest packages should be ones that come with Python.

# Some problems

- HELPtk cannot deal with a large XML file very efficiently due to the restrictions of Stanford CoreNLP via server, especially when annotating the file with pos tag and lemma. Although multithreading speeds up the implememntation, when the problem gets stuck with a process, it will not move forward. A possible way to get around this is to first remake XML files less than certain size. Emprically, files with 500KB are ideal and 1 MB below are acceptable in terms of speed. This should work for the majority of use cases.  

- Building preprocessing and normalization rules is expensive. For me, I used frequency counts and [simple spelling checker algorithm](http://norvig.com/spell-correct.html) (unigram + naive bayes) to get a general view of the linguistic property of early modern English and their differences to the modern one. Nevertheless, this is not sufficient either as the real use of language is much more complex and nuanced than that. Neverthless, the possible post hoc error analysis currently provided by HELPtk can be helpful in discovering new conversion patterns.

- The current release does not include wrapped up navigating functions for exploring the remade XML files, although in principle the functions included in [xmlHandler](https://github.com/jaaack-wang/HELPtk/blob/main/xmlHandler.py) or the more powerful [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) should do the job. This is a concern because pos-tagged and lemmatized XML file can be very large (e.g., 128MB), whereas a normal browser like Safari and Chrome can be very slow opening a XML file over 10MB. Hence the need. 

# Future work

- A Java version of HELPtk. At this point, a small Java prototype has been built that can basically do the core work the `xmlRemaker` does.
- Some more convenient statistical learning based methods to allow a fast exploration and discovery of abnormal textual properties. 
- A general way to utilize the data generated from the remade XML files for training machine learning models. For example, the comparisons between normalized words and the non-normalized ones can yield very rich data samples, both positive and negative, to train a spelling normalization model.
