# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geogridcut
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon,QFileDialog
from qgis.core import QgsProject,QgsFeature,QgsGeometry,QgsMapLayer,QgsMapLayerRegistry,QgsVectorFileWriter,QgsCoordinateReferenceSystem,QgsRasterPipe,QgsRasterFileWriter
from qgis.utils import iface
from os.path import expanduser


# Initialize Qt resources from file resources.py
import resources

# Import the code for the dialog
from geo_grid_cut_dialog import geogridcutDialog
import os.path
import os
import processing
import shutil

class geogridcut:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'geogridcut_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Geo Grid Cut')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'geogridcut')
        self.toolbar.setObjectName(u'geogridcut')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('geogridcut', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = geogridcutDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/geogridcut/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Geo Grid Cut'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Geo Grid Cut'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.cut()


    def cut(self):

        #######  PARAMS  #######

        originX = -15
        originY = 60

        stepX = 10
        stepY = 10

        width =  30  #360
        height = 30  #180

        iterationsX = width / stepX
        iterationsY = height / stepY

        buffer = 1

        j = 0
        i = 0

        targetBaseFolder = "/Users/pedrosousa/geo" #self.dlg.lineEditOutputFolder.text()

        #######  MAIN   #######

        for i in xrange(0,iterationsX):

            for j in xrange(0,iterationsY):

                tileId = str(i) + "_" + str(j)

                folder = targetBaseFolder + "/" + tileId

                if not os.path.exists(folder):
                    os.makedirs(folder)

                #shutil.copy2(QgsProject.instance().homePath() + "/manifest.xml", folder)

                print "Processing tile " + tileId

                minX = (originX + i * stepX) - buffer
                maxY = (originY - j * stepY) + buffer
                maxX = (minX + stepX) + buffer
                minY = (maxY - stepY) -  buffer

                wkt = "POLYGON ((" + str(minX) + " " + str(maxY)+ ", " + str(maxX) + " " + str(maxY) + ", " + str(maxX) + " " + str(minY) + ", " + str(minX) + " " + str(minY) + ", " + str(minX) + " " + str(maxY) + "))"

                tileLayer = iface.addVectorLayer("Polygon?crs=epsg:4326", "tile", "memory")
                provider = tileLayer.dataProvider()
                tileFeature = QgsFeature()

                tileFeature.setGeometry(QgsGeometry.fromWkt(wkt))
                provider.addFeatures( [ tileFeature ] )

                for mapLayer in iface.mapCanvas().layers():

                    layerType = mapLayer.type()
                    layerName = mapLayer.name()
                    intersectionName = "intersection_" + layerName + "_" + tileId

                    #vector layers and raster layers are processed differently
                    if layerType == QgsMapLayer.VectorLayer and layerName != "tile":

                        #Calculate the intersection between the specific grid rectangle and the layer
                        intersection = processing.runalg("qgis:intersection", mapLayer, tileLayer, None)

                        iface.addVectorLayer(intersection.get("OUTPUT"),intersectionName,"ogr")

                        #create a shapefile for this new intersection layer on the filesystem. A separate folder will be added for each square
                        intersectionLayer = QgsMapLayerRegistry.instance().mapLayersByName(intersectionName)[0]
                        QgsVectorFileWriter.writeAsVectorFormat(intersectionLayer, folder + "/" + layerName + ".shp", "utf-8", QgsCoordinateReferenceSystem(4326), "ESRI Shapefile")

                        #remove the intersection layer from the canvas
                        QgsMapLayerRegistry.instance().removeMapLayers( [intersectionLayer.id()] )

                    elif layerType == QgsMapLayer.RasterLayer:

                        #Calculate the intersection between the specific grid rectangle and the raster layer
                        intersection = processing.runalg('saga:clipgridwithpolygon', mapLayer, tileLayer, None)

                        #add the intersection to the map
                        iface.addRasterLayer(intersection.get("OUTPUT"), intersectionName)

                        #export to file
                        intersectionLayer = QgsMapLayerRegistry.instance().mapLayersByName(intersectionName)[0]

                        pipe = QgsRasterPipe()
                        provider = intersectionLayer.dataProvider()
                        pipe.set(provider.clone())

                        rasterWriter = QgsRasterFileWriter(folder + "/" + layerName + ".tif")
                        xSize = provider.xSize()
                        ySize = provider.ySize()

                        rasterWriter.writeRaster(pipe, xSize, ySize, provider.extent(), provider.crs())

                        #remove the intersection layer from the canvas
                        QgsMapLayerRegistry.instance().removeMapLayers( [intersectionLayer.id()] )

                    else:
                        print "layer type not supported"

                #remove the temporary tile
                QgsMapLayerRegistry.instance().removeMapLayers( [tileLayer.id()] )

                #create boundaries file
                text_file = open(folder + "/boundaries.txt", "w")
                text_file.write(str(minX) + " " + str(maxX) + " " + str(minY) + " " + str(maxY))
                text_file.close()

                #create zip file
                shutil.make_archive( targetBaseFolder + "/" + tileId, 'zip', folder)

                #remove temporary folder
                shutil.rmtree(folder)
