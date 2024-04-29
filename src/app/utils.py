from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QMouseEvent


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                # Get the rectangle of the visual part of the list item
                item_rect = self.visualItemRect(item)
                # Define a small rectangle at the start of the item where the checkbox is likely to be
                checkbox_rect = QRect(item_rect.x(), item_rect.y(), 20, item_rect.height())
                
                if checkbox_rect.contains(event.pos()):
                    # Toggle the checkbox state without affecting other interactions
                    item.setCheckState(Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked)
                else:
                    # If not clicking on the checkbox, allow normal item selection behavior
                    super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
