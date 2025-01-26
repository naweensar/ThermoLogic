import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib  # To load the trained model

# Load the pre-trained Gradient Boosting model
model = joblib.load('OntarioModel.pkl')  # Update with the correct file path to the model

# Function to process and plot predictions for a dataset
def process_and_plot(file_path, output_csv, plot_title):
    # Load the CSV file
    data = pd.read_csv(file_path)

    # Rename columns to match those used during model training
    data = data.rename(columns={
        'Sunny Or Cloudy': 'Sunny_Or_Cloudy'
    })

    # Ensure the data has the correct data types
    data['Sunny_Or_Cloudy'] = data['Sunny_Or_Cloudy'].astype(float)
    data['Windy'] = data['Windy'].astype(float)

    # Select only the features used during model training
    features = ['Value', 'Sunny_Or_Cloudy', 'Windy']
    X = data[features]

    # Predict the 'Required Energy' for the data
    predictions = model.predict(X)

    # Extract the actual 'Required Energy' values
    actual_values = data['Required Energy']

    # Limit the actual values to the first 75
    limited_actual_values = actual_values[:75]

    # Plot the actual values (first 75) and predictions (all)
    plt.figure(figsize=(12, 6))
    plt.plot(limited_actual_values, label='Actual Energy (First 75)', color='blue', linewidth=2)
    plt.plot(predictions, label='Predicted Energy (All)', linestyle='dotted', color='orange', linewidth=2)
    plt.title(plot_title)
    plt.xlabel('Time (Index)')
    plt.ylabel('Required Energy')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Save the predictions to a CSV file
    padded_actual_values = pd.concat(
        [limited_actual_values, pd.Series([None] * (len(predictions) - len(limited_actual_values)))],
        ignore_index=True
    )
    predicted_df = pd.DataFrame({
        'Actual Energy (First 75)': padded_actual_values,
        'Predicted Energy': pd.Series(predictions)
    })
    predicted_df.to_csv(output_csv, index=False)

    print(f"Processed and plotted for: {file_path}")
    print(f"Predictions saved to: {output_csv}")

# Process and plot for the first file
process_and_plot(
    file_path="C:\\Users\\Naween\\PycharmProjects\\ThermoLogic\\models\\Ontario1DayCSV.csv",  # Update with the correct file path
    output_csv="predictions_1day.csv",
    plot_title="Comparison of Actual vs Predicted Energy (File 1)"
)

# # Process and plot for the second file
# process_and_plot(
#     file_path="C:\\Users\\ZainP\\Downloads\\Ontario2DayCSV.csv",  # Update with the correct file path
#     output_csv="predictions_2day.csv",
#     plot_title="Comparison of Actual vs Predicted Energy (File 2)"
# )
