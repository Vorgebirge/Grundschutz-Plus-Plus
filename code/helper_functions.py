# Stand 03.05.2026
# Reguläre Ausdrücke https://regex101.com/)
import difflib, hashlib, json, pickle, re, string
from collections import defaultdict, OrderedDict
from configparser import ConfigParser
from datetime import datetime
#from Pympler import asizeof  #ModuleNotFoundError: No module named 'Pympler'

#config = ConfigParser()
#config.read('config.ini')
#STOPWORDS = config['daten']['STOPWORDS_1']
#STOPWORDS = [w for w in re.split(r'\s*,\s*', STOPWORDS) if w]

STOPWORDS = ['aber', 'alle', 'allem', 'allen', 'aller', 'alles', 'als', 'also', 'am', 'an', 'ander', 'andere', 'anderem', 'anderen', 'anderer', 'anderes', 'anderm', 'andern', 'anderr', 'anders', 'auch', 'auf', 'aus', 'bei', 'bin', 'bis', 'bist', 'da', 'damit', 'dann', 'der', 'den', 'des', 'dem', 'die', 'das', 'dass', 'daß', 'derselbe', 'derselben', 'denselben', 'desselben', 'demselben', 'dieselbe', 'dieselben', 'dasselbe', 'dazu', 'dein', 'deine', 'deinem', 'deinen', 'deiner', 'deines', 'denn', 'derer', 'dessen', 'dich', 'dir', 'du', 'dies', 'diese', 'diesem', 'diesen', 'dieser', 'dieses', 'doch', 'dort', 'durch', 'ein', 'eine', 'einem', 'einen', 'einer', 'eines', 'einig', 'einige', 'einigem', 'einigen', 'einiger', 'einiges', 'einmal', 'er', 'ihn', 'ihm', 'es', 'etwas', 'euer', 'eure', 'eurem', 'euren', 'eurer', 'eures', 'für', 'gegen', 'gewesen', 'hab', 'habe', 'haben', 'hat', 'hatte', 'hatten', 'hier', 'hin', 'hinter', 'ich', 'mich', 'mir', 'ihr', 'ihre', 'ihrem', 'ihren', 'ihrer', 'ihres', 'euch', 'im', 'in', 'indem', 'ins', 'ist', 'jede', 'jedem', 'jeden', 'jeder', 'jedes', 'jene', 'jenem', 'jenen', 'jener', 'jenes', 'jetzt', 'kann', 'kein', 'keine', 'keinem', 'keinen', 'keiner', 'keines', 'können', 'könnte', 'machen', 'man', 'manche', 'manchem', 'manchen', 'mancher', 'manches', 'mein', 'meine', 'meinem', 'meinen', 'meiner', 'meines', 'mit', 'muss', 'musste', 'nach', 'nicht', 'nichts', 'noch', 'nun', 'nur', 'ob', 'oder', 'ohne', 'sehr', 'sein', 'seine', 'seinem', 'seinen', 'seiner', 'seines', 'selbst', 'sich', 'sie', 'ihnen', 'sind', 'so', 'solche', 'solchem', 'solchen', 'solcher', 'solches', 'soll', 'sollte', 'sondern', 'sonst', 'über', 'um', 'und', 'uns', 'unsere', 'unserem', 'unseren', 'unser', 'unseres', 'unter', 'viel', 'vom', 'von', 'vor', 'während', 'war', 'waren', 'warst', 'was', 'weg', 'weil', 'weiter', 'welche', 'welchem', 'welchen', 'welcher', 'welches', 'wenn', 'werde', 'werden', 'wie', 'wieder', 'will', 'wir', 'wird', 'wirst', 'wo', 'wollen', 'wollte', 'würde', 'würden', 'zu', 'zum', 'zur', 'zwar', 'zwischen']


TEST_DATA = {
    "name": "Projekt A",
    "tasks": [
        {"title": "Analyse", "done": False},
        {"title": "Implementierung", "done": True, "subtasks": ["Modul 1", "Modul 2"]},
    ],
    "metadata": {
        "created": "2024-01-01",
        "tags": ["python", "visualisierung"]
    }
}



def hash_object(obj):
    data = pickle.dumps(obj)
    return hashlib.sha256(data).hexdigest()

"""
# sorted_nicely(mylist) mit lambda Ausdrücken
def sorted_nicely(mylist):
    Sort the given iterable in the way that humans expect.
    # https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
    # Elemente der Liste l müssen vom Typ str sein
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(mylist, key=alphanum_key)
"""


def kosinus_aehnlichkeit(X: str, Y: str) -> float:
    """Berechne Kosinus-Ähnlichkeit der Strings X und Y

    Ignoriert werden: Wortreihenfolge, Satzzeichen, Groß-/Kleinscheibung

    Wertebereich Kosinus-Ähnlichkeit:
        [0,1]

    Aussagekraft:
        kosinus_aehnlichkeit(X,Y) ignoriert die Reihenfolge der Token/Wörter in X und Y.
        kosinus_aehnlichkeit(X,Y) ignoriert Satzzeichen (RE_SATZZEICHEN)

        kosinus_aehnlichkeit(X,Y) == 1 -> X und Y sind bis auf Reihenfolge der Wörter
        und mögliche Satzzeichen gleich.

        kosinus_aehnlichkeit(X,Y) == 1 ist also nur eine notwendige Bedingung für die
        Gleichheit von X und Y.

        Dass es keine hinreichende Bedingung ist (und dass Satzzeichen
        sehr wohl von Bedeutung sein können), zeigt folgendes Beispiel:
        X = 'Computer arbeitet, nicht ausschalten!' (Verbot)
        Y = 'Computer arbeitet nicht, ausschalten!' (Aufforderung)
        
    Informationen:
        https://www.geeksforgeeks.org/python-measure-similarity-between-two-
        sentences-using-cosine-similarity/
        https://de.wikipedia.org/wiki/Kosinus-%C3%84hnlichkeit   
        https://www.n-joy.de/leben/Warum-Kommas-so-wichtig-sind,deutschesprache150.html
    """
    l1, l2 = [], []
    X_list = [normalisiere(w) for w in wort_segmente(X)]
    Y_list = [normalisiere(w) for w in wort_segmente(Y)]
    
    # remove stop words from the string
    X_set = {w for w in X_list if w not in STOPWORDS}
    Y_set = {w for w in Y_list if w not in STOPWORDS}

    # form a set containing keywords of both strings
    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    # cosine formula
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    return cosine

def inline_diff(str_1, str_2):
    '''
    Copilot Prompt (GPT-5, 07.03.26):
    Create a Python script that compares two text files word-by-word and produces an inline diff.
    Requirements:
    - Ignore case and ignore punctuation for comparison.
    - Preserve the original punctuation exactly as it appears in each file.
    - Do not introduce any extra whitespace before or after punctuation.
    - Mark removed words inline in file1 using this format: [-word-]
    - Mark added words inline in file2 using this format: {+word+}
    - Keep punctuation attached to its word (e.g., "dog." stays "dog.").
    - The output should reconstruct each file's text with the inline markers inserted, without altering spacing or punctuation beyond the markers themselves.
    - Provide the full Python script.
    - Do not use " ".join() to rebuild the text. Reconstruct the output using logic that preserves original spacing rules and does not add spaces before punctuation.
    '''

    def tokenize(text):
        """
        Tokenize text into words while keeping punctuation attached.
        Example: 'dog.' stays 'dog.'
        """
        return re.findall(r"\w+(?:'\w+)?|[^\w\s]", text, re.UNICODE)

    def normalize(word):
        """
        Normalize for comparison:
        - lowercase
        - strip punctuation
        """
        return re.sub(f"[{re.escape(string.punctuation)}]", "", word.lower())

    def rebuild(tokens):
        """
        Rebuild text from tokens without adding extra spaces before punctuation.
        Rules:
        - If token starts with punctuation, attach directly to previous token.
        - Otherwise, add a space before it (unless it's the first token).
        """
        out = ""
        for t in tokens:
            if not out:
                out = t
            elif re.match(r"[^\w\s]", t):  # punctuation token
                out += t
            else:
                out += " " + t
        return out
    
    def refine(text):
        text = text.replace('+}{+', ' ')        
        text = text.replace('-][-', ' ')
        text = text.replace('{+', ' **[+ ')
        text = text.replace('+}', ' +]**')        
        text = text.replace('[-', ' **[- ')
        text = text.replace('-]', ' -]**')        
        text = text.replace('( ', ' (')
        text = text.replace(' )', ')')
        text = replace_odd('" ', ' "', text)
        return text
        
    
    # Tokenize while keeping punctuation attached
    tokens1 = tokenize(str_1)
    tokens2 = tokenize(str_2)

    # Normalized versions for matching
    norm1 = [normalize(t) for t in tokens1]
    norm2 = [normalize(t) for t in tokens2]

    matcher = difflib.SequenceMatcher(None, norm1, norm2)

    out1 = []
    out2 = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            out1.extend(tokens1[i1:i2])
            out2.extend(tokens2[j1:j2])

        elif tag == "delete":
            for w in tokens1[i1:i2]:
                out1.append(f"[-{w}-]")

        elif tag == "insert":
            for w in tokens2[j1:j2]:
                #out2.append(f"[+{w}+]")
                out2.append(f"{{+{w}+}}")

        elif tag == "replace":
            for w in tokens1[i1:i2]:
                out1.append(f"[-{w}-]")
            for w in tokens2[j1:j2]:
                out2.append(f"{{+{w}+}}")

    # Rebuild without adding spaces around punctuation
    text1_marked = rebuild(out1)
    text2_marked = rebuild(out2)
    
    # Refine output
    text1_marked = refine(text1_marked)
    text2_marked = refine(text2_marked)

    return text1_marked, text2_marked

def is_valid_json_string(s):
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
        return False

def list_get(lst, index, default=None):
    '''list equivalent to dict.get(). Lists are index-based, and Python treats out-of-range 
    indexes as errors rather than missing keys. So there’s no built in .get(). But you can 
    emulate it elegantly.
    Code snippet generated with assistance from Microsoft Copilot.
    '''
    try:
        return lst[index]
    except IndexError:
        return default

'''
def mydiff(string_a:str) -> list:    
    wort_list_a = [{'unveraendert': wort, 'normalisiert': normalisiere(wort), 'diff': ''} \
                    for wort in wort_segmente(string_a)]
    
    return wort_list_a
'''


def normalisiere(word: str) -> str:
    """
    Normalize for comparison:
    - lowercase
    - strip punctuation
    """
    return re.sub(f"[{re.escape(string.punctuation)}]", "", word.lower()).strip()


def read_json_file(pfad):
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print("Invalid JSON:", e)
    except OSError as e:
        print("File error:", e)

def replace_odd(pattern, repl, text):
    '''
    Promt: Replace only every odd match of a regex
    '''
    counter = {"i": 0}
    def _repl(match):
        counter["i"] += 1
        if counter["i"] % 2 == 1:   # odd match
            return repl
        return match.group(0)       # leave unchanged

    return re.sub(pattern, _repl, text)

def sort_dict_naturally(mydict: dict) -> dict:
    """ Sortiere mydict Schlüssel-Wert-Paare
    Schlüssel müssen vom Datentyp String sein
    """
    mydict_ordered = OrderedDict()
    ordered_keys = sort_list_naturally(list(mydict.keys()))
    for key in ordered_keys:
        mydict_ordered[key] = mydict[key]
    return mydict_ordered

def sort_list_naturally(mylist: list) -> list:
    """ Sort the given iterable in the way that humans expect.
    https://blog.codinghorror.com/sorting-for-humans-natural-sort-order/
    """
    def convert(text: str):
        return int(text) if text.isdigit() else text
    def alphanum_key(key):
        return [convert(c) for c in re.split('([0-9]+)', key)]
    if mylist:
        return sorted(mylist, key = alphanum_key)
    else:
        return []


def strings_broadly_similar(str_a, str_b, re_pattern = ''):
    # Online Tool zum Testen regulärer Ausdrücke https://regex101.com/
    # Beispiel re_pattern = r'[:;,\.\s]+' -> str_a und str_b gleichen sich bis auf Semikolon, Doppelpunkt, Punkte, Kommas und Leerzeichen
    str_a, str_b = str_a.lower(), str_b.lower()
    if re_pattern:
        str_a = re.sub(re_pattern, '', str_a) 
        str_b = re.sub(re_pattern, '', str_b)        
        return (str_a == str_b)
    else:
        return (str_a == str_b)

def string_in_list_of_strings(str_a, list_str):
    for str_b in list_str:
        if strings_broadly_similar(str_a, str_b, r'[:;,\.\s]+'):
            return True
    return False        

def teilstrings(mystr):
    def entferne_eol(mystr: str) -> str:
        # Entferne und ersetze alle Zeilenenden in mystr

        # Entferne Zeilenenden, die nicht durch ein Leerzeichen ersetzt werden sollen
        while m := re.search(r'\S\-\n\S', mystr):
            mystr1 = m.group(0).replace('\n', '')
            mystr = mystr.replace(m.group(0), mystr1)

        # Ersetze jedes noch verbliebene Zeilende durch ein Leerzeichen
        mystr = mystr.replace('\n', ' ')
        mystr = ' '.join(mystr.split())
        return mystr


    # Online Tool zum Testen regulärer Ausdrücke https://regex101.com/
    
    ABKUERZUNG =  r'\b(bspw\.|bzgl\.|bzw\.|d\.\s*h\.|engl\.|ggf\.|etc\.|inkl\.|[nN]r\.|usw\.|vgl\.|z\.\s*B\.)\B'
                
    SEGMENT_ANFANG = r'\b[1-9]\d*\.\B|\s*•'
    SEGMENT_ENDE = r'[\.\?!](?=\s)'
    SEPARATOR = '(' +  SEGMENT_ANFANG + ')|(' + SEGMENT_ENDE + ')'
            
    RE_KEIN_SEPARATOR = re.compile('{}'.format(ABKUERZUNG))
    RE_SEPARATOR = re.compile('{}'.format(SEPARATOR))          
    
    maske = mystr
            
    for match in RE_KEIN_SEPARATOR.finditer(mystr): 
        maske = maske.replace(match.group(0), len(match.group(0))*'#')        
    
    mylist, start, ende = list(), 0, 0 
    for match in RE_SEPARATOR.finditer(maske):                        
        if match.group(1):                                
            ende = match.span(1)[0]                                        
        elif match.group(2):                   
            ende = match.span(2)[1]
        if start < ende:
            mylist.append(entferne_eol(mystr[start:ende]).strip())                        
        start = ende
    if ende < len(mystr):            
        mylist.append(entferne_eol(mystr[ende:len(mystr)]).strip()) 
    return mylist



def visualize(data, indent=0, selectors=[]):     
    """Gibt eine verschachtelte Datenstruktur als Baum aus."""
    prefix = " " * indent

    if isinstance(data, dict):
        print(f"{prefix}{type(data).__name__}:")
        for key, value in data.items():
            print(f"{prefix}  {key}:")            
            visualize(value, indent + 4, selectors)            

    elif isinstance(data, (list, tuple)):
        print(f"{prefix}{type(data).__name__}:")
        for index, item in enumerate(data):
            print(f"{prefix}  [{index}]:")            
            visualize(item, indent + 4, selectors)
                        
    else:        
        print(f"{prefix}{repr(data)}")  
     

def wort_segmente(string: str) ->  list:     
    ''' Gibt zu einem String eine Liste mit den Wörtern des Strings zurück.
        Leerezeichen im String markieren Wortenden. Ausnahmen sind Leerzeichen zwischen 
        zwei- und dreistelligen Abkürzungen.
        Keine Bereigung von Interpunktionszeichen oder Leerzeichen, d.h. zusammengefügt
        ergeben die Elemente der Liste wieder den ursprünglichen String.
        Online Tool zu regulären Ausdrücken: https://regex101.com/
        '''
    
    WORTENDE = r'\s+'
    # z.B. mögliche Leerzeichen (\s+) zwischen z. und B. in z. B.
    RE_AUSNAHME_1 = r'(\s[a-zA-Z]{1,4}\.)(\s+)([a-zA-Z]{1,4}\.)'  
    # z.B. mögliche Leerzeichen (\s+) zwischen d. und R. in i. d. R.
    RE_AUSNAHME_2 = r'(\s[a-zA-Z]{1,4}\.\s+[a-zA-Z]{1,4}\.)(\s+)([a-zA-Z]{1,4}\.)'  
    
    ausnahmen = [(match.start(2),match.end(2)) for match in re.finditer(RE_AUSNAHME_1, string)]
    ausnahmen += [(match.start(2),match.end(2)) for match in re.finditer(RE_AUSNAHME_2, string)]
    
    wortliste, pointer_anfang, pointer_ende = [], 0, 0
    for match in re.finditer(WORTENDE, string):        
        if match.span() not in ausnahmen:
            pointer_ende = match.span()[1]
            wortliste.append(string[pointer_anfang:pointer_ende])
            pointer_anfang = pointer_ende            
    if pointer_ende < len(string):
        wortliste.append(string[pointer_anfang:len(string)])
    
    return wortliste  

def write_json_file(data, pfad):    
    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def ymd2dmy(yymmdd):
    dd_mm_yy = datetime.strptime(yymmdd, '%y%m%d')
    return dd_mm_yy.strftime('%d.%m.%y')
  
# def main():           
    
    
if __name__ == "__main__":
    main()