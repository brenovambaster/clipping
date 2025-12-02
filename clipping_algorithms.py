"""
Módulo contendo implementações de algoritmos de clipping
"""
from typing import Optional, Tuple, List
from clipping_interface import ClippingAlgorithmReta, ClippingAlgorithmPoligono


class ClippingCohenSutherland(ClippingAlgorithmReta):
    """Implementação do algoritmo de Cohen-Sutherland para clipping de retas"""
    
    # Códigos de região
    INSIDE = 0  # 0000
    LEFT = 1    # 0001
    RIGHT = 2   # 0010
    BOTTOM = 4  # 0100
    TOP = 8     # 1000
    
    def calcular_codigo(self, x: float, y: float, x_min: float, y_min: float, 
                       x_max: float, y_max: float) -> int:
        """
        Calcula o código de região de um ponto
        
        Args:
            x, y: coordenadas do ponto
            x_min, y_min, x_max, y_max: limites da janela
            
        Returns:
            Código da região (bitwise)
        """
        codigo = self.INSIDE
        
        if x < x_min:
            codigo |= self.LEFT
        elif x > x_max:
            codigo |= self.RIGHT
        
        if y < y_min:
            codigo |= self.BOTTOM
        elif y > y_max:
            codigo |= self.TOP
        
        return codigo
    
    def clip(self, x1: float, y1: float, x2: float, y2: float,
             x_min: float, y_min: float, x_max: float, y_max: float
             ) -> Optional[Tuple[float, float, float, float]]:
        """Realiza o clipping de uma reta usando Cohen-Sutherland"""
        codigo1 = self.calcular_codigo(x1, y1, x_min, y_min, x_max, y_max)
        codigo2 = self.calcular_codigo(x2, y2, x_min, y_min, x_max, y_max)
        
        aceitar = False
        
        while True:
            # Ambos os pontos dentro
            if codigo1 == 0 and codigo2 == 0:
                aceitar = True
                break
            # Ambos os pontos na mesma região externa
            elif (codigo1 & codigo2) != 0:
                break
            else:
                # Calcular ponto de interseção
                x, y = 0.0, 0.0
                codigo_out = codigo1 if codigo1 != 0 else codigo2
                
                if codigo_out & self.TOP:
                    x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                    y = y_max
                elif codigo_out & self.BOTTOM:
                    x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                    y = y_min
                elif codigo_out & self.RIGHT:
                    y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                    x = x_max
                elif codigo_out & self.LEFT:
                    y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                    x = x_min
                
                # Substituir o ponto externo pelo ponto de interseção
                if codigo_out == codigo1:
                    x1, y1 = x, y
                    codigo1 = self.calcular_codigo(x1, y1, x_min, y_min, x_max, y_max)
                else:
                    x2, y2 = x, y
                    codigo2 = self.calcular_codigo(x2, y2, x_min, y_min, x_max, y_max)
        
        if aceitar:
            return (x1, y1, x2, y2)
        return None


class ClippingLiangBarsky(ClippingAlgorithmReta):
    """Implementação do algoritmo de Liang-Barsky para clipping de retas"""
    
    def clip(self, x1: float, y1: float, x2: float, y2: float,
             x_min: float, y_min: float, x_max: float, y_max: float
             ) -> Optional[Tuple[float, float, float, float]]:
        """Realiza o clipping de uma reta usando Liang-Barsky"""
        dx = x2 - x1
        dy = y2 - y1
        
        # Parâmetros p e q para as quatro bordas
        p = [-dx, dx, -dy, dy]
        q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
        
        u1, u2 = 0.0, 1.0
        
        for i in range(4):
            if p[i] == 0:
                # Linha paralela à borda
                if q[i] < 0:
                    return None
            else:
                t = q[i] / p[i]
                if p[i] < 0:
                    # Entrada na janela
                    u1 = max(u1, t)
                else:
                    # Saída da janela
                    u2 = min(u2, t)
        
        if u1 > u2:
            return None
        
        # Calcular pontos de interseção
        x1_clip = x1 + u1 * dx
        y1_clip = y1 + u1 * dy
        x2_clip = x1 + u2 * dx
        y2_clip = y1 + u2 * dy
        
        return (x1_clip, y1_clip, x2_clip, y2_clip)


class ClippingSutherlandHodgman(ClippingAlgorithmPoligono):
    """Implementação do algoritmo de Sutherland-Hodgman para clipping de polígonos"""
    
    def clip(self, poligono: List[Tuple[float, float]], 
             x_min: float, y_min: float, x_max: float, y_max: float
             ) -> List[List[Tuple[float, float]]]:
        """Realiza o clipping de um polígono usando Sutherland-Hodgman"""
        if not poligono:
            return []
        
        def clip_borda(poligono_entrada: List[Tuple[float, float]], 
                      teste_dentro, calcular_intersecao) -> List[Tuple[float, float]]:
            """Recorta o polígono contra uma borda"""
            if not poligono_entrada:
                return []
            
            poligono_saida = []
            
            for i in range(len(poligono_entrada)):
                v1 = poligono_entrada[i]
                v2 = poligono_entrada[(i + 1) % len(poligono_entrada)]
                
                v1_dentro = teste_dentro(v1)
                v2_dentro = teste_dentro(v2)
                
                if v1_dentro and v2_dentro:
                    # Ambos dentro: adiciona v2
                    poligono_saida.append(v2)
                elif v1_dentro and not v2_dentro:
                    # Saindo: adiciona interseção
                    intersecao = calcular_intersecao(v1, v2)
                    if intersecao:
                        poligono_saida.append(intersecao)
                elif not v1_dentro and v2_dentro:
                    # Entrando: adiciona interseção e v2
                    intersecao = calcular_intersecao(v1, v2)
                    if intersecao:
                        poligono_saida.append(intersecao)
                    poligono_saida.append(v2)
                # Se ambos fora, não adiciona nada
            
            return poligono_saida
        
        # Definir funções para cada borda
        def dentro_esquerda(p): return p[0] >= x_min
        def dentro_direita(p): return p[0] <= x_max
        def dentro_inferior(p): return p[1] >= y_min
        def dentro_superior(p): return p[1] <= y_max
        
        def intersecao_esquerda(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            if x2 - x1 == 0:
                return None
            t = (x_min - x1) / (x2 - x1)
            return (x_min, y1 + t * (y2 - y1))
        
        def intersecao_direita(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            if x2 - x1 == 0:
                return None
            t = (x_max - x1) / (x2 - x1)
            return (x_max, y1 + t * (y2 - y1))
        
        def intersecao_inferior(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            if y2 - y1 == 0:
                return None
            t = (y_min - y1) / (y2 - y1)
            return (x1 + t * (x2 - x1), y_min)
        
        def intersecao_superior(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            if y2 - y1 == 0:
                return None
            t = (y_max - y1) / (y2 - y1)
            return (x1 + t * (x2 - x1), y_max)
        
        # Aplicar clipping em cada borda
        bordas = [
            (dentro_esquerda, intersecao_esquerda),
            (dentro_direita, intersecao_direita),
            (dentro_inferior, intersecao_inferior),
            (dentro_superior, intersecao_superior)
        ]
        
        resultado = poligono
        for teste_dentro, calcular_intersecao in bordas:
            resultado = clip_borda(resultado, teste_dentro, calcular_intersecao)
            if not resultado:
                return []
        
        return [resultado] if resultado else []
