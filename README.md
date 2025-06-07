# From Bar Charts to Battle Teams: A Pokémon Data Analysis & Recommender

This project began with a simple question:  
**Can we find meaningful patterns in Pokémon stats and types?**

It quickly grew into a multi-stage data science project with:
- Exploratory Data Analysis (EDA)
- Predictive modeling
- A role-based team recommender system
---

## Project Overview

**Goals:**
- Analyze base stats across Pokémon types.
- Predict a Pokémon’s primary type from stats.
- Predict whether a Pokémon is Legendary.
- Build a team recommender based on role diversity, type synergy, and starter choice.

---

## Models Used

### Legendary Prediction
- Random Forest (default and tuned)
- XGBoost (default and tuned)
- StackingClassifier

**Best Result:**  
*StackingClassifier with 90% recall on Legendary Pokémon*

### Type Prediction
- Random Forest
- XGBoost
- Gradient Boosting
- StackingClassifier

**Challenge:**  
Even the best model (StackingClassifier) achieved ~30% accuracy — highlighting that type prediction from stats alone is limited.

---

## Team Recommender System

Given a **starter Pokémon**, the script builds a balanced team:
- Each Pokémon fills a distinct role (DPS, Tank, Speedster, etc.)
- No duplicate Type 1s
- Prioritizes counters to starter weaknesses
- Includes **at most one Legendary**

### Sample logic:
```python
def find_counter_types(starter_type):
    weaknesses = type_weaknesses.get(starter_type, [])
    counter_types = set()
    for weakness in weaknesses:
        counter_types.update(counter_map.get(weakness, []))
    return list(counter_types)
```

Lessons Learned
- Predicting Legendary status is very feasible with base stats alone.
- Predicting Type 1 from stats is much harder, abilities, dual types, and moves matter more.
- Simple rule-based recommenders can still create thoughtful teams using smart constraints.