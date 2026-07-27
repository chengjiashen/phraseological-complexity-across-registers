import glob
import spacy
import numpy
import math



spacy.require_gpu()
nlp = spacy.load("en_core_web_trf")

MULTED_filepaths = glob.glob("E:/Corpora/MULTED/rv/*.txt")
LOCRA_filepaths = glob.glob("E:/Corpora/LOCRA/rv/*.txt")

MULTED_MIs_amod = []
MULTED_MIs_advmod = []
MULTED_MIs_dobj = []

ENCOW_lemma_dict = {}
ENCOW_amod_dict = {}
ENCOW_advmod_dict = {}
ENCOW_dobj_dict = {}

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

reference_lemma_dict(ENCOW_lemma_dict, "E:/Corpora/ENCOW16AX/reference/lemma.txt")
reference_dep_dict(ENCOW_amod_dict, "E:/Corpora/ENCOW16AX/reference/amod.txt")
reference_dep_dict(ENCOW_advmod_dict, "E:/Corpora/ENCOW16AX/reference/advmod.txt")
reference_dep_dict(ENCOW_dobj_dict, "E:/Corpora/ENCOW16AX/reference/dobj.txt")

total_lemma = 0
for entry in ENCOW_lemma_dict.keys():
    total_lemma += ENCOW_lemma_dict[entry]

for filepath in LOCRA_filepaths:
    with open(filepath, "r", encoding="utf-8") as file:
        tokens = []
        index_start = 0
        content = file.read()
        doc = nlp(content)

        MIs_amod = []
        MIs_advmod = []
        MIs_dobj = []

        for token in doc:
            if token.is_alpha:
                tokens.append(token)
        while index_start <= len(tokens) - 300:
            win_MIs_amod = []
            win_MIs_advmod = []
            win_MIs_dobj = []
            for n in range(index_start, index_start + 300):
                if tokens[n].pos_ == "ADJ" and tokens[n].dep_ == "amod" and tokens[n].head.pos_ == "NOUN" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                    collocation = f"{tokens[n].lemma_} {tokens[n].head.lemma_}"
                    if collocation in ENCOW_amod_dict.keys():
                        if ENCOW_amod_dict[collocation] >= 5:
                            collo_1 = tokens[n].lemma_
                            collo_2 = tokens[n].head.lemma_
                            if collo_1 in ENCOW_lemma_dict.keys() and collo_2 in ENCOW_lemma_dict.keys():
                                freq_collocation = ENCOW_amod_dict[collocation]
                                freq_collo_1 = ENCOW_lemma_dict[collo_1]
                                freq_collo_2 = ENCOW_lemma_dict[collo_2]
                                PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                                win_MIs_amod.append(PMI)
                if tokens[n].pos_ == "ADV" and tokens[n].dep_ == "advmod" and tokens[n].head.pos_ == "VERB" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                    collocation = f"{tokens[n].lemma_} {tokens[n].head.lemma_}"
                    if collocation in ENCOW_advmod_dict.keys():
                        if ENCOW_advmod_dict[collocation] >= 5:
                            collo_1 = tokens[n].lemma_
                            collo_2 = tokens[n].head.lemma_
                            if collo_1 in ENCOW_lemma_dict.keys() and collo_2 in ENCOW_lemma_dict.keys():
                                freq_collocation = ENCOW_advmod_dict[collocation]
                                freq_collo_1 = ENCOW_lemma_dict[collo_1]
                                freq_collo_2 = ENCOW_lemma_dict[collo_2]
                                PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                                win_MIs_advmod.append(PMI)
                # if tokens[n].pos_ == "ADV" and tokens[n].dep_ == "advmod" and tokens[n].head.pos_ == "ADJ" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                #     collocation = f"{tokens[n].lemma_} {tokens[n].head.lemma_}"
                #     if collocation in ENCOW_advmod_dict.keys():
                #         if ENCOW_advmod_dict[collocation] >= 5:
                #             collo_1 = tokens[n].lemma_
                #             collo_2 = tokens[n].head.lemma_
                #             if collo_1 in ENCOW_lemma_dict.keys() and collo_2 in ENCOW_lemma_dict.keys():
                #                 freq_collocation = ENCOW_advmod_dict[collocation]
                #                 freq_collo_1 = ENCOW_lemma_dict[collo_1]
                #                 freq_collo_2 = ENCOW_lemma_dict[collo_2]
                #                 PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                #                 win_MIs_advmod.append(PMI)
                # if tokens[n].pos_ == "ADV" and tokens[n].dep_ == "advmod" and tokens[n].head.pos_ == "ADV" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                #     collocation = f"{tokens[n].lemma_} {tokens[n].head.lemma_}"
                #     if collocation in ENCOW_advmod_dict.keys():
                #         if ENCOW_advmod_dict[collocation] >= 5:
                #             collo_1 = tokens[n].lemma_
                #             collo_2 = tokens[n].head.lemma_
                #             if collo_1 in ENCOW_lemma_dict.keys() and collo_2 in ENCOW_lemma_dict.keys():
                #                 freq_collocation = ENCOW_advmod_dict[collocation]
                #                 freq_collo_1 = ENCOW_lemma_dict[collo_1]
                #                 freq_collo_2 = ENCOW_lemma_dict[collo_2]
                #                 PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                #                 win_MIs_advmod.append(PMI)
                if tokens[n].pos_ == "NOUN" and tokens[n].dep_ == "dobj" and tokens[n].head.pos_ == "VERB" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                    collocation = f"{tokens[n].head.lemma_} {tokens[n].lemma_}"
                    if collocation in ENCOW_dobj_dict.keys():
                        if ENCOW_dobj_dict[collocation] >= 5:
                            collo_1 = tokens[n].lemma_
                            collo_2 = tokens[n].head.lemma_
                            if collo_1 in ENCOW_lemma_dict.keys() and collo_2 in ENCOW_lemma_dict.keys():
                                freq_collocation = ENCOW_dobj_dict[collocation]
                                freq_collo_1 = ENCOW_lemma_dict[collo_1]
                                freq_collo_2 = ENCOW_lemma_dict[collo_2]
                                PMI = math.log2(freq_collocation * total_lemma / (freq_collo_1 * freq_collo_2))
                                win_MIs_dobj.append(PMI)

            index_start += 10
        if win_MIs_amod:
            MULTED_MIs_amod.append(float(numpy.mean(win_MIs_amod)))
        if win_MIs_advmod:
            MULTED_MIs_advmod.append(float(numpy.mean(win_MIs_advmod)))
        if win_MIs_dobj:
            MULTED_MIs_dobj.append(float(numpy.mean(win_MIs_dobj)))

# print(MULTED_MIs_amod[:30])
print(MULTED_MIs_amod)
print(numpy.mean(MULTED_MIs_amod))
print(numpy.std(MULTED_MIs_amod), "\n")
# print(MULTED_MIs_advmod[:30])
print(MULTED_MIs_advmod)
print(numpy.mean(MULTED_MIs_advmod))
print(numpy.std(MULTED_MIs_advmod), "\n")
# print(MULTED_MIs_dobj[:30])
print(MULTED_MIs_dobj)
print(numpy.mean(MULTED_MIs_dobj))
print(numpy.std(MULTED_MIs_dobj))