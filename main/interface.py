################
# Author: Kaan Eraslan <kaaneraslan@gmail.com>
# Purpose: Draw polygons on images using a gui and obtain coordinates of the
# polygon.
# Usage: Just lunch the program. Click on draw mode. Click on the picture to put
# connected dots.

# Package Declaration

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from interfaceBrut import Ui_MainWindow as BrutInterface
import os
import sys
import itertools

# End of Package Declaration

class DrawInterfaceInitial(BrutInterface):
    """Initial interface for main window setup"""
    # Constructor
    #
    def __init__(self):
        # The Main Window as it is designed by
        # Qt Designer.
        self.main_window = Qt.QMainWindow()
        super().setupUi(self.main_window)
        #
class ImageData(object):
    """Initializes the image with additional attributes"""
    # Constructor
    def __init__(self):
        #
        self.image_import_path = ""
        self.image_export_path = ""
        # for working with opencv
        self.image_qt_index = Qt.QModelIndex() #
        # for accessing image in functions
        self.image_qt = QtGui.QImage() #
        # for storing the unprocessed image in qt form
        self.image_qt_modified = QtGui.QImage() #
    #
    #
    def _read_image_from_path_qt(self):
        """Read the image from import path"""
        if len(self.image_import_path) == 0:
            raise ValueError("Image import path has not been assigned")
        image_qt = QtGui.QImage(self.image_import_path)
        #
        return image_qt
    #

class DrawerInterface(DrawInterfaceInitial):
    "Final façade of the drawer"""
    # Constructor
    def __init__(self):
        super().__init__()
        #
        #
        # ---- Main Window Events ---------
        #
        self.main_window.setWindowTitle("PSL - Chart Polygon Drawer Interface")
        self.main_window.setWindowIcon(QtGui.QIcon("icons/logo-psl.png"))
        self.main_window.closeEvent = self._closeEvent
        #
        # ---- Central Widget -------------
        #
        self.centralwidget.setMinimumSize(640,480)

        # ---- Image Operations -----------
        #
        self.graphicsScene = QtWidgets.QGraphicsScene()
        self.graphicsScene.mousePressEvent = self.select_pixel
        self.raw_image = ImageData()
        self.pixmap_image = QtGui.QPixmap()
        self.draw_mode = False
        self.pixel_coordinates = []
        #
        # ---- File Directory -------------
        #
        self.image_dict = {} # Stores the images initiated as ImageData
        #
        # Buttons
        #
        self.import_images.clicked.connect(self._browseFolder)
        self.import_images.setShortcut("ctrl+o")
        self.remove_image.clicked.connect(self._remove_image)
        #
        # Load Image ------------------
        self.load_image.clicked.connect(self._get_image)
        #
        self.drawMode_switch.clicked.connect(self.draw_mode_switch)

    # #### Standard Gui Elements ####
    #
    def _browseFolder(self):
        """
        Imports the images to the image list
        from the selected images in the file dialog
        """
        #
        self.image_list.clear()
        # Clears the image in the image list section
        #
        #directory = QFileDialog.getExistingDirectory(self, "Pick Images")
        file_directory = QtWidgets.QFileDialog.getOpenFileNames(
            self.centralwidget,
            "Pick Images",
            "",
            "Images (*.jpg *.png)")
        # Opens a file browsing window, with title pick images.
        #
        if file_directory:
            for file_name in file_directory[0]:
                image = ImageData()
                file_item = QtWidgets.QListWidgetItem(self.image_list)
                image.image_import_path = file_name
                file_item.setText(os.path.basename(file_name))
                image.image_qt_index = self.image_list.indexFromItem(file_item)
                print(image.image_import_path)
                self.image_dict[image.image_qt_index] = image
                self.image_list.sortItems()
    #
    def _remove_image(self):
        """
        Removes selected images in the Widgetlist
        """
        #
        selected_images = self.image_list.selectedItems()
        # Gives the selected images in the image list
        #
        for image in selected_images:
            item_row = self.image_list.row(image)
            # Gives the image row a variable
            self.image_list.takeItem(item_row)
            # Pops the image row from the list.
            #
        #
        #self.image_GraphicScene.clear()
        # Clears the scene
    #
    def _get_image(self):
        """
        gets the selected image from the widget list
        and passes it to the image_cv_read
        """
        #
        if self.graphicsScene.isActive():
            self.graphicsScene.clear()
            # If the scene is occupied the newly
            # selected image clears the old one.
        if len(self.image_list.selectedItems()) > 1:
            # Checks to see if there are images selected in the
            # image list.
            self.statusbar.showMessage("Please select only 1 image for loading")
            return
        elif len(self.image_list.selectedItems()) < 1:
            self.statusbar.showMessage("Please select an image for loading")
            return
        #
        elif len(self.image_list.selectedItems()) == 1:
            selected_image = self.image_list.selectedItems()[0]
            selected_image_index = self.image_list.indexFromItem(
                selected_image
            )
            self.raw_image = self.image_dict[selected_image_index]
            self.raw_image.image_qt = self.raw_image._read_image_from_path_qt()
            qt_image = self.raw_image.image_qt
            print("I GOT THE IMAGE")
            self.view_image(qt_image)
        #
        return
    #
    def view_image(self, qt_image):
        """Display the image in Scene"""
        # Scale qt_image
        self.pixmap_image = QtGui.QPixmap(qt_image)
        width_px, height_px = (self.pixmap_image.width(),
                               self.pixmap_image.height())
        self.graphicsScene.setSceneRect(0,0, width_px, height_px)
        self.graphicsScene.addPixmap(self.pixmap_image)
        self.image_viewer.setSceneRect(0, # item position x
                                       0, # item position y
                                       width_px, height_px)
        self.image_viewer.setScene(self.graphicsScene)
        self.image_viewer.show()
        #
        return
        #
        #
        #
    def select_pixel(self, click_event):
        """Select a point in scene item and get its coordinates"""
        # TODO buna bak
        #
        add_position = click_event.pos()
        self.pixel_coordinates.append(add_position)
        if not self.draw_mode == True:
            self.graphicsScene.clear()
            return
        self.draw_polygons()
        #
        return
    #
    def draw_polygons(self):
        """Draw the polygons based on the coordinates"""
        # TODO Noktayı gördüm gerisi daha yok.
        color = QtGui.QColor("cyan")
        #painterClass.setPen(color)
        draw_pen = QtGui.QPen()
        draw_pen.setColor(color)
        draw_pen.setWidth(400)
        print("COLOR SET!\n")
        if len(self.pixel_coordinates) < 4:
            return
        #
        polygon_points = [(self.pixel_coordinates[i],
                           self.pixel_coordinates[i+1]) for i in range(len(
                               self.pixel_coordinates)) if i+1 < len(
                                   self.pixel_coordinates)]
        print("POLYGON Points!\n")
        #
        polygon_points.append((self.pixel_coordinates[-1],
                              self.pixel_coordinates[0]))
        #
        for point_tuple in polygon_points:
            print("POLYGON DRAW!\n")
            line = QtCore.QLineF(point_tuple[0], point_tuple[1])
            self.graphicsScene.addLine(line, draw_pen)
            #painterClass.drawLine(line)
        #
        return

    def draw_mode_switch(self):
        """Switch draw mode on or off"""
        if self.draw_mode == True:
            self.draw_mode = False
            self.statusbar.showMessage("Draw Mode off")
        else:
            self.draw_mode = True
            self.statusbar.showMessage("Draw Mode On!")
        return
        #
    def _closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self.main_window,'Message',
            "Are you sure to quit?", QtWidgets.QMessageBox.Yes | 
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            #
    def showInterface(self):
        """
        start the interface
        """
        #
        self.main_window.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = DrawerInterface()
    form.showInterface()
    sys.exit(app.exec_())
    #
    #


if __name__ == "__main__":
    main()



