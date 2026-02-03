
import os
import msvcrt
import getpass
from datetime import date

from funcoes import *

def menu():
    print('--- MENU PRINCIPAL ---')
    print('1 - Abrir caixa')
    print('2 - Registrar venda')
    print('3 - Total do caixa')
    print('4 - Fechar caixa')
    print('5 - Cadastros')
    print('0 - Sair')

def main():
    # 🔵 ESTADO ÚNICO DO SISTEMA
    estado = {
        "caixa": {
            "aberto": False,
            "abertura": None,
            "fechamento": None
        },
        "usuario": None,
        "vendas": [],
        "grupos": grupos.copy(),    # mantém os grupos pré-existentes
        "produtos": produtos.copy() # mantém os produtos pré-existentes
    }

    # Login
    usuario = login_user()
    if not usuario:
        return

    estado["usuario"] = usuario

    while True:
        limpar_tela()
        print(f'Usuário: {estado["usuario"]}\n')
        menu()

        op = input('Escolha: ')

        if op == '1':
            abrir_caixa(estado)

        elif op == '2':
            registrar_venda(estado)

        elif op == '3':
            total_caixa(estado["vendas"])

        elif op == '4':
            fechar_caixa(estado)

        elif op == '5':
            menu_cadastros(estado)

        elif op == '0':
            break

        else:
            print('Opção inválida.')
            pausar()

if __name__ == '__main__':
    main()
