import json



with open("test.json", "r") as jsonfile:
    data = json.load(jsonfile) # Reading the file
    print("Read successful")
    jsonfile.close()

print(data["LANE_KEEPING"]["thres2"][0])