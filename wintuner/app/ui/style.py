"""Dark Windows-style theme for WinTuner."""

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background: #2d2d2d;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #555;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* Sidebar */
#sidebar {
    background-color: #252526;
    border-right: 1px solid #3c3c3c;
}
#sidebar QPushButton {
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 4px;
    background: transparent;
    color: #cccccc;
}
#sidebar QPushButton:hover {
    background-color: #2a2d2e;
}
#sidebar QPushButton[active="true"] {
    background-color: #094771;
    color: #ffffff;
}

/* Top search bar */
#searchBar {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px 10px;
    color: #e0e0e0;
}

/* Status bar */
QStatusBar {
    background-color: #007acc;
    color: #ffffff;
    font-size: 12px;
}

/* Cards */
.card {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 12px;
}

/* Buttons */
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #1177bb;
}
QPushButton:pressed {
    background-color: #094771;
}
QPushButton:disabled {
    background-color: #3c3c3c;
    color: #888;
}
QPushButton.secondary {
    background-color: #3c3c3c;
}
QPushButton.secondary:hover {
    background-color: #505050;
}
QPushButton.danger {
    background-color: #a1260d;
}
QPushButton.danger:hover {
    background-color: #c72e0f;
}

/* Labels */
QLabel.title {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
}
QLabel.subtitle {
    font-size: 14px;
    color: #aaaaaa;
}
QLabel.warning {
    color: #cca700;
    background-color: #3a3a00;
    border: 1px solid #665500;
    border-radius: 4px;
    padding: 8px;
}
QLabel.badge-low {
    color: #4ec9b0;
    background-color: #1a3a34;
    border-radius: 3px;
    padding: 2px 6px;
    font-size: 11px;
}
QLabel.badge-medium {
    color: #dcdcaa;
    background-color: #3a3a1a;
    border-radius: 3px;
    padding: 2px 6px;
    font-size: 11px;
}
QLabel.badge-high {
    color: #f48771;
    background-color: #3a1a1a;
    border-radius: 3px;
    padding: 2px 6px;
    font-size: 11px;
}

QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555;
    border-radius: 3px;
    background: #2d2d2d;
}
QCheckBox::indicator:checked {
    background: #0e639c;
    border-color: #0e639c;
}

QListWidget {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    outline: none;
}
QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #3c3c3c;
}
QListWidget::item:selected {
    background-color: #094771;
}
QListWidget::item:hover {
    background-color: #2a2d2e;
}

QComboBox {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    selection-background-color: #094771;
}

QDialog {
    background-color: #1e1e1e;
}
QGroupBox {
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 16px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    padding: 0 6px;
}
"""
