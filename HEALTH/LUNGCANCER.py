import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import pandas as pd

# Load your dataset (assumes a CSV file named "lung_cancer_data.csv")
df = pd.read_csv(r"C:\Users\liam\Pictures\apple its glowtime\iPhone 16\dataset_med.csv")


# Drop irrelevant columns
df = df.drop(columns=['id', 'diagnosis_date', 'end_treatment_date'], errors='ignore')

# Map cancer_stage to numeric
stage_map = {'Stage I': 1, 'Stage II': 2, 'Stage III': 3, 'Stage IV': 4}
df['cancer_stage'] = df['cancer_stage'].map(stage_map)

# Split survivors and non-survivors
survivors = df[df['survived'] == 1]
non_survivors = df[df['survived'] == 0]

# Initialize table
comparison = []

# Categorical comparison
categorical_cols = ['gender', 'country', 'family_history', 'smoking_status',
                    'hypertension', 'asthma', 'cirrhosis', 'other_cancer', 'treatment_type']

for col in categorical_cols:
    if col in df.columns:
        surv_common = survivors[col].mode(dropna=True)[0]
        surv_count = survivors[col].value_counts()[surv_common]
        dead_common = non_survivors[col].mode(dropna=True)[0]
        dead_count = non_survivors[col].value_counts()[dead_common]
        comparison.append([
            col,
            f"{surv_common} ({surv_count})",
            f"{dead_common} ({dead_count})"
        ])

# Numeric comparison
numeric_cols = ['age', 'bmi', 'cholesterol_level', 'cancer_stage']

for col in numeric_cols:
    if col in df.columns:
        surv_mean = survivors[col].mean()
        dead_mean = non_survivors[col].mean()
        comparison.append([
            col,
            f"{surv_mean:.2f}",
            f"{dead_mean:.2f}"
        ])

# Create DataFrame
comparison_df = pd.DataFrame(comparison, columns=["Trait", "Survivors", "Non-Survivors"])

# Display the table
print("\n📋 Trait Comparison Table:\n")
print(comparison_df.to_string(index=False))