import decimal
import re

from collections import namedtuple

Prefix = namedtuple("Prefix", "name symbol exp")

YOTTA = Prefix("yotta", "Y", 24)
ZETTA = Prefix("zetta", "Z", 21)
EXA = Prefix("exa", "E", 18)
PETA = Prefix("peta", "P", 15)
TERA = Prefix("tera", "T", 12)
GIGA = Prefix("giga", "G", 9)
MEGA = Prefix("mega", "M", 6)
KILO = Prefix("kilo", "k", 3)
HECTO = Prefix("hecto", "h", 2)
DECA = Prefix("deca", "da", 1)
NO_PREFIX = Prefix("", "e+0", 0)
DECI = Prefix("deci", "d", -1)
CENTI = Prefix("centi", "c", -2)
MILLI = Prefix("milli", "m", -3)
MICRO = Prefix("micro", "u", -6)
NANO = Prefix("nano", "n", -9)
PICO = Prefix("pico", "p", -12)
FEMTO = Prefix("femto", "f", -15)
ATTO = Prefix("atto", "a", -18)
ZEPTO = Prefix("zepto", "z", -21)
YOCTO = Prefix("yocto", "y", -24)

SI_PREFIXES = [
    YOTTA,
    ZETTA,
    EXA,
    PETA,
    TERA,
    GIGA,
    MEGA,
    KILO,
    HECTO,
    DECA,
    NO_PREFIX,
    DECI,
    CENTI,
    MILLI,
    MICRO,
    NANO,
    PICO,
    FEMTO,
    ATTO,
    ZEPTO,
    YOCTO,
]
SI_PREFIX_SYM = [x.symbol for x in SI_PREFIXES if x.symbol not in ("e+0", "da")]

CRE_SI_NUMBER = re.compile(
    r"\s*(?P<sign>[\+\-><])?"
    r"(?P<integer>\d*)"
    r"(\.(?P<fraction>\d*))?"
    r"\s*(?P<sipre>e\+0|da|[%s])?\s*" % "".join(SI_PREFIX_SYM)
).match


class EngDecimal(decimal.Decimal):
    def __new__(cls, value="0", context=None, prefix=None):
        self = decimal.Decimal.__new__()

        if isinstance(value, str):
            m = CRE_SI_NUMBER(value.strip())
            if m.group("sipre") is None:
                self = super(EngDecimal, cls).__new__(cls, value=value, context=context)
                self.prefix = prefix or NO_PREFIX
                self._exp += self.prefix.exp
                return self

            if m.group("sign") == "-":
                self._sign = 1
            else:
                self._sign = 0
            intpart = m.group("integer")
            if intpart is not None:
                fracpart = m.group("fraction") or ""
                _prefix = [x for x in SI_PREFIXES if x.symbol == m.group("sipre")]
                if len(_prefix) > 0:
                    _prefix = _prefix[0]
                else:
                    _prefix = prefix or NO_PREFIX
                self._int = str(int(intpart + fracpart))
                self._exp = _prefix.exp - len(fracpart)
                self._is_special = False
                self.prefix = _prefix
            return self
        else:
            self = super(EngDecimal, cls).__new__(cls, value=value, context=context)
            self.prefix = prefix or NO_PREFIX
            self._exp += self.prefix.exp
        return self

    def __str__(self, eng=False, context=None, asprefix=None):
        """Return string representation of the number in scientific notation.

        Captures all of the information in the underlying representation.
        """

        sign = ["", "-"][self._sign]
        if self._is_special:
            if self._exp == "F":
                return sign + "Infinity"
            elif self._exp == "n":
                return sign + "NaN" + self._int
            else:  # self._exp == 'N'
                return sign + "sNaN" + self._int

        # number of digits of self._int to left of decimal point
        if asprefix is None:
            leftdigits = self._exp + len(self._int)
            sym = ""
        else:
            leftdigits = self._exp - asprefix.exp + len(self._int)
            sym = " " + asprefix.symbol

        # dotplace is number of digits of self._int to the left of the
        # decimal point in the mantissa of the output string (that is,
        # after adjusting the exponent)
        if self._exp == 0:
            # no exponent required
            dotplace = leftdigits
        elif not eng:
            # usual scientific notation: 1 digit on left of the point
            dotplace = 1
        elif self._int == "0":
            # engineering notation, zero
            dotplace = (leftdigits + 1) % 3 - 1
        else:
            # engineering notation, nonzero
            dotplace = (leftdigits - 1) % 3 + 1

        if dotplace <= 0:
            intpart = "0"
            fracpart = "." + "0" * (-dotplace) + self._int
        elif dotplace >= len(self._int):
            intpart = self._int + "0" * (dotplace - len(self._int))
            fracpart = ""
        else:
            intpart = self._int[:dotplace]
            fracpart = "." + self._int[dotplace:]
        if leftdigits == dotplace:
            exp = ""
        else:
            if context is None:
                context = decimal.getcontext()
            exp = ["e", "E"][context.capitals] + "%+d" % (leftdigits - dotplace)

        return sign + intpart + fracpart + exp + sym

    def to_si_string(self, context=None, hidesym="", asprefix=None):
        """Convert to SI prefix-type string.

        Use the SI prefix to represent the exponent part of the number.
        """
        if asprefix is None:
            sEng = self.__str__(eng=True, context=context)
            n = None
            exp = None
            if "E" in sEng:
                n, exp = sEng.split("E")
            elif "e" in sEng:
                n, exp = sEng.split("e")
            else:
                n = sEng
                exp = 0
            exp = int(exp)
            pre = [x for x in SI_PREFIXES if x.exp == exp]
            if pre[0].symbol == hidesym:
                return n
            return n + " " + pre[0].symbol
        else:
            return self.__str__(eng=True, context=context, asprefix=asprefix)


def dec_to_si_string(dec, hidesym=""):
    """Convert to SI prefix-type string.

    Use the SI prefix to represent the exponent part of the number.
    """
    sEng = dec.to_eng_string()
    n = None
    exp = None
    if "E" in sEng:
        n, exp = sEng.split("E")
    elif "e" in sEng:
        n, exp = sEng.split("e")
    else:
        n = sEng
        exp = 0
    exp = int(exp)
    pre = [x for x in SI_PREFIXES if x.exp == exp]
    if pre[0].symbol == hidesym:
        return n
    return n + " " + pre[0].symbol
