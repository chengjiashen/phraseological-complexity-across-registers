import spacy
import glob
import math


spacy.require_gpu()
nlp = spacy.load("en_core_web_trf")

filepaths = glob.glob("")

amod_MI = {}
advmod_MI = {}
dobj_MI = {}

total_lemma = 9538719919

COCA_lemma_dict = {}
COCA_amod_dict = {}
COCA_advmod_dict = {}
COCA_dobj_dict = {}

def reference_lemma_dict(dict, filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            line_list = line.strip().split(" ")
            dict[line_list[0]] = int(line_list[1])

def reference_dep_dict(dict, filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            line_list = line.strip().split(" ")
            collo = f"{line_list[0]} {line_list[1]}"
            dict[collo] = int(line_list[2])

reference_lemma_dict(COCA_lemma_dict, "/Users/shenjiacheng/Documents/corpora/ENCOW16AX/reference/lemma.txt")
reference_dep_dict(COCA_amod_dict, "/Users/shenjiacheng/Documents/corpora/ENCOW16AX/reference/amod.txt")
reference_dep_dict(COCA_advmod_dict, "/Users/shenjiacheng/Documents/corpora/ENCOW16AX/reference/advmod.txt")
reference_dep_dict(COCA_dobj_dict, "/Users/shenjiacheng/Documents/corpora/ENCOW16AX/reference/dobj.txt")

for filepath in filepaths:
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
        doc = nlp(content)
        for token in doc:
            if token.pos_ == "ADJ" and token.dep_ == "amod" and token.head.pos_ == "NOUN" and token.is_alpha and token.head.is_alpha:
                collocation = f"{token.lemma_} {token.head.lemma_}"
                if collocation not in amod_MI.keys():
                    if collocation in COCA_amod_dict.keys():
                        if COCA_amod_dict[collocation] >= 5:
                            collo_1 = token.lemma_
                            collo_2 = token.head.lemma_
                            if collo_1 in COCA_lemma_dict.keys() and collo_2 in COCA_lemma_dict.keys():
                                freq_collocation = COCA_amod_dict[collocation]
                                freq_collo_1 = COCA_lemma_dict[collo_1]
                                freq_collo_2 = COCA_lemma_dict[collo_2]
                                PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                                amod_MI[collocation] = PMI
            if token.pos_ == "ADV" and token.dep_ == "advmod" and token.head.pos_ == "VERB" and token.is_alpha and token.head.is_alpha:
                collocation = f"{token.lemma_} {token.head.lemma_}"
                if collocation not in advmod_MI.keys():
                    if collocation in COCA_advmod_dict.keys():
                        if COCA_advmod_dict[collocation] >= 5:
                            collo_1 = token.lemma_
                            collo_2 = token.head.lemma_
                            if collo_1 in COCA_lemma_dict.keys() and collo_2 in COCA_lemma_dict.keys():
                                freq_collocation = COCA_advmod_dict[collocation]
                                freq_collo_1 = COCA_lemma_dict[collo_1]
                                freq_collo_2 = COCA_lemma_dict[collo_2]
                                PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                                advmod_MI[collocation] = PMI
            if token.pos_ == "ADV" and token.dep_ == "advmod" and token.head.pos_ == "ADJ" and token.is_alpha and token.head.is_alpha:
                collocation = f"{token.lemma_} {token.head.lemma_}"
                if collocation not in advmod_MI.keys():
                    if collocation in COCA_advmod_dict.keys():
                        if COCA_advmod_dict[collocation] >= 5:
                            collo_1 = token.lemma_
                            collo_2 = token.head.lemma_
                            if collo_1 in COCA_lemma_dict.keys() and collo_2 in COCA_lemma_dict.keys():
                                freq_collocation = COCA_advmod_dict[collocation]
                                freq_collo_1 = COCA_lemma_dict[collo_1]
                                freq_collo_2 = COCA_lemma_dict[collo_2]
                                PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                                advmod_MI[collocation] = PMI
            if token.pos_ == "ADV" and token.dep_ == "advmod" and token.head.pos_ == "ADV" and token.is_alpha and token.head.is_alpha:
                collocation = f"{token.lemma_} {token.head.lemma_}"
                if collocation not in advmod_MI.keys():
                    if collocation in COCA_advmod_dict.keys():
                        if COCA_advmod_dict[collocation] >= 5:
                            collo_1 = token.lemma_
                            collo_2 = token.head.lemma_
                            if collo_1 in COCA_lemma_dict.keys() and collo_2 in COCA_lemma_dict.keys():
                                freq_collocation = COCA_advmod_dict[collocation]
                                freq_collo_1 = COCA_lemma_dict[collo_1]
                                freq_collo_2 = COCA_lemma_dict[collo_2]
                                PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                                advmod_MI[collocation] = PMI
            if token.pos_ == "NOUN" and token.dep_ == "dobj" and token.head.pos_ == "VERB" and token.is_alpha and token.head.is_alpha:
                collocation = f"{token.head.lemma_} {token.lemma_}"
                if collocation not in dobj_MI.keys():
                    if collocation in COCA_dobj_dict.keys():
                        if COCA_dobj_dict[collocation] >= 5:
                            collo_1 = token.lemma_
                            collo_2 = token.head.lemma_
                            if collo_1 in COCA_lemma_dict.keys() and collo_2 in COCA_lemma_dict.keys():
                                freq_collocation = COCA_dobj_dict[collocation]
                                freq_collo_1 = COCA_lemma_dict[collo_1]
                                freq_collo_2 = COCA_lemma_dict[collo_2]
                                PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))