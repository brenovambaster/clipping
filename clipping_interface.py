"""
Módulo contendo interfaces para algoritmos de clipping
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple, List


class ClippingAlgorithmReta(ABC):
    """Interface abstrata para algoritmos de clipping de retas"""
    
    @abstractmethod
    def clip(self, x1: float, y1: float, x2: float, y2: float,
             x_min: float, y_min: float, x_max: float, y_max: float
             ) -> Optional[Tuple[float, float, float, float]]:
        """
        Realiza o clipping de uma reta
        
        Args:
            x1, y1: coordenadas do primeiro ponto
            x2, y2: coordenadas do segundo ponto
            x_min, y_min: coordenadas mínimas da janela de clipping
            x_max, y_max: coordenadas máximas da janela de clipping
            
        Returns:
            Tupla com coordenadas da reta recortada ou None se totalmente fora
        """
        pass


class ClippingAlgorithmPoligono(ABC):
    """Interface abstrata para algoritmos de clipping de polígonos"""
    
    @abstractmethod
    def clip(self, poligono: List[Tuple[float, float]], 
             x_min: float, y_min: float, x_max: float, y_max: float
             ) -> List[List[Tuple[float, float]]]:
        """
        Realiza o clipping de um polígono
        
        Args:
            poligono: lista de coordenadas (x, y) dos vértices
            x_min, y_min: coordenadas mínimas da janela de clipping
            x_max, y_max: coordenadas máximas da janela de clipping
            
        Returns:
            Lista de polígonos resultantes do clipping
        """
        pass
