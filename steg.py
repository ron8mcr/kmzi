#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""КМЗИ. ЛР№3. Стеганография."""

# =============================== ИЗОБРАЖЕНИЯ ===============================
from PIL import Image


def set_lsb(num, bit):
    """устанавливает младший бит БАЙТА num битом bit"""
    if bit == 0:
        num &= 254
    else:
        num |= 1
    return num


def hiding_to_image(container_fname, inf, out_fname):
    # пытаемся открыть изображение-контейнер
    # если не удастся - будет брошено исключение
    cont_img = Image.open(container_fname)

    # получаем байты, в младшие биты которых будем записывать
    # полезную информацию
    raw = list(cont_img.tobytes())

    # если количество бит, которые необходимо спрятать,
    # больше, чем число байт, в которые можно прятать
    if len(inf) * 8 + 20 > len(raw):
        raise Exception('Information file is too large')

    # спрячем размер информационного файла
    inf_size = len(inf)
    for i in range(20):  # отведём под размер 20 бит
        raw[i] = chr(set_lsb(ord(raw[i]), inf_size % 2))
        inf_size /= 2

    # теперь спрячем сам файл
    for i in range(len(inf)):
        byte = ord(inf[i])  # байт, который будем прятать
        for j in range(8):
            raw[20 + i * 8 + j] = chr(
                set_lsb(ord(raw[20 + i * 8 + j]), byte % 2))
            byte /= 2

    # создаем новое изображение на основе изменённых байт
    out_img = Image.frombytes(cont_img.mode, cont_img.size, ''.join(raw))

    # сохраняем обязательно в .bmp, т.к. иначе будет сжатие
    out_img.save(out_fname, "BMP")


def extracting_from_image(container):
    in_img = Image.open(container)

    # получаем байты, в младших битах которых спрятан файл
    raw = list(in_img.tobytes())

    # достанем первые 20 бит - количество байт, спрятанных в остальной части
    size = 0
    for i in range(20):
        size += (ord(raw[i]) % 2) * (2 ** i)

    # теперь достанем size * 8 бит
    byte_list = []
    for j in range(size):
        byte = 0
        for i in range(8):
            byte += (ord(raw[20 + j * 8 + i]) % 2) * (2 ** i)

        byte_list.append(byte)

    # возвращаем список полученных байт
    return [chr(x) for x in byte_list]


# =============================== МУЗЫКА ===============================
import wave
import numpy


def set_last_bit(num, bit):
    """устанавливает младший бит ЧИСЛА num битом bit
    set_lsb не подходит, т.к. в данном случае нет гарантии,
    что число занимает 1 байт
    """
    if num % 2:  # если последний бит числа равен 1
        if bit == 0:
            return num + 1
        else:
            return num
    else:  # если последний бит числа равен 0
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


def hiding_to_wav(container_fname, inf, out_fname):
    # попытаемся открыть .wav файл, в который будем прятать информацию.
    wav = wave.open(container_fname, mode="r")

    # узнаем количество фреймов во входном файле
    n_frames = wav.getnframes()

    # узнаем размер (в байтах) одного сэмпла
    samp_width = wav.getsampwidth()

    # считываем все фреймы и разбиваем на сэмплы
    content = wav.readframes(n_frames)
    samples = numpy.fromstring(content, dtype=types[samp_width])

    # Теперь у нас есть массив сэмплов аудиопотока.
    # по сути - просто числа, определяющие амплитуду
    # аудиосигнала в каждый момент времени.
    # В них то и будем прятать

    # если количество бит, которые необходимо спрятать,
    # больше, чем число сэмплов
    if len(inf) * 8 + 20 > len(samples):
        raise Exception('Information file is too large')

    # спрячем размер информационного файла
    inf_size = len(inf)
    for i in range(20):
        samples[i] = set_last_bit(samples[i], inf_size % 2)
        inf_size /= 2

    # теперь спрячем сам файл
    for i in range(len(inf)):
        byte = ord(inf[i])  # байт, котоырй будем прятать
        for j in range(8):
            samples[20 + i * 8 + j] = set_last_bit(
                samples[20 + i * 8 + j], byte % 2)
            byte /= 2

    # запишем изменённые сэмплы в новый .wav файл
    wav_out = wave.open(out_fname, 'w')
    # параметры выходного .wav совпадают со входным
    wav_out.setparams(wav.getparams())
    wav_out.writeframes(samples.tostring())  # а вот сэмплы уже другие


def extracting_from_wav(container):
    wav = wave.open(container, mode="r")
    n_frames = wav.getnframes()
    samp_width = wav.getsampwidth()
    content = wav.readframes(n_frames)
    samples = numpy.fromstring(content, dtype=types[samp_width])

    # достанем первые 20 бит - количество байт, спрятанных в остальной части
    size = 0
    for i in range(20):
        size += (samples[i] % 2) * (2 ** i)

    # теперь достанем size * 8 бит
    byte_list = []
    for j in range(size):
        byte = 0
        for i in range(8):
            byte += (samples[20 + j * 8 + i] % 2) * (2 ** i)

        # в curByte - очередной байт числа
        # запишем его в массив
        byte_list.append(byte)

    # возвращаем список полученных байт
    return [chr(x) for x in byte_list]


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog="steg", description="3rd lab for cryptographic methods of "
                                 "information security. "
                                 "Steganoraphy to images and music.")
    parser.add_argument('type', choices=['wav', 'img'], help="Wav or Image")
    parser.add_argument('inputFile', help="image or wav container ")
    parser.add_argument('outputFile',
                        help="output file (wav/BMP or hidden file)")
    parser.add_argument('fileForHiding', nargs='?',
                        type=argparse.FileType(mode='rb'),
                        help="file for hiding")
    return parser.parse_args()


def main():
    args = get_args()

    funcs = {'hiding':
             {'img': hiding_to_image, 'wav': hiding_to_wav},
             'extracting':
                 {'img': extracting_from_image, 'wav': extracting_from_wav}
             }

    if args.fileForHiding:  # сокрытие файла
        inf = args.fileForHiding.read()
        func = funcs['hiding'][args.type]
        try:
            func(args.inputFile, inf, args.outputFile)
        except Exception as err:
            print("Error: {0}".format(err))
            return -1

    else:  # извлечение информации
        func = funcs['extracting'][args.type]
        try:
            file_content = func(args.inputFile)
        except Exception as err:
            print("Error: {0}".format(err))
            return -1

        res_file = open(args.outputFile, 'wb')
        res_file.write(''.join(file_content))
        res_file.close()


if __name__ == "__main__":
    main()
