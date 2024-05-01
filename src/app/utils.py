from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QMouseEvent


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # Optional: For more granular mouse event tracking

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if item:
                item_rect = self.visualItemRect(item)
                checkbox_rect = QRect(item_rect.x(), item_rect.y(), 20, item_rect.height())
                if checkbox_rect.contains(event.pos()):
                    # Block signal to avoid any unwanted dialog or state changes
                    self.blockSignals(True)
                    item.setCheckState(Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked)
                    self.blockSignals(False)
                    event.accept()  # Consume the event to prevent further processing
                else:
                    super().mousePressEvent(event)
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        # This could be overridden similarly if there's an issue with release behavior
        super().mouseReleaseEvent(event)
