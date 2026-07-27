import spacy
import glob
import math
import os
import numpy

spacy.require_gpu()
nlp = spacy.load("en_core_web_trf")

filepaths = glob.glob("E:/Corpora/MULTED/300/*.txt")
# filepaths = glob.glob("E:/Corpora/LOCRA/LOCRA/1/*.txt")

# =========================
# Output containers
# =========================

# token/count version
amod_tokens = []
advmod_tokens = []
dobj_tokens = []

# ratio version
amod_ratios = []
advmod_ratios = []
dobj_ratios = []

# =========================
# Lemma reference
# =========================
lemma_ref_dict = {}
lemma_filepath = "E:/Corpora/ENCOW16AX/reference/lemma.txt"

with open(lemma_filepath, "r", encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) == 2:
            lemma, freq = parts
            lemma_ref_dict[lemma] = int(freq)

total_lemma = sum(lemma_ref_dict.values())

# =========================
# amod / advmod / dobj reference
# =========================
def load_ref_dict(filepath):
    ref_dict = {}

    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            contents = line.strip().split()

            if len(contents) == 3:
                freq = int(contents[2])
                collo = f"{contents[0]} {contents[1]}"
                ref_dict[collo] = freq

    return ref_dict


amod_ref_dict = load_ref_dict("E:/Corpora/ENCOW16AX/reference/amod.txt")
advmod_ref_dict = load_ref_dict("E:/Corpora/ENCOW16AX/reference/advmod.txt")
dobj_ref_dict = load_ref_dict("E:/Corpora/ENCOW16AX/reference/dobj.txt")

# merge all
total_ref_dict = {}

for d in [amod_ref_dict, advmod_ref_dict, dobj_ref_dict]:
    for key, value in d.items():
        total_ref_dict[key] = total_ref_dict.get(key, 0) + value

# =========================
# MI calculation
# =========================
def get_MI(collocation):
    parts = collocation.split()

    if len(parts) != 2:
        return None

    collo_1, collo_2 = parts

    if collocation not in total_ref_dict:
        return None

    if collo_1 not in lemma_ref_dict or collo_2 not in lemma_ref_dict:
        return None

    freq_collocation = total_ref_dict[collocation]
    freq_collo_1 = lemma_ref_dict[collo_1]
    freq_collo_2 = lemma_ref_dict[collo_2]

    if (
        freq_collocation == 0
        or freq_collo_1 == 0
        or freq_collo_2 == 0
        or total_lemma == 0
    ):
        return None

    MI = math.log2(
        freq_collocation * total_lemma /
        (freq_collo_1 * freq_collo_2)
    )

    return MI

# =========================
# Dispersion reference
# =========================
ref_dir = r"D:/ENCOW16AX/reference_merged_1995_2014"
size_file = r"D:/ENCOW16AX/year_token_counts_total.txt"
years = list(range(2000, 2015))


def load_year_sizes(filepath):
    year_sizes = {}

    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()

            if len(parts) == 2:
                year_sizes[parts[0]] = int(parts[1])

    return year_sizes


year_sizes = load_year_sizes(size_file)


def get_collocation_freq(filepath, target_collo):
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()

            if len(parts) < 2:
                continue

            freq = int(parts[-1])
            collo = " ".join(parts[:-1])

            if collo == target_collo:
                return freq

    return 0


def juilland_d(values):
    n = len(values)

    if n <= 1:
        return None

    mean_val = sum(values) / n

    if mean_val == 0:
        return 0.0

    variance = sum((x - mean_val) ** 2 for x in values) / n
    sd = math.sqrt(variance)

    return 1 - ((sd / mean_val) / math.sqrt(n - 1))


def calculate_collocation_d(target_collo, ref_dir, year_sizes, years):
    norm_values = []

    for year in years:
        year_str = str(year)
        filepath = os.path.join(ref_dir, f"{year_str}.txt")

        raw_freq = get_collocation_freq(filepath, target_collo)
        tokens = year_sizes[year_str]

        norm_freq = raw_freq / tokens * 1_000_000
        norm_values.append(norm_freq)

    return juilland_d(norm_values)

# =========================
# Cache
# =========================
mi_cache = {}
d_cache = {}

# =========================
# Helper: check whether collocation is qualified
# =========================
def is_qualified_collocation(collocation, collo_1, collo_2):
    if collocation not in total_ref_dict:
        return False

    if total_ref_dict[collocation] < 9538:
        return False

    if collo_1 not in lemma_ref_dict or collo_2 not in lemma_ref_dict:
        return False

    if collocation not in mi_cache:
        mi_cache[collocation] = get_MI(collocation)

    MI = mi_cache[collocation]

    if MI is None or MI < 3:
        return False

    if collocation not in d_cache:
        d_cache[collocation] = calculate_collocation_d(
            collocation,
            ref_dir,
            year_sizes,
            years
        )

    D = d_cache[collocation]

    if D is None or D < 0.45:
        return False

    return True

# =========================
# Main
# =========================
for filepath in filepaths:

    with open(filepath, "r", encoding="utf-8") as file:

        tokens = []
        index_start = 0

        content = file.read()
        doc = nlp(content)

        # per-text window values: token/count version
        ind_amod_token_densities = []
        ind_advmod_token_densities = []
        ind_dobj_token_densities = []

        # per-text window values: ratio version
        ind_amod_ratio_densities = []
        ind_advmod_ratio_densities = []
        ind_dobj_ratio_densities = []

        for token in doc:
            if token.is_alpha:
                tokens.append(token)

        while index_start <= len(tokens) - 300:

            # =========================
            # token/count values per window
            # =========================
            win_amod_token_density = 0
            win_advmod_token_density = 0
            win_dobj_token_density = 0

            # =========================
            # ratio counters per window
            # denominator = all structures
            # numerator = qualified structures
            # =========================
            n_amod = 0
            n_amod_p = 0

            n_advmod = 0
            n_advmod_p = 0

            n_dobj = 0
            n_dobj_p = 0

            for n in range(index_start, index_start + 300):

                tok = tokens[n]
                head = tok.head

                # =========================
                # AMOD: ADJ -> NOUN
                # =========================
                if (
                    tok.pos_ == "ADJ"
                    and tok.dep_ == "amod"
                    and head.pos_ == "NOUN"
                    and tok.is_alpha
                    and head.is_alpha
                ):
                    collo_1 = tok.lemma_
                    collo_2 = head.lemma_
                    collocation = f"{collo_1} {collo_2}"

                    # ratio denominator
                    n_amod += 1

                    if is_qualified_collocation(collocation, collo_1, collo_2):
                        # token/count version
                        win_amod_token_density += 1

                        # ratio numerator
                        n_amod_p += 1

                # =========================
                # ADVMOD: ADV -> VERB
                # =========================
                elif (
                    tok.pos_ == "ADV"
                    and tok.dep_ == "advmod"
                    and head.pos_ == "VERB"
                    and tok.is_alpha
                    and head.is_alpha
                ):
                    collo_1 = tok.lemma_
                    collo_2 = head.lemma_
                    collocation = f"{collo_1} {collo_2}"

                    # ratio denominator
                    n_advmod += 1

                    if is_qualified_collocation(collocation, collo_1, collo_2):
                        # token/count version
                        win_advmod_token_density += 1

                        # ratio numerator
                        n_advmod_p += 1

                # =========================
                # DOBJ: VERB + NOUN
                # spaCy v3 common label is obj, not always dobj
                # =========================
                elif (
                    tok.pos_ == "NOUN"
                    and tok.dep_ in {"dobj", "obj"}
                    and head.pos_ == "VERB"
                    and tok.is_alpha
                    and head.is_alpha
                ):
                    collo_1 = head.lemma_
                    collo_2 = tok.lemma_
                    collocation = f"{collo_1} {collo_2}"

                    # ratio denominator
                    n_dobj += 1

                    if is_qualified_collocation(collocation, collo_1, collo_2):
                        # token/count version
                        win_dobj_token_density += 1

                        # ratio numerator
                        n_dobj_p += 1

            # =========================
            # ratio values per window
            # no structure in window = 0
            # =========================
            if n_amod != 0:
                win_amod_ratio_density = n_amod_p / n_amod
            else:
                win_amod_ratio_density = 0

            if n_advmod != 0:
                win_advmod_ratio_density = n_advmod_p / n_advmod
            else:
                win_advmod_ratio_density = 0

            if n_dobj != 0:
                win_dobj_ratio_density = n_dobj_p / n_dobj
            else:
                win_dobj_ratio_density = 0

            # =========================
            # append window values
            # =========================

            # token/count version
            ind_amod_token_densities.append(win_amod_token_density)
            ind_advmod_token_densities.append(win_advmod_token_density)
            ind_dobj_token_densities.append(win_dobj_token_density)

            # ratio version
            ind_amod_ratio_densities.append(win_amod_ratio_density)
            ind_advmod_ratio_densities.append(win_advmod_ratio_density)
            ind_dobj_ratio_densities.append(win_dobj_ratio_density)

            index_start += 10

        # =========================
        # text-level means
        # =========================

        # token/count version
        if ind_amod_token_densities:
            amod_tokens.append(float(numpy.mean(ind_amod_token_densities)))
        else:
            amod_tokens.append(0)

        if ind_advmod_token_densities:
            advmod_tokens.append(float(numpy.mean(ind_advmod_token_densities)))
        else:
            advmod_tokens.append(0)

        if ind_dobj_token_densities:
            dobj_tokens.append(float(numpy.mean(ind_dobj_token_densities)))
        else:
            dobj_tokens.append(0)

        # ratio version
        if ind_amod_ratio_densities:
            amod_ratios.append(float(numpy.mean(ind_amod_ratio_densities)))
        else:
            amod_ratios.append(0)

        if ind_advmod_ratio_densities:
            advmod_ratios.append(float(numpy.mean(ind_advmod_ratio_densities)))
        else:
            advmod_ratios.append(0)

        if ind_dobj_ratio_densities:
            dobj_ratios.append(float(numpy.mean(ind_dobj_ratio_densities)))
        else:
            dobj_ratios.append(0)

# =========================
# Output: token/count version
# =========================
print("===================================")
print("TOKEN / COUNT VERSION")
print("===================================")

print("amod_tokens:")
print(amod_tokens)
print("mean amod_tokens:")
print(numpy.mean(amod_tokens))

print("\nadvmod_tokens:")
print(advmod_tokens)
print("mean advmod_tokens:")
print(numpy.mean(advmod_tokens))

print("\ndobj_tokens:")
print(dobj_tokens)
print("mean dobj_tokens:")
print(numpy.mean(dobj_tokens))

# =========================
# Output: ratio version
# =========================
print("\n===================================")
print("RATIO VERSION")
print("===================================")

print("amod_ratios:")
print(amod_ratios)
print("mean amod_ratios:")
print(numpy.mean(amod_ratios))

print("\nadvmod_ratios:")
print(advmod_ratios)
print("mean advmod_ratios:")
print(numpy.mean(advmod_ratios))

print("\ndobj_ratios:")
print(dobj_ratios)
print("mean dobj_ratios:")
print(numpy.mean(dobj_ratios))