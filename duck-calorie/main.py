import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_log_error
from lightgbm import LGBMRegressor


# Load your data
train = pd.read_csv(r'duck-calorie\train.csv')
test = pd.read_csv(r'duck-calorie\test.csv')

# Encode 'Sex'
le = LabelEncoder()
train['Sex'] = le.fit_transform(train['Sex'])
test['Sex'] = le.transform(test['Sex'])

# Feature engineering
train['BMI'] = train['Weight'] / (train['Height'] / 100) ** 2
test['BMI'] = test['Weight'] / (test['Height'] / 100) ** 2

train['HRxDur'] = train['Heart_Rate'] * train['Duration']
test['HRxDur'] = test['Heart_Rate'] * test['Duration']

train['TempxDur'] = train['Body_Temp'] * train['Duration']
test['TempxDur'] = test['Body_Temp'] * test['Duration']

# Features list
features = ['Sex', 'Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp', 'BMI', 'HRxDur', 'TempxDur']

# Prepare data
X = train[features]
y = np.log1p(train['Calories'])  # log-transform target for RMSLE

# Split data
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Model averaging setup
val_preds = np.zeros(len(X_val))
test_preds = np.zeros(len(test))

seeds = [0, 42, 1337]

for seed in seeds:
    model = LGBMRegressor(
        objective='regression',
        learning_rate=0.03,
        num_leaves=64,
        max_depth=8,
        min_child_samples=20,
        subsample=0.7,
        colsample_bytree=0.8,
        n_estimators=600,
        random_state=seed
    )
    model.fit(X_train, y_train)
    
    val_preds += model.predict(X_val) / len(seeds)
    test_preds += model.predict(test[features]) / len(seeds)

# Inverse transform predictions
val_preds_exp = np.expm1(val_preds)
y_val_exp = np.expm1(y_val)

# RMSLE evaluation
rmsle = np.sqrt(mean_squared_log_error(y_val_exp, val_preds_exp))
print(f'Validation RMSLE: {rmsle:.5f}')

# Clip negative predictions in test set
test_preds_exp = np.clip(np.expm1(test_preds), 0, None)

# Prepare submission
submission = pd.DataFrame({'id': test['id'], 'Calories': test_preds_exp})
submission.to_csv('submission.csv', index=False)