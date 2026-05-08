This repository contains the Python scripts used in Study I.

types_tokens_ratios.py: This script extracts word combinations based on amod, advmod, and dobj grammatical relations from texts belonging to two expert registers: editorials and research journals. It further employs a moving-window approach (e.g., Vandeweerd et al., 2023), using windows of 300 words with increments of 10 words, to reduce potential biases arising from differences in text length. The script outputs summary statistics of the averaged types, tokens, and type–token ratios across moving windows for each individual text.

txt_split.py: This scrip splits the txt files into manageable subfiles that can be easily processed with spaCy. The splitted txt files are approximately 500kb large.

refernce_corpora_processing.py: This script extracts lemmas and two-word occurrences of amod, advmod, and dobj dependency relationships from any raw reference corpora.

MI_comparisons.py: This scrip extracts two-word combinations of amod, advmod, and dobj dependencies and employs the moving window approach as in the analysis of phraseological diversity (types_tokens_ratios.py) to calculate the pointwise mutual information (MI) scores based on a reference corpus (in this case, ENCOW16AX).

ENCOW_processing: This scrip extracts all two-word combinations of amod, advmod, and dobj dependencies and lemmas from the processed reference ENCOW16AX corpus.

ENCOW_Dispersion: This scrip extracts all amod, advmod_v, and dobj word combinations based on year information from ENCOW16AX. This will be later used for dispersion calculations.

Density: This script calculates phaseological density as ountlined in the report.
