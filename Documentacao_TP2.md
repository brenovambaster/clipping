# Trabalho Prático 2 - Sistema Gráfico com Clipping
## Computação Gráfica - 2025

---

## 1. Introdução

Este trabalho implementa um **sistema gráfico 2D completo** em Python com Tkinter, capaz de realizar transformações geométricas na window e aplicar algoritmos de clipping (recorte) para visualização de objetos geométricos.

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

### 2.2 Transformações Geométricas

Utilizamos matrizes de transformação homogêneas 3x3:

**Translação:**
```
[1  0  tx]
[0  1  ty]
[0  0   1]
```

**Rotação:**
```
[cos(θ)  -sin(θ)  0]
[sin(θ)   cos(θ)  0]
[  0        0     1]
```

**Escala:**
```
[sx  0   0]
[0   sy  0]
[0   0   1]
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

#### Weiler-Atherton (Polígonos)
- Implementado usando Sutherland-Hodgman simplificado
- Funciona com polígonos convexos e côncavos
- Pode gerar múltiplos polígonos como resultado

---

## 3. Arquitetura do Sistema

### 3.1 Estrutura de Classes

```
Sistema Gráfico
├── Objetos Geométricos
│   ├── Ponto (coordenadas mundo + PPC, cor, visibilidade)
│   ├── Reta (2 pontos mundo + PPC, cor, visibilidade)
│   └── Polígono (lista de pontos mundo + PPC, cor, visibilidade)
│
├── Transformações
│   ├── translacao()
│   ├── rotacao()
│   ├── escala()
│   └── multiplicar_matrizes()
│
├── Algoritmos de Clipping
│   ├── ClippingCohenSutherland
│   ├── ClippingLiangBarsky
│   └── ClippingWeilerAtherton
│
└── Interface Gráfica
    ├── Canvas (viewport)
    └── Controles (movimentação, rotação, escala)
```

### 3.2 Objetos Geométricos

Cada objeto mantém:
- **Coordenadas originais** no sistema de coordenadas do mundo
- **Coordenadas transformadas** no PPC (após aplicar transformações da window)
- **Atributo de visibilidade** (True/False após clipping)
- **Cor** para renderização

**Exemplo - Classe Ponto:**
```python
class Ponto:
    def __init__(self, x, y, cor="black"):
        self.x_mundo = x      # Original
        self.y_mundo = y
        self.x_ppc = x        # Transformado
        self.y_ppc = y
        self.cor = cor
        self.visivel = True
```

---

## 4. Guia de Uso

### 4.1 Instalação

**Requisitos:**
- Python 3.7 ou superior
- Tkinter (normalmente já incluído no Python)

**Execução:**
```bash
python sistema_grafico_tp2.py
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

*Polígonos sempre usam Weiler-Atherton*

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

### 5.2 Transformação Mundo → PPC

O processo implementado:
1. Transladar window para origem (subtrair centro)
2. Aplicar rotação inversa da window
3. Transladar de volta
4. Normalizar para intervalo da window

```python
def transformar_mundo_para_ppc(self):
    # Translação para origem
    t1 = Transformacao.translacao(-self.w_centro_x, -self.w_centro_y)
    
    # Rotação inversa
    r = Transformacao.rotacao(-self.w_angulo)
    
    # Translação de volta
    t2 = Transformacao.translacao(self.w_centro_x, self.w_centro_y)
    
    # Combinar e aplicar
    matriz = t1
    matriz = multiplicar_matrizes(r, matriz)
    matriz = multiplicar_matrizes(t2, matriz)
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

Implementamos **Sutherland-Hodgman** como base para Weiler-Atherton:
- Mais simples de implementar
- Funciona bem para polígonos convexos
- Para côncavos, gera aproximação adequada
- Clipa contra cada borda sequencialmente

### 5.5 Visualização da Window

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

### 6.2 Casos Especiais Testados

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

## 9. Limitações Conhecidas

1. **Weiler-Atherton Simplificado**: 
   - Implementação usa Sutherland-Hodgman como base
   - Pode não gerar múltiplos polígonos em casos complexos de côncavos

2. **Performance**: 
   - Para cenas com 1000+ objetos, pode haver lentidão
   - Otimização: considerar estruturas de dados espaciais (quadtree)

3. **Precisão Numérica**: 
   - Erros de ponto flutuante podem acumular em rotações múltiplas
   - Recomendado recarregar cena após muitas transformações

---

## 10. Possíveis Extensões

- **Zoom com mouse wheel**: Mais intuitivo que botões
- **Pan com arrastar**: Movimentação ao arrastar canvas
- **Múltiplas janelas**: Visualizar mesma cena com diferentes windows
- **Animação**: Interpolar transformações suavemente
- **Exportar imagem**: Salvar viewport como PNG
- **Editor interativo**: Criar/editar objetos com mouse

---

## 11. Conclusão

O sistema implementado atende completamente aos requisitos do TP2:

✅ Movimentação livre da window (translação, rotação, escala)  
✅ Transformação Mundo → PPC implementada corretamente  
✅ Clipping de pontos, retas (2 algoritmos) e polígonos  
✅ Interface intuitiva com controles claros  
✅ Objetos mantêm informações originais e transformadas  
✅ Leitura de arquivos XML com cores  
✅ Documentação completa e clara  

O código está organizado, comentado e segue boas práticas de programação Python. A arquitetura orientada a objetos facilita manutenção e extensões futuras.

---

## 12. Referências

- FOLEY, J. D. et al. **Computer Graphics: Principles and Practice**. 2nd ed. Addison-Wesley, 1990.
- HEARN, D.; BAKER, M. P. **Computer Graphics with OpenGL**. 4th ed. Prentice Hall, 2010.
- Documentação Python Tkinter: https://docs.python.org/3/library/tkinter.html

---

**Autores**: [Artur Neto, Breno Vambaster] 
**Disciplina**: Computação Gráfica  
**Instituição**: IFNMG - Campus Montes Claros  
**Ano**: 2025