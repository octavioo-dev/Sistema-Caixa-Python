import os
import msvcrt
import getpass
from datetime import datetime, date


# =========================
# DADOS DO SISTEMA
# =========================

usuarios = {
    'admin': '191063',
    'octavio': 'octa1234',
    'fernando': 'furiagamer'
}

grupos = {
    "01": {
        "nome": "Computadores"
    },
    "02": {
        "nome": "Notebooks"
    }
}

produtos = {
    "01001": {
        "nome": "Pc Gamer 9° geração",
        "grupo": "01",
        "preco": 6599.99,
        "estoque": 10
    },
    "01002": {
        "nome": "Pc Gamer 7° geração",
        "grupo": "01",
        "preco": 4699.99,
        "estoque": 14
    },
    "02001": {
        "nome": "Notebook DELL i7",
        "grupo": "02",
        "preco": 3560.00,
        "estoque": 5
    },
    "02002": {
        "nome": "Notebook ASUS i5",
        "grupo": "02",
        "preco": 2677.99,
        "estoque": 4
    }
}

# =========================
# FUNÇÕES UTILITÁRIAS
# =========================

def normalizar_codigo(codigo):
    codigo = str(codigo).strip()
    if len(codigo) == 1:
        return f"0{codigo}"
    return codigo

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar(msg='Pressione ENTER para continuar...'):
    input(f'\n{msg}')

def buscar_produto(codigo):
    return produtos.get(codigo)

# =========================
# LOGIN
# =========================

def login_user(max_tentativa=3):
    tentativas = 0

    while tentativas < max_tentativa:
        limpar_tela()
        print('--- Sistema de Controle de Caixa ---\n')
        print('Faça o Login para continuar\n')
        user = input('Usuário: ').strip().lower()
        senha = getpass.getpass('Senha: ')

        if user in usuarios and usuarios[user] == senha:
            print(f'\n✅ Bem-vindo, {user}!')
            pausar()
            return user

        tentativas += 1
        print(f'\n❌ Usuário ou senha inválidos ({tentativas}/{max_tentativa})')
        pausar()

    print('\n🚫 Tentativas esgotadas.')
    pausar()
    return False


# =========================
# CAIXA
# =========================

def abrir_caixa(caixa_aberto, data_fechamento):
    hoje = date.today()

    if data_fechamento == hoje:
        print('🚫 Caixa do dia já foi fechado.')
        pausar()
        return caixa_aberto, data_fechamento

    if caixa_aberto:
        print('⚠️ Caixa já está aberto.')
        pausar()
        return caixa_aberto, data_fechamento

    print(f'🔓 Caixa aberto em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    pausar()
    return True, None


def registrar_venda(estado):
    if not caixa_aberto:
        print('🚫 Caixa fechado.')
        pausar()
        return

    limpar_tela()
    print('--- Registrar Venda ---')
    print('Digite o código do produto (0 para finalizar)\n')

    itens = []
    total = 0

    while True:
        codigo = input('Código do produto: ').strip()

        # Finaliza venda
        if codigo == '0':
            break

        # Validação do produto
        if codigo not in produtos:
            print('❌ Produto não encontrado.')
            continue

        produto = produtos[codigo]

        # Quantidade
        try:
            qtd = int(input('Quantidade: '))
            if qtd <= 0:
                print('❌ Quantidade inválida.')
                continue
        except ValueError:
            print('❌ Digite um número válido.')
            continue

        # Estoque
        if produto['estoque'] < qtd:
            print('❌ Estoque insuficiente.')
            continue

        # Cálculos
        subtotal = produto['preco'] * qtd
        total += subtotal

        # Baixa estoque
        produto['estoque'] -= qtd

        itens.append({
            'codigo': codigo,
            'produto': produto['nome'],
            'quantidade': qtd,
            'preco_unitario': produto['preco'],
            'subtotal': subtotal
        })

        print('✅ Item adicionado.\n')

    # Venda cancelada
    if not itens:
        print('Nenhum item registrado.')
        pausar()
        return

    # Registra venda
    vendas.append({
        'itens': itens,
        'total': total,
        'usuario': usuario_logado,
        'data_hora': datetime.now()
    })

    # Resumo
    limpar_tela()
    print('--- Venda Finalizada ---')
    for item in itens:
        print(
            f"- {item['produto']} "
            f"x{item['quantidade']} "
            f"R$ {item['subtotal']:.2f}"
        )

    print(f'\nTOTAL: R$ {total:.2f}')
    pausar()



def total_caixa(vendas):
    limpar_tela()

    if not vendas:
        print('📭 Nenhuma venda registrada.')
        pausar()
        return

    total = 0
    for i, venda in enumerate(vendas, 1):
        print(f'\nVenda {i} - {venda["data_hora"].strftime("%d/%m/%Y %H:%M")}')
        for item in venda['itens']:
            print(f"  {item['produto']} x{item['quantidade']} R$ {item['subtotal']:.2f}")
        print(f"  Total: R$ {venda['total']:.2f}")
        total += venda['total']

    print('\n' + '-'*30)
    print(f'TOTAL EM CAIXA: R$ {total:.2f}')
    pausar()


def fechar_caixa(vendas, caixa_aberto):
    """
    Exibe todas as vendas do dia, mostrando operador, data e hora, e realiza o fechamento.
    """
    if not caixa_aberto:
        print('🚫 Caixa ainda não foi aberto.')
        pausar()
        return caixa_aberto, None

    if not vendas:
        print('📭 Nenhuma venda registrada.')
        pausar()
        return caixa_aberto, None

    limpar_tela()
    print('📊 FECHAMENTO DE CAIXA\n')

    total_geral = 0

    for i, venda in enumerate(vendas, start=1):
        print(
            f'🧾 Venda {i} | '
            f'{venda["data_hora"].strftime("%d/%m/%Y %H:%M:%S")} | '
            f'Operador: {venda["usuario"]}'
        )

        for item in venda['itens']:
            print(
                f'  - {item["produto"]} '
                f'x{item["quantidade"]} '
                f'R$ {item["subtotal"]:.2f}'
            )
            total_geral += item['subtotal']

        print(f'  ➜ Total da venda: R$ {venda["total"]:.2f}\n')

    print('-' * 40)
    print(f'💰 TOTAL DO CAIXA: R$ {total_geral:.2f}')

    confirmar = input('\nDeseja realmente fechar o caixa? (s/n): ').lower()

    if confirmar == 's':
        print('\n🔒 Caixa fechado com sucesso!')
        vendas.clear()
        pausar()
        return False, date.today()

    print('\n❌ Fechamento cancelado.')
    pausar()
    return caixa_aberto, None



# =========================
# CADASTROS
# =========================

def listar_grupos():
    print("\n--- Grupos Cadastrados ---")
    for codigo, dados in grupos.items():
        print(f"{codigo} - {dados['nome']}")

def cadastrar_grupo():
    limpar_tela()
    print('--- Cadastro de Grupo ---')

    while True:
        codigo = input('Código do grupo (0 para voltar): ').strip()

        if codigo == '0':
            return

        if not codigo.isdigit():
            print('❌ Código inválido.')
            continue

        codigo = normalizar_codigo(codigo)

        if codigo in grupos:
            print('❌ Já existe um grupo com esse código.')
            continue

        nome = input('Nome do grupo: ').strip()
        if not nome:
            print('❌ O nome do grupo não pode ser vazio.')
            continue

        grupos[codigo] = {
            'nome': nome
        }

        print('✅ Grupo cadastrado com sucesso!')
        pausar()
        return

def cadastrar_produtos():
    limpar_tela()
    print('--- Cadastro de Produto ---')

    if not grupos:
        print('❌ Nenhum grupo cadastrado!')
        pausar()
        return

    print('Grupos disponíveis:')
    for cod, g in grupos.items():
        print(f'{cod} - {g["nome"]}')

    # Código do grupo
    while True:
        cod_grupo = input('Código do grupo (0 para voltar): ').strip()

        if cod_grupo == '0':
            return

        if not cod_grupo.isdigit():
            print('❌ Código inválido.')
            continue

        cod_grupo = normalizar_codigo(cod_grupo)

        if cod_grupo not in grupos:
            print('❌ Grupo não encontrado.')
            continue

        break

    # Código do produto
    while True:
        cod_prod = input('Código do produto: ').strip()

        if not cod_prod.isdigit():
            print('❌ Código inválido.')
            continue

        cod_prod = cod_prod.zfill(3)  # sempre 001, 002...

        codigo_completo = f'{cod_grupo}{cod_prod}'

        if codigo_completo in produtos:
            print('❌ Produto já cadastrado.')
            continue

        break

    # ✅ VALIDAÇÃO DE NOME
    while True:
        nome = input('Nome do produto: ').strip()
        if nome:
            break
        print('❌ O nome do produto não pode ser vazio.')

    # ✅ VALIDAÇÃO DE PREÇO
    while True:
        preco_input = input('Preço do produto: R$ ').replace(',', '.').strip()
        try:
            preco = float(preco_input)
            if preco <= 0:
                print('❌ O preço deve ser maior que zero.')
                continue
            break
        except ValueError:
            print('❌ Preço inválido.')

    # ✅ ESTOQUE
    while True:
        try:
            estoque = int(input('Quantidade em estoque: '))
            if estoque < 0:
                print('❌ Estoque inválido.')
                continue
            break
        except ValueError:
            print('❌ Digite um número válido.')

    produtos[codigo_completo] = {
        'nome': nome,
        'grupo': cod_grupo,
        'preco': preco,
        'estoque': estoque
    }

    print('✅ Produto cadastrado com sucesso!')
    pausar()

def listar_produtos():
    limpar_tela()
    print('--- Produtos Cadastrados ---')

    if not produtos:
        print('❌ Nenhum produto cadastrado.')
        pausar()
        return

    for codigo, dados in produtos.items():
        grupo_nome = grupos.get(dados['grupo'], {}).get('nome', 'Desconhecido')
        print(
            f'Código: {codigo} | '
            f'Produto: {dados["nome"]} | '
            f'Grupo: {grupo_nome} | '
            f'Preço: R$ {dados["preco"]:.2f} | '
            f'Estoque: {dados["estoque"]}'
        )

    pausar()

def menu_produtos():
    while True:
        limpar_tela()
        print("1 - Listar produtos")
        print("0 - Voltar")

        opcao = input("Escolha: ")

        if opcao == "1":
            listar_produtos()
        elif opcao == "0":
            return

def menu_cadastros(grupos):
    while True:
        limpar_tela()
        print('1 - Cadastrar grupo')
        print('2 - Cadastrar produto')
        print('3 - Listar produtos')
        print('0 - Voltar')

        op = input('Escolha: ')

        if op == '1':
            cadastrar_grupo()
        elif op == '2':
            cadastrar_produtos(grupos)
        elif op == '3':
            listar_produtos()
        elif op == '0':
            break
        else:
            print('Opção inválida.')
            pausar()
                      
def verificar_estoque(codigo, quantidade):
    produto = buscar_produto(codigo)
    if not produto:
        return False, "Produto não encontrado."

    if produto["estoque"] < quantidade:
        return False, "Estoque insuficiente."

    return True, ""

def baixar_estoque(codigo, quantidade):
    produtos[codigo]["estoque"] -= quantidade

def repor_estoque(codigo, quantidade):
    produtos[codigo]["estoque"] += quantidade

