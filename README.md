# Phraseological Complexity across Registers

## Overview

This repository contains the Python scripts and supporting documentation for
Study 1 of the research project investigating phraseological complexity in
argumentative and scientific writing produced by expert writers and learners
of English as a foreign language (EFL).

## Research Questions

The project addresses four related research questions:

1. To what extent and in what ways can the selected measures capture patterns
   of phraseological complexity across registers?
2. To what extent does phraseological complexity differ between argumentative
   and scientific writing produced by expert writers?
3. To what extent do EFL learners demonstrate register sensitivity in their
   phraseological complexity?
4. How does this register sensitivity vary across EFL proficiency levels?

## Methodology

The current scripts operationalize phraseological units as dependency-based
two-word combinations involving three grammatical relations:

- adjectival modifiers (`amod`);
- adverbial modifiers (`advmod_v`);
- direct objects (`dobj`).

The project investigates several dimensions of phraseological complexity,
including:

- **phraseological diversity**, represented by the numbers of combination
  types and tokens and their type–token ratios;
- **phraseological sophistication**, represented by pointwise mutual information
  (MI) scores;
- **phraseological density**, represented by the frequency of phraseological units
- relative to text length and to all combinations of the relevant grammatical type.

To reduce the influence of differences in text length, several measures are
calculated using a moving-window procedure. The current implementation uses
300-word windows advanced in increments of 10 words and averages the values
obtained across the windows of each text.

ENCOW16AX is used as the principal reference corpus for obtaining lemma
frequencies, combination frequencies, association scores, and dispersion
information.

## Repository Structure

```text
phraseological-complexity-across-registers/
│
├── Scripts/
│   ├── README.md
│   ├── txt_split.py
│   ├── reference_corpora_processing.py
│   ├── ENCOW_processing.py
│   ├── ENCOW_Dispersion.py
│   ├── types,tokens,ratios.py
│   ├── MI_comparisons.py
│   ├── Density.py
│   └── Discussion.py
│
├── data/
│   └── reference/
│       └── encow16ax/
│           └── README.md
│
└── README.md
