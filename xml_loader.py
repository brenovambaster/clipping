"""
Módulo para carregar objetos de arquivos XML
"""
import xml.etree.ElementTree as ET
from typing import List, Tuple
from geometric_objects import Ponto, Reta, Poligono


class XMLLoader:
    """Classe para carregar objetos geométricos de arquivos XML"""
    
    @staticmethod
    def carregar_arquivo(filename: str) -> Tuple[dict, List[Ponto], List[Reta], List[Poligono]]:
        """
        Carrega objetos de um arquivo XML
        
        Args:
            filename: caminho do arquivo XML
            
        Returns:
            Tupla contendo (configurações, pontos, retas, polígonos)
        """
        tree = ET.parse(filename)
        root = tree.getroot()
        
        config = {}
        pontos = []
        retas = []
        poligonos = []
        
        # Carregar viewport
        viewport = root.find('viewport')
        if viewport is not None:
            vpmin = viewport.find('vpmin')
            vpmax = viewport.find('vpmax')
            if vpmin is not None and vpmax is not None:
                config['viewport'] = {
                    'x_min': float(vpmin.get('x', 0)),
                    'y_min': float(vpmin.get('y', 0)),
                    'x_max': float(vpmax.get('x', 800)),
                    'y_max': float(vpmax.get('y', 600))
                }
        
        # Carregar window
        window = root.find('window')
        if window is not None:
            wmin = window.find('wmin')
            wmax = window.find('wmax')
            if wmin is not None and wmax is not None:
                config['window'] = {
                    'x_min': float(wmin.get('x', 0)),
                    'y_min': float(wmin.get('y', 0)),
                    'x_max': float(wmax.get('x', 10)),
                    'y_max': float(wmax.get('y', 7.5))
                }
        
        # Carregar pontos
        for ponto_elem in root.findall('ponto'):
            x = float(ponto_elem.get('x'))
            y = float(ponto_elem.get('y'))
            cor = ponto_elem.get('cor', 'black')
            pontos.append(Ponto(x, y, cor))
        
        # Carregar retas
        for reta_elem in root.findall('reta'):
            cor = reta_elem.get('cor', 'black')
            pontos_reta = reta_elem.findall('ponto')
            if len(pontos_reta) >= 2:
                p1 = Ponto(float(pontos_reta[0].get('x')), float(pontos_reta[0].get('y')))
                p2 = Ponto(float(pontos_reta[1].get('x')), float(pontos_reta[1].get('y')))
                retas.append(Reta(p1, p2, cor))
        
        # Carregar polígonos
        for poligono_elem in root.findall('poligono'):
            cor = poligono_elem.get('cor', 'black')
            pontos_poli = []
            for ponto_elem in poligono_elem.findall('ponto'):
                x = float(ponto_elem.get('x'))
                y = float(ponto_elem.get('y'))
                pontos_poli.append(Ponto(x, y))
            if len(pontos_poli) >= 3:
                poligonos.append(Poligono(pontos_poli, cor))
        
        return config, pontos, retas, poligonos
