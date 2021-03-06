import sys
import csv
import json
import str
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

    res = createJsonData(data,robotSegmentsList)
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

def createJsonData(data,robotSegmentsList):
    res = {}
    for param in data:
        if(param=='surface_map'):
            res[param]=[]
            surfaceJsonData = data[param]
            p = len(robotSegmentsList)
            last = 1
            for i in range(len(surfaceJsonData)):
                if(i>len(robotSegmentsList)-1):
                    if(last==1):
                        surfaceJsonData[i]['type']=3
                        surfaceJsonData[i]['width']=600 ####protect from invalid
                        surfaceJsonData[i]['length']=900 ####protect from invalid
                        last = last+1
                    elif(last==2):
                        surfaceJsonData[i]['type']=2
                        surfaceJsonData[i]['width']=3920 ####protect from invalid
                        surfaceJsonData[i]['length']=45000 ####protect from invalid
                        last = 0
                    else:
                        surfaceJsonData[i]['type']=0        
                    res[param].append(surfaceJsonData[i])
                    continue
                surfaceDict = robotSegmentsList[i]

                surfaceJsonData[i]['width']=int(float(surfaceDict['width(M)'])*1000)
                surfaceJsonData[i]['type']=int(surfaceDict['type(B=3,D=1,T=2)'])
                surfaceJsonData[i]['length']=int(float(surfaceDict['length(M)'])*1000)


                if(surfaceDict["Entity"]=='Docking'):
                    if(surfaceDict['parking_type']=='Central'):
                        data["parking_type"]=1
                    elif(surfaceDict['parking_type']=='Edge'):
                        data["parking_type"]=1
                    elif(surfaceDict['parking_type']=='Revivim'):
                        data["parking_type"]=4

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
                #print(param)
        else:
            res[param]=[]
            res[param].append(data[param])
            #print(param)
    return res
    
#unused!!
def createJsonData2(data,robotSegmentsList,panelWidth):
    res = {}
    for param in data:
        print(i)
        if(param=='surface_map'):
            res[param]=[]
            surfaceJsonData = data[param]
            p = len(robotSegmentsList)
            last = True
            for i in range(len(surfaceJsonData)):
                if(i>len(robotSegmentsList)-1):
                    if(last):
                        surfaceJsonData[i]['type']=3
                        surfaceJsonData[i]['width']=600 ####protect from invalid
                        last = False
                    else:
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
                    data["parking_side"]=0
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

def parseLines(csvSurfacesFileName,robotParamsFileName,VersionName,jsonPath,parameterFixFileName):
    i=0
    numRobots = 0
    surfaceCSVfileName = csvSurfacesFileName.split('.csv')[0] +'_Surface_Per_Robot.csv'
    surfaceCSVfile = open(surfaceCSVfileName,'w')
    surfaceCSVfile.write('Row,numNorthSegments,numSouthSegments,parkingType,parkingSide\n')

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
                    createJsonFileLines(doneList,data,newJsonFile,parameterChangeList)
                    newJsonFile.close()
                
                robotSegmentsList.append(line)
        if(len(robotSegmentsList)>0):
            addNumSegmentsCSV(surfaceCSVfile,robotSegmentsList)
    
                
        newJsonFile = open(jsonPath+'\\'+currentRobot+'.json','+w')
        createJsonFileLines(robotSegmentsList,data,newJsonFile,parameterChangeList)
        newJsonFile.close()
    
    
    jsonFile.close()
    csvSurfacesFile.close()
    return i,numRobots

def addNumSegmentsCSV(surfaceCSVfile,robotSegmentsList):
    
    numNorthSegments = 0
    numSouthSegments = 0
    currentRobot = robotSegmentsList[0]['Row']
    isNorth = True
    isSouth = False
    dockingType = ''
    for line in robotSegmentsList:

        if(isNorth):
            if(line['Entity']=='Tracker'):
                numNorthSegments = numNorthSegments+1
            elif(line['Entity']=='Docking'):
                isSouth = True
                isNorth = False
                dockingType = line['parking_type']
                dockingSide = line['parking_side']
        elif(isSouth):
            if(line['Entity']=='Tracker'):
                numSouthSegments = numSouthSegments+1
    if(dockingType == ''):
        print('t')
    if(dockingType=='Revivim' or dockingType=='Edge'):
        if(dockingSide=='North'):
            theLine = '{0},{1},{2},{3},{4}'.format(currentRobot,numNorthSegments,numSouthSegments,dockingType,dockingSide)
        elif(dockingSide=='South'):
            theLine = '{0},{1},{2},{3},{4}'.format(currentRobot,numSouthSegments,numNorthSegments,dockingType,dockingSide)
        else:
            print('oi')
    elif(dockingType=='Central'):
        theLine = '{0},{1},{2},{3},{4}'.format(currentRobot,numNorthSegments,numSouthSegments,dockingType,dockingSide)
    else:
        print('oioi')
    surfaceCSVfile.write(theLine)
    surfaceCSVfile.write('\n')
                

#dir_path = os.path.dirname(os.path.realpath(jsonFile))
def createBinFiles(theDir):
    
    #FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess
    #filename = "my_file.dat"
    args = "C:\\Users\\user\\source\\utils\\parameters_by_segment_csv\\BinGenerator\\BinGenerator.exe -d " + "C:\\Users\\user\\source\\utils\\parameters_by_segment_csv\\V1.30.24_P1.125"
    subprocess.call(args)#, stdout=FNULL, stderr=FNULL, shell=False)


def main(argv):
    if((len(argv)<1) or (not os.path.isdir(argv[1]))):
        return
    #createBinFiles(argv[1])###########################
    theDir = argv[1]
    csvFileName = theDir+'\\SurfaceMap.csv'
    jsonFileName = theDir +'\\versionJson.json'
    parameterFixFileName = theDir +'\\parameterChanges.csv'
    
    VersionNameStr =theDir.split('\\')
    VersionName = VersionNameStr[len(VersionNameStr)-1]


    numRows,numRobots= parseLines(csvFileName,jsonFileName,VersionName,theDir,parameterFixFileName)
    #createBinFiles(theDir)
    print("number of rows parsed = {} and number of robot files created = {}".format(numRows, numRobots))

if __name__=="__main__":
    main(sys.argv)
