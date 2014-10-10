#!/usr/bin/python
# -*- coding: UTF-8 -*-

# КМЗИ. ЛР№1. Шифр Вижинера
def getArgs():
	import argparse
	parser = argparse.ArgumentParser(prog = "vizh", description="1st lab for cryptographic methods of information security. Vigenere cipher.")
	parser.add_argument ('inFile', type = argparse.FileType(mode='rb'), help = "input file")
	parser.add_argument ('keyFile', type = argparse.FileType(mode='rb'), help = "file with key")
	parser.add_argument ('outFile', type = argparse.FileType(mode='wb'), help = "output file")
	parser.add_argument ('cryptOrDecrypt', choices=['c', 'd'], help = "crypt or decrypt")
 	return parser.parse_args()
	
def vizhCrypt(inputList, keyList):
	if len(keyList) == 0:
		raise Exception, 'Vizhiner key is empty'
	return [chr(( ord(inputList[i]) + ord(keyList[i % len(keyList)] )) % 256) for i in range(len(inputList))]
	
def vizhDecrypt(inputList, keyList):
	if len(keyList) == 0:
		raise Exception, 'Vizhiner key is empty'
	return [chr(( ord(inputList[i]) - ord(keyList[i % len(keyList)] )) % 256) for i in range(len(inputList))]
	
def main():	
	args = getArgs()
	try:
		if (args.cryptOrDecrypt == 'c'):
			res = vizhCrypt(list(args.inFile.read()), list(args.keyFile.read()))
		else:
			res = vizhDecrypt(list(args.inFile.read()), list(args.keyFile.read()))
	except Exception as err:
		print("Error: {0}".format(err))
		return
			
	args.outFile.write(''.join(res))

if __name__ == "__main__":
	main()
