import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QTextEdit
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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

        # SECOND Matplotlib canvas for plotting
        self.canvas2 = MatplotlibCanvas(self)
        self.canvas2.setGeometry(450, 400, 1315, 350)  # (x, y, width, height)

        # Output box for displaying model output
        self.output_box = QTextEdit(self)
        self.output_box.setGeometry(20, 280, 400, 700)  # (x, y, width, height)
        self.output_box.setReadOnly(True)  # Make the box read-only
        self.output_box.setStyleSheet('font-size: 14px;')  # Optional styling for text

        # Output box for displaying model output
        self.output_box2 = QTextEdit(self)
        self.output_box2.setGeometry(450, 770, 1315, 210)  # (x, y, width, height)
        self.output_box2.setReadOnly(True)  # Make the box read-only
        self.output_box2.setStyleSheet('font-size: 14px;')  # Optional styling for text

        # Placeholder for CSV file path and processed data
        self.csv_file_path = None
        self.processed_data = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()

            if file_path.endswith('.csv'):
                self.csv_file_path = file_path
                self.csvViewer.setText(f"Loaded File: {file_path}")
                self.process_button.setEnabled(True)
                event.accept()
            else:
                self.csvViewer.setText("Please drop a valid CSV file!")
                event.ignore()

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

                # Display the model's output in the output box
                self.output_box.setText("Model Output:\n" + df.head().to_string())

                # Display the model's output in the output box
                self.output_box2.setText("Model Output:\n" + df.head().to_string())

                # Plot the data
                self.plot_graph(df)
            except Exception as e:
                self.csvViewer.setText(f"Error processing file: {e}")
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
