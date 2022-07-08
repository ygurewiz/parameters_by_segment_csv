
drag and drop directory containing:
INPUT:
	1) "versionJson.json" - json version file containing parameters for all site robots.
		script will use all parameters except:
		1) surface map - make sure invalid sufraces parameters are set in this file, since script will use "surfaceMap.csv" file to create then all up to invalids
		2) parameters refernced in "parameterChanges.csv" file
	2) "surfaceMap.csv" - should always use these headers:
		[Row	Entity	id	width(M)	west(BridgeCenter)	length(M)	type(B=3,D=1,T=2)	parking_type	parking_side]
		if row name is different - script will fail!
		Row = free text
		Entity = text of type [Tracker	BridgeS	Bridge	Docking], where BridgeS is side bridge
		id = id of surface
		width,west,length = number in meters
		type = number [2=Tracker, 3=BridgeS, 3=Bridge, 1=Docking]
		parking_type = specific text of type: 
											[Revivim,Edge,CA,Central] - widthwise
											[Nadec,Nadec_Edge] - lengthwise
		
		parking_side = specific text of type [north,south]
		ALL ENTITY SHOULD BE SETUP IN JSON FROM NORTH TO SOUTH!
	3) "parameterChanges.csv"
		first column should be exact entities, in same order as "surfaceMap.csv" and name text. each robot exactly once.
		next columns should be parameter names, exact as "versionJson.json"
		script will replace values set in "versionJson.json" to those in csv, per robot as needed. 
		not relevant to surface_map parameters.
		*** if parameters are TLV - need to add first column as "isSeverLengthwise" = TRUE/FALSE
		
OUTPUTS:
	0) print to output window all entities json files supplied, and number of rows edited in "surfaceMap.csv"
	1) ALL SITE ROBOTS specific JSON files according to data. names of files will be names of entities
	2) file "SurfaceMap_Surface_Per_Robot.csv" containing data: [Row	numNorthSegments	numSouthSegments	parkingType	parkingSide	areaRowN	areaRowS	numSequencesN	numSequencesS]
	3) file "surfaceMapJsonsForServer.json" containing JSON data for each robot per row.
		in each row data will be:
		1) "rowID" = random number in range(0,255)
		2) "robot" = assetId in string format
		3) "surface_map" = list of surface_map jsons including "allignment" parameter set to 0/1 according to location vs docking
	