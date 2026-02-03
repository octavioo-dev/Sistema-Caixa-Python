
import os
import msvcrt
import getpass
from datetime import date
import json

from funcoes import *

# =========================
# DADOS INICIAIS DE USUÁRIOS
# =========================
usuarios_padrao = {
    'admin': '191063',
    'octavio': 'octa1234',
    'fernando': 'furiagamer'
}

# =========================
# MENU PRINCIPAL
# =========================
def menu():
    print('--- MENU PRINCIPAL ---')
    print('1 - Abrir caixa')
    print('2 - Registrar venda')
    print('3 - Total do caixa')
    print('4 - Fechar caixa')
    print('5 - Cadastros')
    print('0 - Sair')

# =========================
# MAIN
# =========================
def main():
    # 🔵 ESTADO ÚNICO DO SISTEMA (carregado dentro do main)
    estado = {
        "caixa": carregar_json('caixa.json', {"aberto": False, "abertura": None, "fechamento": None}),
        "usuario": None,
        "vendas": carregar_json('vendas.json', []),
        "grupos": carregar_json('grupos.json', {"01": {"nome": "Computadores"}, "02": {"nome": "Notebooks"}}),
        "produtos": carregar_json('produtos.json', {
            "01001": {"nome": "Pc Gamer 9° geração", "grupo": "01", "preco": 6599.99, "estoque": 10},
            "01002": {"nome": "Pc Gamer 7° geração", "grupo": "01", "preco": 4699.99, "estoque": 14},
            "02001": {"nome": "Notebook DELL i7", "grupo": "02", "preco": 3560.00, "estoque": 5},
            "02002": {"nome": "Notebook ASUS i5", "grupo": "02", "preco": 2677.99, "estoque": 4}
        })
    }

    # Carregar usuários do JSON ou usar padrão
    estado["usuarios"] = carregar_json('usuarios.json', usuarios_padrao)

    # Login
    usuario = login_user()
    if not usuario:
        return
    estado["usuario"] = usuario

    # Loop do menu
    while True:
        limpar_tela()
        print(f'Usuário: {estado["usuario"]}\n')
        menu()

        op = input('Escolha: ').strip()

        if op == '1':
            abrir_caixa(estado)
            salvar_json('caixa.json', estado["caixa"])

        elif op == '2':
            registrar_venda(estado)
            salvar_json('vendas.json', estado["vendas"])

        elif op == '3':
            total_caixa(estado)

        elif op == '4':
            fechar_caixa(estado)
            salvar_json('vendas.json', estado["vendas"])
            salvar_json('caixa.json', estado["caixa"])

        elif op == '5':
            menu_cadastros(estado)
            salvar_json('grupos.json', estado["grupos"])
            salvar_json('produtos.json', estado["produtos"])

        elif op == '0':
            break

        else:
            print('❌ Opção inválida.')
            pausar()

if __name__ == '__main__':
    main()