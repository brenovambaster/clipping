"""
Módulo contendo as classes de objetos geométricos
"""
from typing import List
import numpy as np


class Ponto:
    """Representa um ponto no espaço 2D"""
    
    def __init__(self, x: float, y: float, cor: str = "black"):
        self.x_mundo = x
        self.y_mundo = y
        self.x_ppc = x
        self.y_ppc = y
        self.cor = cor
        self.visivel = True
    
    def __repr__(self):
        return f"Ponto({self.x_mundo}, {self.y_mundo})"
    
    def get_coords_mundo(self) -> np.ndarray:
        """Retorna coordenadas do mundo como vetor homogêneo"""
        return np.array([self.x_mundo, self.y_mundo, 1.0])
    
    def get_coords_ppc(self) -> np.ndarray:
        """Retorna coordenadas do PPC"""
        return np.array([self.x_ppc, self.y_ppc])
    
    def set_coords_ppc(self, coords: np.ndarray):
        """Define coordenadas do PPC"""
        self.x_ppc = coords[0]
        self.y_ppc = coords[1]


class Reta:
    """Representa uma reta no espaço 2D"""
    
    def __init__(self, p1: Ponto, p2: Ponto, cor: str = "black"):
        self.p1_mundo = Ponto(p1.x_mundo, p1.y_mundo)
        self.p2_mundo = Ponto(p2.x_mundo, p2.y_mundo)
        self.p1_ppc = Ponto(p1.x_mundo, p1.y_mundo)
        self.p2_ppc = Ponto(p2.x_mundo, p2.y_mundo)
        self.cor = cor
        self.visivel = True
    
    def __repr__(self):
        return f"Reta({self.p1_mundo}, {self.p2_mundo})"
    
    def get_pontos_mundo(self) -> List[np.ndarray]:
        """Retorna pontos do mundo como vetores homogêneos"""
        return [
            self.p1_mundo.get_coords_mundo(),
            self.p2_mundo.get_coords_mundo()
        ]
    
    def set_pontos_ppc(self, p1_coords: np.ndarray, p2_coords: np.ndarray):
        """Define coordenadas dos pontos no PPC"""
        self.p1_ppc.set_coords_ppc(p1_coords[:2])
        self.p2_ppc.set_coords_ppc(p2_coords[:2])


class Poligono:
    """Representa um polígono no espaço 2D"""
    
    def __init__(self, pontos: List[Ponto], cor: str = "black"):
        self.pontos_mundo = [Ponto(p.x_mundo, p.y_mundo) for p in pontos]
        self.poligonos_ppc = [[Ponto(p.x_mundo, p.y_mundo) for p in pontos]]
        self.cor = cor
        self.visivel = True
    
    def __repr__(self):
        return f"Poligono({len(self.pontos_mundo)} vértices)"
    
    def get_pontos_mundo(self) -> List[np.ndarray]:
        """Retorna pontos do mundo como vetores homogêneos"""
        return [p.get_coords_mundo() for p in self.pontos_mundo]
    
    def get_coords_mundo_2d(self) -> List[tuple]:
        """Retorna coordenadas 2D dos pontos do mundo"""
        return [(p.x_mundo, p.y_mundo) for p in self.pontos_mundo]
