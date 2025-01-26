import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY", "")  # Ensure the environment variable is set
)

# Get the Groq response
try:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "just say 'russy is silly boy'."},
            {"role": "user", "content": "say it"}
        ],
        model="llama-3.3-70b-versatile",
    )
    groq_response = chat_completion["choices"][0]["message"]["content"]
except Exception as e:
    groq_response = f"Error fetching Groq response: {e}"


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        fig.tight_layout()  # Automatically adjust the plot to fit within the canvas
        super().__init__(fig)
        self.setParent(parent)


class CSVDragDropApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag-and-Drop CSV Processor with Custom Layout")
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
        self.canvas.setGeometry(450, 20, 1315, 350)  # (x, y, width, height)

        # Second Matplotlib canvas for plotting
        self.canvas2 = MatplotlibCanvas(self)
        self.canvas2.setGeometry(450, 400, 1315, 350)  # (x, y, width, height)

        # Output box for displaying model output
        self.output_box = QTextEdit(self)
        self.output_box.setGeometry(20, 280, 400, 700)  # (x, y, width, height)
        self.output_box.setReadOnly(True)  # Make the box read-only
        self.output_box.setStyleSheet('font-size: 14px;')  # Optional styling for text

        # Output box for displaying Groq response
        self.output_box2 = QTextEdit(self)
        self.output_box2.setGeometry(450, 770, 1315, 210)  # (x, y, width, height)
        self.output_box2.setReadOnly(True)  # Make the box read-only
        self.output_box2.setStyleSheet('font-size: 14px;')  # Optional styling for text

        # Display the Groq response in the second output box
        self.output_box2.setText(f"Groq Response:\n{groq_response}")

        # Placeholder for CSV file path and processed data
        self.csv_file_path = None
        self.processed_data = None

    def dragEnterEvent(self, event):
        print("Drag Enter Event Triggered")
        if event.mimeData().hasUrls():
            event.accept()
            print("Drag Accepted")
        else:
            event.ignore()
            print("Drag Ignored")

    def dragMoveEvent(self, event):
        print("Drag Move Event Triggered")
        if event.mimeData().hasUrls():
            event.accept()
            print("Drag Move Accepted")
        else:
            event.ignore()
            print("Drag Move Ignored")

    def dropEvent(self, event):
        print("Drop Event Triggered")
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            print(f"Dropped File Path: {file_path}")

            if file_path.lower().endswith('.csv'):
                self.csv_file_path = file_path
                self.csvViewer.setText(f"Loaded File: {file_path}")
                self.process_button.setEnabled(True)
                event.accept()
                print("CSV File Accepted")
            else:
                self.csvViewer.setText("Please drop a valid CSV file!")
                event.ignore()
                print("Invalid File Type")
        else:
            event.ignore()
            print("Drop Ignored")

    def process_csv(self):
        if self.csv_file_path:
            try:
                # Read the CSV file
                df = pd.read_csv(self.csv_file_path)

                # Example processing: Adding a "Processed" column
                df["Processed"] = range(1, len(df) + 1)
                self.processed_data = df

                # Display feedback
                self.csvViewer.setText("CSV processed successfully! Plotting data...")

                # Display the processed CSV data in the first output box
                self.output_box.setText("Processed CSV Data:\n" + df.head().to_string())

                # Plot the data
                self.plot_graph(df)
            except Exception as e:
                self.csvViewer.setText(f"Error processing file: {e}")
                print(f"Error: {e}")
        else:
            self.csvViewer.setText("No file selected!")

    def plot_graph(self, df):
        """Plots the graph from the processed CSV."""
        self.canvas.axes.clear()

        # Adjust layout to make borders smaller
        self.canvas.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

        # Plotting first two numeric columns (example)
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            self.canvas.axes.plot(df[x_col], df[y_col], label=f"{x_col} vs {y_col}")
            self.canvas.axes.set_xlabel(x_col)
            self.canvas.axes.set_ylabel(y_col)
            self.canvas.axes.set_title("CSV Data Plot")
            self.canvas.axes.legend()
        else:
            self.canvas.axes.text(
                0.5, 0.5, "Not enough numeric columns to plot",
                fontsize=12, ha='center', transform=self.canvas.axes.transAxes
            )

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVDragDropApp()
    window.show()
    sys.exit(app.exec_())
