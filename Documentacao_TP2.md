# Trabalho Prático 2 - Sistema Gráfico com Clipping
## Computação Gráfica - 2025

- [Trabalho Prático 2 - Sistema Gráfico com Clipping](#trabalho-prático-2---sistema-gráfico-com-clipping)
  - [Computação Gráfica - 2025](#computação-gráfica---2025)
  - [1. Introdução](#1-introdução)
  - [2. Fundamentação Teórica](#2-fundamentação-teórica)
    - [2.1 Pipeline Gráfico](#21-pipeline-gráfico)
    - [2.2 Transformações Geométricas com NumPy](#22-transformações-geométricas-com-numpy)
    - [2.3 Algoritmos de Clipping](#23-algoritmos-de-clipping)
      - [Cohen-Sutherland (Retas)](#cohen-sutherland-retas)
      - [Liang-Barsky (Retas)](#liang-barsky-retas)
      - [Sutherland-Hodgman (Polígonos)](#sutherland-hodgman-polígonos)
  - [3. Arquitetura do Sistema](#3-arquitetura-do-sistema)
    - [3.1 Estrutura Modular de Arquivos](#31-estrutura-modular-de-arquivos)
    - [3.2 Diagrama de Classes](#32-diagrama-de-classes)
    - [3.3 Descrição dos Módulos](#33-descrição-dos-módulos)
      - [`main.py` - Ponto de Entrada](#mainpy---ponto-de-entrada)
      - [`geometric_objects.py` - Objetos Geométricos](#geometric_objectspy---objetos-geométricos)
      - [`transformations.py` - Transformações com NumPy](#transformationspy---transformações-com-numpy)
      - [`clipping_interface.py` - Interfaces Abstratas](#clipping_interfacepy---interfaces-abstratas)
  - [4. Guia de Uso](#4-guia-de-uso)
    - [4.1 Instalação](#41-instalação)
    - [4.2 Carregando Arquivos XML](#42-carregando-arquivos-xml)
    - [4.3 Controles da Window](#43-controles-da-window)
      - [Movimentação](#movimentação)
      - [Rotação](#rotação)
      - [Zoom](#zoom)
    - [4.4 Algoritmos de Clipping](#44-algoritmos-de-clipping)
  - [5. Decisões de Implementação](#5-decisões-de-implementação)
    - [5.1 Estrutura de Dados](#51-estrutura-de-dados)
    - [5.2 Transformação Mundo → PPC com NumPy](#52-transformação-mundo--ppc-com-numpy)
    - [5.3 Movimentação com Rotação](#53-movimentação-com-rotação)
    - [5.4 Clipping de Polígonos](#54-clipping-de-polígonos)
    - [5.5 Uso de Interfaces Abstratas (ABC)](#55-uso-de-interfaces-abstratas-abc)
    - [5.6 Visualização da Window](#56-visualização-da-window)
  - [6. Testes Realizados](#6-testes-realizados)
    - [6.1 Arquivo de Teste: entrada.xml](#61-arquivo-de-teste-entradaxml)
    - [6.2 Testes de Módulos](#62-testes-de-módulos)
    - [6.3 Casos Especiais Testados](#63-casos-especiais-testados)
  - [7. Exemplos de Uso](#7-exemplos-de-uso)
    - [7.1 Explorar uma Cena Grande](#71-explorar-uma-cena-grande)
    - [7.2 Comparar Algoritmos](#72-comparar-algoritmos)
    - [7.3 Testar Rotação](#73-testar-rotação)
  - [8. Cores Suportadas](#8-cores-suportadas)
  - [9. Melhorias Implementadas](#9-melhorias-implementadas)
    - [9.1 Uso de NumPy para Operações Matriciais](#91-uso-de-numpy-para-operações-matriciais)
    - [9.2 Arquitetura Modular](#92-arquitetura-modular)
    - [9.3 Interfaces Abstratas (ABC)](#93-interfaces-abstratas-abc)
    - [9.4 Tipagem Estática](#94-tipagem-estática)
  - [10. Limitações Conhecidas](#10-limitações-conhecidas)
  - [11. Possíveis Extensões](#11-possíveis-extensões)
  - [12. Conclusão](#12-conclusão)
  - [13. Referências](#13-referências)

---

## 1. Introdução

Este trabalho implementa um **sistema gráfico 2D completo** em Python com Tkinter e NumPy, capaz de realizar transformações geométricas na window e aplicar algoritmos de clipping (recorte) para visualização de objetos geométricos.

O sistema foi desenvolvido seguindo **boas práticas de engenharia de software**, com arquitetura modular, uso de interfaces abstratas (ABC), tipagem estática e operações matriciais otimizadas com NumPy.

O sistema permite:
- Carregar cenas de arquivos XML
- Movimentar, rotacionar e escalar a window livremente
- Aplicar clipping de pontos, retas e polígonos
- Escolher entre algoritmos de Cohen-Sutherland ou Liang-Barsky para retas
- Visualizar apenas objetos dentro da área da window

---

## 2. Fundamentação Teórica

### 2.1 Pipeline Gráfico

O sistema implementa o pipeline gráfico clássico:

1. **Mundo → PPC (Plano de Projeção)**: Transformação dos objetos considerando posição, rotação e escala da window
2. **Clipping**: Recorte dos objetos para a área visível
3. **PPC → Viewport**: Mapeamento para o espaço de tela

### 2.2 Transformações Geométricas com NumPy

Utilizamos matrizes de transformação homogêneas 3x3 implementadas com `numpy.ndarray`:

**Translação:**
```python
np.array([
    [1, 0, tx],
    [0, 1, ty],
    [0, 0, 1]
], dtype=float)
```

**Rotação:**
```python
np.array([
    [cos(θ), -sin(θ), 0],
    [sin(θ),  cos(θ), 0],
    [0,       0,      1]
], dtype=float)
```

**Escala:**
```python
np.array([
    [sx, 0,  0],
    [0,  sy, 0],
    [0,  0,  1]
], dtype=float)
```

### 2.3 Algoritmos de Clipping

#### Cohen-Sutherland (Retas)
- Divide o espaço em 9 regiões usando 4 bits
- Testa rapidamente aceitação/rejeição trivial
- Calcula interseções apenas quando necessário

#### Liang-Barsky (Retas)
- Usa equações paramétricas da reta
- Mais eficiente que Cohen-Sutherland
- Calcula interseções diretamente com limites

#### Sutherland-Hodgman (Polígonos)
- Implementação baseada em clipping sequencial por borda
- Funciona com polígonos convexos e côncavos
- Pode gerar múltiplos polígonos como resultado

---

## 3. Arquitetura do Sistema

### 3.1 Estrutura Modular de Arquivos

O projeto foi organizado em **módulos separados** para melhor manutenibilidade:

```
clipping/
├── main.py                  # Ponto de entrada da aplicação
├── graphics_system.py       # Sistema gráfico principal (SistemaGrafico)
├── geometric_objects.py     # Classes de objetos (Ponto, Reta, Poligono)
├── transformations.py       # Operações de transformação (Transformacao)
├── clipping_algorithms.py   # Algoritmos de clipping
├── clipping_interface.py    # Interfaces abstratas (ABC)
├── xml_loader.py            # Carregador de arquivos XML
├── entrada_teste.xml        # Arquivo de teste
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação resumida
```

### 3.2 Diagrama de Classes
![](clipping-png.png)

### 3.3 Descrição dos Módulos

#### `main.py` - Ponto de Entrada
```python
def main():
    root = tk.Tk()
    app = SistemaGrafico(root)
    root.mainloop()
```

#### `geometric_objects.py` - Objetos Geométricos
Cada objeto mantém:
- **Coordenadas originais** no sistema de coordenadas do mundo
- **Coordenadas transformadas** no PPC (após aplicar transformações da window)
- **Atributo de visibilidade** (True/False após clipping)
- **Cor** para renderização
- **Métodos NumPy** para manipulação de coordenadas homogêneas

```python
class Ponto:
    def __init__(self, x: float, y: float, cor: str = "black"):
        self.x_mundo = x
        self.y_mundo = y
        self.x_ppc = x
        self.y_ppc = y
        self.cor = cor
        self.visivel = True
    
    def get_coords_mundo(self) -> np.ndarray:
        """Retorna coordenadas do mundo como vetor homogêneo"""
        return np.array([self.x_mundo, self.y_mundo, 1.0])
```

#### `transformations.py` - Transformações com NumPy
```python
class Transformacao:
    @staticmethod
    def translacao(tx: float, ty: float) -> np.ndarray:
        return np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], dtype=float)
    
    @staticmethod
    def rotacao(angulo_graus: float) -> np.ndarray:
        ang = math.radians(angulo_graus)
        return np.array([
            [math.cos(ang), -math.sin(ang), 0],
            [math.sin(ang),  math.cos(ang), 0],
            [0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def compor_transformacoes(*matrizes: np.ndarray) -> np.ndarray:
        resultado = np.eye(3)
        for matriz in matrizes:
            resultado = matriz @ resultado
        return resultado
```

#### `clipping_interface.py` - Interfaces Abstratas
```python
class ClippingAlgorithmReta(ABC):
    @abstractmethod
    def clip(self, x1, y1, x2, y2, x_min, y_min, x_max, y_max) -> Optional[Tuple]:
        pass

class ClippingAlgorithmPoligono(ABC):
    @abstractmethod
    def clip(self, poligono, x_min, y_min, x_max, y_max) -> List[List[Tuple]]:
        pass
```

---

## 4. Guia de Uso

### 4.1 Instalação

**Requisitos:**
- Python 3.7 ou superior
- NumPy
- Tkinter (normalmente já incluído no Python)

**Instalação das dependências:**
```bash
pip install -r requirements.txt
```

**Execução:**
```bash
python main.py
```

### 4.2 Carregando Arquivos XML

1. Clique no botão **"Carregar XML"**
2. Selecione um arquivo XML com a estrutura especificada
3. Os objetos serão carregados e exibidos automaticamente

**Estrutura do XML:**
```xml
<?xml version="1.0"?>
<dados>
    <viewport>
        <vpmin x="0" y="0"/>
        <vpmax x="800" y="600"/>
    </viewport>
    
    <window>
        <wmin x="0.0" y="0.0"/>
        <wmax x="10.0" y="7.5"/>
    </window>
    
    <ponto cor="black" x="2.0" y="3.0"/>
    
    <reta cor="blue">
        <ponto x="1.0" y="1.0"/>
        <ponto x="5.0" y="5.0"/>
    </reta>
    
    <poligono cor="red">
        <ponto x="6.0" y="2.0"/>
        <ponto x="8.0" y="2.0"/>
        <ponto x="7.0" y="4.0"/>
    </poligono>
</dados>
```

### 4.3 Controles da Window

#### Movimentação
- **Setas ↑ ↓ ← →**: Move a window nas direções
- **Campo "Passo"**: Define quantas unidades mover (padrão: 1.0)

#### Rotação
- **↶ Esquerda**: Rotaciona no sentido anti-horário
- **Direita ↷**: Rotaciona no sentido horário
- **Campo "Ângulo"**: Define graus por rotação (padrão: 15°)

#### Zoom
- **+ Ampliar (10%)**: Reduz a window em 10% (zoom in)
- **− Reduzir (10%)**: Aumenta a window em 10% (zoom out)

### 4.4 Algoritmos de Clipping

Escolha o algoritmo para retas:
- ⚪ **Cohen-Sutherland**: Clássico, divide espaço em regiões
- ⚪ **Liang-Barsky**: Mais eficiente, usa equações paramétricas

*Polígonos sempre usam Sutherland-Hodgman*

---

## 5. Decisões de Implementação

### 5.1 Estrutura de Dados

**Por que manter coordenadas originais e transformadas separadas?**
- Permite aplicar múltiplas transformações sem perda de precisão
- Facilita reverter transformações
- Essencial para recalcular clipping após mudanças na window

**Por que polígonos podem ter múltiplos polígonos PPC?**
- Após clipping, um polígono pode ser dividido em várias partes
- Mantém informação completa do resultado do recorte

### 5.2 Transformação Mundo → PPC com NumPy

O processo implementado utiliza composição de matrizes NumPy:

```python
def transformar_mundo_para_ppc(self):
    # Compor transformações usando NumPy
    t1 = Transformacao.translacao(-self.w_centro_x, -self.w_centro_y)
    r = Transformacao.rotacao(-self.w_angulo)
    t2 = Transformacao.translacao(self.w_centro_x, self.w_centro_y)
    
    # Multiplicação matricial eficiente com operador @
    matriz = Transformacao.compor_transformacoes(t2, r, t1)
    
    # Aplicar transformação a cada ponto
    for ponto in self.pontos:
        coords = ponto.get_coords_mundo()  # np.array([x, y, 1])
        resultado = Transformacao.aplicar_transformacao(coords, matriz)
        ponto.set_coords_ppc(resultado)
```

### 5.3 Movimentação com Rotação

Quando a window está rotacionada, a movimentação considera a orientação:
- Movimento "para cima" move na direção Y local da window
- Usa transformação de rotação para converter direção global → local

```python
def mover_window(self, dx, dy):
    ang = math.radians(self.w_angulo)
    dx_rot = dx * math.cos(ang) - dy * math.sin(ang)
    dy_rot = dx * math.sin(ang) + dy * math.cos(ang)
    # Aplica movimento rotacionado
```

### 5.4 Clipping de Polígonos

Implementamos **Sutherland-Hodgman** para clipping de polígonos:
- Mais simples de implementar e eficiente
- Funciona bem para polígonos convexos e côncavos
- Clipa contra cada borda sequencialmente
- Implementa a interface abstrata `ClippingAlgorithmPoligono`

### 5.5 Uso de Interfaces Abstratas (ABC)

O sistema utiliza o padrão de projeto **Strategy** através de interfaces abstratas:

```python
from abc import ABC, abstractmethod

class ClippingAlgorithmReta(ABC):
    @abstractmethod
    def clip(self, x1, y1, x2, y2, x_min, y_min, x_max, y_max):
        pass
```

Isso permite trocar facilmente entre algoritmos de clipping.

### 5.6 Visualização da Window

- Bordas da window são desenhadas como **linhas tracejadas vermelhas**
- Permite visualizar a área de clipping
- Útil para debug e entendimento do sistema

---

## 6. Testes Realizados

### 6.1 Arquivo de Teste: entrada.xml

**Objetos incluídos:**
- 3 pontos em diferentes posições
- 2 retas (azul e verde)
- 1 triângulo vermelho

**Testes realizados:**

| Operação         | Resultado Esperado             | Status |
| ---------------- | ------------------------------ | ------ |
| Carregar XML     | Todos objetos visíveis         | ✅ OK   |
| Mover direita    | Objetos à esquerda desaparecem | ✅ OK   |
| Mover esquerda   | Objetos à direita desaparecem  | ✅ OK   |
| Rotação 45°      | Window gira, clipping correto  | ✅ OK   |
| Zoom in 50%      | Menos objetos visíveis         | ✅ OK   |
| Zoom out 50%     | Mais objetos visíveis          | ✅ OK   |
| Cohen-Sutherland | Retas cortadas corretamente    | ✅ OK   |
| Liang-Barsky     | Mesmo resultado que CS         | ✅ OK   |
| Polígono parcial | Polígono cortado mantém forma  | ✅ OK   |

### 6.2 Testes de Módulos

| Módulo               | Teste                    | Status |
| -------------------- | ------------------------ | ------ |
| geometric_objects.py | Criação de objetos       | ✅ OK   |
| transformations.py   | Matrizes NumPy corretas  | ✅ OK   |
| clipping_algorithms  | Interfaces implementadas | ✅ OK   |
| xml_loader.py        | Parsing de XML           | ✅ OK   |
| graphics_system.py   | Pipeline completo        | ✅ OK   |

### 6.3 Casos Especiais Testados

1. **Reta completamente fora**: visivel = False
2. **Reta parcialmente dentro**: cortada corretamente
3. **Polígono atravessando borda**: vértices adicionados nas interseções
4. **Window muito pequena**: apenas objetos próximos ao centro visíveis
5. **Rotação 90°**: orientação correta mantida

---

## 7. Exemplos de Uso

### 7.1 Explorar uma Cena Grande

1. Carregue um XML com muitos objetos espalhados
2. Use **zoom out** (-) para ver panorama geral
3. Use **movimentação** para navegar
4. Use **zoom in** (+) para ver detalhes

### 7.2 Comparar Algoritmos

1. Carregue cena com várias retas
2. Observe resultado com **Cohen-Sutherland**
3. Mude para **Liang-Barsky**
4. Verifique que resultados são idênticos
5. *(Liang-Barsky é mais eficiente computacionalmente)*

### 7.3 Testar Rotação

1. Carregue cena simples
2. Use **rotação** gradualmente (15° por vez)
3. Observe como objetos entram/saem da window
4. Note que bordas da window também giram

---

## 8. Cores Suportadas

O sistema suporta todas as cores X11. Exemplos:

**Cores básicas:**
- `black`, `white`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`

**Tons:**
- `darkred`, `lightblue`, `darkgreen`, `lightgray`

**Especiais:**
- `orange`, `purple`, `pink`, `brown`, `gold`, `silver`

Lista completa: [X11 Color Names](https://en.wikipedia.org/wiki/X11_color_names)

---

## 9. Melhorias Implementadas

### 9.1 Uso de NumPy para Operações Matriciais
- Operações vetorizadas mais eficientes
- Uso do operador `@` para multiplicação de matrizes
- Coordenadas homogêneas como `np.ndarray`

### 9.2 Arquitetura Modular
- Separação de responsabilidades em arquivos distintos
- Facilita manutenção e testes unitários
- Permite reutilização de componentes

### 9.3 Interfaces Abstratas (ABC)
- Padrão Strategy para algoritmos de clipping
- Fácil adição de novos algoritmos
- Type hints para melhor documentação do código

### 9.4 Tipagem Estática
- Uso de `typing` para anotações de tipo
- Melhor documentação e detecção de erros
- Compatível com ferramentas como mypy

---

## 10. Limitações Conhecidas

1. **Sutherland-Hodgman**: 
   - Pode não gerar múltiplos polígonos em casos complexos de côncavos

2. **Performance**: 
   - Para cenas com 1000+ objetos, pode haver lentidão
   - Otimização: considerar estruturas de dados espaciais (quadtree)

3. **Precisão Numérica**: 
   - Erros de ponto flutuante podem acumular em rotações múltiplas
   - Recomendado recarregar cena após muitas transformações

---

## 11. Possíveis Extensões

- **Zoom com mouse wheel**: Mais intuitivo que botões
- **Animação**: Interpolar transformações suavemente
- **Exportar imagem**: Salvar viewport como PNG
- **Novos algoritmos**: Adicionar novos algoritmos implementando as interfaces

---

## 12. Conclusão


✅ Movimentação livre da window (translação, rotação, escala)  
✅ Transformação Mundo → PPC implementada corretamente com NumPy  
✅ Clipping de pontos, retas (2 algoritmos) e polígonos  
✅ Interface intuitiva com controles claros  
✅ Objetos mantêm informações originais e transformadas  
✅ Leitura de arquivos XML com cores  
✅ Documentação completa e clara  
✅ Arquitetura modular com separação de responsabilidades  
✅ Uso de NumPy para operações matriciais eficientes  
✅ Interfaces abstratas (ABC) para extensibilidade
✅ Tipagem estática com type hints  


---

## 13. Referências

- FOLEY, J. D. et al. **Computer Graphics: Principles and Practice**. 2nd ed. Addison-Wesley, 1990.
- HEARN, D.; BAKER, M. P. **Computer Graphics with OpenGL**. 4th ed. Prentice Hall, 2010.
- Documentação Python Tkinter: https://docs.python.org/3/library/tkinter.html
- Documentação NumPy: https://numpy.org/doc/

---

**Autores**: [Artur Neto, Breno Vambaster] 
**Disciplina**: Computação Gráfica  
**Instituição**: IFNMG - Campus Montes Claros  
**Ano**: 2025