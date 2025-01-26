import sys
import os
import pandas as pd
import joblib
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit, QSlider
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY", "")  # Ensure the environment variable is set
)

# Load the pre-trained Gradient Boosting model
model = joblib.load('C:\\Users\\ZainP\\Documents\\Qhacks\\ThermoLogic\\models\\OntarioModel.pkl')  # Update with the correct file path to the model


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(facecolor="#2C2C2C")  # Set the figure background to greyish
        self.axes = fig.add_subplot(111)
        self.axes.set_facecolor("#383838")  # Set the plot area background to a darker grey
        fig.tight_layout()  # Automatically adjust the plot to fit within the canvas
        super().__init__(fig)
        self.setParent(parent)

    def apply_dark_mode(self):
        """Apply dark mode settings to the plot."""
        self.axes.title.set_color("#FFFFFF")  # Set title text color
        self.axes.xaxis.label.set_color("#FFFFFF")  # Set x-axis label color
        self.axes.yaxis.label.set_color("#FFFFFF")  # Set y-axis label color
        self.tick_params(axis='x', colors="#FFFFFF")  # Set x-axis tick colors
        self.tick_params(axis='y', colors="#FFFFFF")  # Set y-axis tick colors
        self.axes.grid(color="#444444", linestyle="--", linewidth=0.5)  # Set grid color and style
        self.figure.patch.set_facecolor("#2C2C2C")  # Ensure figure background is greyish
        self.draw()


class PredictionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Energy Prediction with CSV Drag-and-Drop")
        self.setGeometry(100, 100, 1600, 800)  # Set the window size and position
        self.setAcceptDrops(True)  # Enable drag-and-drop functionality

        # Apply a greyish background and styling for the entire application
        self.setStyleSheet('''
            QWidget {
                background-color: #111111;  /* Greyish background */
                color: #FFFFFF;            /* White text color */
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                border: 4px dashed #444444;
                font-size: 16px;
                color: #DDDDDD;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #444444;
                color: #FFFFFF;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QTextEdit, QLineEdit {
                background-color: #383838;
                color: #FFFFFF;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 8px;
            }
        ''')

        # Logo
        self.logo = QLabel(self)
        self.logo.setGeometry(120, 40, 200, 200)
        pixmap = QPixmap("C:\\Users\\ZainP\\Documents\\Qhacks\\ThermoLogic\\images\\logo.png")
        self.logo.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Drag-and-drop CSV viewer
        self.csvViewer = QLabel(self)
        self.csvViewer.setText('\n\n Drag and drop a CSV file here \n\n')
        self.csvViewer.setAlignment(Qt.AlignCenter)
        self.csvViewer.setGeometry(20, 270, 400, 200)

        # Process button
        self.process_button = QPushButton("Process CSV", self)
        self.process_button.setGeometry(20, 500, 400, 40)
        self.process_button.setEnabled(False)
        self.process_button.setStyleSheet('''
            QPushButton {
                background-color: #006400;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        ''')
        self.process_button.clicked.connect(self.process_csv)

        # Matplotlib canvas for plotting
        self.canvas = MatplotlibCanvas(self)
        self.canvas.setGeometry(450, 20, 1100, 300)

        # Second Matplotlib canvas for plotting the city data
        self.city_canvas = MatplotlibCanvas(self)
        self.city_canvas.setGeometry(450, 340, 1100, 300)

        # Output box for displaying model output
        self.output_box = QTextEdit(self)
        self.output_box.setGeometry(20, 550, 400, 200)
        self.output_box.setReadOnly(True)

        # Output box for displaying Groq response
        self.output_box2 = QTextEdit(self)
        self.output_box2.setGeometry(450, 680, 1100, 100)
        self.output_box2.setReadOnly(True)

        # Slider for adjusting a parameter
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(550, 650, 400, 30)
        self.slider.setMinimum(0)
        self.slider.setMaximum(10)
        self.slider.setValue(5)  # Initial value
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.update_slider_label)

        # Label for displaying slider value
        self.slider_label = QLabel(f"Slider Value: {self.slider.value()}", self)
        self.slider_label.setGeometry(-960, -650, -200, -30)
        self.slider_label.setStyleSheet("font-size: 8px; color: #FFFFFF;")



        # Placeholder for CSV file path
        self.csv_file_path = None

    

    def update_slider_label(self):
        """Update the slider label when the slider value changes."""
        value = self.slider.value()
        print(self.slider.value())
        self.slider_label.setText(f"Slider Value: {value}")

    def plot_efficiency_comparison(self):
        """
        Plot the `eff` and `effnew` values from the hardcoded CSV file on `self.city_canvas`.
        """
        # Path to the hardcoded CSV file
        csv_file_path = r'C:\Users\ZainP\Documents\Qhacks\ThermoLogic\models\factorydata.csv'

        # Load the CSV file
        data = pd.read_csv(csv_file_path)

        # Extract `eff` and `effnew` columns
        eff = data['eff']
        effnew = data['effnew']


        self.city_canvas.axes.clear()
        self.city_canvas.axes.plot(eff, label='Old Eff', color='Green', linewidth=2)
        self.city_canvas.axes.plot(effnew, label='New Eff', color="Yellow", linewidth=2)
        self.city_canvas.axes.set_title("Eff", fontsize=10, pad=0, color="#EEE")
        self.city_canvas.axes.set_ylim(.5, 1)
        self.city_canvas.axes.set_xlabel('Increments', color="#CCC")
        self.city_canvas.axes.set_ylabel('Eff Perent', color="#CCC")
        self.city_canvas.axes.legend()
        self.city_canvas.axes.grid(True)
        self.city_canvas.draw()




    def process_and_plot(self, file_path, output_csv, plot_title):
        # Load the CSV file
        data = pd.read_csv(file_path)

        # Plot the data with ticks and labels styled for dark mode
        self.canvas.axes.clear()
        self.canvas.axes.plot(data['Days'], data['Cost'], label='Cost Over Time', color='Grey', linewidth=2)
        self.canvas.axes.set_title(plot_title, fontsize=10, pad=10, color="#FFFFFF")
        self.canvas.axes.set_xlabel('Days', fontsize=10, color="#FFFFFF")
        self.canvas.axes.set_ylabel('Cost (cents per kWh)', fontsize=10, color="#FFFFFF")
        self.canvas.tick_params(axis='x', colors="#FFFFFF")
        self.canvas.tick_params(axis='y', colors="#FFFFFF")
        self.canvas.axes.grid(color="#444444", linestyle="--", linewidth=0.5)
        self.canvas.axes.legend(facecolor="#383838", edgecolor="#555555", fontsize=9)
        self.canvas.apply_dark_mode()

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
                # Process and plot the first graph
                self.process_and_plot(
                    file_path=self.csv_file_path,
                    output_csv="predictions_output.csv",
                    plot_title="Comparison of Actual vs Predicted Energy"
                )

                # Plot the efficiency comparison graph
                self.plot_efficiency_comparison()

                # Optional: Update the output box with Groq response
                file_path = r'C:\Users\ZainP\Documents\Qhacks\ThermoLogic\predictions_output.csv'
                self.output_box2.setText(f"Groq Response:\n{self.talkingWithGrq(file_path)}")
            except Exception as e:
                self.output_box.setText(f"Error processing file: {e}")


    def talkingWithGrq(self, filepath):
        # Read the contents of the file
        try:
            with open(filepath, "r") as f:
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
        self.canvas.axes.plot(predictions, label='Predicted Energy (All)', color='Green', linewidth=2)
        self.canvas.axes.plot(limited_actual_values, label='Actual Energy (First 75)', linestyle='dotted' , color="White", linewidth=2)
        self.canvas.axes.set_title(plot_title, fontsize=10, pad=0, color="#EEE")
        self.canvas.axes.set_xlabel('Time (Index)', color="#CCC")
        self.canvas.axes.set_ylabel('Required Energy', color="#CCC")
        self.canvas.axes.legend()
        self.canvas.axes.grid(True)
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PredictionApp()
    window.show()
    sys.exit(app.exec_())
