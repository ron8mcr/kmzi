#!/usr/bin/python
# -*- coding: UTF-8 -*-

# КМЗИ. ЛР№3. Стеганография.
	
# =============================== ИЗОБРАЖЕНИЯ ===============================
from PIL import Image

# устанавливает младший бит БАЙТА num битом bit
def setLSB(num, bit):
	if bit == 0:
		num = num & 254
	else:
		num = num | 1
	return num

def hidingToImage(containerFName, inf):
	# пытаемся открыть изображение-контейнер
	# если не удастся - будет брошено исключение
	contImg = Image.open(containerFName)
	
	# получаем байты, в младшие биты которых будем записывать
	# полезную информацию
	raw = list(contImg.tobytes())
	
	# если количество бит, которые необходимо спрятать, больше, чем число байт, в которые можно прятать
	if len(inf) * 8 + 20 > len(raw):
		raise Exception, 'Information file is too large'
	
	# спрячем размер информационного файла
	infSize = len(inf)
	for i in range(20): # отведём под размер 20 бит
		raw[i] = chr(setLSB(ord(raw[i]), infSize % 2))
		infSize /= 2
		
	# теперь спрячем сам файл
	for i in range (len(inf)):
		byte = ord(inf[i]) # байт, который будем прятать
		for j in range (8):
			raw[20 + i * 8 + j] = chr(setLSB(ord(raw[20 + i * 8 + j]), byte % 2))
			byte /= 2
	
	# создаем новое изображение на основе изменённых байт
	outImg = Image.frombytes(contImg.mode, contImg.size, ''.join(raw)) 
	#contImg.close()
	return outImg
	
def extractingFromImage(container):
	inimg = Image.open(container)
	
	# получаем байты, в младших битах которых спрятан файл
	raw = list(inimg.tobytes())

	# достанем первые 20 бит - количество байт, спрятанных в остальной части
	size = 0
	for i in range(20):
		size += (ord(raw[i]) % 2) * (2 ** i)
		
	# теперь достанем size * 8 бит	
	byteList = []
	for j in range (size):
		byte = 0
		for i in range (8):
			byte += (ord(raw[20 + j * 8 + i]) % 2) * (2 ** i)

		byteList.append(byte)
	
	# возвращаем список полученных байт
	return [chr(x) for x in byteList]
	

	
# =============================== МУЗЫКА ===============================
import wave
import numpy

# устанавливает младший бит ЧИСЛА num битом bit
# setLSB не подходит, т.к. в данном случае нет гарантии, что число занимает 1 байт
def setLastBit(num, bit):
	if num % 2: # если последний бит числа равен 1
		if bit == 0:
			return num + 1
		else:
			return num
	else: # если последний бит числа равен 0
		if bit == 1:
			return num + 1
		else:
			return num

# список типов, которые могут использоваться для хранения сэмплов
types = {
    1: numpy.int8,
    2: numpy.int16,
    4: numpy.int32
}

def hidingToWav(containerFName, inf, outFName):
	# попытаемся открыть .wav файл, в который будем прятать информацию, 
	wav = wave.open(containerFName, mode="r")
		
	nframes = wav.getnframes() # узнаем количество фреймов во входном файле	
	
	# узнаем размер (в байтах) одного сэмпла
	sampwidth = wav.getsampwidth()

	# считываем все фреймы и разбиваем на сэмплы
	content = wav.readframes(nframes)
	samples = numpy.fromstring(content, dtype=types[sampwidth])
	
	# Теперь у нас есть массив сэмплов аудиопотока.
	# по сути - просто числа, определяющие амплитуду аудиосигнала в каждый момент времени.
	# в них то и будем прятать
		
	if len(inf) * 8 + 20 > len(samples): # если количество бит, которые необходимо спрятать, больше, чем число сэмплов
		raise Exception, 'Information file is too large'
		
	# спрячем размер информационного файла
	infSize = len(inf)
	for i in range(20):
		samples[i] = setLastBit(samples[i], infSize % 2)
		infSize /= 2
		
	# теперь спрячем сам файл
	for i in range(len(inf)):
		byte = ord(inf[i]) # байт, котоырй будем прятать
		for j in range (8):
			samples[20 + i * 8 + j] = setLastBit(samples[20 + i * 8 + j], byte % 2)
			byte /= 2
		
	# запишем изменённые сэмплы в новый .wav файл
	wavOut = wave.open(outFName, 'w')
	wavOut.setparams( wav.getparams() ) # параметры выходного .wav совпадают со входным
	wavOut.writeframes(samples.tostring()) # а вот сэмплы уже другие	
	
	
def extractingFromWav(container):
	wav = wave.open(container, mode="r")	
	nframes = wav.getnframes()
	sampwidth = wav.getsampwidth()
	content = wav.readframes(nframes)
	samples = numpy.fromstring(content, dtype=types[sampwidth])
	
	# достанем первые 20 бит - количество байт, спрятанных в остальной части
	size = 0
	for i in range(20):
		size += (samples[i] % 2) * (2 ** i)
		
	# теперь достанем size * 8 бит	
	byteList = []
	for j in range (size):
		byte = 0
		for i in range (8):
			byte += (samples[20 + j * 8 + i] % 2) * (2 ** i)
		
		# в curByte - очередной байт числа
		# запишем его в массив
		byteList.append(byte)

	# возвращаем список полученных байт
	return [chr(x) for x in byteList]
	
	

def getArgs():
	import argparse
	parser = argparse.ArgumentParser(prog = "steg", description="3rd lab for cryptographic methods of information security. Steganoraphy to images and music.")
	parser.add_argument ('type', choices=['w', 'i'], help = "Wav or Image")
	parser.add_argument ('input_file', help = "image or wav container ")
	parser.add_argument ('output_file',  help = "output file (wav/BMP or hidden file)")
	parser.add_argument ('file_for_hiding', nargs='?', type = argparse.FileType(mode='rb'), help = "file for hiding")
 	return parser.parse_args()

def main():	
	args = getArgs()
	
	if args.type == 'i': # стеганография в изображения
		if args.file_for_hiding: # сокрытие файла
			try:
				# считываем содержимое ифнормационного файла
				inf = list(args.file_for_hiding.read())
				args.file_for_hiding.close()
	
				outImg = hidingToImage(args.input_file, inf)
			except Exception as err:
				print("Error: {0}".format(err))
				return -1
			# сохраняем обязательно в .bmp, т.к. иначе будет сжатие
			outImg.save(args.output_file, "BMP")
			
		else: # извлечение информации из изображения
			try:
				fileContent = extractingFromImage(args.input_file)
			except Exception as err:
				print("Error: {0}".format(err))
				return -1
				
			resfile = open(args.output_file, 'wb')
			resfile.write(''.join( fileContent ))
			resfile.close()
	
	else: # стеганография в музыку
	# модули Wave и Image устроены по-разному,
	# поэтому и обращение несколько иное
		if args.file_for_hiding:
			try:
				# считываем содержимое ифнормационного файла
				inf = list(args.file_for_hiding.read())
				args.file_for_hiding.close()				
				hidingToWav(args.input_file, inf, args.output_file)
			except Exception as err:
				print("Error: {0}".format(err))
				return -1
			
		else:
			try:
				fileContent = extractingFromWav(args.input_file)
			except Exception as err:
				print("Error: {0}".format(err))
				return -1
				
			resfile = open(args.output_file, 'wb')
			resfile.write(''.join( fileContent ))
			resfile.close()
	
if __name__ == "__main__":
	main()
