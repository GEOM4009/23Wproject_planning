import numpy as np
import shapely.geometry as geom

def hex_grid(hex_area, grid_area, center_lon, center_lat):
    # calculate the side length of each hexagon from the area
    hex_side = np.sqrt(hex_area / (3 * np.sqrt(3) / 2))

    # calculate the number of hexagons in each row and column
    n_rows = int(np.sqrt(grid_area / hex_area))
    n_cols = int(np.sqrt(grid_area / hex_area))

    # calculate the total number of hexagons
    n_hexagons = n_rows * n_cols

    # create an empty list to store the hexagons
    hexagons = []

    # loop over the rows and columns
    for i in range(n_rows):
        for j in range(n_cols):
            # calculate the center point of the hexagon
            x = center_lon + (j * hex_side * 3/2)
            y = center_lat + (i * hex_side * np.sqrt(3))
            if i % 2 == 1:
                x += hex_side * 3/2
            center = (x, y)

            # create a list of vertices for the hexagon
            vertices = []
            for k in range(6):
                angle = 2 * np.pi * (2/6 + k/6)
                x = center[0] + hex_side * np.cos(angle)
                y = center[1] + hex_side * np.sin(angle)
                vertices.append((x, y))

            # create a Shapely polygon from the vertices
            hexagon = geom.Polygon(vertices)

            # add the hexagon to the list
            hexagons.append(hexagon)

    # return the list of hexagons
    return hexagons
