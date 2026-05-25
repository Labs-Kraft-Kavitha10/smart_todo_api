# Model Validation Report

## Model
- **Pipeline:** `TfidfVectorizer(ngram_range=(1, 2))` → `MultinomialNB`
- **Train/test split:** 80 / 20, stratified, `random_state=42`
- **Dataset:** `data/tasks.csv` — 201 labeled examples (70 High / 71 Medium / 60 Low)

## Final accuracy

**0.9268 (92.68%)** on the held-out test set of 41 samples — well above the 70% acceptance threshold.

## Confusion matrix

Rows = true label, columns = predicted label. Label order: `[High, Low, Medium]`.

|              | Pred: High | Pred: Low | Pred: Medium |
|--------------|:----------:|:---------:|:------------:|
| **True High**   | 13 | 0  | 1  |
| **True Low**    | 0  | 10 | 2  |
| **True Medium** | 0  | 0  | 15 |

## Classification report

| Class    | Precision | Recall | F1   | Support |
|----------|:---------:|:------:|:----:|:-------:|
| High     | 1.00      | 0.93   | 0.96 | 14      |
| Low      | 1.00      | 0.83   | 0.91 | 12      |
| Medium   | 0.83      | 1.00   | 0.91 | 15      |

## Insight

The model never confuses **High** with **Low** or vice versa — those two classes are linguistically well-separated (urgent/bug language vs. casual/leisure language). All errors collapse into the **Medium** bucket: 1 High and 2 Low samples were predicted as Medium. In other words, Medium is acting as the model's "default" when a task sits between the two extremes. For the demo, this means borderline phrasing ("plan something for tomorrow") is more likely to drift toward Medium than to flip across the urgency spectrum — a safe and intuitive failure mode.
