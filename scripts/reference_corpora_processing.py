import spacy
import glob



spacy.require_gpu()
nlp = spacy.load("en_core_web_trf")

filepaths = glob.glob("E:/Corpora/COCA/COCA_Aca/ori/*.txt")

write_filepaths = ["E:/Corpora/COCA/COCA_Aca/COCA_lemma_dict.txt", "E:/Corpora/COCA/COCA_Aca/COCA_amod_dict.txt",
                   "E:/Corpora/COCA/COCA_Aca/COCA_advmod_dict.txt", "E:/Corpora/COCA/COCA_Aca/COCA_dobj_dict.txt"]

COCA_lemma = {}
COCA_amod = {}
COCA_advmod = {}
COCA_dobj = {}
COCAs = [COCA_lemma, COCA_amod, COCA_advmod, COCA_dobj]

def store(token, dict):
    if token not in dict.keys():
        dict[token] = 1
    else:
        dict[token] += 1

def write_dict(dict, filepath):
    with open(filepath, "w", encoding="utf-8") as file:
        for key in dict.keys():
            file.write(f"{key} {dict[key]}\n")


for filepath in filepaths:
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                doc = nlp(line.strip())
                for token in doc:
                    if token.is_alpha:
                        store(token.lemma_.lower(), COCA_lemma)
                    if token.pos_ == "ADJ" and token.dep_ == "amod" and token.head.pos_ == "NOUN" and token.is_alpha and token.head.is_alpha:
                        collocation = f"{token.lemma_} {token.head.lemma_}"
                        store(collocation, COCA_amod)
                    if token.pos_ == "ADV" and token.dep_ == "advmod" and token.head.pos_ == "VERB" and token.is_alpha and token.head.is_alpha:
                        collocation = f"{token.lemma_} {token.head.lemma_}"
                        store(collocation, COCA_advmod)
                    if token.pos_ == "ADV" and token.dep_ == "advmod" and token.head.pos_ == "ADJ" and token.is_alpha and token.head.is_alpha:
                        collocation = f"{token.lemma_} {token.head.lemma_}"
                        store(collocation, COCA_advmod)
                    if token.pos_ == "ADV" and token.dep_ == "advmod" and token.head.pos_ == "ADV" and token.is_alpha and token.head.is_alpha:
                        collocation_3 = f"{token.lemma_} {token.head.lemma_}"
                        store(collocation, COCA_advmod)
                    if token.pos_ == "NOUN" and token.dep_ == "dobj" and token.head.pos_ == "VERB" and token.is_alpha and token.head.is_alpha:
                        collocation = f"{token.head.lemma_} {token.lemma_}"
                        store(collocation, COCA_dobj)

for i in range(4):
    write_dict(COCAs[i], write_filepaths[i])
