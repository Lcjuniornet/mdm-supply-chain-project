"""
═══════════════════════════════════════════════════════════════════════════════
PROJETO MDM SUPPLY CHAIN
Script: Gerador de Dados Simulados de Materiais
Autor: Luiz Carlos Junior
Data: Fevereiro 2026
═══════════════════════════════════════════════════════════════════════════════

DESCRIÇÃO:
Gera dataset simulado de 3.000 materiais com características realistas de
ambiente supply chain/logística, incluindo problemas propositais de qualidade
de dados para análise.

PROBLEMAS SIMULADOS:
- 8-12% duplicatas (códigos e descrições)
- 15-25% campos vazios
- 5-10% materiais parados (sem movimento 12+ meses)
- Distribuição Curva ABC realista
- Inconsistências nomenclatura/NCM

OUTPUT:
- data/raw/materiais_raw.csv (3000+ registros)
═══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Configurar seed para reprodutibilidade
np.random.seed(42)
random.seed(42)

print("\n" + "="*80)
print("🏭 GERADOR DE DADOS SIMULADOS - PROJETO MDM")
print("="*80 + "\n")

# ═══════════════════════════════════════════════════════════════════════════
# 1. CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════════════════

N_MATERIAIS = 3000
TAXA_DUPLICATAS = 0.10  # 10% duplicatas
TAXA_CAMPOS_VAZIOS = 0.20  # 20% campos vazios
TAXA_PARADOS = 0.08  # 8% materiais parados

print(f"📊 Configuração:")
print(f"   - Total materiais: {N_MATERIAIS}")
print(f"   - Taxa duplicatas: {TAXA_DUPLICATAS*100:.0f}%")
print(f"   - Taxa campos vazios: {TAXA_CAMPOS_VAZIOS*100:.0f}%")
print(f"   - Taxa materiais parados: {TAXA_PARADOS*100:.0f}%\n")

# ═══════════════════════════════════════════════════════════════════════════
# 2. DADOS BASE
# ═══════════════════════════════════════════════════════════════════════════

# Categorias de materiais
CATEGORIAS = [
    'Fixação', 'Ferramentas', 'Elétrico', 'Hidráulico', 'Pneumático',
    'Eletrônico', 'Mecânico', 'Embalagem', 'EPI', 'Limpeza',
    'Escritório', 'Químico', 'Lubrificante', 'Peças', 'Acessórios'
]

# Unidades de medida
UNIDADES = ['UN', 'KG', 'L', 'M', 'M²', 'CX', 'PCT', 'RL', 'GL']

# Tipos de materiais por categoria
TIPOS_MATERIAIS = {
    'Fixação': ['Parafuso', 'Porca', 'Arruela', 'Rebite', 'Prego'],
    'Ferramentas': ['Chave', 'Martelo', 'Alicate', 'Furadeira', 'Serra'],
    'Elétrico': ['Cabo', 'Disjuntor', 'Tomada', 'Interruptor', 'Lâmpada'],
    'Hidráulico': ['Tubo', 'Conexão', 'Válvula', 'Mangueira', 'Registro'],
    'Pneumático': ['Cilindro', 'Válvula', 'Mangueira', 'Conexão', 'Filtro'],
    'Eletrônico': ['Resistor', 'Capacitor', 'LED', 'Sensor', 'Módulo'],
    'Mecânico': ['Rolamento', 'Correia', 'Engrenagem', 'Eixo', 'Bucha'],
    'Embalagem': ['Caixa', 'Fita', 'Plástico', 'Papelão', 'Etiqueta'],
    'EPI': ['Luva', 'Capacete', 'Óculos', 'Bota', 'Máscara'],
    'Limpeza': ['Detergente', 'Desinfetante', 'Pano', 'Vassoura', 'Balde'],
    'Escritório': ['Papel', 'Caneta', 'Pasta', 'Grampeador', 'Clips'],
    'Químico': ['Solvente', 'Ácido', 'Base', 'Reagente', 'Catalisador'],
    'Lubrificante': ['Óleo', 'Graxa', 'Spray', 'Pasta', 'Fluido'],
    'Peças': ['Rolamento', 'Anel', 'Vedação', 'Junta', 'Retentor'],
    'Acessórios': ['Suporte', 'Abraçadeira', 'Gancho', 'Presilha', 'Clipe']
}

# Especificações por tipo
ESPECIFICACOES = {
    'Parafuso': ['M6', 'M8', 'M10', 'M12', 'M16'],
    'Porca': ['M6', 'M8', 'M10', 'M12', 'M16'],
    'Cabo': ['2,5mm²', '4mm²', '6mm²', '10mm²', '16mm²'],
    'Tubo': ['1/2"', '3/4"', '1"', '1.1/4"', '2"'],
    'Luva': ['P', 'M', 'G', 'GG', 'XG'],
}

# Materiais comuns
MATERIAIS_BASE = ['Aço', 'Inox', 'PVC', 'Plástico', 'Alumínio', 'Cobre', 'Latão']

# Fornecedores
FORNECEDORES = [
    'Metalúrgica ABC', 'Distribuidora XYZ', 'Comercial DEF',
    'Industrial GHI', 'Importadora JKL', 'Nacional MNO',
    'Suprimentos PQR', 'Materiais STU', 'Fornecedor VWX'
]

# Localizações (formato: Corredor-Prateleira-Altura)
def gerar_localizacao():
    corredor = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
    prateleira = random.randint(1, 20)
    altura = random.randint(1, 5)
    return f"{corredor}-{prateleira:02d}-{altura:02d}"

# Centros de custo
CENTROS_CUSTO = ['LOG-001', 'LOG-002', 'MAN-001', 'MAN-002', 'ADM-001', 'PRO-001']

# Responsáveis
RESPONSAVEIS = [
    'João Silva', 'Maria Santos', 'Carlos Oliveira', 'Ana Costa',
    'Pedro Souza', 'Paula Lima', 'Ricardo Alves', 'Fernanda Rocha'
]

# Status
STATUS_LISTA = ['Ativo', 'Ativo', 'Ativo', 'Ativo', 'Ativo', 'Ativo',  # 90% ativos
                'Inativo', 'Bloqueado']

# ═══════════════════════════════════════════════════════════════════════════
# 3. FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

def gerar_ncm():
    """Gera código NCM realista (8 dígitos)"""
    # NCMs comuns para materiais industriais
    ncms_base = [
        '73181', '84841', '85443', '39269', '40169',
        '73269', '39174', '85369', '73089', '84831'
    ]
    ncm = random.choice(ncms_base) + str(random.randint(100, 999))
    return ncm

def gerar_descricao(categoria, i):
    """Gera descrição realista de material"""
    tipo = random.choice(TIPOS_MATERIAIS.get(categoria, ['Item']))
    material = random.choice(MATERIAIS_BASE)
    
    # Especificação se disponível
    espec = ''
    if tipo in ESPECIFICACOES:
        espec = ' ' + random.choice(ESPECIFICACOES[tipo])
    
    # Variações na descrição (para gerar duplicatas propositais)
    if random.random() < 0.15:  # 15% chance de variação
        variacao = random.choice([
            f"{tipo}{espec} {material}",
            f"{tipo} {material}{espec}",
            f"{tipo}{espec} em {material}",
            f"{tipo.lower()}{espec} {material}",  # lowercase
        ])
        return variacao
    else:
        return f"{tipo}{espec} {material}"

def gerar_preco_curva_abc():
    """Gera preço seguindo distribuição Curva ABC"""
    # Curva ABC: 20% materiais = 80% valor
    rand = random.random()
    
    if rand < 0.20:  # Classe A (20%)
        return round(random.uniform(100, 2000), 2)
    elif rand < 0.50:  # Classe B (30%)
        return round(random.uniform(10, 100), 2)
    else:  # Classe C (50%)
        return round(random.uniform(0.10, 10), 2)

def gerar_data_cadastro():
    """Gera data de cadastro nos últimos 2 anos"""
    dias_atras = random.randint(0, 730)  # 2 anos
    data = datetime.now() - timedelta(days=dias_atras)
    return data.strftime('%Y-%m-%d')

def gerar_ultima_movimentacao(data_cadastro):
    """Gera data última movimentação (pode ser parada propositalmente)"""
    data_cad = datetime.strptime(data_cadastro, '%Y-%m-%d')
    
    # 8% materiais parados (sem movimento 12+ meses)
    if random.random() < TAXA_PARADOS:
        dias_parado = random.randint(365, 730)  # 1-2 anos parado
    else:
        dias_parado = random.randint(0, 90)  # Movimento recente
    
    data_mov = data_cad + timedelta(days=random.randint(0, 365)) - timedelta(days=dias_parado)
    return max(data_cad, data_mov).strftime('%Y-%m-%d')

# ═══════════════════════════════════════════════════════════════════════════
# 4. GERAR DADOS
# ═══════════════════════════════════════════════════════════════════════════

print("🔄 Gerando materiais...")

dados = []

for i in range(N_MATERIAIS):
    categoria = random.choice(CATEGORIAS)
    data_cadastro = gerar_data_cadastro()
    
    material = {
        'codigo_material': f'MAT-{i+1:05d}',
        'descricao': gerar_descricao(categoria, i),
        'categoria': categoria,
        'unidade_medida': random.choice(UNIDADES),
        'preco_unitario': gerar_preco_curva_abc(),
        'estoque_atual': random.randint(0, 5000),
        'estoque_minimo': random.randint(10, 500),
        'fornecedor_principal': random.choice(FORNECEDORES),
        'data_cadastro': data_cadastro,
        'ultima_movimentacao': gerar_ultima_movimentacao(data_cadastro),
        'status': random.choice(STATUS_LISTA),
        'centro_custo': random.choice(CENTROS_CUSTO),
        'ncm': gerar_ncm(),
        'localizacao_fisica': gerar_localizacao(),
        'responsavel_cadastro': random.choice(RESPONSAVEIS),
    }
    
    dados.append(material)
    
    if (i + 1) % 500 == 0:
        print(f"   ✓ {i + 1}/{N_MATERIAIS} materiais gerados")

print(f"   ✅ {N_MATERIAIS} materiais gerados!\n")

# Criar DataFrame
df = pd.DataFrame(dados)

# ═══════════════════════════════════════════════════════════════════════════
# 5. INSERIR PROBLEMAS PROPOSITAIS
# ═══════════════════════════════════════════════════════════════════════════

print("🔧 Inserindo problemas propositais de qualidade...")

# 5.1. DUPLICATAS (10%)
n_duplicatas = int(N_MATERIAIS * TAXA_DUPLICATAS)
indices_duplicar = random.sample(range(N_MATERIAIS), n_duplicatas)

for idx in indices_duplicar:
    # Criar duplicata modificando código
    duplicata = df.iloc[idx].copy()
    duplicata['codigo_material'] = f'MAT-{N_MATERIAIS + len(dados) + 1:05d}'
    
    # Pequena variação no preço
    duplicata['preco_unitario'] *= random.uniform(0.95, 1.05)
    
    # Variação na descrição (maiúscula/minúscula, espaços)
    if random.random() < 0.5:
        duplicata['descricao'] = duplicata['descricao'].upper()
    
    df = pd.concat([df, duplicata.to_frame().T], ignore_index=True)

print(f"   ✓ {n_duplicatas} duplicatas inseridas ({TAXA_DUPLICATAS*100:.0f}%)")

# 5.2. CAMPOS VAZIOS (20%)
campos_opcionais = [
    'fornecedor_principal', 'localizacao_fisica', 'ncm',
    'estoque_minimo', 'centro_custo'
]

for campo in campos_opcionais:
    n_vazios = int(len(df) * TAXA_CAMPOS_VAZIOS)
    indices_vazio = random.sample(range(len(df)), n_vazios)
    df.loc[indices_vazio, campo] = np.nan

print(f"   ✓ {TAXA_CAMPOS_VAZIOS*100:.0f}% campos opcionais vazios")

# 5.3. INCONSISTÊNCIAS
# Alguns NCMs inválidos (zeros)
n_ncm_invalido = int(len(df) * 0.05)
indices_ncm = random.sample(range(len(df)), n_ncm_invalido)
df.loc[indices_ncm, 'ncm'] = '00000000'
print(f"   ✓ 5% NCMs inválidos")

# Alguns preços zerados
n_preco_zero = int(len(df) * 0.03)
indices_preco = random.sample(range(len(df)), n_preco_zero)
df.loc[indices_preco, 'preco_unitario'] = 0.00
print(f"   ✓ 3% preços zerados")

print()

# ═══════════════════════════════════════════════════════════════════════════
# 6. SALVAR ARQUIVO
# ═══════════════════════════════════════════════════════════════════════════

# Criar diretório se não existir
os.makedirs('data/raw', exist_ok=True)

# Salvar CSV
output_file = 'data/raw/materiais_raw.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("💾 Salvando arquivo...")
print(f"   📁 Arquivo: {output_file}")
print(f"   📊 Registros: {len(df)}")
print(f"   📏 Colunas: {len(df.columns)}")
print(f"   💽 Tamanho: {os.path.getsize(output_file) / 1024:.1f} KB\n")

# ═══════════════════════════════════════════════════════════════════════════
# 7. ESTATÍSTICAS FINAIS
# ═══════════════════════════════════════════════════════════════════════════

print("="*80)
print("📊 ESTATÍSTICAS DO DATASET GERADO")
print("="*80 + "\n")

print(f"Total registros: {len(df)}")
print(f"Total colunas: {len(df.columns)}\n")

print("Distribuição Categorias:")
print(df['categoria'].value_counts().head(5).to_string())
print()

print("Distribuição Status:")
print(df['status'].value_counts().to_string())
print()

print(f"Preço médio: R$ {df['preco_unitario'].mean():.2f}")
print(f"Preço mínimo: R$ {df['preco_unitario'].min():.2f}")
print(f"Preço máximo: R$ {df['preco_unitario'].max():.2f}\n")

print(f"Valor total estoque: R$ {(df['estoque_atual'] * df['preco_unitario']).sum():,.2f}\n")

print("Completude campos:")
completude = (1 - df.isnull().sum() / len(df)) * 100
print(completude.sort_values().to_string())
print()

# Materiais parados (sem movimento 12+ meses)
data_atual = datetime.now()
df['dias_sem_movimento'] = (data_atual - pd.to_datetime(df['ultima_movimentacao'])).dt.days
parados_12m = len(df[df['dias_sem_movimento'] > 365])
print(f"Materiais parados 12+ meses: {parados_12m} ({parados_12m/len(df)*100:.1f}%)\n")

print("="*80)
print("✅ DATASET GERADO COM SUCESSO!")
print("="*80 + "\n")

print("📌 PRÓXIMOS PASSOS:")
print("   1. Verificar arquivo: data/raw/materiais_raw.csv")
print("   2. Abrir Excel e conferir dados")
print("   3. Executar: scripts/01_identificar_duplicatas.py")
print("   4. Executar: scripts/02_calcular_completude.py\n")

print("🚀 Bom trabalho com as análises!\n")
