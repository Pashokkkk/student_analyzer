import sqlite3
import pandas as pd
import datetime
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Load data
def load_students():
    conn = sqlite3.connect("data/student_performance.db")
    df = pd.read_sql("SELECT * FROM students_predictions", conn)
    conn.close()
    print(f"\n✅ Loaded {df.shape[0]} students.\n")
    return df

# Encode categorical features
def encode_features(df):
    le = LabelEncoder()
    df_encoded = df.copy()
    for col in df_encoded.select_dtypes(include=["object"]).columns:
        df_encoded[col] = le.fit_transform(df_encoded[col])
    return df_encoded

# Predict Risk
def predict_risk(df_encoded):
    X = df_encoded.drop(columns=["final_grade", "risk"])
    y = df_encoded["risk"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n📊 Risk Prediction Model Evaluation:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print(f"Precision: {precision_score(y_test, y_pred):.2f}")
    print(f"Recall: {recall_score(y_test, y_pred):.2f}")

    # Predict for all
    full_pred = model.predict(X)
    return full_pred

# Predict Final Grade
def predict_final_grade(df_encoded):
    X = df_encoded.drop(columns=["final_grade", "risk"])
    y = df_encoded["final_grade"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    reg_model = LinearRegression()
    reg_model.fit(X_train, y_train)

    y_pred = reg_model.predict(X_test)

    print("\n📊 Final Grade Prediction Model Evaluation:")
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
    print(f"R²: {r2_score(y_test, y_pred):.2f}")

    # Predict for all
    full_pred = reg_model.predict(X)
    return full_pred

# Save updated predictions
def save_predictions(df, predicted_risk, predicted_final_grade):
    df_copy = df.copy()
    df_copy["predicted_risk"] = predicted_risk
    df_copy["predicted_final_grade"] = predicted_final_grade
    df_copy["prediction_date"] = datetime.datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("data/student_performance.db")
    df_copy.to_sql("students_predictions", conn, if_exists="replace", index=False)
    conn.close()
    print("\n✅ Predictions saved successfully.\n")

# Generate simple report
def generate_report():
    conn = sqlite3.connect("data/student_performance.db")
    risky_students = pd.read_sql("SELECT * FROM students_predictions WHERE predicted_risk = 1", conn)
    low_scores = pd.read_sql("SELECT * FROM students_predictions WHERE predicted_final_grade < 10", conn)
    conn.close()

    print("\n📝 Risky Students (Predicted):", risky_students.shape[0])
    print("📝 Students Predicted Final Grade < 10:", low_scores.shape[0])

# Main CLI Loop
def main():
    df = None
    df_encoded = None
    predicted_risk = None
    predicted_final_grade = None

    while True:
        print("\n📚 SMART STUDENT PERFORMANCE ANALYZER")
        print("1. Load Students")
        print("2. Predict Risk")
        print("3. Predict Final Grade")
        print("4. Save Predictions")
        print("5. Generate Report")
        print("6. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            df = load_students()
            df_encoded = encode_features(df)
        elif choice == "2":
            if df_encoded is None:
                print("\n❗ Please load the students first!")
            else:
                predicted_risk = predict_risk(df_encoded)
        elif choice == "3":
            if df_encoded is None:
                print("\n❗ Please load the students first!")
            else:
                predicted_final_grade = predict_final_grade(df_encoded)
        elif choice == "4":
            if df is None or predicted_risk is None or predicted_final_grade is None:
                print("\n❗ Please complete predictions first!")
            else:
                save_predictions(df, predicted_risk, predicted_final_grade)
        elif choice == "5":
            generate_report()
        elif choice == "6":
            print("\n👋 Exiting. Have a great day!")
            break
        else:
            print("\n❗ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
