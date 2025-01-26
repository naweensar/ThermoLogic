import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Load the dataset
data = pd.read_csv("C:\\Users\\ZainP\\Downloads\\cleaned_sunny_windy_data.csv")

# Clean the dataset: Ensure proper data types
# Rename columns to avoid spaces
data.rename(columns={
    "Sunny Or Cloudy": "Sunny_Or_Cloudy",
    "Required Energy": "Required_Energy"
}, inplace=True)

# Ensure 'Sunny_Or_Cloudy' and 'Windy' are normalized between 0 and 1
if data["Sunny_Or_Cloudy"].max() > 1 or data["Windy"].max() > 1:
    print("Ensure 'Sunny_Or_Cloudy' and 'Windy' are normalized between 0 and 1")
data["Sunny_Or_Cloudy"] = pd.to_numeric(data["Sunny_Or_Cloudy"])
data["Windy"] = pd.to_numeric(data["Windy"])
data["Required_Energy"] = pd.to_numeric(data["Required_Energy"])

# Split the dataset into training and testing sets
X = data[["Value", "Sunny_Or_Cloudy", "Windy"]]
y = data["Required_Energy"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train a Gradient Boosting Model
gbm = GradientBoostingRegressor(
    n_estimators=200,    # Number of trees
    learning_rate=0.1,   # Shrinkage parameter
    max_depth=3,         # Depth of each tree
    random_state=42
)

gbm.fit(X_train, y_train)

# Predict on the test set
y_pred = gbm.predict(X_test)

# Evaluate the model
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"GBM MAE: {mae:.2f}")
print(f"GBM R-squared: {r2:.2f}")

joblib.dump(gbm, "OntarioModel.pkl")
print("Model saved successfully!")
