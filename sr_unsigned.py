#! /usr/bin/python

import numpy as np
import time
import argparse
import math

np.seterr(all='ignore')

parser = argparse.ArgumentParser()
parser.add_argument("filename",help="The filename of the assembly program to execute.")
parser.add_argument("-t","--timer",help="Displays the time taken by the assembly program after it finishes",action="store_true")
parser.add_argument("-n","--n",help="Displays the total number of instruction used.",action="store_true")
parser.add_argument("-s","--statistics",help="Displays statistics about operations used",action="store_true")
args = parser.parse_args()

done = False

def do():
	res = firstNumber*secondNumber
	for i in range(128):
		temp = res%16
		memoryArray[128+i] = temp
		res=res/16 

memoryArray = np.zeros(2048,np.uint32)										# array of size 4096, with each element being of 4 bytes		
registerArray = np.zeros(16,np.uint32)
flagE = False
flagGT = False	

def registerIndex(regstr):
	if(regstr=="sp"):
		return 14
	elif(regstr=="ra"):
		return 15
	return int(regstr[1:])

def ifreg(string):
	if(string=="sp"):
		return True
	elif(string=="ra"):
		return True
	else:
		return (string[0]=='r')

def checkHex(string):
	return ((string[0:2]=='0x') or (string[0:2]=='0X'))

def convertStringToHex(hexString,modifier):
	immediate = hexString.replace(" ","")
	if(modifier=="n"):
		return np.uint32(int(immediate,16))
	elif (modifier=='u'):
		return np.uint32(np.uint16(int(immediate,16)))
	elif (modifier=='h'):
		return np.uint32(np.uint16(int(immediate,16))<<16)


def rshift(val,n): 
	return (val % 0x100000000) >> n

##########
##########				OPERATOR FUNCTIONS
##########
def highOrderFunc(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,opFuncPointer):
	destRegIndex = registerIndex(destRegStr)
	sourceReg1Index = registerIndex(sourceReg1Str)
	if(ifreg(sourceReg2ORimmediate)):
		immediate=0
		sourceReg2Index = registerIndex(sourceReg2ORimmediate)
	else:
		immediate=sourceReg2ORimmediate
		ifHex = checkHex(immediate)
	if(immediate==0):
		registerArray[destRegIndex] = opFuncPointer(registerArray[sourceReg1Index],registerArray[sourceReg2Index])		
	else:
		if(ifHex):
				tempNumber = convertStringToHex(immediate,modifier)
				registerArray[destRegIndex] = opFuncPointer(registerArray[sourceReg1Index],tempNumber)
		else:
			if modifier=='h':
				immediate = np.uint16(immediate)<<16
			else:
				immediate = np.int16(immediate)
			registerArray[destRegIndex] = opFuncPointer(registerArray[sourceReg1Index],np.uint32(immediate))	

def addPointer(a,b):	return a+b
def subPointer(a,b):	return a-b
def mulPointer(a,b):	return a*b
def divPointer(a,b):	return a/b
def modPointer(a,b):	return a%b
def  orPointer(a,b):	return a|b
def andPointer(a,b):	return a&b

def add(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,ifSubtract):
	if(ifSubtract):
		return highOrderFunc(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,subPointer)
	else:
		return highOrderFunc(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,addPointer)

def addn(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return add(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'n',False)

def addu(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return add(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'u',False)

def addh(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return add(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'h',False)

def subn(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return add(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'n',True)

def subu(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return add(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'u',True)

def subh(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return add(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'h',True)

def multiply(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier):
	return highOrderFunc(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,mulPointer)

def  muln(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return multiply(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'n')

def  mulu(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return multiply(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'u')

def  mulh(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return multiply(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'h')

def divide(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier):
	return highOrderFunc(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,divPointer)

def divn(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return divide(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'n')

def divu(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return divide(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'u')
	
def divh(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return divide(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'h')
	
def mod(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier):
	return highOrderFunc(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,modPointer)

def modn(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return mod(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'n')
	
def modh(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return mod(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'h')

def modu(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return mod(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'u')

def logicalOR(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier):
	return highOrderFunc(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,orPointer)

def orn(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return logicalOR(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'n')
	
def oru(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return logicalOR(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'u')

def orh(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return logicalOR(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'h')

def logicalAND(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier):
	return highOrderFunc(destRegStr,sourceReg1Str,sourceReg2ORimmediate,modifier,andPointer)	

def andn(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return logicalAND(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'n')


def andu(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return logicalAND(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'u')

def andh(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return logicalAND(destRegStr,sourceReg1Str,sourceReg2ORimmediate,'h')

#################
#################
###   NUMBER DETERMINING SHIFT CANT BE NEGATIVE

def lslPointer(a,b):	return a<<b
def asrPointer(a,b):	return a>>b

def highOrderFunc2(destRegStr,sourceReg1Str,sourceReg2ORimmediate,opFuncPointer):
	destRegIndex = registerIndex(destRegStr)
	sourceReg1Index = registerIndex(sourceReg1Str)
	if(ifreg(sourceReg2ORimmediate)):
		immediate=0
		sourceReg2Index = registerIndex(sourceReg2ORimmediate)
	else:
		immediate=sourceReg2ORimmediate
		ifHex = checkHex(immediate)	
	if(immediate==0):
		registerArray[destRegIndex] = opFuncPointer(registerArray[sourceReg1Index],registerArray[sourceReg2Index])	
	else:
		if(ifHex):
			tempNumber = convertStringToHex(immediate,'n')
			registerArray[destRegIndex] = opFuncPointer(registerArray[sourceReg1Index],tempNumber)
		else:
				immediate = np.uint16(immediate)
				registerArray[destRegIndex] = opFuncPointer(registerArray[sourceReg1Index],immediate)

def leftShiftLogical(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return highOrderFunc2(destRegStr,sourceReg1Str,sourceReg2ORimmediate,lslPointer)

def rightShiftArithmetic(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return highOrderFunc2(destRegStr,sourceReg1Str,sourceReg2ORimmediate,asrPointer)


def rightShiftLogical(destRegStr,sourceReg1Str,sourceReg2ORimmediate):
	return highOrderFunc2(destRegStr,sourceReg1Str,sourceReg2ORimmediate,rshift)

def loadMemory(destRegStr,immediate,sourceRegStr):
	if immediate=='':
		immediate='0'
	destRegIndex=registerIndex(destRegStr)
	sourceRegIndex=registerIndex(sourceRegStr)
	ifHex = checkHex(immediate)
	if(ifHex):
		tempNumber = np.int16(int(immediate,16))
		registerArray[destRegIndex] = memoryArray[(registerArray[sourceRegIndex]+tempNumber)/4]
	else:
		registerArray[destRegIndex] = memoryArray[(registerArray[sourceRegIndex]+np.int32(immediate))/4]		

def storeMemory(sourceRegStr,immediate,destRegStr):
	if immediate=='':
		immediate='0'		
	destRegIndex=registerIndex(destRegStr)
	sourceRegIndex=registerIndex(sourceRegStr)
	ifHex = checkHex(immediate)						
	if(ifHex):
		tempNumber = np.int16(int(immediate,16))
		memoryArray[(registerArray[destRegIndex]+tempNumber)/4] = registerArray[sourceRegIndex]
	else:
		memoryArray[(registerArray[destRegIndex]+np.int32(immediate))/4] = registerArray[sourceRegIndex]	


def move(destRegStr,sourceRegORimmediate,modifier):
	if(ifreg(sourceRegORimmediate)):
		immediate=0
		destRegIndex = registerIndex(destRegStr)
		sourceRegIndex = registerIndex(sourceRegORimmediate)
	else:
		destRegIndex = registerIndex(destRegStr)
		ifHex=checkHex(sourceRegORimmediate)
		if (ifHex):	
			immediate= convertStringToHex(sourceRegORimmediate,modifier)
		else:
			immediate = sourceRegORimmediate
	if (immediate==0):
		registerArray[destRegIndex] = registerArray[sourceRegIndex]
	else:
		if(ifHex):
			registerArray[destRegIndex] = np.uint32(immediate)
		else:
			if modifier=='h':
				immediate = np.uint16(immediate)<<16
			else:
				immediate = np.int16(immediate)
			registerArray[destRegIndex] = np.uint32(immediate)

def moven(destRegStr,sourceRegORimmediate):
	return move(destRegStr,sourceRegORimmediate,'n')

def moveh(destRegStr,sourceRegORimmediate):
	return move(destRegStr,sourceRegORimmediate,'h')

def moveu(destRegStr,sourceRegORimmediate):
	return move(destRegStr,sourceRegORimmediate,'u')

def cmp(destRegStr,sourceRegORimmediate,modifier):
	global flagGT,flagE
	if(ifreg(sourceRegORimmediate)):
		immediate=0
		destRegIndex = registerIndex(destRegStr)
		sourceRegIndex = registerIndex(sourceRegORimmediate)
	else:
		destRegIndex = registerIndex(destRegStr)
		ifHex=checkHex(sourceRegORimmediate)
		immediate = sourceRegORimmediate
	if (immediate==0):
		flagGT =  (np.int32(registerArray[destRegIndex]) > np.int32(registerArray[sourceRegIndex]))
		flagE =  (np.int32(registerArray[destRegIndex]) == np.int32(registerArray[sourceRegIndex]))
	else:
		if (ifHex):
			immediate = convertStringToHex(immediate,modifier)
			flagGT =  (np.int32(registerArray[destRegIndex]) > np.int32(immediate))
			flagE =  (np.int32(registerArray[destRegIndex]) == np.int32(immediate))
		else:
			if modifier=='h':
				immediate = np.uint16(immediate)<<16
			else:
				immediate = np.int16(immediate)
			flagGT =  (registerArray[destRegIndex] > np.int32(immediate))
			flagE  = (registerArray[destRegIndex] == np.int32(immediate))

def cmpn(destRegStr,sourceRegORimmediate):
	return cmp(destRegStr,sourceRegORimmediate,'n')

def cmpu(destRegStr,sourceRegORimmediate):
	return cmp(destRegStr,sourceRegORimmediate,'u')

def cmph(destRegStr,sourceRegORimmediate):
	return cmp(destRegStr,sourceRegORimmediate,'h')

def logicalNOT(destRegStr,sourceRegORimmediate,modifier):
	if(ifreg(sourceRegORimmediate)):
		immediate=0
		destRegIndex = registerIndex(destRegStr)
		sourceRegIndex = registerIndex(sourceRegORimmediate)
	else:
		destRegIndex = registerIndex(destRegStr)
		immediate=sourceRegORimmediate
		ifHex=checkHex(immediate)
	if(immediate==0):
		registerArray[destRegIndex] = ~registerArray[sourceRegIndex]
	else:
		if (ifHex):
			registerArray[destRegIndex] = ~convertStringToHex(immediate,modifier)			
		else:
			if modifier=='h':
				immediate = np.uint16(immediate)<<16
			else:
				immediate = np.int16(immediate)
			registerArray[destRegIndex] = ~np.uint32(immediate)

def notn(destRegStr,sourceRegORimmediate):
	return logicalNOT(destRegStr,sourceRegORimmediate,'n')

def noth(destRegStr,sourceRegORimmediate):
	return logicalNOT(destRegStr,sourceRegORimmediate,'h')

def notu(destRegStr,sourceRegORimmediate):
	return logicalNOT(destRegStr,sourceRegORimmediate,'u')

def printMacro(reg):
	print np.int32(registerArray[registerIndex(reg)])

def printkaratsuba():
	do()
	result ="0x"
	for i in range(128):
		if(i%2==0):
			result += " "
		result += hex(memoryArray[255-i]).replace("0x","").replace("L","").upper()
	print result

#######
#######							ENDS HERE
#######

programCounter = 0
programArray = []
labelDict = {}


def init(filename):
	i = 0
	registerArray[14] = 8000
	with open(filename) as f:
		for line in f:
			line=line.strip()
			if(len(line)>1 and ("#" not in line)):
			#(line[0]=='.') and			
				if ( (':' in line)):
					line = line.split(':')
					labelDict[line[0]] = i
					programArray.append(line[0]+':')
					i = i + 1
					if line[1]!='':
						programArray.append(line[1])
						i = i + 1
				else:
					programArray.append(line.lower())
					i = i + 1

def beq(label):
	global programCounter
	if flagE == True:
		programCounter = labelDict[label]

def bgt(label):
	global programCounter
	if flagGT == True:
		programCounter = labelDict[label]

def b(label):
	global programCounter
	programCounter = labelDict[label]

def call(label):
	global programCounter
	registerArray[15] = programCounter + 1
	programCounter = labelDict[label]

def ret():
	global programCounter
	if registerArray[15]==0:
		return
	else:
		programCounter = registerArray[15]
		registerArray[15]=0

def nop():
	pass

operatorDict = {"add":addn,"addu":addu,"addh":addh,"sub":subn,"subu":subu,"subh":subh,"mul":muln,"mulh":mulh,
				"div":divn,"divu":divu,"divh":divh,"mod":modn,"modu":modu,"modn":modn,"or":orn,"oru":oru,
				"orh":orh,"and":andn,"andh":andh,"andu":andu,"cmp":cmpn,"cmph":cmph,"cmpu":cmpu,
				"not":notn,"notu":notu,"noth":noth,"mov":moven,"movh":moveh,"movu":moveu,"lsl":leftShiftLogical,
				"lsr":rightShiftLogical,"asr":rightShiftArithmetic,".print":printMacro,"b":b,"beq":beq,"bgt":bgt,
				"nop":nop,"call":call,"ret":ret,"ld":loadMemory,"st":storeMemory,".prinkarat":printkaratsuba}

instructions_memory = ["ld","st"]

instruction_count = {}
for key in operatorDict.keys():
	instruction_count[key]=0

def lineParser(line):
	line = line.strip()
	try:
		if((':' in line)):
			#call a function to save state
			return
		stringList = line.split(" ")
		operator = stringList[0]
		instruction_count[operator] += 1
		stringList = " ".join(stringList[1:])
		stringList = stringList.replace(" ","").replace("	","")
		if (operator not in instructions_memory):
			operandList = stringList.split(",")
			if operandList == ['']:
				operatorDict[operator]()
			else:	
				operatorDict[operator](*operandList)
		else:
			stringList = stringList.replace("[",",")
			stringList = stringList.replace("]","")
			operandList = stringList.split(",")
			if (len(operandList)==2):
				operandList.insert(1,'0')
			operatorDict[operator](*operandList)
			pass
	except KeyError:
		print "The program called an undefined label in line :\n"+line.strip()
		raise
	except TypeError:
		print "Wrong number of arguments provided in line:\n" + line.strip()
		raise
	except IndexError:
		print "The program tried to access an unreachable register or memory location. \n"+line.strip()
		raise
	except ValueError:
		print "Immediate value can either be an integer or a hex starting with 0x or 0X.\n" + line.strip()
		raise

noInstructions = 0

def run(filename):
	global programCounter,noInstructions
	init(filename)
	programCounter = labelDict[".main"]
	while(programCounter < len(programArray)):
		noInstructions +=1
		temp = programCounter
		lineParser(programArray[programCounter])
		if(temp==programCounter):
			programCounter = programCounter +1


firstNumber =0
secondNumber = 0


		


message = ""

if args.timer:
	global startTime
	startTime = time.time()

run(args.filename)



if args.statistics:
	for key in instruction_count.keys():
		message+= key + ":	" + str(instruction_count[key])+"\n"
		
if args.timer:
	global endTime
	endTime = time.time()
	message += "\nThe program took " + str(endTime-startTime) +" seconds\n"
if args.n:
	message += "Total number of instructions used were:  " + str(noInstructions)
if (args.timer or args.statistics or args.n):
	print message

