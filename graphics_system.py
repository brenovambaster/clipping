"""
Módulo do sistema gráfico principal
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from typing import List, Tuple

from geometric_objects import Ponto, Reta, Poligono
from transformations import Transformacao
from clipping_algorithms import ClippingCohenSutherland, ClippingLiangBarsky, ClippingSutherlandHodgman
from xml_loader import XMLLoader


class SistemaGrafico:
    """Sistema gráfico principal com pipeline de visualização"""
    
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
        self.w_angulo = 0.0
        
        # Objetos da cena
        self.pontos: List[Ponto] = []
        self.retas: List[Reta] = []
        self.poligonos: List[Poligono] = []
        
        # Algoritmos de clipping
        self.algoritmo_reta_cs = ClippingCohenSutherland()
        self.algoritmo_reta_lb = ClippingLiangBarsky()
        self.algoritmo_poligono = ClippingSutherlandHodgman()
        self.algoritmo_reta_atual = "Cohen-Sutherland"
        
        # Configurações de movimentação
        self.passo_movimento = 1.0
        self.passo_rotacao = 15.0
        
        self.criar_interface()
    
    def criar_interface(self):
        """Cria a interface gráfica"""
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
        
        self._criar_controles_arquivo(control_frame)
        self._criar_controles_movimentacao(control_frame)
        self._criar_controles_rotacao(control_frame)
        self._criar_controles_zoom(control_frame)
        self._criar_controles_algoritmo(control_frame)
        self._criar_painel_informacoes(control_frame)
        
        self.atualizar_info()
    
    def _criar_controles_arquivo(self, parent):
        """Cria controles de arquivo"""
        arquivo_frame = ttk.LabelFrame(parent, text="Arquivo")
        arquivo_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(arquivo_frame, text="Carregar XML", 
                  command=self.carregar_xml).pack(fill=tk.X, padx=5, pady=5)
    
    def _criar_controles_movimentacao(self, parent):
        """Cria controles de movimentação"""
        mov_frame = ttk.LabelFrame(parent, text="Movimentação da Window")
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
    
    def _criar_controles_rotacao(self, parent):
        """Cria controles de rotação"""
        rot_frame = ttk.LabelFrame(parent, text="Rotação da Window")
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
    
    def _criar_controles_zoom(self, parent):
        """Cria controles de zoom"""
        escala_frame = ttk.LabelFrame(parent, text="Zoom da Window")
        escala_frame.pack(fill=tk.X, pady=(0, 10))
        
        escala_btn_frame = ttk.Frame(escala_frame)
        escala_btn_frame.pack(pady=5)
        
        ttk.Button(escala_btn_frame, text="+ Ampliar (10%)", 
                  command=lambda: self.escalar_window(0.9)).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(escala_btn_frame, text="− Reduzir (10%)", 
                  command=lambda: self.escalar_window(1.1)).pack(fill=tk.X, padx=5, pady=2)
    
    def _criar_controles_algoritmo(self, parent):
        """Cria controles de seleção de algoritmo"""
        clip_frame = ttk.LabelFrame(parent, text="Algoritmo de Clipping (Retas)")
        clip_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.algoritmo_var = tk.StringVar(value="Cohen-Sutherland")
        ttk.Radiobutton(clip_frame, text="Cohen-Sutherland", 
                       variable=self.algoritmo_var, value="Cohen-Sutherland",
                       command=self.atualizar_cena).pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(clip_frame, text="Liang-Barsky", 
                       variable=self.algoritmo_var, value="Liang-Barsky",
                       command=self.atualizar_cena).pack(anchor=tk.W, padx=5, pady=2)
    
    def _criar_painel_informacoes(self, parent):
        """Cria painel de informações"""
        info_frame = ttk.LabelFrame(parent, text="Informações")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, height=10, width=30, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def carregar_xml(self):
        """Carrega objetos de um arquivo XML"""
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo XML",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            config, pontos, retas, poligonos = XMLLoader.carregar_arquivo(filename)
            
            # Atualizar configurações
            if 'viewport' in config:
                vp = config['viewport']
                self.vp_x_min = vp['x_min']
                self.vp_y_min = vp['y_min']
                self.vp_x_max = vp['x_max']
                self.vp_y_max = vp['y_max']
            
            if 'window' in config:
                w = config['window']
                self.w_x_min = w['x_min']
                self.w_y_min = w['y_min']
                self.w_x_max = w['x_max']
                self.w_y_max = w['y_max']
                self.w_centro_x = (self.w_x_min + self.w_x_max) / 2
                self.w_centro_y = (self.w_y_min + self.w_y_max) / 2
                self.w_angulo = 0.0
            
            # Atualizar objetos
            self.pontos = pontos
            self.retas = retas
            self.poligonos = poligonos
            
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
        
        # Considerar a rotação da window
        ang = np.radians(self.w_angulo)
        dx_rot = dx * np.cos(ang) - dy * np.sin(ang)
        dy_rot = dx * np.sin(ang) + dy * np.cos(ang)
        
        deslocamento = passo * np.array([dx_rot, dy_rot])
        
        self.w_x_min += deslocamento[0]
        self.w_x_max += deslocamento[0]
        self.w_y_min += deslocamento[1]
        self.w_y_max += deslocamento[1]
        self.w_centro_x += deslocamento[0]
        self.w_centro_y += deslocamento[1]
        
        self.atualizar_cena()
    
    def rotacionar_window(self, sentido: int):
        """Rotaciona a window em torno do seu centro"""
        angulo = self.passo_rot_var.get() * sentido
        self.w_angulo = (self.w_angulo + angulo) % 360
        
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
        """Transforma objetos do mundo para o PPC usando numpy"""
        # Criar matriz de transformação composta
        t1 = Transformacao.translacao(-self.w_centro_x, -self.w_centro_y)
        r = Transformacao.rotacao(-self.w_angulo)
        t2 = Transformacao.translacao(self.w_centro_x, self.w_centro_y)
        
        # Compor transformações
        matriz = Transformacao.compor_transformacoes(t2, r, t1)
        
        # Aplicar aos pontos
        for ponto in self.pontos:
            coords_mundo = ponto.get_coords_mundo()
            coords_ppc = Transformacao.aplicar_transformacao(coords_mundo, matriz)
            ponto.set_coords_ppc(coords_ppc)
        
        # Aplicar às retas
        for reta in self.retas:
            pontos_mundo = reta.get_pontos_mundo()
            p1_ppc = Transformacao.aplicar_transformacao(pontos_mundo[0], matriz)
            p2_ppc = Transformacao.aplicar_transformacao(pontos_mundo[1], matriz)
            reta.set_pontos_ppc(p1_ppc, p2_ppc)
        
        # Aplicar aos polígonos
        for poligono in self.poligonos:
            pontos_mundo = poligono.get_pontos_mundo()
            poligono.poligonos_ppc = [[]]
            for coords_mundo in pontos_mundo:
                coords_ppc = Transformacao.aplicar_transformacao(coords_mundo, matriz)
                p = Ponto(coords_ppc[0], coords_ppc[1])
                p.set_coords_ppc(coords_ppc)
                poligono.poligonos_ppc[0].append(p)
    
    def aplicar_clipping(self):
        """Aplica clipping nos objetos"""
        # Clipping de pontos
        for ponto in self.pontos:
            coords = ponto.get_coords_ppc()
            ponto.visivel = (self.w_x_min <= coords[0] <= self.w_x_max and
                           self.w_y_min <= coords[1] <= self.w_y_max)
        
        # Selecionar algoritmo de clipping de retas
        if self.algoritmo_var.get() == "Cohen-Sutherland":
            algoritmo = self.algoritmo_reta_cs
        else:
            algoritmo = self.algoritmo_reta_lb
        
        # Clipping de retas
        for reta in self.retas:
            resultado = algoritmo.clip(
                reta.p1_ppc.x_ppc, reta.p1_ppc.y_ppc,
                reta.p2_ppc.x_ppc, reta.p2_ppc.y_ppc,
                self.w_x_min, self.w_y_min, self.w_x_max, self.w_y_max
            )
            
            if resultado:
                reta.visivel = True
                x1, y1, x2, y2 = resultado
                reta.p1_ppc.x_ppc = x1
                reta.p1_ppc.y_ppc = y1
                reta.p2_ppc.x_ppc = x2
                reta.p2_ppc.y_ppc = y2
            else:
                reta.visivel = False
        
        # Clipping de polígonos
        for poligono in self.poligonos:
            pontos_originais = [(p.x_ppc, p.y_ppc) for p in poligono.poligonos_ppc[0]]
            
            poligonos_resultado = self.algoritmo_poligono.clip(
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
                        p.set_coords_ppc(np.array([x, y]))
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
                coords = ponto.get_coords_ppc()
                x, y = self.transformar_ppc_para_viewport(coords[0], coords[1])
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
        """Atualiza toda a cena (pipeline completo)"""
        self.transformar_mundo_para_ppc()
        self.aplicar_clipping()
        self.desenhar_cena()
        self.atualizar_info()
    
    def atualizar_info(self):
        """Atualiza as informações na interface"""
        self.info_text.delete(1.0, tk.END)
        
        pontos_visiveis = sum(1 for p in self.pontos if p.visivel)
        retas_visiveis = sum(1 for r in self.retas if r.visivel)
        poligonos_visiveis = sum(1 for p in self.poligonos if p.visivel)
        
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
  Pontos: {pontos_visiveis}
  Retas: {retas_visiveis}
  Polígonos: {poligonos_visiveis}

Algoritmo: {self.algoritmo_var.get()}
"""
        
        self.info_text.insert(1.0, info)
