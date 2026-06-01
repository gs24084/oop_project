def window_style():
    return """
        QMainWindow {
            background-color: #f5f6f8;
        }
        QPushButton {
            padding: 7px 10px;
            border: 1px solid #d0d0d0;
            background-color: #ffffff;
            border-radius: 6px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #eef3ff;
            border: 1px solid #9bb8ff;
        }
        QLabel {
            color: #222222;
            font-size: 13px;
        }
    """


def panel_style():
    return """
        QFrame {
            background-color: #ffffff;
            border: 1px solid #dddddd;
            border-radius: 8px;
        }
    """


def title_style():
    return """
        QLabel {
            font-size: 15px;
            font-weight: bold;
            padding: 4px;
            border: none;
        }
    """


def tab_style():
    return """
        QTabWidget::pane {
            border: 1px solid #dddddd;
            border-radius: 6px;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background-color: #f1f2f4;
            border: 1px solid #d0d0d0;
            padding: 7px 13px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }
        QTabBar::tab:selected {
            background-color: #ffffff;
            font-weight: bold;
        }
        QTabBar::tab:hover {
            background-color: #eef3ff;
        }
    """


def editor_style():
    return """
        QPlainTextEdit {
            font-family: Consolas;
            font-size: 15px;
            background-color: #ffffff;
            color: #111111;
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 8px;
        }
    """


def console_style():
    return """
        QTextEdit {
            font-family: Consolas;
            font-size: 14px;
            background-color: #fbfbfb;
            color: #111111;
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 8px;
        }
    """


def small_box_style():
    return """
        QTextEdit {
            font-family: Consolas;
            font-size: 13px;
            background-color: #fbfbfb;
            color: #111111;
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 6px;
        }
    """


def toolbar_style():
    return """
        QToolBar {
            background-color: #ffffff;
            border-bottom: 1px solid #dddddd;
            spacing: 6px;
            padding: 6px;
        }
        QPushButton {
            padding: 6px 13px;
            border: 1px solid #d0d0d0;
            background-color: #ffffff;
            border-radius: 6px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #eef3ff;
            border: 1px solid #9bb8ff;
        }
    """


def floating_header_style():
    return """
        QLabel {
            background-color: #f1f2f4;
            border: 1px solid #d0d0d0;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding-left: 10px;
            font-weight: bold;
        }
    """


def floating_container_style():
    return """
        QFrame {
            background-color: #ffffff;
            border: 1px solid #dddddd;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        }
    """