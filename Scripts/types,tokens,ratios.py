import spacy
import glob
import numpy



spacy.require_gpu()
nlp = spacy.load("en_core_web_trf")

# filepaths = glob.glob("E:/Corpora/MULTED/300/*.txt")
# filepaths = glob.glob("E:/Corpora/LOCRA/LOCRA/1/*.txt")

def dict_total(x):
    n = 0
    for key in x.keys():
        n += x[key]
    return n

def rounded(x):
    return round(x, 2)

means_amod_type = []
means_advmod_type = []
means_dobj_type = []

means_amod_token = []
means_advmod_token = []
means_dobj_token = []

means_amod_ratio = []
means_advmod_ratio = []
means_dobj_ratio = []

for filepath in filepaths:
    with open(filepath, "r", encoding="utf-8") as file:
        tokens = []
        index_start = 0
        content = file.read()
        doc = nlp(content)

        n_amod_type_list = []
        n_advmod_type_list = []
        n_dobj_type_list = []
        n_amod_token_list = []
        n_advmod_token_list = []
        n_dobj_token_list = []
        ratio_amod = []
        ratio_advmod = []
        ratio_dobj = []

        for token in doc:
            if token.is_alpha:
                tokens.append(token)
        while index_start <= len(tokens) - 300:
            amod_dict = {}
            advmod_dict = {}
            dobj_dict = {}
            for n in range(index_start, index_start + 300):
                if tokens[n].pos_ == "ADJ" and tokens[n].dep_ == "amod" and tokens[n].head.pos_ == "NOUN" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                    collocation = f"{tokens[n].lemma_} {tokens[n].head.lemma_}"
                    if collocation not in amod_dict.keys():
                        amod_dict[collocation] = 1
                    else:
                        amod_dict[collocation] += 1
                elif tokens[n].pos_ == "ADV" and tokens[n].dep_ == "advmod" and tokens[n].head.pos_ == "VERB" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                    collocation = f"{tokens[n].lemma_} {tokens[n].head.lemma_}"
                    if collocation not in advmod_dict.keys():
                        advmod_dict[collocation] = 1
                    else:
                        advmod_dict[collocation] += 1
                elif tokens[n].pos_ == "ADV" and tokens[n].dep_ == "advmod" and tokens[n].head.pos_ == "ADJ" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                    collocation = f"{tokens[n].lemma_} {tokens[n].head.lemma_}"
                    if collocation not in advmod_dict.keys():
                        advmod_dict[collocation] = 1
                    else:
                        advmod_dict[collocation] += 1
                elif tokens[n].pos_ == "ADV" and tokens[n].dep_ == "advmod" and tokens[n].head.pos_ == "ADV" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                    collocation = f"{tokens[n].lemma_} {tokens[n].head.lemma_}"
                    if collocation not in advmod_dict.keys():
                        advmod_dict[collocation] = 1
                    else:
                        advmod_dict[collocation] += 1
                elif tokens[n].pos_ == "NOUN" and tokens[n].dep_ == "dobj" and tokens[n].head.pos_ == "VERB" and tokens[n].is_alpha and tokens[n].head.is_alpha:
                    collocation = f"{tokens[n].head.lemma_} {tokens[n].lemma_}"
                    if collocation not in dobj_dict.keys():
                        dobj_dict[collocation] = 1
                    else:
                        dobj_dict[collocation] += 1

            n_amod_type_list.append(len(amod_dict.keys()))
            n_advmod_type_list.append(len(advmod_dict.keys()))
            n_dobj_type_list.append(len(dobj_dict.keys()))

            n_amod_token_list.append(dict_total(amod_dict))
            n_advmod_token_list.append(dict_total(advmod_dict))
            n_dobj_token_list.append(dict_total(dobj_dict))

            if dict_total(amod_dict) != 0:
                ratio_amod.append(len(amod_dict) / dict_total(amod_dict))
            if dict_total(advmod_dict) != 0:
                ratio_advmod.append(len(advmod_dict) / dict_total(advmod_dict))
            if dict_total(dobj_dict) != 0:
                ratio_dobj.append(len(dobj_dict) / dict_total(dobj_dict))

            index_start += 10

        means_amod_type.append(sum(n_amod_type_list) / len(n_amod_type_list))
        means_advmod_type.append(sum(n_advmod_type_list) / len(n_advmod_type_list))
        means_dobj_type.append(sum(n_dobj_type_list) / len(n_dobj_type_list))
        means_amod_token.append(sum(n_amod_token_list) / len(n_amod_token_list))
        means_advmod_token.append(sum(n_advmod_token_list) / len(n_advmod_token_list))
        means_dobj_token.append(numpy.mean(n_dobj_token_list))
        means_amod_ratio.append(numpy.mean(ratio_amod))
        means_advmod_ratio.append(numpy.mean(ratio_advmod))
        means_dobj_ratio.append(numpy.mean(ratio_dobj))

print(f"Type amod: mean: {rounded(numpy.mean(means_amod_type))}, median: {rounded(numpy.median(means_amod_type))}, standard deviation: {rounded(numpy.std(means_amod_type))}, IQR: {rounded(numpy.percentile(means_amod_type, 75) - numpy.percentile(means_amod_type, 25))}")
print(f"Token amod: mean: {rounded(numpy.mean(means_amod_token))}, median: {rounded(numpy.median(means_amod_token))}, standard deviation: {rounded(numpy.std(means_amod_token))}, IQR: {rounded(numpy.percentile(means_amod_token, 75) - numpy.percentile(means_amod_token, 25))}")
print(f"Type advmod: mean: {rounded(numpy.mean(means_advmod_type))}, median: {rounded(numpy.median(means_advmod_type))}, standard deviation: {rounded(numpy.std(means_advmod_type))}, IQR: {rounded(numpy.percentile(means_advmod_type, 75) - numpy.percentile(means_advmod_type, 25))}")
print(f"Token advmod: mean: {rounded(numpy.mean(means_advmod_token))}, median: {rounded(numpy.median(means_advmod_token))}, standard deviation: {rounded(numpy.std(means_advmod_token))}, IQR: {rounded(numpy.percentile(means_advmod_token, 75) - numpy.percentile(means_advmod_token, 25))}")
print(f"Type dobj: mean: {rounded(numpy.mean(means_dobj_type))}, median: {rounded(numpy.median(means_dobj_type))}, standard deviation: {rounded(numpy.std(means_dobj_type))}, IQR: {rounded(numpy.percentile(means_dobj_type, 75) - numpy.percentile(means_dobj_type, 25))}")
print(f"Token dobj: mean: {rounded(numpy.mean(means_dobj_token))}, median: {rounded(numpy.median(means_dobj_token))}, standard deviation: {rounded(numpy.std(means_dobj_token))}, IQR: {rounded(numpy.percentile(means_dobj_token, 75) - numpy.percentile(means_dobj_token, 25))}\n")

print(f"Ratios amod: mean: {round(numpy.mean(means_amod_ratio), 4)}, median: {round(numpy.median(means_amod_ratio), 3)}, standard deviation: {round(numpy.std(means_amod_ratio), 3)}, IQR: {numpy.percentile(means_amod_ratio, 75) - numpy.percentile(means_amod_ratio, 25)}")
print(f"Ratios advmod: mean: {round(numpy.mean(means_advmod_ratio), 4)}, median: {round(numpy.median(means_advmod_ratio), 3)}, standard deviation: {round(numpy.std(means_advmod_ratio), 3)}, IQR: {numpy.percentile(means_advmod_ratio, 75) - numpy.percentile(means_advmod_ratio, 25)}")
print(f"Ratios dobj: mean: {round(numpy.mean(means_dobj_ratio), 4)}, median: {round(numpy.median(means_dobj_ratio), 3)}, standard deviation: {round(numpy.std(means_dobj_ratio), 3)}, IQR: {numpy.percentile(means_dobj_ratio, 75) - numpy.percentile(means_dobj_ratio, 25)}\n")

