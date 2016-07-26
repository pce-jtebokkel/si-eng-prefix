from __future__ import division

import decimal
import re

from collections import namedtuple
Prefix = namedtuple('Prefix', 'name symbol exp')

YOTTA = Prefix('yotta', 'Y', 24)
ZETTA = Prefix('zetta', 'Z', 21)
EXA = Prefix('exa', 'E', 18)
PETA = Prefix('peta', 'P', 15)
TERA = Prefix('tera', 'T', 12)
GIGA = Prefix('giga', 'G', 9)
MEGA = Prefix('mega', 'M', 6)
KILO = Prefix('kilo', 'k', 3)
HECTO = Prefix('hecto', 'h', 2)
DECA = Prefix('deca', 'da', 1)
NO_PREFIX = Prefix('', '', 0)
DECI = Prefix('deci', 'd', -1)
CENTI = Prefix('centi', 'c', -2)
MILLI = Prefix('milli', 'm', -3)
MICRO = Prefix('micro', 'u', -6)
NANO = Prefix('nano', 'n', -9)
PICO = Prefix('pico', 'p', -12)
FEMTO = Prefix('femto', 'f', -15)
ATTO = Prefix('atto', 'a', -18)
ZEPTO = Prefix('zepto', 'z', -21)
YOCTO = Prefix('yocto', 'y', -24)

SI_PREFIXES = [YOTTA,
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
               YOCTO]
SI_PREFIX_SYM = [x.symbol for x in SI_PREFIXES]
CRE_SI_NUMBER = re.compile(r'\s*(?P<sign>[\+\-><])?'
                           r'(?P<integer>\d*)'
                           r'(\.(?P<fraction>\d*))?'
                           r'\s*(?P<sipre>[%s])?\s*' % ''.join(SI_PREFIX_SYM)).match


class EngDecimal(decimal.Decimal):
    def __new__(cls, value="0", context=None, prefix=None):
        try:
            self = super(EngDecimal, cls).__new__(cls, value=value, context=context)
        except (decimal.ConversionSyntax, decimal.InvalidOperation) as e:
            self = object.__new__(cls)

            if isinstance(value, str) or isinstance(value, unicode):
                m = CRE_SI_NUMBER(value.strip())
                if m is None:
                    raise e

                if m.group('sign') == '-':
                    self._sign = 1
                else:
                    self._sign = 0
                intpart = m.group('integer')
                if intpart is not None:
                    fracpart = m.group('fraction') or ''
                    _prefix = [x for x in SI_PREFIXES if x.symbol == m.group('sipre')]
                    if len(_prefix) > 0:
                        _prefix = _prefix[0]
                    else:
                        _prefix = prefix or NO_PREFIX
                    self._int = str(int(intpart+fracpart))
                    self._exp = _prefix.exp - len(fracpart)
                    self._is_special = False
                    self.prefix = _prefix
                return self
            raise e
        self.prefix = prefix or NO_PREFIX
        self._exp += self.prefix.exp
        return self

    def to_si_string(self, context=None):
        """Convert to SI prefix-type string.

        Use the SI prefix to represent the exponent part of the number.
        """
        sEng = self.__str__(eng=True, context=context)
        n = None
        exp = None
        if 'E' in sEng:
            n, exp = sEng.split('E')
        elif 'e' in sEng:
            n, exp = sEng.split('e')
        else:
            n = sEng
            exp = 0
        exp = int(exp)
        pre = [x for x in SI_PREFIXES if x.exp == exp]
        if pre[0].symbol == '':
            return n
        return n + ' ' + pre[0].symbol

def dec_to_si_string(dec):
    """Convert to SI prefix-type string.

    Use the SI prefix to represent the exponent part of the number.
    """
    sEng = dec.to_eng_string()
    n = None
    exp = None
    if 'E' in sEng:
        n, exp = sEng.split('E')
    elif 'e' in sEng:
        n, exp = sEng.split('e')
    else:
        n = sEng
        exp = 0
    exp = int(exp)
    pre = [x for x in SI_PREFIXES if x.exp == exp]
    if pre[0].symbol == '':
        return n
    return n + ' ' + pre[0].symbol
