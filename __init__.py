# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geogridcut
                                 A QGIS plugin
 This plugin is able to split the various layers of a map into smaller chunks according to a configurable grid
                             -------------------
        begin                : 2016-10-23
        copyright            : (C) 2016 by Pedro Sousa
        email                : pedro.sousa1@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load geogridcut class from file geogridcut.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .geo_grid_cut import geogridcut
    return geogridcut(iface)
