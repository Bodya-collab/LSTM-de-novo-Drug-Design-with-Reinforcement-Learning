# De Novo Drug Design: LSTM & Reinforcement Learning Pipeline
This project implements a Recurrent Neural Network (LSTM) optimized with Reinforcement Learning (RL) to generate novel, drug-like molecules from scratch (de novo generation)

This repository contains a complete pipeline for *de novo* molecular generation using a Long Short-Term Memory (LSTM) Recurrent Neural Network optimized via Reinforcement Learning (RL). The goal of this project is to generate valid, synthetically accessible, and non-toxic drug-like molecules that strictly adhere to Lipinski's Rule of Five.

## Overview

Training a language model to generate SMILES strings natively often results in invalid syntax or "mode collapse" (where the model finds a single high-scoring pattern, such as infinite carbon chains or toxic sulfur spam, and repeats it). 

This project solves these issues using a two-step architecture:
1. **Foundation Model:** An LSTM pre-trained on a filtered MOSES dataset to learn the strict grammatical rules of SMILES.
2. **The RL Judge (Scoring Function):** A heavily customized reward function incorporating RDKit descriptors (QED, Lipinski rules, rotatable bonds, synthetic accessibility) and an XGBoost model trained on the ESOL dataset to predict solubility (LogS).

By actively penalizing cheap exploits (e.g., carbon spam, hyper-hydrophobicity, and toxic heteroatom overloads), the RL loop forces the generator to explore complex, realistic chemical spaces.

##  Analytics & Model Interpretability

The following visualizations demonstrate how the model's behavior evolved and adapted to the strict chemical constraints imposed by the RL Judge.

### 1. Chemical Space and Lipinski's Rule of Five
![Chemical Space]<img width="665" height="450" alt="Chemical Space (Lipinski&#39;s Rule of Five)" src="https://github.com/user-attachments/assets/ecd6c14f-ebf5-4d50-847c-e9d82648508d" />
This scatter plot provides direct visual proof of the RL loop's success. 
* **The Axes:** Molecular Weight (X) vs. Lipophilicity / LogP (Y). The red dashed lines represent the boundaries of Lipinski's Rule of Five (Weight < 500 Da, LogP < 5).
* **The Clustering:** The color gradient represents the AI Score (Reward). The model's "Elite" outputs (yellow/green dots, Score > 0.75) are perfectly clustered in the bottom-left quadrant—the optimal therapeutic window. 
* **Weak compounds:** The rejected structures (dark purple, Score < 0.4) are scattered wildly, frequently breaching the 500 Da weight limit and the LogP = 5 threshold. The model actively learned to avoid these regions.

### 2. Controlling Molecule Size (SMILES Length vs. Reward)
![SMILES Length]<img width="665" height="450" alt="Lenght_smiles vs Ai_score" src="https://github.com/user-attachments/assets/e022f26c-5021-41d2-b03a-3d5cc649393e" />
A common issue in ML-driven drug design is the model inflating molecule size to artificially boost parameters like LogP or weight. The strong negative correlation shown here proves that the Judge successfully penalized unnecessary chain elongations. The model learned that highly compact, efficient representations yield the highest rewards.

### 3. Toxicity and Heteroatom Control
![Heteroatoms]<img width="665" height="450" alt="Heteroatoms vs Ai_score" src="https://github.com/user-attachments/assets/63330b3b-a44f-469b-8149-82016e6690c3" />
During early RL iterations, the model attempted "Reward Hacking" by spamming sulfur and oxygen atoms (sulfonamides/sulfones) to hit target weights quickly, resulting in highly toxic and unsynthesizable candidates. By introducing a strict penalty for excessive heteroatoms and rigid constraints on rotatable bonds, the model was forced to limit its heteroatom usage. The negative correlation confirms the model favors stable, balanced structures (e.g., standard amide bonds) over toxic heteroatom spam.

### 4. Reward Distribution (Preventing Mode Collapse)
![Distribution]<img width="665" height="450" alt="Heteroatoms vs Ai_score" src="https://github.com/user-attachments/assets/5ff49b29-9161-41c2-a631-33a9beef0234" />
This density plot illustrates the distribution of rewards across a generated batch. Instead of a single massive spike at 1.0 (which would indicate catastrophic mode collapse, where the model outputs the exact same molecule 10,000 times), we see a healthy, multimodal distribution. This confirms the model maintains high structural diversity (Tanimoto dissimilarity) while consistently shifting the bulk of its generations toward the high-reward threshold.

### 5. Druglikeness (QED) Optimization
![QED vs Reward]<img width="665" height="450" alt="QED" src="https://github.com/user-attachments/assets/c38a301b-7931-4704-9879-78448c802d9f" />
The Quantitative Estimate of Druglikeness (QED) is the industry standard for evaluating the viability of *de novo* generated molecules. This plot confirms that the Reinforcement Learning agent successfully learned to prioritize high-QED structures.

*Note on the plot's topology:* The distinct diagonal banding (rather than a diffuse scatter cloud) is an expected mathematical artifact of our customized reward function. The final AI Score uses QED as a continuous baseline weight (`QED * 0.7`), combined with strict discrete step-bonuses (e.g., `+0.2` for specific ring/heteroatom complexities) and hard penalty multipliers. Consequently, the molecules form parallel linear clusters based on which discrete logical conditions they satisfied during the scoring phase.

### 6. Global Feature Correlation (Heatmap)
<img width="665" height="450" alt="Correlation Heatmap of Molecular Features and AI Score" src="https://github.com/user-attachments/assets/65b5fcfa-91c4-4e07-8f9f-984788e03a5f" />
![Correlation Heatmap]

To summarize the global impact of the Reinforcement Learning constraints, a correlation matrix was computed for the key physicochemical properties of the generated batch.

**Key Insights:**
* **Lipinski Adherence:** The strong negative correlations between the AI Score and both `MolWt` (-0.73) and `LogP` (-0.63) prove that the RL loop successfully forced the generative model to penalize heavy, highly lipophilic structures.
* **Curing "Reward Hacking":** The near-zero correlation between the AI Score and `heteroatom_count` (-0.06) is a massive success. In early iterations, the model attempted to exploit the scoring function by spamming sulfur and oxygen atoms. After implementing strict synthetic constraints, the model learned to use heteroatoms naturally to form stable amides and heterocycles, rather than using them to artificially inflate the reward.

##  Future Work
While this pipeline successfully generates druglike molecules, *de novo* generation is only the first step in the drug discovery cascade. Future improvements to this project include:
1. **Target-Specific Generation (Molecular Docking):** Integrating a docking engine (e.g., AutoDock Vina) into the RL reward loop to generate ligands optimized for specific protein targets (e.g., kinase inhibitors).
2. **Deep ADMET Profiling:** Replacing basic Lipinski filters with deep learning ADMET predictors to screen for hERG toxicity, BBB permeability, and metabolic stability.
3. **Retrosynthetic Accessibility:** Implementing a strict retrosynthesis evaluator to ensure all generated elite molecules can be synthesized in under 5 standard reaction steps.

## 🛠 Project Structure & Usage

* `1_data_preparation.ipynb`: Downloads, cleans, and filters the ZINC/MOSES dataset to establish a strict SMILES vocabulary.
* `2_pretraining_lstm.ipynb`: Trains the foundation LSTM to predict the next SMILES character.
* `3_xgboost_scorer.ipynb`: Trains the LogS predictor on the Delaney (ESOL) dataset.
* `4_rl_generation.ipynb`: The core Reinforcement Learning loop. Includes the custom Judge function and elite-batch fine-tuning.
* `analytics.R`: RStudio scripts (`ggplot2`, `ggcorrplot`) used to generate the final analytical visualizations.

### Requirements
* `Python 3.10+`
* `TensorFlow`, `RDKit`, `XGBoost`, `Pandas`, `NumPy`
* `R` (for analytics: `ggplot2`, `readr`, `dplyr`)
