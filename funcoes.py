import os
import msvcrt
import getpass
from datetime import datetime, date
import json


# =========================
# DADOS DO SISTEMA
# =========================

usuarios = {
    'admin': '191063',
    'octavio': 'octa1234',
    'fernando': 'furiagamer'
}

# =========================
# UTILITÁRIOS JSON
# =========================
def salvar_json(arquivo, dados):
    """
    Salva o dicionário 'dados' em um arquivo JSON.
    🔹 Substitui o arquivo existente.
    🔹 Converte objetos datetime em string automaticamente.
    """
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4, default=str)
    except Exception as e:
        print(f"❌ Erro ao salvar {arquivo}: {e}")


def carregar_json(arquivo, default=None):
    """
    Carrega dados de um arquivo JSON.
    🔹 Retorna 'default' se o arquivo não existir ou estiver vazio/corrompido.
    🔹 Datas salvas como string permanecerão como string.
    """
    if default is None:
        default = {}

    if not os.path.exists(arquivo):
        return default

    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar {arquivo}: {e}")
        return default


# =========================
# FUNÇÕES UTILITÁRIAS
# =========================

def normalizar_codigo(codigo):
    """Transforma código de 1 dígito em 2 dígitos, ex: 1 -> 01"""
    codigo = str(codigo).strip()
    if len(codigo) == 1:
        return f"0{codigo}"
    return codigo

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar(msg='Pressione ENTER para continuar...'):
    input(f'\n{msg}')

def buscar_produto(estado, codigo):
    return estado["produtos"].get(codigo)


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

    # Converter abertura/fechamento para date se vier do JSON
    fechamento = caixa.get("fechamento")
    if isinstance(fechamento, str):
        try:
            fechamento = datetime.fromisoformat(fechamento).date()
        except:
            fechamento = None

    if fechamento == hoje:
        print('🚫 Caixa do dia já foi fechado.')
        pausar()
        return

    if caixa.get("aberto"):
        print('⚠️ Caixa já está aberto.')
        pausar()
        return

    # Abrir caixa
    caixa["aberto"] = True
    caixa["abertura"] = datetime.now()
    caixa["fechamento"] = None
    print(f'🔓 Caixa aberto em {caixa["abertura"].strftime("%d/%m/%Y %H:%M:%S")}')
    pausar()



def registrar_venda(estado):
    """
    Registra uma venda enquanto o caixa estiver aberto.
    Atualiza estoque, total da venda e registra no estado.
    Salva vendas no JSON automaticamente.
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
        'data_hora': datetime.now().isoformat()  # salva como string ISO
    })

    # Salva vendas no JSON
    salvar_json('vendas.json', vendas)

    # Resumo da venda
    limpar_tela()
    print('--- Venda Finalizada ---')
    for item in itens:
        print(f"- {item['produto']} x{item['quantidade']} R$ {item['subtotal']:.2f}")
    print(f'\nTOTAL: R$ {total:.2f}')
    pausar()


def total_caixa(estado):
    """
    Exibe todas as vendas registradas, mostrando operador, itens, total da venda,
    e calcula o total acumulado em caixa somando todos os itens de todas as vendas.
    """
    vendas = estado["vendas"]
    limpar_tela()

    if not vendas:
        print('📭 Nenhuma venda registrada.')
        pausar()
        return

    total_caixa = 0  # total acumulado de todas as vendas

    for i, venda in enumerate(vendas, 1):
        data_hora = venda["data_hora"]
        if isinstance(data_hora, str):
            try:
                data_hora = datetime.fromisoformat(data_hora)
            except:
                data_hora = datetime.now()  # fallback

        print(f'\n📄 Venda {i} - {data_hora.strftime("%d/%m/%Y %H:%M")} | Operador: {venda["usuario"]}')

        total_venda = 0  # soma dos itens desta venda
        for item in venda['itens']:
            print(f"   {item['produto']} x{item['quantidade']} R$ {item['subtotal']:.2f}")
            total_venda += item['subtotal']

        print(f"   Total da venda: R$ {total_venda:.2f}")

        total_caixa += total_venda  # acumula no total do caixa

    print('\n' + '-'*30)
    print(f'💰 TOTAL EM CAIXA: R$ {total_caixa:.2f}')
    pausar()


def fechar_caixa(estado):
    """
    Exibe todas as vendas do dia, mostrando operador, data e hora,
    calcula o total e realiza o fechamento do caixa.
    """
    caixa = estado["caixa"]
    vendas = estado["vendas"]

    if not caixa.get("aberto"):
        print('🚫 Caixa ainda não foi aberto.')
        pausar()
        return

    if not vendas:
        print('📭 Nenhuma venda registrada.')
        pausar()
        return

    limpar_tela()
    print('📊 FECHAMENTO DE CAIXA\n')

    total_geral = 0

    for i, venda in enumerate(vendas, start=1):
        data_hora = venda["data_hora"]
        if isinstance(data_hora, str):
            try:
                data_hora = datetime.fromisoformat(data_hora)
            except:
                data_hora = datetime.now()  # fallback

        print(
            f'🧾 Venda {i} | '
            f'{data_hora.strftime("%d/%m/%Y %H:%M:%S")} | '
            f'Operador: {venda["usuario"]}'
        )

        for item in venda['itens']:
            print(
                f'  - {item["produto"]} x{item["quantidade"]} R$ {item["subtotal"]:.2f}'
            )
            total_geral += item['subtotal']

        print(f'  ➜ Total da venda: R$ {venda["total"]:.2f}\n')

    print('-' * 40)
    print(f'💰 TOTAL DO CAIXA: R$ {total_geral:.2f}')

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
    Atualiza o estado da aplicação e salva no JSON.
    """
    grupos = estado["grupos"]
    limpar_tela()
    print('--- Cadastro de Grupo ---')

    while True:
        # Solicita código do grupo
        codigo = input('Código do grupo (0 para voltar): ').strip()
        if codigo == '0':  # Voltar ao menu
            return
        
        if not codigo.isdigit():  # Código numérico
            print('❌ Código inválido.')
            continue

        codigo = normalizar_codigo(codigo)

        if codigo in grupos:  # Código duplicado
            print('❌ Já existe um grupo com esse código.')
            continue

        # Nome do grupo
        nome = input('Nome do grupo: ').strip()

        if not nome:
            print('❌ O nome do grupo não pode ser vazio.')
            continue

        # Adiciona ao estado e salva
        grupos[codigo] = {'nome': nome}
        salvar_json('grupos.json', grupos)
        print('✅ Grupo cadastrado com sucesso!')
        pausar()
        return
    
def cadastrar_produtos(estado):
    """
    Permite cadastrar um novo produto, garantindo código único,
    grupo existente, nome não vazio, preço positivo e estoque válido.
    Atualiza o estado e salva no JSON.
    """
    grupos = estado["grupos"]
    produtos = estado["produtos"]

    limpar_tela()
    print('--- Cadastro de Produto ---')

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

    # Adiciona produto ao estado e salva
    produtos[codigo_completo] = {
        'nome': nome,
        'grupo': cod_grupo,
        'preco': preco,
        'estoque': estoque
    }
    salvar_json('produtos.json', produtos)
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

