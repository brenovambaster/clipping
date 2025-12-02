import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import math
from typing import List, Tuple, Optional

# ==================== CLASSES DE OBJETOS GEOMÉTRICOS ====================

class Ponto:
    """Representa um ponto no espaço 2D"""
    def __init__(self, x: float, y: float, cor: str = "black"):
        self.x_mundo = x  # Coordenadas originais no mundo
        self.y_mundo = y
        self.x_ppc = x    # Coordenadas no PPC
        self.y_ppc = y
        self.cor = cor
        self.visivel = True
    
    def __repr__(self):
        return f"Ponto({self.x_mundo}, {self.y_mundo})"

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

class Poligono:
    """Representa um polígono no espaço 2D"""
    def __init__(self, pontos: List[Ponto], cor: str = "black"):
        self.pontos_mundo = [Ponto(p.x_mundo, p.y_mundo) for p in pontos]
        self.poligonos_ppc = [[Ponto(p.x_mundo, p.y_mundo) for p in pontos]]
        self.cor = cor
        self.visivel = True
    
    def __repr__(self):
        return f"Poligono({len(self.pontos_mundo)} vértices)"

# ==================== TRANSFORMAÇÕES GEOMÉTRICAS ====================

class Transformacao:
    """Classe para operações de transformação geométrica"""
    
    @staticmethod
    def translacao(tx: float, ty: float) -> List[List[float]]:
        """Matriz de translação"""
        return [
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ]
    
    @staticmethod
    def rotacao(angulo_graus: float) -> List[List[float]]:
        """Matriz de rotação"""
        ang = math.radians(angulo_graus)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        return [
            [cos_a, -sin_a, 0],
            [sin_a, cos_a, 0],
            [0, 0, 1]
        ]
    
    @staticmethod
    def escala(sx: float, sy: float) -> List[List[float]]:
        """Matriz de escala"""
        return [
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ]
    
    @staticmethod
    def multiplicar_matrizes(m1: List[List[float]], m2: List[List[float]]) -> List[List[float]]:
        """Multiplica duas matrizes 3x3"""
        resultado = [[0, 0, 0] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    resultado[i][j] += m1[i][k] * m2[k][j]
        return resultado
    
    @staticmethod
    def aplicar_transformacao(x: float, y: float, matriz: List[List[float]]) -> Tuple[float, float]:
        """Aplica uma transformação a um ponto"""
        x_novo = matriz[0][0] * x + matriz[0][1] * y + matriz[0][2]
        y_novo = matriz[1][0] * x + matriz[1][1] * y + matriz[1][2]
        return x_novo, y_novo

# ==================== ALGORITMOS DE CLIPPING ====================

class ClippingCohenSutherland:
    """Algoritmo de Cohen-Sutherland para clipping de retas"""
    
    INSIDE = 0  # 0000
    LEFT = 1    # 0001
    RIGHT = 2   # 0010
    BOTTOM = 4  # 0100
    TOP = 8     # 1000
    
    @staticmethod
    def calcular_codigo(x: float, y: float, x_min: float, y_min: float, 
                       x_max: float, y_max: float) -> int:
        """Calcula o código de região de um ponto"""
        codigo = ClippingCohenSutherland.INSIDE
        
        if x < x_min:
            codigo |= ClippingCohenSutherland.LEFT
        elif x > x_max:
            codigo |= ClippingCohenSutherland.RIGHT
        
        if y < y_min:
            codigo |= ClippingCohenSutherland.BOTTOM
        elif y > y_max:
            codigo |= ClippingCohenSutherland.TOP
        
        return codigo
    
    @staticmethod
    def clip(x1: float, y1: float, x2: float, y2: float,
             x_min: float, y_min: float, x_max: float, y_max: float) -> Optional[Tuple[float, float, float, float]]:
        """Realiza o clipping de uma reta"""
        codigo1 = ClippingCohenSutherland.calcular_codigo(x1, y1, x_min, y_min, x_max, y_max)
        codigo2 = ClippingCohenSutherland.calcular_codigo(x2, y2, x_min, y_min, x_max, y_max)
        
        aceitar = False
        
        while True:
            if codigo1 == 0 and codigo2 == 0:
                aceitar = True
                break
            elif (codigo1 & codigo2) != 0:
                break
            else:
                x, y = 0.0, 0.0
                codigo_out = codigo1 if codigo1 != 0 else codigo2
                
                if codigo_out & ClippingCohenSutherland.TOP:
                    x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                    y = y_max
                elif codigo_out & ClippingCohenSutherland.BOTTOM:
                    x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                    y = y_min
                elif codigo_out & ClippingCohenSutherland.RIGHT:
                    y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                    x = x_max
                elif codigo_out & ClippingCohenSutherland.LEFT:
                    y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                    x = x_min
                
                if codigo_out == codigo1:
                    x1, y1 = x, y
                    codigo1 = ClippingCohenSutherland.calcular_codigo(x1, y1, x_min, y_min, x_max, y_max)
                else:
                    x2, y2 = x, y
                    codigo2 = ClippingCohenSutherland.calcular_codigo(x2, y2, x_min, y_min, x_max, y_max)
        
        if aceitar:
            return (x1, y1, x2, y2)
        return None

class ClippingLiangBarsky:
    """Algoritmo de Liang-Barsky para clipping de retas"""
    
    @staticmethod
    def clip(x1: float, y1: float, x2: float, y2: float,
             x_min: float, y_min: float, x_max: float, y_max: float) -> Optional[Tuple[float, float, float, float]]:
        """Realiza o clipping de uma reta"""
        dx = x2 - x1
        dy = y2 - y1
        
        p = [-dx, dx, -dy, dy]
        q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
        
        u1, u2 = 0.0, 1.0
        
        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    return None
            else:
                t = q[i] / p[i]
                if p[i] < 0:
                    u1 = max(u1, t)
                else:
                    u2 = min(u2, t)
        
        if u1 > u2:
            return None
        
        x1_clip = x1 + u1 * dx
        y1_clip = y1 + u1 * dy
        x2_clip = x1 + u2 * dx
        y2_clip = y1 + u2 * dy
        
        return (x1_clip, y1_clip, x2_clip, y2_clip)

class ClippingWeilerAtherton:
    """Algoritmo de Weiler-Atherton para clipping de polígonos"""
    
    @staticmethod
    def clip(poligono: List[Tuple[float, float]], x_min: float, y_min: float, 
             x_max: float, y_max: float) -> List[List[Tuple[float, float]]]:
        """Realiza o clipping de um polígono"""
        if not poligono:
            return []
        
        # Clipping simplificado usando Sutherland-Hodgman
        def clip_borda(poligono_entrada, borda):
            if not poligono_entrada:
                return []
            
            poligono_saida = []
            
            for i in range(len(poligono_entrada)):
                v1 = poligono_entrada[i]
                v2 = poligono_entrada[(i + 1) % len(poligono_entrada)]
                
                v1_dentro = borda(v1)
                v2_dentro = borda(v2)
                
                if v1_dentro and v2_dentro:
                    poligono_saida.append(v2)
                elif v1_dentro and not v2_dentro:
                    intersecao = calcular_intersecao(v1, v2, borda)
                    if intersecao:
                        poligono_saida.append(intersecao)
                elif not v1_dentro and v2_dentro:
                    intersecao = calcular_intersecao(v1, v2, borda)
                    if intersecao:
                        poligono_saida.append(intersecao)
                    poligono_saida.append(v2)
            
            return poligono_saida
        
        def calcular_intersecao(p1, p2, borda):
            x1, y1 = p1
            x2, y2 = p2
            
            # Determinar qual borda e calcular interseção
            if borda == borda_esquerda:
                if x2 - x1 == 0:
                    return None
                t = (x_min - x1) / (x2 - x1)
                return (x_min, y1 + t * (y2 - y1))
            elif borda == borda_direita:
                if x2 - x1 == 0:
                    return None
                t = (x_max - x1) / (x2 - x1)
                return (x_max, y1 + t * (y2 - y1))
            elif borda == borda_inferior:
                if y2 - y1 == 0:
                    return None
                t = (y_min - y1) / (y2 - y1)
                return (x1 + t * (x2 - x1), y_min)
            elif borda == borda_superior:
                if y2 - y1 == 0:
                    return None
                t = (y_max - y1) / (y2 - y1)
                return (x1 + t * (x2 - x1), y_max)
            return None
        
        # Definir bordas
        borda_esquerda = lambda p: p[0] >= x_min
        borda_direita = lambda p: p[0] <= x_max
        borda_inferior = lambda p: p[1] >= y_min
        borda_superior = lambda p: p[1] <= y_max
        
        # Aplicar clipping em cada borda
        resultado = poligono
        for borda in [borda_esquerda, borda_direita, borda_inferior, borda_superior]:
            resultado = clip_borda(resultado, borda)
            if not resultado:
                return []
        
        return [resultado] if resultado else []

# ==================== SISTEMA GRÁFICO ====================

class SistemaGrafico:
    """Sistema gráfico principal"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Gráfico - TP2 - Computação Gráfica")
        
        # Configurações da viewport
        self.vp_x_min = 0
        self.vp_y_min = 0
        self.vp_x_max = 800
        self.vp_y_max = 600
        
        # Configurações da window
        self.w_x_min = 0.0
        self.w_y_min = 0.0
        self.w_x_max = 10.0
        self.w_y_max = 7.5
        self.w_centro_x = (self.w_x_min + self.w_x_max) / 2
        self.w_centro_y = (self.w_y_min + self.w_y_max) / 2
        self.w_angulo = 0.0  # Ângulo de rotação da window
        
        # Objetos da cena
        self.pontos: List[Ponto] = []
        self.retas: List[Reta] = []
        self.poligonos: List[Poligono] = []
        
        # Configurações
        self.algoritmo_reta = "Cohen-Sutherland"
        self.passo_movimento = 1.0
        self.passo_rotacao = 15.0
        
        self.criar_interface()
    
    def criar_interface(self):
        """Cria a interface gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para desenho
        canvas_frame = ttk.LabelFrame(main_frame, text="Viewport")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.canvas = tk.Canvas(canvas_frame, width=self.vp_x_max, height=self.vp_y_max, 
                               bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas.pack(padx=5, pady=5)
        
        # Painel de controle
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Arquivo
        arquivo_frame = ttk.LabelFrame(control_frame, text="Arquivo")
        arquivo_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(arquivo_frame, text="Carregar XML", 
                  command=self.carregar_xml).pack(fill=tk.X, padx=5, pady=5)
        
        # Movimentação
        mov_frame = ttk.LabelFrame(control_frame, text="Movimentação da Window")
        mov_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mov_frame, text="Passo:").pack(padx=5, pady=(5, 0))
        self.passo_mov_var = tk.DoubleVar(value=1.0)
        ttk.Entry(mov_frame, textvariable=self.passo_mov_var, width=10).pack(padx=5, pady=(0, 5))
        
        btn_frame = ttk.Frame(mov_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="↑", width=5, 
                  command=lambda: self.mover_window(0, 1)).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(btn_frame, text="←", width=5, 
                  command=lambda: self.mover_window(-1, 0)).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(btn_frame, text="↓", width=5, 
                  command=lambda: self.mover_window(0, -1)).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(btn_frame, text="→", width=5, 
                  command=lambda: self.mover_window(1, 0)).grid(row=1, column=2, padx=2, pady=2)
        
        # Rotação
        rot_frame = ttk.LabelFrame(control_frame, text="Rotação da Window")
        rot_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rot_frame, text="Ângulo (graus):").pack(padx=5, pady=(5, 0))
        self.passo_rot_var = tk.DoubleVar(value=15.0)
        ttk.Entry(rot_frame, textvariable=self.passo_rot_var, width=10).pack(padx=5, pady=(0, 5))
        
        rot_btn_frame = ttk.Frame(rot_frame)
        rot_btn_frame.pack(pady=5)
        
        ttk.Button(rot_btn_frame, text="↶ Esquerda", 
                  command=lambda: self.rotacionar_window(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(rot_btn_frame, text="Direita ↷", 
                  command=lambda: self.rotacionar_window(-1)).pack(side=tk.LEFT, padx=5)
        
        # Escala
        escala_frame = ttk.LabelFrame(control_frame, text="Zoom da Window")
        escala_frame.pack(fill=tk.X, pady=(0, 10))
        
        escala_btn_frame = ttk.Frame(escala_frame)
        escala_btn_frame.pack(pady=5)
        
        ttk.Button(escala_btn_frame, text="+ Ampliar (10%)", 
                  command=lambda: self.escalar_window(0.9)).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(escala_btn_frame, text="− Reduzir (10%)", 
                  command=lambda: self.escalar_window(1.1)).pack(fill=tk.X, padx=5, pady=2)
        
        # Algoritmo de clipping
        clip_frame = ttk.LabelFrame(control_frame, text="Algoritmo de Clipping (Retas)")
        clip_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.algoritmo_var = tk.StringVar(value="Cohen-Sutherland")
        ttk.Radiobutton(clip_frame, text="Cohen-Sutherland", 
                       variable=self.algoritmo_var, value="Cohen-Sutherland",
                       command=self.atualizar_cena).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(clip_frame, text="Liang-Barsky", 
                       variable=self.algoritmo_var, value="Liang-Barsky",
                       command=self.atualizar_cena).pack(anchor=tk.W, padx=5, pady=2)
        
        # Informações
        info_frame = ttk.LabelFrame(control_frame, text="Informações")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, height=10, width=30, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.atualizar_info()
    
    def carregar_xml(self):
        """Carrega objetos de um arquivo XML"""
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo XML",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            
            # Limpar objetos anteriores
            self.pontos.clear()
            self.retas.clear()
            self.poligonos.clear()
            
            # Carregar viewport
            viewport = root.find('viewport')
            if viewport is not None:
                vpmin = viewport.find('vpmin')
                vpmax = viewport.find('vpmax')
                if vpmin is not None and vpmax is not None:
                    self.vp_x_min = float(vpmin.get('x', 0))
                    self.vp_y_min = float(vpmin.get('y', 0))
                    self.vp_x_max = float(vpmax.get('x', 800))
                    self.vp_y_max = float(vpmax.get('y', 600))
            
            # Carregar window
            window = root.find('window')
            if window is not None:
                wmin = window.find('wmin')
                wmax = window.find('wmax')
                if wmin is not None and wmax is not None:
                    self.w_x_min = float(wmin.get('x', 0))
                    self.w_y_min = float(wmin.get('y', 0))
                    self.w_x_max = float(wmax.get('x', 10))
                    self.w_y_max = float(wmax.get('y', 7.5))
                    self.w_centro_x = (self.w_x_min + self.w_x_max) / 2
                    self.w_centro_y = (self.w_y_min + self.w_y_max) / 2
                    self.w_angulo = 0.0
            
            # Carregar pontos
            for ponto_elem in root.findall('ponto'):
                x = float(ponto_elem.get('x'))
                y = float(ponto_elem.get('y'))
                cor = ponto_elem.get('cor', 'black')
                self.pontos.append(Ponto(x, y, cor))
            
            # Carregar retas
            for reta_elem in root.findall('reta'):
                cor = reta_elem.get('cor', 'black')
                pontos_reta = reta_elem.findall('ponto')
                if len(pontos_reta) >= 2:
                    p1 = Ponto(float(pontos_reta[0].get('x')), float(pontos_reta[0].get('y')))
                    p2 = Ponto(float(pontos_reta[1].get('x')), float(pontos_reta[1].get('y')))
                    self.retas.append(Reta(p1, p2, cor))
            
            # Carregar polígonos
            for poligono_elem in root.findall('poligono'):
                cor = poligono_elem.get('cor', 'black')
                pontos_poli = []
                for ponto_elem in poligono_elem.findall('ponto'):
                    x = float(ponto_elem.get('x'))
                    y = float(ponto_elem.get('y'))
                    pontos_poli.append(Ponto(x, y))
                if len(pontos_poli) >= 3:
                    self.poligonos.append(Poligono(pontos_poli, cor))
            
            self.atualizar_cena()
            messagebox.showinfo("Sucesso", f"Arquivo carregado com sucesso!\n"
                              f"Pontos: {len(self.pontos)}\n"
                              f"Retas: {len(self.retas)}\n"
                              f"Polígonos: {len(self.poligonos)}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
    
    def mover_window(self, dx: int, dy: int):
        """Move a window na direção especificada"""
        passo = self.passo_mov_var.get()
        
        # Considerar a rotação da window para movimento correto
        ang = math.radians(self.w_angulo)
        dx_rot = dx * math.cos(ang) - dy * math.sin(ang)
        dy_rot = dx * math.sin(ang) + dy * math.cos(ang)
        
        self.w_x_min += dx_rot * passo
        self.w_x_max += dx_rot * passo
        self.w_y_min += dy_rot * passo
        self.w_y_max += dy_rot * passo
        self.w_centro_x += dx_rot * passo
        self.w_centro_y += dy_rot * passo
        
        self.atualizar_cena()
    
    def rotacionar_window(self, sentido: int):
        """Rotaciona a window em torno do seu centro"""
        angulo = self.passo_rot_var.get() * sentido
        self.w_angulo += angulo
        
        # Normalizar ângulo
        self.w_angulo = self.w_angulo % 360
        
        self.atualizar_cena()
    
    def escalar_window(self, fator: float):
        """Escala a window em relação ao seu centro"""
        largura = self.w_x_max - self.w_x_min
        altura = self.w_y_max - self.w_y_min
        
        nova_largura = largura * fator
        nova_altura = altura * fator
        
        self.w_x_min = self.w_centro_x - nova_largura / 2
        self.w_x_max = self.w_centro_x + nova_largura / 2
        self.w_y_min = self.w_centro_y - nova_altura / 2
        self.w_y_max = self.w_centro_y + nova_altura / 2
        
        self.atualizar_cena()
    
    def transformar_mundo_para_ppc(self):
        """Transforma objetos do mundo para o PPC"""
        # Criar matriz de transformação
        # 1. Translação para origem (centro da window)
        t1 = Transformacao.translacao(-self.w_centro_x, -self.w_centro_y)
        
        # 2. Rotação inversa
        r = Transformacao.rotacao(-self.w_angulo)
        
        # 3. Translação de volta
        t2 = Transformacao.translacao(self.w_centro_x, self.w_centro_y)
        
        # 4. Normalização para [0,1]
        largura_w = self.w_x_max - self.w_x_min
        altura_w = self.w_y_max - self.w_y_min
        
        # Combinar transformações
        matriz = t1
        matriz = Transformacao.multiplicar_matrizes(r, matriz)
        matriz = Transformacao.multiplicar_matrizes(t2, matriz)
        
        # Aplicar aos pontos
        for ponto in self.pontos:
            x, y = Transformacao.aplicar_transformacao(ponto.x_mundo, ponto.y_mundo, matriz)
            ponto.x_ppc = x
            ponto.y_ppc = y
        
        # Aplicar às retas
        for reta in self.retas:
            x1, y1 = Transformacao.aplicar_transformacao(reta.p1_mundo.x_mundo, 
                                                         reta.p1_mundo.y_mundo, matriz)
            x2, y2 = Transformacao.aplicar_transformacao(reta.p2_mundo.x_mundo, 
                                                         reta.p2_mundo.y_mundo, matriz)
            reta.p1_ppc.x_ppc = x1
            reta.p1_ppc.y_ppc = y1
            reta.p2_ppc.x_ppc = x2
            reta.p2_ppc.y_ppc = y2
        
        # Aplicar aos polígonos
        for poligono in self.poligonos:
            poligono.poligonos_ppc = [[]]
            for ponto in poligono.pontos_mundo:
                x, y = Transformacao.aplicar_transformacao(ponto.x_mundo, ponto.y_mundo, matriz)
                p = Ponto(x, y)
                p.x_ppc = x
                p.y_ppc = y
                poligono.poligonos_ppc[0].append(p)
    
    def aplicar_clipping(self):
        """Aplica clipping nos objetos"""
        # Clipping de pontos
        for ponto in self.pontos:
            ponto.visivel = (self.w_x_min <= ponto.x_ppc <= self.w_x_max and
                           self.w_y_min <= ponto.y_ppc <= self.w_y_max)
        
        # Clipping de retas
        algoritmo = self.algoritmo_var.get()
        
        for reta in self.retas:
            if algoritmo == "Cohen-Sutherland":
                resultado = ClippingCohenSutherland.clip(
                    reta.p1_ppc.x_ppc, reta.p1_ppc.y_ppc,
                    reta.p2_ppc.x_ppc, reta.p2_ppc.y_ppc,
                    self.w_x_min, self.w_y_min, self.w_x_max, self.w_y_max
                )
            else:  # Liang-Barsky
                resultado = ClippingLiangBarsky.clip(
                    reta.p1_ppc.x_ppc, reta.p1_ppc.y_ppc,
                    reta.p2_ppc.x_ppc, reta.p2_ppc.y_ppc,
                    self.w_x_min, self.w_y_min, self.w_x_max, self.w_y_max
                )
            
            if resultado:
                reta.visivel = True
                reta.p1_ppc.x_ppc, reta.p1_ppc.y_ppc, reta.p2_ppc.x_ppc, reta.p2_ppc.y_ppc = resultado
            else:
                reta.visivel = False
        
        # Clipping de polígonos
        for poligono in self.poligonos:
            pontos_originais = [(p.x_ppc, p.y_ppc) for p in poligono.poligonos_ppc[0]]
            
            poligonos_resultado = ClippingWeilerAtherton.clip(
                pontos_originais,
                self.w_x_min, self.w_y_min, self.w_x_max, self.w_y_max
            )
            
            if poligonos_resultado:
                poligono.visivel = True
                poligono.poligonos_ppc = []
                for poli in poligonos_resultado:
                    pontos_poli = []
                    for x, y in poli:
                        p = Ponto(x, y)
                        p.x_ppc = x
                        p.y_ppc = y
                        pontos_poli.append(p)
                    poligono.poligonos_ppc.append(pontos_poli)
            else:
                poligono.visivel = False
    
    def transformar_ppc_para_viewport(self, x: float, y: float) -> Tuple[int, int]:
        """Transforma coordenadas do PPC para a viewport"""
        # Normalização
        x_norm = (x - self.w_x_min) / (self.w_x_max - self.w_x_min)
        y_norm = (y - self.w_y_min) / (self.w_y_max - self.w_y_min)
        
        # Mapeamento para viewport (inverter Y)
        x_vp = self.vp_x_min + x_norm * (self.vp_x_max - self.vp_x_min)
        y_vp = self.vp_y_max - y_norm * (self.vp_y_max - self.vp_y_min)
        
        return int(x_vp), int(y_vp)
    
    def desenhar_cena(self):
        """Desenha todos os objetos visíveis na viewport"""
        self.canvas.delete("all")
        
        # Desenhar pontos
        for ponto in self.pontos:
            if ponto.visivel:
                x, y = self.transformar_ppc_para_viewport(ponto.x_ppc, ponto.y_ppc)
                self.canvas.create_oval(x-3, y-3, x+3, y+3, fill=ponto.cor, outline=ponto.cor)
        
        # Desenhar retas
        for reta in self.retas:
            if reta.visivel:
                x1, y1 = self.transformar_ppc_para_viewport(reta.p1_ppc.x_ppc, reta.p1_ppc.y_ppc)
                x2, y2 = self.transformar_ppc_para_viewport(reta.p2_ppc.x_ppc, reta.p2_ppc.y_ppc)
                self.canvas.create_line(x1, y1, x2, y2, fill=reta.cor, width=2)
        
        # Desenhar polígonos
        for poligono in self.poligonos:
            if poligono.visivel:
                for poli in poligono.poligonos_ppc:
                    if len(poli) >= 3:
                        coords = []
                        for ponto in poli:
                            x, y = self.transformar_ppc_para_viewport(ponto.x_ppc, ponto.y_ppc)
                            coords.extend([x, y])
                        self.canvas.create_polygon(coords, outline=poligono.cor, 
                                                  fill="", width=2)
        
        # Desenhar bordas da window
        self.desenhar_bordas_window()
    
    def desenhar_bordas_window(self):
        """Desenha as bordas da window na viewport"""
        cantos = [
            (self.w_x_min, self.w_y_min),
            (self.w_x_max, self.w_y_min),
            (self.w_x_max, self.w_y_max),
            (self.w_x_min, self.w_y_max)
        ]
        
        coords = []
        for x, y in cantos:
            x_vp, y_vp = self.transformar_ppc_para_viewport(x, y)
            coords.extend([x_vp, y_vp])
        
        self.canvas.create_polygon(coords, outline="red", fill="", width=2, dash=(5, 3))
    
    def atualizar_cena(self):
        """Atualiza toda a cena"""
        self.transformar_mundo_para_ppc()
        self.aplicar_clipping()
        self.desenhar_cena()
        self.atualizar_info()
    
    def atualizar_info(self):
        """Atualiza as informações na interface"""
        self.info_text.delete(1.0, tk.END)
        
        info = f"""Window:
  Min: ({self.w_x_min:.2f}, {self.w_y_min:.2f})
  Max: ({self.w_x_max:.2f}, {self.w_y_max:.2f})
  Centro: ({self.w_centro_x:.2f}, {self.w_centro_y:.2f})
  Rotação: {self.w_angulo:.1f}°

Objetos:
  Pontos: {len(self.pontos)}
  Retas: {len(self.retas)}
  Polígonos: {len(self.poligonos)}

Visíveis:
  Pontos: {sum(1 for p in self.pontos if p.visivel)}
  Retas: {sum(1 for r in self.retas if r.visivel)}
  Polígonos: {sum(1 for p in self.poligonos if p.visivel)}

Algoritmo: {self.algoritmo_var.get()}
"""
        
        self.info_text.insert(1.0, info)

# ==================== MAIN ====================

def main():
    root = tk.Tk()
    app = SistemaGrafico(root)
    root.mainloop()

if __name__ == "__main__":
    main()