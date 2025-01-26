import sys
import os
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QLineEdit
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY", "")  # Ensure the environment variable is set
)

# Load the pre-trained Gradient Boosting model
model = joblib.load('C:\\Users\\Naween\\PycharmProjects\\ThermoLogic\\models\\OntarioModel.pkl')  # Update with the correct file path to the model


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        fig.tight_layout()  # Automatically adjust the plot to fit within the canvas
        super().__init__(fig)
        self.setParent(parent)


class PredictionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Energy Prediction with CSV Drag-and-Drop")
        self.setGeometry(100, 100, 1800, 1000)  # Set the window size and position
        self.setAcceptDrops(True)  # Enable drag-and-drop functionality

        # Drag-and-drop CSV viewer
        self.csvViewer = QLabel(self)
        self.csvViewer.setText('\n\n Drag and drop a CSV file here \n\n')
        self.csvViewer.setAlignment(Qt.AlignCenter)
        self.csvViewer.setStyleSheet('''
            QLabel {
                border: 4px dashed #aaa;
                font-size: 16px;
                padding: 10px;
            }
        ''')
        self.csvViewer.setGeometry(20, 20, 400, 200)  # (x, y, width, height)

        # Process button
        self.process_button = QPushButton("Process CSV", self)
        self.process_button.setGeometry(20, 230, 400, 40)  # (x, y, width, height)
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_csv)

        # Matplotlib canvas for plotting
        self.canvas = MatplotlibCanvas(self)
        self.canvas.setGeometry(450, 70, 1300, 300)  # (x, y, width, height)

        # Second Matplotlib canvas for plotting the city data
        self.city_canvas = MatplotlibCanvas(self)
        self.city_canvas.setGeometry(450, 380, 1300, 300)  # (x, y, width, height)

        # Output box for displaying model output
        self.output_box = QTextEdit(self)
        self.output_box.setGeometry(20, 280, 400, 300)  # (x, y, width, height)
        self.output_box.setReadOnly(True)  # Make the box read-only
        self.output_box.setStyleSheet('font-size: 14px;')  # Optional styling for text

        # Output box for displaying Groq response
        self.output_box2 = QTextEdit(self)
        self.output_box2.setGeometry(450, 770, 1315, 210)  # (x, y, width, height)
        self.output_box2.setReadOnly(True)  # Make the box read-only
        self.output_box2.setStyleSheet('font-size: 14px;')  # Optional styling for text

        # Placeholder for CSV file path
        self.csv_file_path = None


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.lower().endswith('.csv'):
                self.csv_file_path = file_path
                self.csvViewer.setText(f"Loaded File: {file_path}")
                self.process_button.setEnabled(True)
                event.accept()
            else:
                self.csvViewer.setText("Please drop a valid CSV file!")
                event.ignore()
        else:
            event.ignore()

    def process_csv(self):
        if self.csv_file_path:
            try:
                self.process_and_plot(
                    file_path=self.csv_file_path,
                    output_csv="predictions_output.csv",
                    plot_title="Comparison of Actual vs Predicted Energy"
                )
                self.output_box2.setText(f"Groq Response:\n{self.talkingWithGrq('C:\\Users\\Naween\\PycharmProjects\\ThermoLogic\\gui\\predictions_output.csv')}")
            except Exception as e:
                self.output_box.setText(f"Error processing file: {e}")

    def talkingWithGrq(self, file_path):
        # Read the contents of the file
        try:
            with open(file_path, "r") as f:
                csv_contents = f.read()
        except Exception as e:
            return f"Error reading the file: {e}"

        # Send the file contents to Groq
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You will receive a CSV file containing data. Analyze it and I want you to tell me 2 Main data points from me tell me how actuate the model is say stats, when in the day is our power plant most needed also give times frames, say this in 2 simple direct sentences different lines."},
                    {"role": "user", "content": f"The CSV data is:\n{csv_contents}"}
                ],
                model="llama-3.3-70b-versatile",
            )
            # Access the content properly based on the object's structure
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error fetching Groq response: {e}"

    def process_and_plot(self, file_path, output_csv, plot_title):
        # Load the CSV file
        data = pd.read_csv(file_path)

        # Rename columns to match those used during model training
        data = data.rename(columns={'Sunny Or Cloudy': 'Sunny_Or_Cloudy'})

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
        self.canvas.axes.clear()
        self.canvas.axes.plot(limited_actual_values, label='Actual Energy (First 75)', color='blue', linewidth=2)
        self.canvas.axes.plot(predictions, label='Predicted Energy (All)', linestyle='dotted', color='orange', linewidth=2)
        self.canvas.axes.set_title(plot_title, fontsize=10, pad=0)
        self.canvas.axes.set_xlabel('Time (Index)')
        self.canvas.axes.set_ylabel('Required Energy')
        self.canvas.axes.legend()
        self.canvas.axes.margins(x=0, y=0)
        self.canvas.axes.grid(True)
        self.canvas.draw()

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

        # Display the processed CSV data in the output box
        self.output_box.setText(f"Processed and plotted for: {file_path}\nPredictions saved to: {output_csv}")

    def plot_graph(self, df):
        self.canvas.axes.clear()
        self.canvas.axes.plot(df["Days"], df["Cost"], label="Electricity Cost")
        self.canvas.axes.set_title("Electricity Cost Over Time", fontsize=10, pad=0)
        self.canvas.axes.set_xlabel("Days")
        self.canvas.axes.set_ylabel("Cost (cents per kWh)")
        self.canvas.axes.legend()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PredictionApp()
    window.show()
    sys.exit(app.exec_())
