import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


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
        self.setFixedSize(400, 200)  # Set the fixed size for the label

    def setText(self, text):
        super().setText(text)


class CSVDragDropApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag-and-Drop CSV Processor")
        self.resize(1420, 800)
        self.setAcceptDrops(True)

        # Main layout
        self.main_layout = QVBoxLayout()

        # Top-left layout for the drag-and-drop box
        self.top_left_layout = QHBoxLayout()
        self.csvViewer = CSVLabel()
        self.top_left_layout.addWidget(self.csvViewer, alignment=Qt.AlignLeft | Qt.AlignTop)
        self.main_layout.addLayout(self.top_left_layout)

        # Add buttons at the bottom of the GUI
        self.process_button = QPushButton("Process CSV")
        self.process_button.setEnabled(False)
        self.process_button.clicked.connect(self.process_csv)
        self.main_layout.addWidget(self.process_button)

        self.download_button = QPushButton("Download Processed CSV")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.download_csv)
        self.main_layout.addWidget(self.download_button)

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
                self.csvViewer.setText("CSV processed successfully! You can now download it.")
                self.download_button.setEnabled(True)
            except Exception as e:
                self.csvViewer.setText(f"Error processing file: {e}")
        else:
            self.csvViewer.setText("No file selected!")

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
