import sys
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableView,
    QVBoxLayout,
    QWidget,
)


class PandasModel(QAbstractTableModel):
    """A table model to interface a Qt view with a pandas DataFrame."""

    def __init__(self, dataframe: pd.DataFrame):
        super().__init__()
        self._df = dataframe.copy()
        self._highlight_rows: set[int] = set()  # row indices that should be highlighted

    # ----------------------------------------------------------
    # Required table model overrides
    # ----------------------------------------------------------
    def rowCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return len(self._df.index)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return len(self._df.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):  # noqa: N802
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role in (Qt.DisplayRole, Qt.EditRole):
            value = self._df.iat[row, col]
            # Convert NaNs to empty string for nicer display
            return "" if pd.isna(value) else str(value)

        if role == Qt.BackgroundRole and row in self._highlight_rows:
            # Light red background for highlighted rows
            return QBrush(Qt.red)

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):  # noqa: N802
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._df.columns[section])
        return str(self._df.index[section])

    # ----------------------------------------------------------
    # Highlight support
    # ----------------------------------------------------------
    def set_highlight_mask(self, mask: pd.Series | None):
        """Update which rows are highlighted given a boolean mask."""
        self.beginResetModel()
        if mask is None:
            self._highlight_rows = set()
        else:
            self._highlight_rows = set(mask[mask].index.tolist())
        self.endResetModel()

    # ----------------------------------------------------------
    # Convenience helpers
    # ----------------------------------------------------------
    @property
    def dataframe(self) -> pd.DataFrame:  # noqa: D401
        "Return a *copy* so original data stays immutable inside the model."  # noqa: D401
        return self._df.copy()

    @property
    def highlight_rows(self) -> set[int]:
        return self._highlight_rows


class ExcelAssistant(QMainWindow):
    """A lightweight Excel data viewer/analyser with row‑highlight filtering."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("💡 AI Excel Assistant — PySide Edition")
        self.resize(1100, 700)

        # ------------------------- widgets ------------------------- #
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # File‑bar
        file_bar = QHBoxLayout()
        layout.addLayout(file_bar)

        self.path_label = QLabel("No file loaded ⛔")
        self.path_label.setStyleSheet("font-weight: bold;")
        file_bar.addWidget(self.path_label, 1)

        open_btn = QPushButton("📂 Open Excel…")
        open_btn.clicked.connect(self.open_file)
        file_bar.addWidget(open_btn)

        export_btn = QPushButton("📤 Export with Highlights…")
        export_btn.clicked.connect(self.export_file)
        export_btn.setEnabled(False)
        file_bar.addWidget(export_btn)
        self._export_btn = export_btn

        # Filter‑bar
        filter_bar = QHBoxLayout()
        layout.addLayout(filter_bar)

        filter_bar.addWidget(QLabel("Highlight filter (pandas query):"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("e.g. `\u0060Hole Depth\u0060 > 5.8 and Status == 'Open'`")
        filter_bar.addWidget(self.filter_edit, 1)

        filter_btn = QPushButton("🎯 Apply / Clear")
        filter_btn.clicked.connect(self.apply_filter)
        filter_bar.addWidget(filter_btn)
        self._filter_btn = filter_btn

        # Table view
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_view, 1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # ------------------------- state ------------------------- #
        self.model: PandasModel | None = None

    # ==============================================================
    # File handling slots
    # ==============================================================
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel file",
            str(Path.home()),
            "Excel files (*.xlsx *.xls)",
        )
        if not path:
            return
        self.load_dataframe(Path(path))

    def load_dataframe(self, path: Path):
        try:
            df = pd.read_excel(path)
        except FileNotFoundError:
            QMessageBox.warning(self, "File Error", f"File not found: {path}")
            return
        except EmptyDataError:
            QMessageBox.warning(self, "File Error", "The selected file is empty.")
            return
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Load Error", str(exc))
            return

        self.model = PandasModel(df)
        self.table_view.setModel(self.model)
        self.path_label.setText(str(path))
        self.status_bar.showMessage("✅ Loaded successfully.")
        self._export_btn.setEnabled(True)
        self.filter_edit.setText("")

    # ==============================================================
    # Filter / highlight slots
    # ==============================================================
    def apply_filter(self):
        """Highlight rows matching the boolean expression (pandas query syntax)."""
        if not self.model:
            return

        expr = self.filter_edit.text().strip()
        if not expr:
            # Clear highlights
            self.model.set_highlight_mask(None)
            self.status_bar.showMessage("Highlights cleared.")
            return

        df = self.model.dataframe
        try:
            mask = df.query(expr, engine="python").index  # rows matching query
            highlight_mask = df.index.isin(mask)
            self.model.set_highlight_mask(pd.Series(highlight_mask, index=df.index))
            self.status_bar.showMessage(f"Highlighted {highlight_mask.sum()} rows 🔥")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(
                self,
                "Filter Error",
                "Could not apply filter. Check your syntax.\n\n" + str(exc),
            )

    # ==============================================================
    # Export
    # ==============================================================
    def export_file(self):
        if not self.model:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            str(Path.home() / "highlighted.xlsx"),
            "Excel files (*.xlsx)",
        )
        if not path:
            return

        df = self.model.dataframe
        highlight_rows = self.model.highlight_rows

        try:
            with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")
                workbook = writer.book
                worksheet = writer.sheets["Sheet1"]

                red_fmt = workbook.add_format({"bg_color": "#FFC7CE"})

                # Apply red background to each highlighted row (offset +1 for header)
                for row_idx in highlight_rows:
                    worksheet.set_row(row_idx + 1, None, red_fmt)

            self.status_bar.showMessage(f"✅ Exported to {path}")
            QMessageBox.information(self, "Export Complete", f"File saved to:\n{path}")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Export Error", str(exc))


# -------------------------- main -------------------------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelAssistant()
    window.show()
    sys.exit(app.exec())
