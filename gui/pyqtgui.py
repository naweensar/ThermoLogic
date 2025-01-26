import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class CSVLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drag and drop a CSV file here \n\n')
        self.setStyleSheet('''
            QLabel {
                border: 4px dashed #aaa;
                font-size: 16px;
                padding: 10px;
            }
        ''')
        self.setFixedSize(400, 200)  # Fixed size for the drag-and-drop area

    def setText(self, text):
        super().setText(text)


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)


class CSVDragDropApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag-and-Drop CSV Processor and Graph Plotter")
        self.resize(1420, 800)
        self.setAcceptDrops(True)

        # Main layout
        self.main_layout = QVBoxLayout()

        # Drag-and-drop CSV viewer
        self.csvViewer = CSVLabel()
        self.main_layout.addWidget(self.csvViewer, alignment=Qt.AlignLeft | Qt.AlignTop)

        # Matplotlib canvas for plotting
        self.canvas = MatplotlibCanvas(self)
        self.main_layout.addWidget(self.canvas)
        self.main_layout.addSpacerItem(QSpacerItem(100, 0, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Process button
        self.process_button = QPushButton("Process CSV")
        self.process_button.setFixedWidth(400)
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_csv)
        self.main_layout.addWidget(self.process_button, alignment=Qt.AlignLeft)


        self.setLayout(self.main_layout)

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
                self.download_button.setEnabled(True)

                # Plot the data
                self.plot_graph(df)
            except Exception as e:
                self.csvViewer.setText(f"Error processing file: {e}")
        else:
            self.csvViewer.setText("No file selected!")

    def plot_graph(self, df):
        """Plots the graph from the processed CSV."""
        self.canvas.axes.clear()

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
                0.5, 0.5, "Not enough numeric columns to plot", fontsize=12, ha='center'
            )

        self.canvas.draw()

    def download_csv(self):
        if self.processed_data is not None:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Processed CSV", "", "CSV Files (*.csv)")
            if save_path:
                try:
                    self.processed_data.to_csv(save_path, index=False)
                    self.csvViewer.setText(f"Processed CSV saved successfully at: {save_path}")
                except Exception as e:
                    self.csvViewer.setText(f"Error saving file: {e}")
        else:
            self.csvViewer.setText("No processed data to save!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVDragDropApp()
    window.show()
    sys.exit(app.exec_())
