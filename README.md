# Pokémon Legendary Analysis & Prediction

As most people born in the late 90s or early 2000s, Pokemon was a big part of my childhood. So why not use my Data Analysis and Data Science skills 
to see if I can find insights in this world.

Some of the tasks I will be working on:
- Understanding what separates Legendary Pokémon from the rest
- Testing whether we can predict Legendary status using data alone


### Exploratory Data Analysis (EDA)

Before touching any models, I spent time exploring the data and checking whether common Pokémon “myths” actually show up statistically. 
I looked at:

- Distribution of base stats (HP, Attack, Defense, Sp. Atk, Sp. Def, Speed)
- Differences between Legendary vs Non-Legendary Pokémon
- Stat trends across generations
- Tradeoffs between offense, defense, and speed
- Capture rate, egg steps, and experience growth as difficulty signals
- Type-based stat tendencies and combat vulnerabilities

### Main findings

- Legendary Pokémon clearly sit in a different stat regime, especially in base total. 
They tend to be harder to catch and slower to train.
- Some non-Legendary Pokémon overlap heavily with legendary pokemon in raw stats, but often they are heavily specialied Pokemon.
- Type alone is not enough to identify legendary pokemon, but it helps when combined with stats
- Egg steps is a great indicator if a Pokemon is legendary or not, as they are often over 300k steps.


### Feature Engineering

To prepare for modeling, I went ahead and used One-hot encoding on Pokémon types (type1, type2),
Ordinal encoding for experience growth rate. Then I aggregated defensive metrics using type effectiveness. Then I dropped
any identifier and non-informative text features such as names, abilities, which was not useful for the model.

### Legendary Prediction Modeling

I noticed that during my previous attempt on this project, my training pipeline had data leakage which was no good.
So I implemented pipelines to ensure no data leakage and ease training. So all the preprocessing steps were handled inside
pipelines, not befor ethe train/test split.

My goal was very simple, can the models predict whether a Pokemon is **Legendary** using only the stats, types, and metadata?


- **Models Used**
  - Random Forest
  - Ridge Classifier
  - SGD Classifier
  - K-Nearest Neighbors
  - XGBoost
  - Stacking Classifier
  - Voting Classifier

Due to class imbalance, I focused mostly on the F1 score as the primary metrics, but also used Accuracy, ROC-AUC, and average precision
as the secondary metrics. I also ensured to add class weighting for all the models if that was an option and included cross-validation to reduce
the chances of overfitting.

### Model Insights

**WIP**

### Clustering

As a step before working on the recommender system, I would like to see what cluster can the models make, trying to find 
certain Pokemon classes, such as bruiser, glass cannon, tank, buffer, etc