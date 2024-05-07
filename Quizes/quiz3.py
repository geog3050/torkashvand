
try:
    climate = str(input("Please enter the climate: ")).lower()
    temperature = eval(input("Please enter the temperatures with comma in between: "))
except Exception as e:
    print ("Please enter the correct input")
    print (f"An error occured: {e}")
    exit()

for temp in temperature:
    try:
        temp = float(temp)
        if climate == "tropical" and temp <= 30:
            print("F")
        elif climate == "continental" and temp <= 25:
            print ("F")
        elif temp <= 18:
            print ("F")
        else:
            print ("U")
    except Exception as e:
        print (f"An error occured: {e}")

