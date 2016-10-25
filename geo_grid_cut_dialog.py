# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geogridcutDialog
                                 A QGIS plugin
 This plugin is able to split the various layers of a map into smaller chunks according to a configurable grid
                             -------------------
        begin                : 2016-10-23
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Pedro Sousa
        email                : pedro.sousa1@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QFileDialog
from qgis.core import QgsRectangle,QgsFeature,QgsGeometry,QgsMapLayer,QgsMapLayerRegistry
from qgis.utils import iface

import os
from os.path import expanduser

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geo_grid_cut_dialog_base.ui'))


class geogridcutDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):

        """Constructor."""
        super(geogridcutDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # Extent

        self.radioButtonLayersExtent.toggled.connect(self.__toggleExtent)
        self.radioButtonCanvasExtent.toggled.connect(self.__toggleExtent)
        self.radioButtonCustomExtent.toggled.connect(self.__toggleExtent)

        extent = self.__getLayerBounds()
        self.__setExtentValues(extent)

        # Output

        self.lineEditOutputFolder.clear()
        self.pushButtonSelectOutputFolder.clicked.connect(self.__select_output_folder)


    def __toggleExtent(self, checked):
        if checked:

            custom = self.sender() is self.radioButtonCustomExtent

            self.spinMinLon.setEnabled(custom)
            self.labelMinLon.setEnabled(custom)

            self.spinMaxLon.setEnabled(custom)
            self.labelMaxLon.setEnabled(custom)

            self.spinMinLat.setEnabled(custom)
            self.labelMinLat.setEnabled(custom)

            self.spinMaxLat.setEnabled(custom)
            self.labelMaxLat.setEnabled(custom)


            if self.sender() is self.radioButtonLayersExtent:
                extent = self.__getLayerBounds()
                self.__setExtentValues(extent)

            elif self.sender() is self.radioButtonCanvasExtent:
                extent = iface.mapCanvas().extent()
                self.__setExtentValues(extent)

    def __setExtentValues(self, extent):

        self.spinMinLon.setValue(extent.xMinimum())
        self.spinMaxLon.setValue(extent.xMaximum())
        self.spinMinLat.setValue(extent.yMinimum())
        self.spinMaxLat.setValue(extent.yMaximum())

    def __select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self,"Open a folder",expanduser("~"),QFileDialog.ShowDirsOnly)
        self.lineEditOutputFolder.setText(folder)

    def __getLayerBounds(self):

        minLon = 180
        maxLon = -180
        minLat = 90
        maxLat = -90

        # Calculate current max extent
        for mapLayer in iface.mapCanvas().layers():

            layerExtent = mapLayer.extent()
            if layerExtent.xMinimum() < minLon:
                minLon = layerExtent.xMinimum()

            if layerExtent.xMaximum() > maxLon:
                maxLon = layerExtent.xMaximum()

            if layerExtent.yMinimum() < minLat:
                minLat = layerExtent.yMinimum()

            if layerExtent.yMaximum() > maxLat:
                maxLat = layerExtent.yMaximum()

        return QgsRectangle(minLon,minLat,maxLon,maxLat)
