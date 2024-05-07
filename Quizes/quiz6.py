import arcpy

def calculatePercentAreaOfPolygonAInPolygonB(input_geodatabase, fcPolygonA, fcPolygonB, idFieldPolygonB):

    # Defining workspace
    arcpy.env.workspace = input_geodatabase

    # Check if the feature classes exist in the geodatabase
    featureclasses = arcpy.ListFeatureClasses()
    if fcPolygonA not in featureclasses:
        raise Exception(f"{fcPolygonA} not found in the geodatabase")
    if fcPolygonB not in featureclasses:
        raise Exception(f"{fcPolygonB} not found in the geodatabase")

    # Calculate area for feature class B (larger area)
    try:
        arcpy.AddField_management(fcPolygonB, "Area_sqmi", "DOUBLE")
        arcpy.CalculateGeometryAttributes_management(fcPolygonB, [["Area_sqmi", "AREA_GEODESIC"]], "MILES_US")
    except Exception as e:
        print(f"Area for {fcPolygonB} cannot be calculated. Error: {e}")

    # Make an intersection layer
    try:
        intersect_fc = "intersect_fc"
        arcpy.Intersect_analysis([fcPolygonB, fcPolygonA], intersect_fc)
    except Exception as e:
        print(f"Intersection cannot be calculated. Error: {e}")

    # calculate intersected area for each intersected polygon
    intersect_area = "intersect_area_sqmi"
    try:
        arcpy.AddField_management(intersect_fc, intersect_area, "DOUBLE")
        arcpy.CalculateGeometryAttributes_management(intersect_fc, [[intersect_area, "AREA_GEODESIC"]], "MILES_US")
    except Exception as e:
        print(f"Area for intersect cannot be calculated. Error: {e}")

    ## Calculate sum of areas for all polygons from polygonsA within each polygon in PolygonB
    # create a dictionary to store the sum of intersected areas for each polygon in PolygonB and update it based on idFieldPolygonB
    intesected_dict = {}
    with arcpy.da.SearchCursor(intersect_fc, ["{}".format(idFieldPolygonB), "{}".format(intersect_area)]) as cursor:
        for row in cursor:
            try:
                joinid = row[0]
                if joinid in intesected_dict.keys():
                    intesected_dict[joinid] += row[1]
                else:
                    intesected_dict[joinid] = row[1]
            except Exception as e:
                print(f" Searching for {idFieldPolygonB} failed. Error: {e}")

    # create sum of intersected area field
    try:
        sum_intersect_area = "sum_intersect_area_sqmi"
        arcpy.AddField_management(fcPolygonB, sum_intersect_area, "DOUBLE")
    except Exception as e:
        print(f"Sum intersect area field cannot be created. Error: {e}")

    # update sum interssected area field using cursor update and the dictionary
    with arcpy.da.UpdateCursor(fcPolygonB, ["{}".format(idFieldPolygonB), "{}".format(sum_intersect_area)]) as cursor:
        for row in cursor:
            try:
                if row[0] in intesected_dict.keys():
                    row[1] = intesected_dict[row[0]]
                else:
                    row[1] = 0
                cursor.updateRow(row)
            except Exception as e:
                print(f"Updating sum_intersect_area field failed. Error: {e}")

    # calculate and add percentage of intersected area field
    try:
        intersect_pct_field = "intersect_pct"
        arcpy.AddField_management(fcPolygonB, intersect_pct_field, "DOUBLE")
        arcpy.CalculateField_management(fcPolygonB, intersect_pct_field, "!sum_intersect_area_sqmi!/!Area_sqmi!", "PYTHON3")
    except Exception as e:
        print(f"Intersect percentage field cannot be created or calculated. Error: {e}")