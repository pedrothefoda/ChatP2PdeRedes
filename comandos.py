#############################################
###               GRUPO 15                ###
###   Pedro Dantas Freitas - 200026011    ###
###      Renato Correia - 242027390       ###
#############################################

import json

import contatos
import rendevouz
import mensagens
import conexoes


def encerrar_tudo():
    
    parametros = contatos.carregar_parametros()
    lista = contatos.carregar_json()
    meu_nome = parametros['Name']
    meu_space = parametros['@']
    meu_IP = parametros['IP']
    
    for c in lista:
        if c['IP'] == meu_IP:
            erro = rendevouz.unregister(c['@'], c['Name'])
            if erro:
                print(f"Falha ao desregistrar {c['Name']}@{c['@']}: {erro['payload']} \n")
                
    print("----- Desregistrado do Rendevouz")
    
    lista = [
        {
        "Name": "vm_giga",
        "@": "CIC",
        "IP": "45.171.101.167",
        "Port": "8081",
        "Active": "False",
        "RTT" : []
        }
    ]
    contatos.salvar_json(lista, "CONTATOS.json")
    print("----- Contatos deletados")

    chaves = list(mensagens.conexoes_ativas.keys())
    for ch in chaves:
        conexoes.encerra_conexao(ch)
    #print(f"--- {mensagens.conexoes_ativas} e {conexoes.escutadas}")
    print("----- Conexões encerradas\n")

def pega_comando():
    pega = True
    while pega:
        comando = input("Insira um comando: \n")
        comando = comando.split()
        print()
        
        if comando == []:
            pass
        
        ############# /quit #############
        elif comando[0] == "/quit":
            pega = False

        ############# /peers #############
        elif comando[0] == "/peers":    
            if len(comando) == 1:
                peers = rendevouz.discover()
                print(f"Pares descobertos:")
                for p in peers:
                    print(f"-> {p}")

                lista = contatos.carregar_json()
                print(f"\nSua lista de contatos atualizada:")
                for c in lista:
                    print(f"-> {c['Name']}@{c['@']}\t| Active: {c['Active']}")
                
                
            elif len(comando) == 2:
                if comando[1] == "*":
                    peers = rendevouz.discover()
                    print(f"Pares descobertos:")
                    for p in peers:
                         print(f"-> {p}")
                         
                    lista = contatos.carregar_json()
                    print(f"\nSua lista de contatos atualizada:")
                    for c in lista:
                        print(f"-> {c['Name']}@{c['@']}\t| Active: {c['Active']}")
                    
                elif "#" in comando[1]:
                    namespace = comando[1].replace("#","")
                    peers = rendevouz.discover(namespace)
                    print(f"Pares descobertos:")
                    for p in peers:
                        print(f"-> {p}")
                         
                    lista = contatos.carregar_json()
                    print(f"\nSua lista de contatos atualizada:")
                    for c in lista:
                        print(f"-> {c['Name']}@{c['@']}\t| Active: {c['Active']}")
                    
                else:
                    print(f"Please use '/peers' or '/peers *' or '/peers #namespace' or '/peers # namespace'")
            
            elif len(comando) == 3:
                if comando[1] == "#":
                    namespace = comando[2]
                    peers = rendevouz.discover(namespace)
                    print(f"Pares descobertos:")
                    for p in peers:
                        print(f"-> {p}")
                         
                    lista = contatos.carregar_json()
                    print(f"\nSua lista de contatos atualizada:")
                    for c in lista:
                        print(f"-> {c['Name']}@{c['@']}\t| Active: {c['Active']}")
                    
                else:
                    print(f"Please use '/peers' or '/peers *' or '/peers #namespace' or '/peers # namespace'")
            print()
            
        ############# /msg #############
        elif comando[0] == "/msg":
            del comando[0]
            dst = comando[0]
            del comando[0]
            msg = " ".join(comando)
            erro = mensagens.send(msg, dst)
            if erro['type'] == "ERRO":
                print(f"Erro: {erro['payload']}")
                print("Tente novamente... \n")
            elif erro['type'] == "OK":
                print(f"Mensagem enviada para {dst} \n")
                
            
            
        ############# /pub #############  consertar a mensagem aki igual fiz no send
        elif comando[0] == "/pub":
            if len(comando) > 2:
                del comando[0]
                if comando[0] == "*":
                    del comando[0]
                    msg = " ".join(comando)
                    lista = contatos.carregar_json()
                    ex = False
                    for c in lista:
                        dst = f"{c['Name']}@{c['@']}"
                        erro = mensagens.pub(msg, dst)
                        
                        if erro['type'] == "ERRO":
                            ex = True
                            print(f"Erro: {erro['payload']}")
                            IPport = erro['IPport']
                            ip, port = IPport
                            peer = contatos.resolver_ip(ip,port)
                            print(f"{peer} não alcançado. Tente novamente...")
                            print()
                            
                    if not ex: print(f"Mensagem enviada para todos contatos salvos \n")
                            
                elif "#" in comando[0]:
                    namespace = comando[0].strip("#")
                    del comando[0]
                    msg = " ".join(comando)
                    lista = contatos.carregar_json()
                    ex = False
                    for c in lista:
                        if c['@'] == namespace:
                            dst = f"{c['Name']}@{c['@']}"
                            erro = mensagens.pub(msg, dst)
                            if erro['type'] == "ERRO":
                                ex = True
                                print(f"Erro: {erro['payload']}")
                                IPport = erro['IPport']
                                ip, port = IPport
                                peer = contatos.resolver_ip(ip,port)
                                print(f"{peer} não alcançado. Tente novamente...")
                                print()
                                
                    if not ex: print(f"Mensagem enviada para todos @{namespace} salvos \n")
                            
                else:
                    print(f"Please use '/pub #<namespace> <'mensagem'>' or /pub * <'mensagem'> \n")
            else:
                print(f"Please use '/pub #<namespace> <'mensagem'>' or /pub * <'mensagem'> \n")
        

        ############# /conn #############
        elif comando[0] == "/conn":
            print(f"Conexões Inbound:")
            for c in mensagens.Inbound:
                print(f"-> {c}")
            print()
            print(f"Conexões Outbound:")
            for c in mensagens.Outbound:
                print(f"-> {c}")
            print()
            
        ############# /rtt #############
        elif comando[0] == "/rtt":
            lista = contatos.carregar_json()
            print(f"RTT médio por peer: ")
            for c in lista:
                if c['RTT'] == []:
                    RTT = 'sem resposta'
                else:
                    RTT = 0
                    for rt in c['RTT']:
                        RTT += rt
                    RTT = RTT/len(c['RTT'])
                    
                print(f"-> {c['Name']}@{c['@']}\t| RTT: {RTT}")
            print()
            
        ############# /reconnect #############
        elif comando[0] == "/reconnect":
            lista = contatos.carregar_json()
            erro = False
            for c in lista:
                dst = f"{c['Name']}@{c['@']}"
                funcionou = mensagens.hello(dst)
                if funcionou.get("type") == "ERRO":
                    erro = True
                    print(f"\t Erro: {dst} - {funcionou['payload']} \n")
            if not erro:
                print(f"HELLO enviado para todos os contatos \n")
                    
            

        ############# COMANDO INVALIDO #############
        else:
            print("Comando inválido!\nUse um dos comandos a seguir:")
            print("->'/peers' or '/peers *' or '/peers #<namespace>'")
            print("->'/msg <peer_id> <'mensagem'>'")
            print("->'/pub * <'mensagem'>' or '/pub #<namespace> <'mensagem'>'")
            print("->'/conn'")
            print("->'/rtt'")
            print("->'/reconnect'")
            print("->'/quit'")
            print()
            

    encerrar_tudo()
                
                    
                




##################### TESTES #####################
if __name__ == "__main__":
    pega_comando()













                
    
    
