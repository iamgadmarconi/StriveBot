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
                    # Toggling the checkbox state
                    item.setCheckState(Qt.Checked if item.checkState() == Qt.Unchecked else Qt.Unchecked)
                    
                    # Prevent the event from propagating to avoid unwanted behavior
                    event.accept()
                else:
                    # For clicks outside the checkbox area, allow normal behavior
                    super().mousePressEvent(event)
            else:
                # Clicks not on items should also behave normally
                super().mousePressEvent(event)
        else:
            # Handle other mouse buttons normally
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        # This could be overridden similarly if there's an issue with release behavior
        super().mouseReleaseEvent(event)
