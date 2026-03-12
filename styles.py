APP_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #F8F9FA;
        color: #212529;
        font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
        font-size: 13px;
    }

    QLabel#title {
        font-size: 22px;
        font-weight: 700;
        color: #1A1A2E;
    }
    QLabel#subtitle {
        font-size: 11px;
        color: #6C757D;
        margin-bottom: 4px;
    }
    QLabel#sectionTitle {
        font-size: 13px;
        font-weight: 700;
        color: #343A40;
    }
    QLabel#colHeader {
        font-weight: 600;
        color: #495057;
        font-size: 12px;
    }
    QLabel#status {
        font-size: 11px;
        color: #6C757D;
    }

    QLabel#dotA { color: #E74C3C; font-size: 14px; }
    QLabel#dotB { color: #F39C12; font-size: 14px; }
    QLabel#dotC { color: #27AE60; font-size: 14px; }

    QGroupBox {
        font-weight: 600;
        font-size: 12px;
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        margin-top: 10px;
        padding: 10px 8px 8px 8px;
        background-color: #FFFFFF;
        color: #495057;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }

    QSpinBox, QDoubleSpinBox {
        border: 1px solid #CED4DA;
        border-radius: 5px;
        padding: 3px 5px;
        background: #FFFFFF;
        min-width: 72px;
        color: #212529;
    }
    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 1px solid #4A90D9;
        outline: none;
    }
    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        border: none;
        background: transparent;
    }

    QPushButton#runBtn {
        background-color: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 7px;
        padding: 11px;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }
    QPushButton#runBtn:hover {
        background-color: #1D4ED8;
    }
    QPushButton#runBtn:pressed {
        background-color: #1E40AF;
    }
    QPushButton#runBtn:disabled {
        background-color: #93C5FD;
        color: #DBEAFE;
    }

    QProgressBar#progress {
        border: none;
        border-radius: 2px;
        background: #E9ECEF;
    }
    QProgressBar#progress::chunk {
        background: #2563EB;
        border-radius: 2px;
    }

    QTableWidget#statsTable {
        border: 1px solid #DEE2E6;
        border-radius: 6px;
        background: #FFFFFF;
        gridline-color: #F1F3F5;
        selection-background-color: #EFF6FF;
    }
    QHeaderView::section {
        background-color: #F1F3F5;
        border: none;
        border-bottom: 1px solid #DEE2E6;
        padding: 7px 4px;
        font-weight: 600;
        font-size: 12px;
        color: #495057;
    }

    QFrame#separator {
        color: #DEE2E6;
        max-width: 1px;
    }
"""
