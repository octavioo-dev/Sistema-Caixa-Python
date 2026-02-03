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
# LOGIN DE USUÁRIO
# =========================
def login_user(max_tentativa=3):
    """
    Solicita login do usuário com limite de tentativas.
    Retorna o nome do usuário autenticado ou None se falhar.
    """
    tentativas = 0

    while tentativas < max_tentativa:
        limpar_tela()
        print('--- Sistema de Controle de Caixa ---\n')
        print('Faça o Login para continuar\n')

        user = input('Usuário: ').strip().lower()
        senha = getpass.getpass('Senha: ').strip()

        # Verifica se o usuário existe e senha confere
        if user in usuarios and usuarios[user] == senha:
            print(f'\n✅ Bem-vindo(a), {user}!')
            pausar()
            return user  # Usuário autenticado

        tentativas += 1
        print(f'\n❌ Usuário ou senha inválidos ({tentativas}/{max_tentativa})')
        pausar('Tente novamente...')

    # Excede tentativas
    print('\n🚫 Número máximo de tentativas atingido. Saindo do sistema.')
    pausar()
    return None



# =========================
# CAIXA
# =========================

def abrir_caixa(estado):
    """
    Abre o caixa se ainda não estiver aberto e se o caixa do dia atual
    não tiver sido fechado. Atualiza o estado da aplicação.
    """
    hoje = date.today()
    caixa = estado["caixa"]

    # Verifica se o caixa já foi fechado hoje
    if caixa["fechamento"] == hoje:
        print('🚫 Caixa do dia já foi fechado.')
        pausar()
        return

    # Verifica se o caixa já está aberto
    if caixa["aberto"]:
        print('⚠️ Caixa já está aberto.')
        pausar()
        return

    # Abrindo caixa
    caixa["aberto"] = True
    caixa["abertura"] = datetime.now()
    caixa["fechamento"] = None
    print(f'🔓 Caixa aberto em {caixa["abertura"].strftime("%d/%m/%Y %H:%M:%S")}')
    pausar()



def registrar_venda(estado):
    """
    Registra uma venda enquanto o caixa estiver aberto.
    Atualiza estoque, total da venda e registra no estado.
    """
    caixa = estado["caixa"]
    usuario_logado = estado["usuario"]
    vendas = estado["vendas"]
    produtos = estado["produtos"]

    if not caixa["aberto"]:
        print('🚫 Caixa fechado.')
        pausar()
        return

    limpar_tela()
    print('--- Registrar Venda ---')
    

    itens = []
    total = 0

    while True:
        print('\nDigite 0 para finalizar a venda\n')
        codigo = input('Código do produto: ').strip()
        
        # Finaliza venda
        if codigo == '0':
            break

        # Validação do produto
        if codigo not in produtos:
            print('❌ Produto não encontrado.')
            continue

        produto = produtos[codigo]

        # Solicita quantidade
        try:
            qtd = int(input('Quantidade: ').strip())
            if qtd <= 0:
                print('❌ Quantidade inválida.')
                continue
        except ValueError:
            print('❌ Digite um número válido.')
            continue

        # Verifica estoque
        if produto['estoque'] < qtd:
            print('❌ Estoque insuficiente.')
            continue

        # Cálculo do subtotal
        subtotal = produto['preco'] * qtd
        total += subtotal

        # Baixa no estoque
        produto['estoque'] -= qtd

        # Adiciona item à venda
        # Após calcular subtotal e adicionar item
        itens.append({
            'codigo': codigo,
            'produto': produto['nome'],
            'quantidade': qtd,
         'preco_unitario': produto['preco'],
         'subtotal': subtotal
        })

        print(f'✅ Item adicionado: {produto["nome"]} x{qtd} R$ {subtotal:.2f}\n')

    # Se não houver itens, cancela a venda
    if not itens:
        print('Nenhum item registrado.')
        pausar()
        return

    # Registra venda no estado
    vendas.append({
        'itens': itens,
        'total': total,
        'usuario': usuario_logado,
        'data_hora': datetime.now()
    })

    # Resumo da venda
    limpar_tela()
    print('--- Venda Finalizada ---')
    for item in itens:
        print(f"- {item['produto']} x{item['quantidade']} R$ {item['subtotal']:.2f}")

    print(f'\nTOTAL: R$ {total:.2f}')
    pausar()


def total_caixa(vendas):
    """
    Exibe todas as vendas registradas e o total acumulado.
    """
    limpar_tela()

    if not vendas:
        print('📭 Nenhuma venda registrada.')
        pausar()
        return

    total = 0
    for i, venda in enumerate(vendas, 1):
        print(f'\n📄 Venda {i} - {venda["data_hora"].strftime("%d/%m/%Y %H:%M")}')
        for item in venda['itens']:
            print(f"   {item['produto']} x{item['quantidade']} R$ {item['subtotal']:.2f}")
        print(f"   Total: R$ {venda['total']:.2f}")
        total += venda['total']

    print('\n' + '-'*30)
    print(f'💰 TOTAL EM CAIXA: R$ {total:.2f}')
    pausar()


def fechar_caixa(estado):
    """
    Exibe todas as vendas do dia, mostrando operador, data e hora,
    calcula o total e realiza o fechamento do caixa.
    """
    caixa = estado["caixa"]
    vendas = estado["vendas"]

    # Valida se o caixa está aberto
    if not caixa["aberto"]:
        print('🚫 Caixa ainda não foi aberto.')
        pausar()
        return

    # Valida se há vendas
    if not vendas:
        print('📭 Nenhuma venda registrada.')
        pausar()
        return

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

    # Confirmação de fechamento
    confirmar = input('\nDeseja realmente fechar o caixa? (s/n): ').lower()

    if confirmar == 's':
        print('\n🔒 Caixa fechado com sucesso!')
        caixa["aberto"] = False
        caixa["fechamento"] = date.today()
        caixa["abertura"] = None
        vendas.clear()
        pausar()
        return

    print('\n❌ Fechamento cancelado.')
    pausar()




# =========================
# CADASTROS
# =========================

def listar_grupos(estado):
    """
    Exibe todos os grupos cadastrados no sistema.
    """
    grupos = estado["grupos"]

    if not grupos:
        print("\n📭 Nenhum grupo cadastrado.")
        pausar()
        return

    print("\n--- Grupos Cadastrados ---")
    for codigo, dados in grupos.items():
        print(f"{codigo} - {dados['nome']}")
    
    pausar()

def cadastrar_grupo(estado):
    """
    Permite cadastrar um novo grupo, validando código e nome.
    Atualiza o estado da aplicação.
    """
    grupos = estado["grupos"]
    limpar_tela()
    print('--- Cadastro de Grupo ---')

    while True:
        codigo = input('Código do grupo (0 para voltar): ').strip()

        # Voltar ao menu
        if codigo == '0':
            return

        # Validação de código numérico
        if not codigo.isdigit():
            print('❌ Código inválido.')
            continue

        # Normaliza código (1 -> 01)
        codigo = normalizar_codigo(codigo)

        # Verifica se já existe
        if codigo in grupos:
            print('❌ Já existe um grupo com esse código.')
            continue

        # Nome do grupo
        nome = input('Nome do grupo: ').strip()
        if not nome:
            print('❌ O nome do grupo não pode ser vazio.')
            continue

        # Adiciona ao estado
        grupos[codigo] = {'nome': nome}

        print('✅ Grupo cadastrado com sucesso!')
        pausar()
        return
    
def cadastrar_produtos(estado):
    """
    Permite cadastrar um novo produto, garantindo código único,
    grupo existente, nome não vazio, preço positivo e estoque válido.
    Atualiza o estado da aplicação.
    """
    grupos = estado["grupos"]
    produtos = estado["produtos"]

    limpar_tela()
    print('--- Cadastro de Produto ---')

    # Verifica se há grupos cadastrados
    if not grupos:
        print('❌ Nenhum grupo cadastrado!')
        pausar()
        return

    print('Grupos disponíveis:')
    for cod, g in grupos.items():
        print(f'{cod} - {g["nome"]}')

    # Seleção de grupo
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

    # Nome do produto
    while True:
        nome = input('Nome do produto: ').strip()
        if nome:
            break
        print('❌ O nome do produto não pode ser vazio.')

    # Preço
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

    # Estoque
    while True:
        try:
            estoque = int(input('Quantidade em estoque: '))
            if estoque < 0:
                print('❌ Estoque inválido.')
                continue
            break
        except ValueError:
            print('❌ Digite um número válido.')

    # Adiciona produto ao estado
    produtos[codigo_completo] = {
        'nome': nome,
        'grupo': cod_grupo,
        'preco': preco,
        'estoque': estoque
    }

    print('✅ Produto cadastrado com sucesso!')
    pausar()

def listar_produtos(estado):
    """
    Exibe todos os produtos cadastrados, mostrando código, nome,
    grupo, preço e estoque.
    """
    produtos = estado["produtos"]
    grupos = estado["grupos"]

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

def menu_produtos(estado):
    """
    Menu para listar produtos ou voltar ao menu principal.
    """
    while True:
        limpar_tela()
        print("1 - Listar produtos")
        print("0 - Voltar")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            listar_produtos(estado)
        elif opcao == "0":
            return
        else:
            print('❌ Opção inválida.')
            pausar()

def menu_cadastros(estado):
    """
    Menu de cadastros do sistema: grupos e produtos.
    Todas as operações manipulam o estado centralizado.
    """
    while True:
        limpar_tela()
        print('--- MENU DE CADASTROS ---')
        print('1 - Cadastrar grupo')
        print('2 - Cadastrar produto')
        print('3 - Listar produtos')
        print('0 - Voltar')

        op = input('Escolha: ').strip()

        if op == '1':
            cadastrar_grupo(estado)
        elif op == '2':
            cadastrar_produtos(estado)
        elif op == '3':
            listar_produtos(estado)
        elif op == '0':
            break
        else:
            print('❌ Opção inválida.')
            pausar()
                      
def verificar_estoque(estado, codigo, quantidade):
    """
    Verifica se um produto existe e se há estoque suficiente.
    Retorna (True, "") se tudo ok, ou (False, mensagem) em caso de erro.
    """
    produto = estado["produtos"].get(codigo)
    if not produto:
        return False, "Produto não encontrado."

    if produto["estoque"] < quantidade:
        return False, "Estoque insuficiente."

    return True, ""

def baixar_estoque(estado, codigo, quantidade):
    """
    Reduz a quantidade em estoque de um produto.
    """
    produto = estado["produtos"].get(codigo)
    if produto:
        produto["estoque"] -= quantidade

def repor_estoque(estado, codigo, quantidade):
    """
    Aumenta a quantidade em estoque de um produto.
    """
    produto = estado["produtos"].get(codigo)
    if produto:
        produto["estoque"] += quantidade

