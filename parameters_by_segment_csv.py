import sys
import csv
import json
import string
import string
import os
import subprocess


def createParmeterChangeList(csvParametersReader):
    data = {}
    for row in csvParametersReader:
        robot = row['Row']
        data[robot] = row
    return data

def createJsonFileLines(robotSegmentsList,data,newJsonFile,parameterChangeList):

    res,surfaceJsonForServer = createJsonData(data,robotSegmentsList)           ##############################surfaceJsonForServer
    parking_type = data['parking_type']
    robotName = robotSegmentsList[0]['Row']

    if(not parameterChangeList==[]):
        paramData = parameterChangeList[robotName]
        for p in paramData:
            if(p =='Row'):
                continue
            res[p] = [int(paramData[p])] 

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
        #if(headToken=='distance_reverse_after_wall_collision'):
         #   print('t')
    addLineToJson(True,'}\n',res,newJsonFile,True)
    return surfaceJsonForServer         ##############################surfaceJsonForServer
 
    

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



def getsurfaceJsonData(surfaceJsonData):
    res = []
    for p in surfaceJsonData:
        if p['type']==0:
            break
        res.append(p)
    return res

def createJsonData(data,robotSegmentsList):
    res = {}
    surfaceJsonForServer = []            ##############################surfaceJsonForServer
    for param in data:
        if(param=='surface_map'):
            res[param]=[]
            surfaceJsonData = data[param]
            p = len(robotSegmentsList)
            last = 1
            for i in range(len(surfaceJsonData)):
                if(i>len(robotSegmentsList)-1):
                    if(last==1):
                        surfaceJsonData[i]['type']=0
                        surfaceJsonData[i]['width']=0 ####protect from invalid
                        surfaceJsonData[i]['length']=0 ####protect from invalid
                        surfaceJsonData[i]['west']=0 ####protect from invalid
                        surfaceJsonData[i]['east']=0 ####protect from invalid
                        last = last+1
                    elif(last==2):
                        surfaceJsonData[i]['type']=0
                        surfaceJsonData[i]['width']=0 ####protect from invalid
                        surfaceJsonData[i]['length']=0 ####protect from invalid
                        surfaceJsonData[i]['west']=0 ####protect from invalid
                        surfaceJsonData[i]['east']=0 ####protect from invalid
                        last = 0
                    else:
                        surfaceJsonData[i]['type']=0 
                        surfaceJsonData[i]['width']=0 
                        surfaceJsonData[i]['length']=0
                        surfaceJsonData[i]['west']=0
                        surfaceJsonData[i]['east']=0
                    res[param].append(surfaceJsonData[i])
                    continue
                surfaceDict = robotSegmentsList[i]

                surfaceJsonData[i]['width']=int(float(surfaceDict['width(M)'])*1000)
                surfaceJsonData[i]['type']=int(surfaceDict['type(B=3,D=1,T=2)'])
                surfaceJsonData[i]['length']=int(float(surfaceDict['length(M)'])*1000)
                surfaceJsonData[i]['west']=int(float(surfaceDict['west(BridgeCenter)'])*1000)


                if(surfaceDict["Entity"]=='Docking'):
                    if(surfaceDict['parking_type']=='Central'):
                        data["parking_type"]=1
                    elif(surfaceDict['parking_type']=='Edge'):
                        data["parking_type"]=1
                    elif(surfaceDict['parking_type']=='Revivim'):
                        data["parking_type"]=4
                    elif(surfaceDict['parking_type']=='CA'):
                        data["parking_type"]=2
                    elif(surfaceDict['parking_type']=='Nadec'):
                        data["parking_type"]=5
                    elif(surfaceDict['parking_type']=='Nadec_Edge'):
                        data["parking_type"]=6

                    if(surfaceDict['parking_side']=='South'):
                        data["parking_side"]=0
                    elif(surfaceDict['parking_side']=='North'):
                        data["parking_side"]=1

                elif(surfaceDict["Entity"]=='Gap'):
                    surfaceJsonData[i]['type']=0
                    gaps = surfaceDict['Gap'].split('-')
                    gap = max(int(gaps[0]),int(gaps[1]))
                    surfaceJsonData[i]['length']=gap*10

                res[param].append(surfaceJsonData[i])  
                
                surfaceJsonForServer = getsurfaceJsonData(surfaceJsonData[:p])              ##############################surfaceJsonForServer
                #print(surfaceJsonForServer)                              ##############################surfaceJsonForServer
        else:
            res[param]=[]
            res[param].append(data[param])
            #print(param)
    return res,surfaceJsonForServer
    

def parseLines(csvSurfacesFileName,robotParamsFileName,VersionName,jsonPath,parameterFixFileName):
    i=0
    numRobots = 0
    surfaceCSVfileName = csvSurfacesFileName.split('.csv')[0] +'_Surface_Per_Robot.csv'
    surfaceCSVfile = open(surfaceCSVfileName,'w')
    surfaceCSVfile.write('Row,numNorthSegments,numSouthSegments,parkingType,parkingSide,areaRowN,areaRowS,numSequencesN,numSequencesS\n')
    #fieldNames = ['Row','numNorthSegments','numSouthSegments','parkingType','parkingSide','areaRowN','areaRowS']           ####***
#    csvSurfaceFileWriter = csv.DictWriter(surfaceCSVfile,fieldNames)

    with  open(csvSurfacesFileName, newline='') as csvSurfacesFile:
        csvReader = csv.DictReader(csvSurfacesFile)
        jsonFile = open(robotParamsFileName)
        try:
            parameterFixFile = open(parameterFixFileName)
            csvParametersReader = csv.DictReader(parameterFixFile)
            parameterChangeList = createParmeterChangeList(csvParametersReader)
            parameterFixFile.close()

        except:
            print(sys.exc_info()[0])
            parameterChangeList = []


        
        data = json.load(jsonFile)

        currentRobot = ''
        newRobot = True
        robotSegmentsList = list()
        doneList = robotSegmentsList
        doneRobot = currentRobot

        surfaceJsonForServerList = []

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
                    if(len(robotSegmentsList)>0):
                        addNumSegmentsCSV(surfaceCSVfile,robotSegmentsList)
                    robotSegmentsList = list()
                    numRobots+=1

                    newJsonFile = open(jsonPath+'\\'+doneRobot+'.json','+w')
                    surfaceJsonForServer = createJsonFileLines(doneList,data,newJsonFile,parameterChangeList) 
                    surfaceJsonForServerList.append(doneRobot+'\t'+json.dumps(surfaceJsonForServer)+'\n')
                    newJsonFile.close()
                
                robotSegmentsList.append(line)
        if(len(robotSegmentsList)>0):
            addNumSegmentsCSV(surfaceCSVfile,robotSegmentsList)
    
                
        newJsonFile = open(jsonPath+'\\'+currentRobot+'.json','+w')
        surfaceJsonForServer = createJsonFileLines(robotSegmentsList,data,newJsonFile,parameterChangeList)
        surfaceJsonForServerList.append(doneRobot+'\t'+json.dumps(surfaceJsonForServer)+'\n')
        newJsonFile.close()
    
    
    jsonFile.close()
    csvSurfacesFile.close()
    return i,numRobots,surfaceJsonForServerList

def addNumSegmentsCSV(surfaceCSVfile,robotSegmentsList):
    
    numNorthSegments = 0
    numSouthSegments = 0
    currentRobot = robotSegmentsList[0]['Row']
    isNorth = True
    isSouth = False
    dockingType = ''
    lengthRowN=0
    lengthRowS=0
    widthSegment = 0
    numStrips = 0

    for line in robotSegmentsList:

        if(isNorth):
            if(line['Entity']=='Tracker'):
                numNorthSegments = numNorthSegments+1
                lengthRowN = lengthRowN+float(line['length(M)'])
                if widthSegment==0:
                    widthSegment = float(line['width(M)'])
            elif(line['Entity']=='Docking'):
                isSouth = True
                isNorth = False
                dockingType = line['parking_type']
                dockingSide = line['parking_side']
        elif(isSouth):
            if(line['Entity']=='Tracker'):
                numSouthSegments = numSouthSegments+1
                lengthRowS = lengthRowS+float(line['length(M)'])
                if widthSegment==0:
                    widthSegment = float(line['width(M)'])
    wholeWidth = round(widthSegment,0)
    if wholeWidth==4:
        numStrips = 12
    elif wholeWidth==2:
        numStrips=6
    elif wholeWidth==3:
        numStrips=10
    else:
        print('UNKNOWN_WIDTH_ERROR')

    rowAreaN = round(lengthRowN*widthSegment,0)
    rowAreaS = round(lengthRowS*widthSegment,0)

    numSequencesN = numNorthSegments*numStrips
    numSequencesS = numSouthSegments*numStrips

    if(dockingType == ''):
        print('DockingType INVALID')
    elif(dockingType=='Revivim' or dockingType=='Edge' or dockingType=='CA'):
        if(dockingSide=='North'):
            theLine = '{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(currentRobot,numNorthSegments,numSouthSegments,dockingType,dockingSide,rowAreaN,rowAreaS,numSequencesN,numSequencesS)
        elif(dockingSide=='South'):
            theLine = '{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(currentRobot,numSouthSegments,numNorthSegments,dockingType,dockingSide,rowAreaN,rowAreaS,numSequencesN,numSequencesS)
        else:
            print('PARSE_ERROR')
    elif(dockingType=='Central' or dockingType=='Nadec' or dockingType=='Nadec_Edge'):
        theLine = '{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(currentRobot,numNorthSegments,numSouthSegments,dockingType,dockingSide,rowAreaN,rowAreaS,numSequencesN,numSequencesS)
    else:
        print('PARSE_ERROR_2')
    surfaceCSVfile.write(theLine)
    surfaceCSVfile.write('\n')
                




def main(argv):
    if((len(argv)<1) or (not os.path.isdir(argv[1]))):
        return
    theDir = argv[1]
    csvFileName = theDir+'\\SurfaceMap.csv'
    jsonFileName = theDir +'\\versionJson.json'
    parameterFixFileName = theDir +'\\parameterChanges.csv'
    surfaceMapJsonsForServer = theDir + '\\surfaceMapJsonsForServer.txt'
    surfaceMapJsonsForServerFile = open(surfaceMapJsonsForServer,'w')
    
    VersionNameStr =theDir.split('\\')
    VersionName = VersionNameStr[len(VersionNameStr)-1]


    numRows,numRobots,surfaceJsonForServerList= parseLines(csvFileName,jsonFileName,VersionName,theDir,parameterFixFileName)
    print("number of rows parsed = {} and number of robot files created = {}".format(numRows, numRobots))
    
    for t in surfaceJsonForServerList:
        surfaceMapJsonsForServerFile.write(t)

if __name__=="__main__":
    main(sys.argv)
