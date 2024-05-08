import logging

from PySide6.QtWidgets import QListWidget
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import QPoint, QRect
from PySide6.QtCore import Qt


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        logging.debug("CustomListWidget initialized with mouse tracking enabled.")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            point = event.position().toPoint()
            item = self.itemAt(point)
            if item:
                item_rect = self.visualItemRect(item)
                checkbox_rect = QRect(item_rect.x(), item_rect.y(), 20, item_rect.height())
                if checkbox_rect.contains(event.pos()):
                    # Directly toggle the checkbox state
                    self.blockSignals(True)
                    item.setCheckState(Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked)
                    self.blockSignals(False)
                    event.accept()
                else:
                    # Explicitly manage the selection state
                    if item.isSelected():
                        item.setSelected(False)
                    else:
                        item.setSelected(True)
                    super().mousePressEvent(event)  # Allow default processing
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        logging.debug(f"Mouse release event at: {event.position()}")
        super().mouseReleaseEvent(event)
