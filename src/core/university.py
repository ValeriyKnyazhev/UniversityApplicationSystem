from enum import Enum


class University(Enum):
    MIPT: str = 'МФТИ'
    VSE: str = 'ВШЭ'
    MSU: str = 'МГУ'
    MEPHI: str = 'МИФИ'
    BMSTU: str = 'Бауманка'
    MIREA: str = 'МИРЭА'
    MAI: str = 'МАИ'
    MPEI: str = 'МЭИ'
    MTUCI: str = 'МТУСИ'
    MPOLITECH: str = 'МосПолитех'
    MIET: str = 'МИЭТ'
    ITMO: str = 'ИТМО'
    SPBSU: str = 'СПБГУ'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name
