#!/usr/bin/env python3

"""КМЗИ. ЛР№3. Стеганография."""

from PIL import Image
import wave
import numpy


class ImageSteg:
    """Класс для скорытия/извлечения информации из изображений"""

    def __init__(self, image_name):
        '''
        image_name: имя файла с изображением, с которым
            будет работа (сокрытие/извлечение информации)
        '''

        # сразу же пробуем открыть изображение-контейнер
        # если не удастся - будет брошено исключение
        self.cont_img = Image.open(image_name)

        # получаем байты, в которе будем прятать/спрятана информация
        self.raw = bytearray(self.cont_img.tobytes())

    def _set_LSB(self, num, bit):
        """устанавливает младший бит БАЙТА num битом bit"""
        if bit == 0:
            num &= 254
        else:
            num |= 1
        return num

    def hide(self, data, out_fname):
        # создаем копию байт изображения, чтобы можно было
        # использовать один файл как для сокрытия,
        # так и извлечения информации
        raw = bytearray(self.raw)

        # если количество бит, которые необходимо спрятать,
        # больше, чем число байт, в которые можно прятать
        if len(data) * 8 + 20 > len(raw):
            raise Exception('Information file is too large')

        # спрячем размер информационного файла
        inf_size = len(data)
        for i in range(20):  # отведём под размер 20 бит
            raw[i] = self._set_LSB(raw[i], inf_size % 2)
            inf_size //= 2

        # теперь спрячем сам файл
        for i in range(len(data)):
            byte = data[i]  # байт, который будем прятать
            for j in range(8):
                raw[20 + i * 8 + j] = self._set_LSB(
                    raw[20 + i * 8 + j], byte % 2)
                byte //= 2

        # создаем новое изображение на основе изменённых байт
        out_img = Image.frombytes(self.cont_img.mode, self.cont_img.size,
                                  bytes(raw))

        # сохраняем обязательно в .bmp, т.к. иначе будет сжатие
        out_img.save(out_fname, "BMP")

    def extract(self):
        # достанем первые 20 бит - количество спрятанных байт
        size = 0
        for i in range(20):
            size += (self.raw[i] % 2) * (2 ** i)

        # теперь достанем size * 8 бит
        bytes_ = bytearray()
        for j in range(size):
            byte = 0
            for i in range(8):
                byte += (self.raw[20 + j * 8 + i] % 2) * (2 ** i)
            bytes_.append(byte)

        return bytes_


class WaveSteg:
    """Класс для скорытия/извлечения информации из .wav файлов"""

    def __init__(self, wave_name):
        '''
        wave_name: имя .wav файла, с которым
            будет работа (сокрытие/извлечение информации)
        '''

        self.wav = wave.open(wave_name, mode="r")

        # список типов, которые могут использоваться для хранения сэмплов
        self.types = {
            1: numpy.int8,
            2: numpy.int16,
            4: numpy.int32
        }

        # узнаем количество фреймов во входном файле
        n_frames = self.wav.getnframes()

        # узнаем размер (в байтах) одного сэмпла
        samp_width = self.wav.getsampwidth()

        # считываем все фреймы и разбиваем на сэмплы
        content = self.wav.readframes(n_frames)
        self.samples = numpy.fromstring(content, dtype=self.types[samp_width])

        # Теперь у нас есть массив сэмплов аудиопотока.
        # по сути - просто числа, определяющие амплитуду
        # аудиосигнала в каждый момент времени.
        # В них то и будем прятать информацию
        # (или извлекать из них)

    def set_LSB(self, num, bit):
        """устанавливает младший бит ЧИСЛА num битом bit """
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

    def hide(self, data, out_fname):
        samples = numpy.array(self.samples)

        # если количество бит, которые необходимо спрятать,
        # больше, чем число сэмплов
        if len(data) * 8 + 20 > len(samples):
            raise Exception('Information file is too large')

        # спрячем размер информационного файла
        inf_size = len(data)
        for i in range(20):
            samples[i] = self.set_LSB(samples[i], inf_size % 2)
            inf_size //= 2

        # теперь спрячем сам файл
        for i in range(len(data)):
            byte = data[i]  # байт, котоырй будем прятать
            for j in range(8):
                samples[20 + i * 8 + j] = self.set_LSB(
                    samples[20 + i * 8 + j], byte % 2)
                byte //= 2

        # запишем изменённые сэмплы в новый .wav файл
        wav_out = wave.open(out_fname, 'w')
        # параметры выходного .wav совпадают со входным
        wav_out.setparams(self.wav.getparams())
        wav_out.writeframes(samples.tostring())  # а вот сэмплы уже другие
        wav_out.close()

    def extract(self):
        # достанем первые 20 бит - количество спрятанных байт
        size = 0
        for i in range(20):
            size += (self.samples[i] % 2) * (2 ** i)

        # теперь достанем size * 8 бит
        bytes_ = bytearray()
        for j in range(size):
            byte = 0
            for i in range(8):
                byte += (self.samples[20 + j * 8 + i] % 2) * (2 ** i)
            bytes_.append(byte)

        return bytes_


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

    stegs = {'wav': WaveSteg, 'img': ImageSteg}

    try:
        # создаем "стеганографера" выбранного типа
        # для работы с выбранным файлом
        s = stegs[args.type](args.inputFile)
    except Exception as err:
        print("Error: {0}".format(err))
        return -1

    if args.fileForHiding:  # сокрытие файла
        inf = args.fileForHiding.read()
        try:
            s.hide(inf, args.outputFile)
        except Exception as err:
            print("Can't hide information: {0}".format(err))
            return -1

    else:  # извлечение информации
        try:
            data = s.extract()
        except Exception as err:
            print("Can't extract information: {0}".format(err))
            return -1

        with open(args.outputFile, 'wb') as res_file:
            res_file.write(data)


if __name__ == "__main__":
    main()
