import numpy as np
import utils as ut
from typing import Iterable

Kostka = np.ndarray

def nova_kostka() -> Kostka:
    kostka = np.zeros((6,3,3), dtype=np.uint8)
    for barva in range(6):
        kostka[barva] = barva# + 1
    return kostka

SLOZENA_KOSTKA = nova_kostka()


def print_kostku(kostka: Kostka) -> None:
    for l in kostka[0]:
        print(" "*7, l, sep="")
    for i in range(3):
        for s in kostka[1:5]:
            print(s[i], end="")
        print()
    for l in kostka[5]:
        print(" "*7, l, sep="")

def je_slozena(kostka: Kostka) -> bool:
    return np.array_equal(kostka, SLOZENA_KOSTKA)


def tahni_tah(kostka: Kostka, tah: int) -> None:
    """
    Tahy jsou 1 ... 6, po smeru hodinovych rucicek.
    Zaporne znamenaji otacet proti smeru 
    hodinovych rucicek.
    """
    abs_tah = np.abs(tah) - 1
    smer_01 = (1-np.sign(tah))//2
    smer_11 = -np.sign(tah)

    okoli = ut.OKOLI[abs_tah] 
    
    okoli_posun = ut.OKOLI_POSUN[smer_01, abs_tah]

    kostka[abs_tah] = np.rot90(kostka[abs_tah], smer_11)
    #kostka[*okoli] = kostka[*okoli_posun]
    kostka[okoli[0], okoli[1], okoli[2]] = kostka[okoli_posun[0], okoli_posun[1], okoli_posun[2]] # kvůli pythonu 3.10
    


def tahni_tahy(kostka: Kostka, tahy: Iterable[int]) -> None:
    for tah in tahy:
        tahni_tah(kostka, tah)

def vygeneruj_nahodny_tah() -> int:
    return np.random.randint(1, 6) * np.random.choice([-1, 1])

