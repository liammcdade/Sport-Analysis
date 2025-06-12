import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from tqdm.auto import tqdm # Import tqdm for progress bars
import os

def main():
    print("Starting agricultural data analysis script with MAP@3 submission format...")

    # --- 1. Loading Data from CSV Files ---
    # IMPORTANT: Replace 'train_data.csv' and 'test_data.csv' with the actual
    # paths to your files if they are not in the same directory as this script.
    try:
        print("\nAttempting to load data from 'kaggle/train.csv' and 'kaggle/test.csv'...")
        train_df = pd.read_csv(os.path.join('kaggle', 'train.csv'))
        test_df = pd.read_csv(os.path.join('kaggle', 'test.csv'))
        print("Data loaded successfully.")
    except FileNotFoundError as e:
        print(f"Error: One or both CSV files not found. Please ensure 'kaggle/train.csv' and 'kaggle/test.csv' are in the correct directory.")
        print(f"Details: {e}")
        exit()
    except Exception as e:
        print(f"An unexpected error occurred while loading CSV files: {e}")
        exit()

    print("\nTrain DataFrame head:")
    print(train_df.head())
    print("\nTest DataFrame head:")
    print(test_df.head())

    # Store original test IDs for submission file
    test_ids = test_df['id']

    # --- 2. Data Preprocessing ---
    # Define features (X) and target (y) for the training data
    X_train = train_df.drop(['Fertilizer Name', 'id'], axis=1)
    y_train = train_df['Fertilizer Name']
    X_test = test_df.drop('id', axis=1).copy()

    # Identify categorical and numerical features
    numerical_features = ['Temparature', 'Humidity', 'Moisture', 'Nitrogen', 'Potassium', 'Phosphorous']
    categorical_features = ['Soil Type', 'Crop Type']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='drop'
    )

    # --- 3. Model Training ---
    print("\nTraining the Random Forest Classifier model...")
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=5, random_state=42, n_jobs=-1))
    ])

    print("Training in progress...")
    model_pipeline.fit(X_train, y_train)
    print("Model training complete.")

    # --- 4. Prediction on Test Data for MAP@3 Submission ---
    print("\nGenerating predictions for MAP@3 submission...")
    test_probabilities = model_pipeline.predict_proba(X_test)
    class_labels = model_pipeline.named_steps['classifier'].classes_
    submission_predictions = []

    for i, probs in tqdm(enumerate(test_probabilities), total=len(test_probabilities), desc="Processing Test Samples"):
        prob_series = pd.Series(probs, index=class_labels)
        top_3_fertilizers = prob_series.nlargest(3).index.tolist()
        formatted_prediction = " ".join(top_3_fertilizers)
        submission_predictions.append(formatted_prediction)

    submission_df = pd.DataFrame({
        'id': test_ids,
        'Fertilizer Name': submission_predictions
    })
    submission_file_name = 'submission.csv'
    submission_df.to_csv(submission_file_name, index=False)

    print(f"\nSubmission file '{submission_file_name}' created successfully:")
    print(submission_df.head())

    classifier = model_pipeline.named_steps['classifier']
    preprocessor_fitted = model_pipeline.named_steps['preprocessor']

    try:
        onehot_features = preprocessor_fitted.named_transformers_['cat'].get_feature_names_out(categorical_features)
        all_features = numerical_features + list(onehot_features)
    except AttributeError:
        print("Warning: Could not get precise one-hot encoded feature names. Using a simpler approach.")
        all_features = numerical_features + categorical_features

    if hasattr(classifier, 'feature_importances_'):
        print("\nFeature Importances (higher means more influential):")
        feature_importances = pd.Series(classifier.feature_importances_, index=all_features)
        print(feature_importances.sort_values(ascending=False))
    else:
        print("\nClassifier does not have 'feature_importances_' attribute (e.g., Logistic Regression).")

    print("\nAnalysis and submission file generation complete.")

if __name__ == "__main__":
    main()
