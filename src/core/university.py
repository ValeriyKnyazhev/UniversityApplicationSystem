from enum import Enum


class University(Enum):
    MIPT = 'МФТИ'
    VSE = 'ВШЭ'
    MSU = 'МГУ'
    MEPHI = 'МИФИ'
    BMSTU = 'Бауманка'
    MIREA = 'МИРЭА'
    MAI = 'МАИ'
    MPEI = 'МЭИ'
    MTUCI = 'МТУСИ'
    MPOLITECH = 'МосПолитех'
    MIET = 'МИЭТ'
    ITMO = 'ИТМО'
    SPBSU = 'СПБГУ'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name
