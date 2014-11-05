#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""КМЗИ. ЛР№2. AES."""


class AESCoder:

    """класс для шифрования и дешифрования AES
     при создании экземпляра класса необходимо указать,
     какой ключ будет использован
     """

    def __init__(self, key):
        """конструктор класса
        дабы не морочиться с различной длинной ключей,
        будем рассматривать случай, когда ключ 128 байт
        """
        if len(key) != 16:
            raise Exception('Wrong key size, must be 16 bytes!')
        self.Nk = 4  # число 32-х битных слов, составляющих шифроключ
        self.Nb = 4  # число столбцов(32-х битных слов), составляющих State
        self.Nr = 10  # число раундов, которое является функцией Nk и Nb
        self.w = self._key_expansion([ord(x) for x in key])

    def _key_expansion(self, key):
        """ получение ключей для всех раундов """
        # массив, который состоит из битов 32-х разрядного слова
        # и является постоянным для данного раунда
        r_con = [
            [0x00, 0x00, 0x00, 0x00],
            [0x01, 0x00, 0x00, 0x00],
            [0x02, 0x00, 0x00, 0x00],
            [0x04, 0x00, 0x00, 0x00],
            [0x08, 0x00, 0x00, 0x00],
            [0x10, 0x00, 0x00, 0x00],
            [0x20, 0x00, 0x00, 0x00],
            [0x40, 0x00, 0x00, 0x00],
            [0x80, 0x00, 0x00, 0x00],
            [0x1b, 0x00, 0x00, 0x00],
            [0x36, 0x00, 0x00, 0x00]
        ]

        w = [0] * (self.Nb * (self.Nr + 1))  # куда будут сохранены ключи

        for i in range(self.Nk):
            w[i] = [key[4 * i], key[4 * i + 1], key[4 * i + 2], key[4 * i + 3]]
            i += 1

        for i in range(self.Nk, self.Nb * (self.Nr + 1)):
            temp = w[i - 1]
            if i % self.Nk == 0:
                temp = self._sub_word(self._rot_word(temp))
                temp = [temp[j] ^ r_con[i / self.Nk][j] for j in range(4)]
            w[i] = [temp[j] ^ w[i - self.Nk][j] for j in range(4)]
        return w

    def _crypt(self, data128):
        """ функция шифрования блока данных
        данные шифруются блоками по 128 бит (16 байт)
        """
        state = []
        # сначала данные разбиваются на таблицу из 4-х строк и Nb столбцов
        # причем заполнение идёт по столбцам
        for i in range(4):
            state.append(data128[i::self.Nb])

        state = self._add_round_key(state, self.w[0:self.Nb])
        for round in range(1, self.Nr):
            state = self._sub_bytes(state)
            state = self._shift_rows(state)
            state = self._mix_columns(state)
            state = self._add_round_key(
                state, self.w[round * self.Nb:(round + 1) * self.Nb])

        state = self._sub_bytes(state)
        state = self._shift_rows(state)
        state = self._add_round_key(
            state, self.w[self.Nr * self.Nb:(self.Nr + 1) * self.Nb])

        # собираем state в список
        result = []
        for i in range(self.Nb):
            for j in range(4):
                result.append(state[j][i])
        return result

    def _decrypt(self, data128):
        state = []
        for i in range(4):
            state.append(data128[i::self.Nb])

        state = self._add_round_key(
            state, self.w[self.Nr * self.Nb:(self.Nr + 1) * self.Nb])
        for round in range(self.Nr - 1, 0, -1):
            state = self._inv_shift_rows(state)
            state = self._inv_sub_bytes(state)
            state = self._add_round_key(
                state, self.w[self.Nb * round:self.Nb * (round + 1)])
            state = self._inv_mix_columns(state)

        state = self._inv_shift_rows(state)
        state = self._inv_sub_bytes(state)
        state = self._add_round_key(state, self.w[0: self.Nb])

        # собираем state в список
        result = []
        for i in range(self.Nb):
            for j in range(4):
                result.append(state[j][i])
        return result

    def _sub_1_byte(self, byte):
        """ прогонка одного байта через блок нелинейной замены"""
        s_box = [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
                 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
                 0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
                 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
                 0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
                 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
                 0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
                 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
                 0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
                 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
                 0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
                 0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
                 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
                 0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
                 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
                 0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
        return s_box[byte]

    def _inv_sub_1_byte(self, byte):
        """ прогонка одного байта через блок обратной нелинейной замены"""
        inv_s_box = [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
                     0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
                     0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
                     0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
                     0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
                     0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
                     0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
                     0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
                     0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
                     0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
                     0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
                     0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
                     0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
                     0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
                     0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
                     0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d]
        return inv_s_box[byte]

    def _sub_bytes(self, state):
        """трансформации при шифровании, которые обрабатывают State, используя
        нелинейную таблицу замещения байтов(S-box), применяя её независимо к
        каждому байту State
        """
        for i in range(4):
            for j in range(self.Nb):
                state[i][j] = self._sub_1_byte(state[i][j])
        return state

    def _inv_sub_bytes(self, state):
        for i in range(4):
            for j in range(self.Nb):
                state[i][j] = self._inv_sub_1_byte(state[i][j])
        return state

    def _rot_word(self, word):
        """функция, использующаяся в процедуре Key Expansion,
        которая берет 4-х байтное слово и производит над ним
        циклическую перестановку
        """
        return word[1:] + word[:1]

    def _sub_word(self, word4):
        """функция, используемая в процедуре Key Expansion,
        которая берет на входе четырёхбайтное слово и, применяя S-box к каждому
        из четырёх байтов, выдаёт выходное слово
        """
        return [self._sub_1_byte(x) for x in word4]

    def _add_round_key(self, state, round_key):
        """ трансформация при шифровании и обратном шифровании,
        при которой Round Key XOR’ится c State.
        """
        for i in range(4):
            for j in range(self.Nb):
                state[i][j] ^= round_key[i][j]
        return state

    def _shift_rows(self, state):
        """трансформации при шифровании, которые обрабатывают State,
        циклически смещая последние три строки State на разные величины
        """
        for i in range(4):
            state[i] = state[i][i:] + state[i][0:i]
        return state

    def _inv_shift_rows(self, state):
        for i in range(4):
            state[i] = state[i][-i:] + state[i][:-i]
        return state

    def _gmul(self, a, b):
        """ _gmul - умножение двух чисел в поле Галуа"""
        p = 0
        for counter in range(8):
            if b & 1:
                p ^= a
            hi_bit_set = a & 0x80
            a <<= 1
            a &= 0xff
            if hi_bit_set:
                a ^= 0x1b
            b >>= 1
        return p

    def step_mix_columns(self, state, i, i1, i2, i3, i4):
        """Для красоты методов _mix_columns и _inv_mix_columns"""
        return self._gmul(state[i][0], i1) ^ self._gmul(state[i][1], i2) ^ \
            self._gmul(state[i][2], i3) ^ self._gmul(state[i][3], i4)

    def _mix_columns(self, state):
        """В процедуре _mix_columns, четыре байта каждой колонки State
        смешиваются, используя для этого обратимую линейную трансформацию.
        _mix_columns обрабатывает состояния по колонкам, трактуя каждую из них
        как полином четвёртой степени. Над этими полиномами производится
        умножение в поле Галуа. В общем, матан.
        """
        for i in range(self.Nb):  # для всех столбцов таблицы
            b = [0] * 4
            b[0] = self.step_mix_columns(state, i, 2, 3, 1, 1)
            b[1] = self.step_mix_columns(state, i, 1, 2, 3, 1)
            b[2] = self.step_mix_columns(state, i, 1, 1, 2, 3)
            b[3] = self.step_mix_columns(state, i, 3, 1, 1, 2)

            for j in range(4):
                state[i][j] = b[j]
        return state

    def _inv_mix_columns(self, state):
        for i in range(self.Nb):
            b = [0] * 4
            b[0] = self.step_mix_columns(state, i, 14, 11, 13, 9)
            b[1] = self.step_mix_columns(state, i, 9, 14, 11, 13)
            b[2] = self.step_mix_columns(state, i, 13, 9, 14, 11)
            b[3] = self.step_mix_columns(state, i, 11, 13, 9, 14)

            for j in range(4):
                state[i][j] = b[j]
        return state

    def crypt_list(self, input_):
        """шифрование input
        на выходе - зашифрованные данные (список байт) и количество
        нулевых байт, вставленных для выравнивания длинны
        (кратной 16 байтам (128 битам))
        """
        # первым делом переведём символы (байты) в int
        input_ = [ord(x) for x in input_]

        output = []
        for i in range(len(input_) / 16):
            output += self._crypt(input_[i * 16: (i + 1) * 16])

        last_len = len(input_) % 16
        n_zeroes = 16 - last_len
        last_part = input_[-last_len::] + [0] * n_zeroes
        output += self._crypt(last_part)
        return [chr(n_zeroes)] + [chr(x) for x in output]

    def decrypt_list(self, input_):
        n_zeroes = ord(input_[0])
        input_ = [ord(x) for x in input_[1:]]

        output = []
        for i in range(len(input_) / 16):
            output += self._decrypt(input_[i * 16: (i + 1) * 16])

        output = output[:-n_zeroes]  # избавимся от фиктивных нулей в конце
        return [chr(x) for x in output]


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog="aes", description="2nd lab for cryptographic methods "
                                "of information security. AES.")
    parser.add_argument('inFile', type=argparse.FileType(mode='rb'),
                        help="input file")
    parser.add_argument('keyFile', type=argparse.FileType(mode='rb'),
                        help="file with key")
    parser.add_argument('outFile', type=argparse.FileType(mode='wb'),
                        help="output file")
    parser.add_argument('cryptOrDecrypt', choices=['c', 'd'],
                        help="crypt or decrypt")
    return parser.parse_args()


def main():
    args = get_args()

    # пытаемся создать шифратор с данным ключом
    try:
        coder = AESCoder(args.keyFile.read())
    except Exception as err:
        print("Error: {0}".format(err))
        return -1

    funcs = {'c': coder.crypt_list, 'd': coder.decrypt_list}
    res = funcs[args.cryptOrDecrypt](args.inFile.read())
    args.outFile.write(''.join(res))


if __name__ == "__main__":
    main()
