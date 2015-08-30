__author__ = 'Diogo Alves'


class Crc:

    order = ""
    polynom = ""
    init = ""
    xor = ""
    reflect0 = False
    reflect1 = False
    direct = False
    data = ""
    result = ""

    def __init__(self):
        pass

    def setCRC8(self):
        """
        Sets the CRC Calculation tothe CRC8. The values are set as follow:
        Width = 8 bits
        Truncated Polynomial = 0x01
        Initial Value = 0x0000
        Data is reflected
        Output is reflected
        No XOR is performed on the output CRC
        """
        self.reflect1 = True
        self.direct = True
        self.reflect0 = True
        self.init = "0"
        self.xor = "0"
        self.order = "8"
        self.polynom = "1"

    def setCRCccitt(self):
        """
        Sets the CRC Calculation tothe CRC16-CCITT. The values are set as follow:
        Width = 16 bits
        Truncated Polynomial = 0x1021
        Initial Value = 0xFFFF
        Data is not reflected
        Output is not reflected
        No XOR is performed on the output CRC
        """
        self.order = "16"
        self.polynom = "1021"
        self.init = "ffff"
        self.xor = ""
        self.reflect0 = False
        self.reflect1 = False
        self.direct = True

    def setCRC16(self):
        """
        Sets the CRC Calculation to the CRC16. The values are set as follow:
        Width = 16 bits
        Truncated Polynomial = 0x8005
        Initial Value = 0x0000
        Data is reflected
        Output is reflected
        No XOR is performed on the output CRC
        """
        self.order = "16"
        self.polynom = "8005"
        self.init = "0"
        self.xor = "0"
        self.reflect0 = True
        self.reflect1 = True
        self.direct = True

    def setCRC32(self):
        """
        Sets the CRC Calculation to the CRC32. The values are set as follow:
        Width = 32 bits
        Truncated Polynomial = 0x4c11db7
        Initial Value = 0xffffffff
        Data is reflected
        Output is reflected
        XOR is performed on the output CRC
        """
        self.order = "32"
        self.polynom = "4c11db7"
        self.init = "ffffffff"
        self.xor = "ffffffff"
        self.reflect0 = True
        self.reflect1 = True
        self.direct = True

    def compute(self):
        """
        Computes the CRC with the selected values and store the result at self.result
        """
        i = 0
        j = 0
        k = 0
        bit = False
        datalen = 0
        lenght = 0
        flag = False
        counter = 0
        c = 0
        crc = ["", "", "", "", "", "", "", "", ""]
        mask = ["", "", "", "", "", "", "", ""]
        init = ["", "", "", "", "", "", "", ""]
        hexnum = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]

        data = ""
        order = ""
        polynom = ["", "", "", "", "", "", "", ""]
        xor = ["", "", "", "", "", "", "", ""]

        # Check if parameters are present
        if self.order == "" or self.polynom == "" or self.init == "" or self.xor == "":
            raise Exception("Invalid Parameters")

        # Convert CRC Order
        order = int(self.order, 10)
        if order < 1 or order > 64:
            raise Exception("CRC order must be between 1 and 64")

        #Convert CRC Polynom
        polynom = self.convertentry(self.polynom, order)
        if polynom[0] < 0:
            raise Exception("Invalid CRC polynom")

        if not(polynom[7] & 1):
            raise Exception("CRC polynom LSB must be set")

        init = self.convertentry(self.init, order)
        if init[0] < 0:
            raise Exception("Invalid initial value")

        # Convert CRC XOR value
        xor = self.convertentry(self.xor, order)
        if xor[0] < 0:
            raise Exception("Invalid XOR value")

        # Generate bit mask
        counter = order
        for i in range(7, -1, -1):
            if counter >= 8:
                mask[i] = 255
            else:
                mask[i] = (1 << counter) - 1
            counter -= 8

            if counter < 0:
                counter = 0
        crc = init

        if self.direct:  # Non Direct -> Direct
            crc.append(0)

            for i in range(0, order):
                bit = crc[7-((order-1) >> 3)] & (1 << ((order-1) & 7))
                for k in range(0, 8):
                    crc[k] = ((crc[k] << 1) | (crc[k+1] >> 7)) & mask[k]
                    if bit:
                        crc[k] ^= polynom[k]

        data = self.data
        datalen = len(data)
        lenght = 0  # number of data bytes

        crc.append(0)

        for i in range(0, datalen):
            c = ord(data[i])
            if data[i] == '%':
                if i > datalen-3:
                    raise Exception("Invalid data Sequence")
                try:
                    ch = int(data[++i], 16)
                except ValueError:
                    raise Exception("Invalid data Sequence")
                c = (c & 15) | ((ch & 15) << 4)

            # perform revin
            if self.reflect0:
                c = self.reflectByte(c)

            # rotate one data byte including crcmask
            for j in range(0,8):
                bit = 0
                if crc[7-((order-1) >> 3)] & (1 << ((order-1) & 7)):
                    bit = 1
                if c & 0x80:
                    bit ^= 1
                c <<= 1

                for k in range(0,8):  # Rotate all (max 8) crc bytes
                    crc[k] = ((crc[k] << 1) | (crc[k+1] >> 7)) & mask[k]
                    if bit:
                        crc[k] ^= polynom[k]
                lenght += 1
        # perform revout
        if self.reflect1:
            crc = self.reflect(crc, order, 0)

        # perform xor value
        for i in range(0, 8):
            crc[i] ^= xor[i]

        # write results
        self.result = ""
        flag = 0

        for i in range(0,8):
            actchar = crc[i] >> 4
            if flag or actchar:
                self.result += hexnum[actchar]
                flag=1
            actchar = crc[i] & 15
            if flag or actchar or i == 7:
                self.result += hexnum[actchar]
                flag = 1

    def revpoly(self):
        """
        Reverses the polynom
        """
        # reverses poly
        polynom = ["", "", "", "", "", "", "", "", ""]
        order = 0
        actchar = ""
        flag = False
        hexnum = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]

        self.result = ""

        #  convert crc order
        try:
            order = int(self.order, 10)
        except ValueError:
            raise Exception("CRC order must be between 1 and 64")

        # convert crc polynom
        polynom = self.convertentry(self.polynom, order)
        if polynom[0] < 0:
            raise Exception("Invalid CRC polynom")

        # check if polynom is valid
        if not (polynom[7] & 1):
            raise Exception("CRC polynom LSB must be set")

        # compute reversed polynom

        polynom = self.reflect(polynom, order, 1)

        # write result

        self.polynom = ""

        flag = 0

        for i in range(0, 8):
            actchar = polynom[i] >> 4
            if flag or actchar:
                self.polynom += hexnum[actchar]
                flag = 1

            actchar = polynom[i] & 15
            if flag or actchar or i == 7:
                self.polynom += hexnum[actchar]
                flag = 1

    def reflectByte(self, inbyte):
        """
        Reflects a byte
        :param inbyte: input byte
        :return: reflected input byte
        """
        outbyte = 0
        i = 0x01
        j = 0x80

        while j != 0:
            if inbyte & i:
                outbyte |= j
            i <<= 1
            j>>=1
        return outbyte

    def reflect(self, crc, bitnum, startLSB):
        """
        Reflect a number of bits starting a the lowest bit defined by startLSB
        :param crc: the current crc hash
        :param bitnum: the number of bits to reflect
        :param startLSB: the index of the the LSB
        :return: returns a crc with the reflected bits
        """
        # reflect bitnum bits starting at lowest bit = startLSB
        i = 0
        j = 0
        k = 0
        iw = 0
        jw = 0
        bit = 0

        while k+startLSB < bitnum-1-k:
            iw = 7-((k+startLSB) >> 3)
            jw = 1 << ((k+startLSB) & 7)
            i = 7-((bitnum-1-k) >> 3)
            j = 1 << ((bitnum-1-k) & 7)

            bit = crc[iw] & jw
            if crc[i] & j:
                crc[iw] |= jw
            else:
                crc[iw] &= (0xff-jw)
            if bit:
                crc[i] |= j
            else:
                crc[i] &= (0xff-j)

            k += 1
        return crc

    def convertentry(self, input, order):
        """
        Converts from a ASCII value to another base value
        :param input: string input value
        :param order: base order
        :return:
        """
        # convert from ascii to hexadecimal value
        lenght = 0
        actchar = 0
        polynom = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        brk = [-1, 0, 0, 0, 0, 0, 0, 0]

        #convert crc value into byte sequence
        lenght = len(input)
        for i in range(0, lenght):
            try:
                actchar = int(input[i], 16)
            except ValueError:
                return brk
            actchar &=15
            for j in range(0, 8):
                polynom[j] = ((polynom[j] << 4) | (polynom[j+1] >> 4 )) & 255
            polynom[7] = ((polynom[7] << 4) | actchar) & 255

        # compute and check crc order
        count = 64
        for i in range(0, 8):
            j = 0x80
            while j > 0:
                if polynom[i] & j:
                    break
                count -= 1
                j >>= 1
            if polynom[i] & j:
                break
        if count > order:
            return brk
        return polynom
