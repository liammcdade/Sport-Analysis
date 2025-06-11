import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

print("Starting agricultural data analysis script...")

# --- 1. Loading Data from CSV Files ---
# IMPORTANT: Replace 'train_data.csv' and 'test_data.csv' with the actual
# paths to your files if they are not in the same directory as this script.
try:
    print("\nAttempting to load data from 'train_data.csv' and 'test_data.csv'...")
    train_df = pd.read_csv('train_data.csv')
    test_df = pd.read_csv('test_data.csv')
    print("Data loaded successfully.")
except FileNotFoundError as e:
    print(f"Error: One or both CSV files not found. Please ensure 'train_data.csv' and 'test_data.csv' are in the correct directory.")
    print(f"Details: {e}")
    # Exit or handle the error appropriately if files are missing
    exit() # Exiting for demonstration; in a real app, you might raise an error or prompt the user.
except Exception as e:
    print(f"An unexpected error occurred while loading CSV files: {e}")
    exit()


print("\nTrain DataFrame head:")
print(train_df.head())
print("\nTest DataFrame head:")
print(test_df.head())

# --- 2. Data Preprocessing ---
# Define features (X) and target (y) for the training data
# 'Fertilizer Name' is our target variable for prediction.
# Ensure 'id' is dropped from features as it's typically just an identifier.
X_train = train_df.drop(['Fertilizer Name', 'id'], axis=1)
y_train = train_df['Fertilizer Name']
X_test = test_df.drop('id', axis=1).copy() # Features for making predictions on the test set, dropping 'id'

# Identify categorical and numerical features based on your provided schema
numerical_features = ['Temparature', 'Humidity', 'Moisture', 'Nitrogen', 'Potassium', 'Phosphorous']
categorical_features = ['Soil Type', 'Crop Type']

# Create a preprocessor using ColumnTransformer for one-hot encoding categorical features
# and leaving numerical features untouched.
preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='drop' # Drop any columns not specified
)

# --- 3. Model Training ---
print("\nTraining the Random Forest Classifier model...")
# Create a pipeline that first preprocesses the data and then applies the classifier
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Train the model
model_pipeline.fit(X_train, y_train)
print("Model training complete.")

# Evaluate the model on the training data (optional, but good for sanity check)
y_train_pred = model_pipeline.predict(X_train)
print("\nTraining Set Evaluation:")
print(f"Accuracy: {accuracy_score(y_train, y_train_pred):.2f}")
print("Classification Report:\n", classification_report(y_train, y_train_pred))

# --- 4. Prediction on Test Data ---
print("\nMaking predictions on the test data...")
test_predictions = model_pipeline.predict(X_test)

# Add predictions to the test DataFrame, aligning by original test_df index
test_df['Predicted_Fertilizer_Name'] = test_predictions
print("\nTest data with predictions:")
print(test_df)

# --- 5. Feature Importance Analysis ---
# Access the trained classifier from the pipeline
classifier = model_pipeline.named_steps['classifier']
preprocessor_fitted = model_pipeline.named_steps['preprocessor']

# Get feature names after one-hot encoding
# The order of features will be numerical first, then one-hot encoded categorical.
try:
    # Ensure to use get_feature_names_out from the fitted preprocessor
    onehot_features = preprocessor_fitted.named_transformers_['cat'].get_feature_names_out(categorical_features)
    all_features = numerical_features + list(onehot_features)
except AttributeError:
    # Fallback for older scikit-learn versions or if get_feature_names_out is not available
    print("Warning: Could not get precise one-hot encoded feature names. Using a simpler approach.")
    all_features = numerical_features + categorical_features


if hasattr(classifier, 'feature_importances_'):
    print("\nFeature Importances (higher means more influential):")
    feature_importances = pd.Series(classifier.feature_importances_, index=all_features)
    # Sort for better readability
    print(feature_importances.sort_values(ascending=False))
else:
    print("\nClassifier does not have 'feature_importances_' attribute (e.g., Logistic Regression).")

print("\nAnalysis complete.")
print("The 'test_df' now contains the 'Predicted_Fertilizer_Name' column.")
