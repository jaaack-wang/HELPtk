'''
- Author: Zhengxiang (Jack) Wang 
- Date: 2021-08-26
- GitHub: https://github.com/jaaack-wang 
- About: A Stanford CoreNLP Toolbox with three wrapped up class methods
that enable Python to tokenize and annotate without text length restrictions. 
'''
# if you do not have stanfordcorenlp installed, import the one that comes with HELPtk.
# please note that the original stanfordcorenlp can be problematic 
try:
    from stanfordcorenlp import StanfordCoreNLP
except:
    from corenlp import StanfordCoreNLP
import json


# Please change the path to StanfordCoreNLP here when you first run the scripts.
# StanfordCoreNLP can be downloaded from: https://stanfordnlp.github.io/CoreNLP/index.html
path_to_corenlp = "/Users/wzx/stanford-corenlp-4.2.2"


class CoreNLP:
    ''''A parent class that re-adopts the stanfordcorenlp to make Python a more effective 
    text processing and annotating tool that in principle has no text length restrictions 
    (which is 100,000 chars because of the use of server). More concretely, this class
    allow oversized text to be processed by Stanford CoreNLP sever by automatic text slicing'''
    
    def __init__(self, path_to_corenlp, props, whitespace_based=False, split_hyphen=False, step=5000):
        
        self._nlp = StanfordCoreNLP(path_to_corenlp)
        self.props = props
        if whitespace_based: 
            self.props['tokenize.whitespace'] = 'true'
        else:
            self.props['tokenize.whitespace'] = 'false'
        if split_hyphen:
            self.props['tokenize.options'] = "splitHyphenated=true"
        else:
            self.props['tokenize.options'] = "splitHyphenated=false"
        self._step = step
        self._text = ''
    
    def _annotating(self, text):
        '''Annotating given text based on preset properties (annotating setups).'''
        try:
            annotated_text = self._nlp.annotate(text, properties=self.props)
            return json.loads(annotated_text)
        except Exception as e:
            print("\033[32mTokenizingError: \033[0m", e)
            if "Expecting value: line 1 column 1 (char 0)" in str(e):
                print("Trying to re-do the process by narrowing the slicing steps by 500. Was: %i. Now: %i" 
                 % (self._step, self._step - 500))
                self._step -= 500
                return
            
    def _text_annotating(self, text):
        '''Annotating given text in a way that allows annotating oversized text in Python. 
        When the text is oversized (>100000 chars), perform text slicing by adjustable number of tokens.'''
        
        self._text = text
        annotated_text = []
        if len(text) <= 100000:
            annotated_text.append(self._annotating(text))
        else:
            tokens = text.split()
            for i in range(0, len(tokens), self._step):
                sub_text = ' '.join(tokens[i: i + self._step])
                rturn = self._annotating(sub_text)
                if rturn:
                    annotated_text.append(rturn)
                else:
                    return 
                
        return annotated_text
    
    def get_annotated_text(self, text):
        '''Auto-adjust the slicing steps when needed to get the final annotated text.'''
        annotated_text = []
        while not annotated_text:
            annotated_text = self._text_annotating(text)
            if self._step == 0:
                self._step = 5000
                raise TypeError("Text impossible to parse and annotate. Please check the text type or if it has spaces.")
        
        self._step = 5000
        return annotated_text
        

class stanfordTokenizer(CoreNLP):
    '''A wrapped-up Standard Stanford Tokenizer but with splitHyphenated turned off. 
    Also allows to set "whitespace_based=True" so that the tokenizer can tokenize by whitespace, 
    or set "split_hyphen=True" so that the tokenizer does not always skip hyphens. This class 
    inherits the CoreNLP class method so it can tokenize a text without text length restrictions.'''
        
    def __init__(self, path_to_corenlp=path_to_corenlp, 
                 whitespace_based=False, split_hyphen=False, step=5000):
        props = {'annotators': 'tokenize', 'outputFormat': 'json'} 
        super().__init__(path_to_corenlp, props, whitespace_based, split_hyphen, step)
        
    def tokenize(self, text, list_out=True):
        annotated_text = self.get_annotated_text(text)
        out = []
        try:
            for t in annotated_text:
                for token in t['tokens']:
                    out.append(token['originalText'])
                    
            if list_out: return out
            else: return ' '.join(out)
        except Exception as e:
            print("\033[32mTokenizingError: \033[0m", e)


class stanfordAnnotator(CoreNLP):
    '''A wrapped-up Standard Stanford Pos Tag and Lemma Annotator but with tokenize.whitespace=True. 
    Also allows to set "whitespace_based=False", or set "split_hyphen=True". This class inherits the
    CoreNLP class method so it can annotate a text without text length restrictions. Currently, this
    stanfordAnnotator only allows pos tagging and/or lemmatization, but it can be extended easily.
    Please note that, pos tagging or lemmatizing a long text can be extremely time-consuming in Python
    enviroment (such as text over 4,000,000 tokens), so it is not recommended to use Python to conduct 
    such tasks. Java is a more native, stable and realiable option as Standfore CoreNLP is written in Java.'''
    
    def __init__(self, path_to_corenlp=path_to_corenlp, 
                 whitespace_based=True, split_hyphen=False, step=5000):
        props = {'annotators': 'tokenize,ssplit,pos,lemma', 'outputFormat': 'json'}
        super().__init__(path_to_corenlp, props, whitespace_based, split_hyphen, step)
    
    def _get_attr_values(self, text, attr, include_tokens):  
        annotated_text = self.get_annotated_text(text)
        out = []
        try:
            for t in annotated_text:
                for s in t['sentences']:
                    for token in s['tokens']:
                        out.append(token[attr])
            if not include_tokens: return out
            else: return text.split(), out
        except Exception as e:
            print(e)
   
    def get_pos_tags(self, text, include_tokens=False):
        return self._get_attr_values(text, 'pos', include_tokens)
        
    def get_lemma(self, text, include_tokens=False):
        return self._get_attr_values(text, 'lemma', include_tokens)
    
    def get_pos_and_lemma(self, text, include_tokens=False):
        annotated_text = self.get_annotated_text(text)
        pos, lemma = [], []
        try:
            for t in annotated_text:
                for s in t['sentences']:
                    for token in s['tokens']:
                        pos.append(token['pos'])
                        lemma.append(token['lemma'])
                        
            if not include_tokens: return pos, lemma 
            else: return text.split(), pos, lemma 
        except Exception as e:
            print(e)
