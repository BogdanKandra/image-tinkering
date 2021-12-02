import cv2
import numpy as np
import random
import math


def generate_voronoi_diagram(width, height, cells_count):
    """ better set indexing and minimum hypot pre calc """
    seeds_x_coords, seeds_y_coords, seeds_r_colours, seeds_g_colours, seeds_b_colours = [], [], [], [], []

    for i in range(cells_count):
        seeds_x_coords.append(random.randrange(height))
        seeds_y_coords.append(random.randrange(width))
        seeds_r_colours.append(random.randrange(256))
        seeds_g_colours.append(random.randrange(256))
        seeds_b_colours.append(random.randrange(256))

    voronoi = np.zeros((height, width, 3), dtype='uint8')
    maximum_distance = math.hypot(width - 1, height - 1)

    for y in range(width):
        for x in range(height):
            minimum_distance = maximum_distance
            closest_colour_index = -1

            for i in range(cells_count):
                distance = math.hypot(seeds_x_coords[i] - x, seeds_y_coords[i] - y)
                if distance < minimum_distance:
                    minimum_distance = distance
                    closest_colour_index = i

            voronoi[x, y, 0] = seeds_b_colours[closest_colour_index]
            voronoi[x, y, 1] = seeds_g_colours[closest_colour_index]
            voronoi[x, y, 2] = seeds_r_colours[closest_colour_index]

    return voronoi


def point_is_on_frontier(point, cell_points):
    """ Takes a point as an argument (as an (x, y) tuple) and decides whether the point is on the
    edge of the given cell or not; this is done by checking whether any of the surrounding points
    are still in the cell or not. The cell is specified by a list of points in the form of (x, y)
    tuples """
    if (point[0] + 1, point[1]) not in cell_points or (point[0], point[1] + 1) not in cell_points \
            or (point[0] - 1, point[1]) not in cell_points or (point[0], point[1] - 1) not in cell_points:
        return True
    else:
        return False


##### Kintsugi Filter test -- brute force detection, very slow
# width = 300
# height = 300
# num_cells = 15
#
# image = Image.new("RGB", (width, height))
# imgx, imgy = image.size
# nx, ny, nr, ng, nb = [], [], [], [], []
#
# points = {}
#
## Initialisation
# for i in range(num_cells):
#    nx.append(random.randrange(imgx))
#    ny.append(random.randrange(imgy))
#    nr.append(random.randrange(256))
#    ng.append(random.randrange(256))
#    nb.append(random.randrange(256))
#    points[i] = []
#
## Voronoi Diagram creation and building the points dictionary
# for y in range(imgy):
#    for x in range(imgx):
#        dmin = math.hypot(imgx-1, imgy-1) # Initialise with maximum distance
#        j = -1
#
#        # Compute the distances from the current point to each of the seeds / sites / generators
#        # Associate the point to the cell whose site is closest to the point
#        for i in range(num_cells):
#            d = math.hypot(nx[i]-x, ny[i]-y)
#            if d < dmin:
#                dmin = d
#                j = i
#        points[j].append((x, y))
#        image.putpixel((x, y), (nr[j], ng[j], nb[j]))
#
## Detecting the points on edges
# cells = [(i, len(points[i])) for i in range(num_cells)]
# cells.sort(key=lambda x: x[1])
#
# edge_points = {}
# for i in range(num_cells):
#    edge_points[i] = []
#
# for i in range(num_cells):
#    print('Cell #{}'.format(str(i)))
#    for point in points[i]:
#        if point_is_on_frontier(point, points[i]):
#            image.putpixel(point, (0, 0, 0))
#            edge_points[i].append(point)
#
# image.show()



image_path = '../webui/static/testinputs/rainbow.jpg'
img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)


# cv2.imshow('', )
# cv2.waitKey(0)
# cv2.destroyAllWindows()
