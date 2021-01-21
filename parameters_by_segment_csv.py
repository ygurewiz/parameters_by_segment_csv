import sys
import csv
import json
import str
import string
import os

def createJsonFileLines(robotSegmentsList,data,newJsonFile,panelWidth):

    res = createJsonData(data,robotSegmentsList,panelWidth)

    addLineToJson(True,'{\n',res,newJsonFile,False)
    length = 0
    p = len(res)
    for headToken in res:
        length +=1
        addLineToJson(False,headToken,'',newJsonFile,False)
        if(length==p):
            addLineToJson(False,headToken,res,newJsonFile,True)
        else:
            addLineToJson(False,headToken,res,newJsonFile,False)
        #if(not length==p):
         #   newJsonFile.write(',')
    addLineToJson(True,'}\n',res,newJsonFile,True)
 
    

def addLineToJsonList(tokensList,newJsonFile,islast):    
    l = len(tokensList)
    if(l>1):
        i=0
        newJsonFile.write('[\n')
        for line in tokensList:
            i+=1
            newJsonFile.write('{\n')
            k = 0
            for token in line:
                k+=1
                json.dump(token, newJsonFile)
                newJsonFile.write(': ')
                json.dump(line[token], newJsonFile)
                if(k==len(line)):
                    newJsonFile.write('\n')
                else:
                    newJsonFile.write(',\n')
            if(i==l):
                newJsonFile.write('}\n]')
            else:
                newJsonFile.write('},\n')
        if (not islast):
            newJsonFile.write(',\n')
        return
    else:
        if(type(tokensList[0])==dict):
            i=0
            theDict = tokensList[0]
            newJsonFile.write('{\n')
            for t in theDict:
                i+=1
                json.dump(t, newJsonFile)
                newJsonFile.write(' : ')
                json.dump(theDict[t], newJsonFile)
                if(not i==len(theDict)):
                    newJsonFile.write(',\n')
                else:
                    newJsonFile.write('\n}')
        else:
            json.dump(tokensList[0], newJsonFile)
        if(not islast):
            newJsonFile.write(',\n')
        else:
            newJsonFile.write('\n')
        return

def addLineToJson(istoken,headToken,res,newJsonFile,islast):
    if(istoken):
        newJsonFile.write(headToken)
        return
    if(res==''):
        json.dump(headToken, newJsonFile)
        newJsonFile.write(': ')
        return
    if(type(res[headToken])==list):
        addLineToJsonList(res[headToken],newJsonFile,islast)
    else:
        print(headToken)


    

def createJsonData(data,robotSegmentsList,panelWidth):
    res = {}
    for param in data:
        if(param=='surface_map'):
            res[param]=[]
            surfaceJsonData = data[param]
            p = len(robotSegmentsList)
            for i in range(len(surfaceJsonData)):
                if(i>len(robotSegmentsList)-1):
                        surfaceJsonData[i]['type']=0
                        res[param].append(surfaceJsonData[i])
                        continue
                surfaceDict = robotSegmentsList[i]

                if(surfaceDict["Entity"]=='Tracker'):
                    surfaceJsonData[i]['type']=2
                    surfaceJsonData[i]['length']=int(int(surfaceDict['Area'])*1000/int(panelWidth))
                    surfaceJsonData[i]['width']=3920         #hard coded!
                    surfaceJsonData[i]['east']=2320         #hard coded!

                elif(surfaceDict["Entity"]=='Bridge'):
                    surfaceJsonData[i]['type']=3
                    surfaceJsonData[i]['width']=600         #hard coded!
                    surfaceJsonData[i]['east']=2020         #hard coded!
                    if('-' in surfaceDict['Gap']):
                        gaps = surfaceDict['Gap'].split('-')
                        gap = max(int(gaps[0]),int(gaps[1]))
                        surfaceJsonData[i]['length']=gap*10
                    elif('<' in surfaceDict['Gap']):
                        gaps = surfaceDict['Gap'].split('<')
                        gap = int(gaps[1])
                        surfaceJsonData[i]['length']=gap*10
                    elif('>' in surfaceDict['Gap']):
                        gaps = surfaceDict['Gap'].split('>')
                        gap = int(gaps[1])
                        surfaceJsonData[i]['length']=gap*10
                    else:
                        print("NOOO!!")

                elif(surfaceDict["Entity"]=='Dock'):
                    surfaceJsonData[i]['type']=1
                    surfaceJsonData[i]['width']=900              #hard coded!
                    surfaceJsonData[i]['east']=2320             #hard coded!
                    if(surfaceDict['Gap']=='Edge'):
                        data["parking_type"]=1                  #edge table
                        surfaceJsonData[i]['length']=750
                        parkingType = surfaceDict['Row'].split('-')[2]
                        if(parkingType=='01'):
                            data["parking_side"]=1
                        elif(parkingType=='02' or parkingType=='03'):
                            data["parking_side"]=0
                        else:
                            print("NOOO!!")
                    else:
                        if('-' in surfaceDict['Gap']):
                            gaps = surfaceDict['Gap'].split('-')
                            gap = max(int(gaps[0]),int(gaps[1]))
                            surfaceJsonData[i]['length']=gap*10
                        elif('<' in surfaceDict['Gap']):
                            gaps = surfaceDict['Gap'].split('<')
                            gap = int(gaps[1])
                            surfaceJsonData[i]['length']=gap*10
                        elif('>' in surfaceDict['Gap']):
                            gaps = surfaceDict['Gap'].split('>')
                            gap = int(gaps[1])
                            surfaceJsonData[i]['length']=gap*10
                        else:
                            print("NOOO!!")

                elif(surfaceDict["Entity"]=='Gap'):
                    surfaceJsonData[i]['type']=0
                    gaps = surfaceDict['Gap'].split('-')
                    gap = max(int(gaps[0]),int(gaps[1]))
                    surfaceJsonData[i]['length']=gap*10

                res[param].append(surfaceJsonData[i])  
                #print(param)
        else:
            res[param]=[]
            res[param].append(data[param])
            #print(param)
    return res

def parseLines(csvSurfacesFileName,robotParamsFileName,VersionName,jsonPath):
    panelWidth = 4  #hard coded
    i=0
    numRobots = 0
    with  open(csvSurfacesFileName, newline='') as csvSurfacesFile:
        csvReader = csv.DictReader(csvSurfacesFile)
        jsonFile = open(robotParamsFileName)
        #jsonDir = robotParamsFileName.split('//')
        #jsonDir = jsonFile.name.split('.json')[0]
        #jsonPath = jsonDir

        #if not os.path.isdir(jsonPath):
        #    try:
        #        os.mkdir(jsonPath)
        #    except OSError:
        #        print ("Creation of the directory %s failed" % jsonPath)
        #    else:
        #        print ("Successfully created the directory %s " % jsonPath)

        data = json.load(jsonFile)

        currentRobot = ''
        newRobot = True
        robotSegmentsList = list()
        doneList = robotSegmentsList
        doneRobot = currentRobot
        for line in csvReader:
            i+=1
            if(newRobot):
                currentRobot=line['Row']
                newRobot = False
                robotSegmentsList.append(line)
                print(currentRobot)
            else:
                if(not line['Row']==currentRobot):
                    if(line['Row']==''):
                        continue
                    doneRobot = currentRobot
                    currentRobot = line['Row']
                    newRobot = True
                    doneList = robotSegmentsList
                    robotSegmentsList = list()
                    numRobots+=1

                    newJsonFile = open(jsonPath+'\\'+doneRobot+'.json','+w')
                    createJsonFileLines(doneList,data,newJsonFile,panelWidth)
                    newJsonFile.close()
                
                robotSegmentsList.append(line)
        newJsonFile = open(jsonPath+'\\'+currentRobot+'.json','+w')
        createJsonFileLines(robotSegmentsList,data,newJsonFile,panelWidth)
        newJsonFile.close()

        

    jsonFile.close()
    csvSurfacesFile.close()
    return i,numRobots

#def main(argv):
#    if(len(argv)<4):
#        print("error in input")
#        return
#    panelWidth = argv[3]        #hard coded
#    numRows,numRobots= parseLines(argv[1],argv[2],argv[3])
#    print("number of rows parsed = {} and number of robot files created = {}".format(numRows, numRobots))

def main(argv):
    if((len(argv)<1) or (not os.path.isdir(argv[1]))):
        return
    theDir = argv[1]
    csvFileName = theDir+'\\SurfaceMap.csv'
    jsonFileName = theDir +'\\versionJson.json'
    
    VersionNameStr =theDir.split('\\')
    VersionName = VersionNameStr[len(VersionNameStr)-1]


    numRows,numRobots= parseLines(csvFileName,jsonFileName,VersionName,theDir)
    print("number of rows parsed = {} and number of robot files created = {}".format(numRows, numRobots))

if __name__=="__main__":
    main(sys.argv)
