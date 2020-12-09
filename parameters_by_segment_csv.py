import sys
import csv
import json

def createJsonFile(robotSegmentsList,newJsonFile):
    for line in newJsonFile.readlines()
        if l in robotSegmentsList:



def parseLines(csvSurfacesFileName,robotParamsFileName):
    with  open(csvSurfacesFileName, newline='') as csvSurfacesFile:
        csvReader = csv.DictReader(csvSurfacesFile)
        jsonFile = open(robotParamsFileName)
        currentRobot = ''
        lastRobot = ''
        numRobots = 0
        i=0
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
            newJsonFile = open(currentRobot+'json','+w')
            #res = createJsonFile(robotSegmentsList,newJsonFile)

            print(i)
    csvSurfacesFile.close()

def main(argv):
    if(len(argv)<3):
        print("error in input")
        return
    res= parseLines(argv[1],argv[2])
    print(res)

if __name__=="__main__":
    main(sys.argv)
