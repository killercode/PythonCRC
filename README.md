# PythonCRC
A CRC Flexible and easy to use calculator module

# How to use
This module is very easy to use.
Just instantiate the class, choose what CRC type you want and compute.

Sample:

    import crc
    
    crccalc = crc()
    crccalc.setCRC8()  # Let's calculate the CRC8 of a value
    crccalc.data = "My Data"
    crccalc.compute()
    print crccalc.result
    
You can costumize the CRC calculation by setting manually the definitions like
Base Order, Polynom, Init Value, XOR Value, Reflection, and direct or non direct calculation.

Hope you like :)
