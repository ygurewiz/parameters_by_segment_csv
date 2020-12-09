import sys
import csv
import json

def createJsonFileLines(robotSegmentsList,jsonFile,newJsonFile):
    data = json.load(jsonFile)
    res = {}
    for param in data:
        if(param=='surface_map'):
            continue
        if(param=='ProtocolVersion'):
            continue
        res[param]=[]
        res[param].append(data[param])
    newJsonFile.write('{')
    for r in res:
        newJsonFile.write('\t')
        json.dump(r, newJsonFile)
        newJsonFile.write(':')
        json.dump(res[r][0], newJsonFile)
        newJsonFile.write(',\n')
    newJsonFile.write('}')
    


def parseLines(csvSurfacesFileName,robotParamsFileName):
    i=0
    numRobots = 0
    with  open(csvSurfacesFileName, newline='') as csvSurfacesFile:
        csvReader = csv.DictReader(csvSurfacesFile)
        jsonFile = open(robotParamsFileName)
        currentRobot = ''
        lastRobot = ''
        robotSegmentsList = list()
        for line in csvReader:
            i+=1
            if(currentRobot==''):
                currentRobot=line['Row']
                numRobots+=1
                robotSegmentsList.append(line)
                print(currentRobot)
            else:
                if(not line['Row']==currentRobot):
                    lastRobot = currentRobot
                    currentRobot = ''
                    robotSegmentsList = list()
            newJsonFile = open(currentRobot+'.json','+w')
            createJsonFileLines(robotSegmentsList,jsonFile,newJsonFile)
            jsonFile.close()
            newJsonFile.close()
            if(i==1):
                break
            print(i)

    csvSurfacesFile.close()
    return i,numRobots

def main(argv):
    if(len(argv)<3):
        print("error in input")
        return
    numRows,numRobots= parseLines(argv[1],argv[2])
    print('number of rows parsed = '+str(numRows))
    print('number of robot files created = '+str(numRobots))

if __name__=="__main__":
    main(sys.argv)
