from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QMouseEvent


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Determine the item at the click position
            item = self.itemAt(event.pos())
            if item:
                # Calculate the checkbox area (assuming default size and padding)
                checkbox_rect = QRect(item.boundingRect().topLeft(), QSize(20, item.boundingRect().height()))
                if checkbox_rect.contains(event.pos()):
                    # If clicked on the checkbox, toggle the state
                    item.setCheckState(Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked)
                else:
                    # Otherwise, emit the item clicked signal manually
                    super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)