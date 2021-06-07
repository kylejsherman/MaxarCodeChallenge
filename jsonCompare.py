from shapely.geometry import Polygon

def polygon_intersect(event, context) -> bool:
    """
    Function to deterine if two GeoJSON Polygons intersect
    :param poly_dict: A dictionary containg the two Polygon objects
    :type poly_dict: dict
    ...
    :return: A boolean indicating whether the polygons overlap
    :rtype: bool
    """
    
    poly_dict = event
    
    poly1_coords = poly_dict['features'][0]['geometry']['coordinates'][0]
    poly2_coords = poly_dict['features'][1]['geometry']['coordinates'][0]
    poly1 = Polygon([(coord[0], coord[1]) for coord in poly1_coords])
    poly2 = Polygon([(coord[0], coord[1]) for coord in poly2_coords])
    return {'PolygonsIntersect': not(poly1.intersection(poly2).is_empty)}
