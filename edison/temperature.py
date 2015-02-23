from math import exp, log1p
import mraa


ADBITS = 10.0
VCC = 5.0
THERMISTER_REFERENCE_RESISTENCE = 10000.0
THERMISTER_REFERENCE_TEMP = 25.0
REFERENCE_RESISTANCE = 10000.0
BETA = 3750.0


# Temperature calculation section, nasty formula below
# beta/(ln(((vcc/analogin/(2^ADbits)*vcc))-1)*Lowerlegres/(thermistorr25*e^(-beta/298))))-273
def convert_to_celsius(temp_read_value):
    thermister_resistance = (
        VCC / (
            (temp_read_value / (2 ** ADBITS) * VCC)
            ) - 1) * REFERENCE_RESISTANCE
    return BETA / (
        log1p(
            thermister_reseistance / (
                THERMISTER_REFERENCE_RESISTENCE *
                exp(-BETA /(273 + THERMISTER_REFERENCE_TEMP))))) - 273

def read_temperature():
    return convert_to_celsius(mraa.Aio(0).read())
