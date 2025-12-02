"""
Módulo contendo operações de transformação geométrica
"""
import numpy as np
import math


class Transformacao:
    """Classe para operações de transformação geométrica usando numpy"""
    
    @staticmethod
    def translacao(tx: float, ty: float) -> np.ndarray:
        """
        Retorna matriz de translação 3x3 homogênea
        
        Args:
            tx: translação em x
            ty: translação em y
            
        Returns:
            Matriz de translação 3x3
        """
        return np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def rotacao(angulo_graus: float) -> np.ndarray:
        """
        Retorna matriz de rotação 3x3 homogênea
        
        Args:
            angulo_graus: ângulo de rotação em graus
            
        Returns:
            Matriz de rotação 3x3
        """
        ang = math.radians(angulo_graus)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        return np.array([
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def escala(sx: float, sy: float) -> np.ndarray:
        """
        Retorna matriz de escala 3x3 homogênea
        
        Args:
            sx: fator de escala em x
            sy: fator de escala em y
            
        Returns:
            Matriz de escala 3x3
        """
        return np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def aplicar_transformacao(coords: np.ndarray, matriz: np.ndarray) -> np.ndarray:
        """
        Aplica uma transformação a um vetor de coordenadas homogêneas
        
        Args:
            coords: vetor de coordenadas [x, y, 1]
            matriz: matriz de transformação 3x3
            
        Returns:
            Vetor transformado [x', y', 1]
        """
        return matriz @ coords
    
    @staticmethod
    def compor_transformacoes(*matrizes: np.ndarray) -> np.ndarray:
        """
        Compõe múltiplas transformações em uma única matriz
        
        Args:
            *matrizes: matrizes de transformação a serem compostas
            
        Returns:
            Matriz composta resultante
        """
        resultado = np.eye(3)
        for matriz in matrizes:
            resultado = matriz @ resultado
        return resultado
