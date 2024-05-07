import arcpy

# Defining workspace
arcpy.env.workspace  = "C:\\Users\\torkashvand\\OneDrive - University of Iowa\\My_Phd\\Phd_Courses\\Spring_2024\\Geoprogramming\\airportdata"
#print (arcpy.env.workspace)

# Save and print list of feature classes in the workspace
fcList = arcpy.ListFeatureClasses()
#print(fcList)

# define the airport feature class and fields in variables
fc = 'airports'
fcFields = arcpy.ListFields(fc)
# for field in fcFields:
#     print(field.name)
fields = ['FEATURE', 'TOT_ENP']

# Make a list of unique values in the 'FEATURE' field
feature_values = set()
with arcpy.da.SearchCursor(fc, fields) as cursor:
    for row in cursor:
        feature_values.add(row[0])

feature_lst = list(feature_values)
#print(feature_lst)

# Adding a new field 'Buffer' into the feature class with LONG data type
try:
    arcpy.management.AddField(fc, "Buffer", "LONG")
except Exception as e:
    print(e)

# Add the Buffer field to the fields list
fields.append("Buffer")
#print(fields)

# Create update cursor for feature class
with arcpy.da.UpdateCursor(fc, fields) as cursor:
    try:
        for row in cursor:
            try:
                if row[0] == 'Airport':
                    if row[1] >= 10000:
                        row[2] = 15000
                    elif row[1] < 10000:
                        row[2] = 10000
                elif row[0] == 'Seaplane Base':
                    if row[1] >= 1000:
                        row[2] = 7500
                    else:
                        row[2] = 0
                else:
                    row[2] = 0
            except Exception as e:
                print(e)
            cursor.updateRow(row)
    except Exception as e:
        print(f'rows are not updated. Error: {e}')

# buffer feature class
try:
    arcpy.Buffer_analysis(fc, 'airports_buffer', 'Buffer')
except Exception as e:
    print(f'buffer feature class cannot be processed. Error: {e}')