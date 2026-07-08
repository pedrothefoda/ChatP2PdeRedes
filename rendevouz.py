#############################################
###               GRUPO 15                ###
###   Pedro Dantas Freitas - 200026011    ###
###      Renato Correia - 242027390       ###
#############################################

import json
import os
import socket

import contatos

parametros = contatos.carregar_parametros()

server_IP = parametros.get("IP Rendevouz")
server_port = int(parametros.get("Port Rendevouz"))


def send_server(mensagem):
    try:
        conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conexao.settimeout(5.0)
        conexao.connect((server_IP, server_port))
        mensagem_json = json.dumps(mensagem) + "\n"
        conexao.sendall(mensagem_json.encode('utf-8'))

        resposta = conexao.recv(4096)
        if resposta:
            resposta = resposta.decode('utf-8')
            resposta = json.loads(resposta)
        else:
            resposta = {"status": "ERRO", "payload": "sem resposta do servidor"}
        return resposta

    except Exception as e:
        erro = {"status": "ERRO", "payload": e}
        return erro


##################### REGISTER #####################
def register(namespace, name, port=4000, ttl=300):
    mensagem ={}
    mensagem["type"] = "REGISTER"
    mensagem["namespace"] = namespace
    mensagem["name"] = name
    mensagem["port"] = str(port)
    mensagem["ttl"] = ttl

    resposta = send_server(mensagem)
    return resposta


##################### DISCOVER #####################
def discover(namespace=False):
    mensagem ={}
    mensagem["type"] = "DISCOVER"
    if namespace: mensagem["namespace"] = namespace

    resposta = send_server(mensagem)
    if resposta['status'] == "ERRO":
        return resposta
    elif resposta['status'] == "OK":
        peers = resposta['peers']
        
        nomes_peers = []
        for p in peers:
            name = p["name"]
            namespace = p["namespace"]
            nomes_peers.append(f"{name}@{namespace}")
            ip = p["ip"]
            port = p["port"]
            contatos.adicionar_contato(name,namespace,ip,port)
        return nomes_peers


##################### UNREGISTER #####################
def unregister(namespace, name=False, port=False):
    mensagem ={}
    mensagem["type"] = "UNREGISTER"
    mensagem["namespace"] = namespace
    if name: mensagem["name"] = name
    if port: mensagem["port"] = port

    resposta = send_server(mensagem)
    if resposta['status'] == "ERRO":
        return resposta
    elif resposta['status'] == "OK":
        return None



if __name__ == "__main__":
    eu_json = "EU.json"
    if os.path.exists(eu_json):
        with open(eu_json, 'r', encoding='utf-8') as arquivo:
            eu = json.load(arquivo)
    else:
        eu = [
            {
            "Name": "pedro",
            "@": "unb",
            "IP": "177.18.227.163",
            "Port": "4000",
            "Active": "True",
            "RTT" : None
            }
        ]
        
    dom = eu[0]['@']
    nome = eu[0]['Name']
    porta = eu[0]["Port"]
    ttl = 500
    print(register(dom,nome,porta,ttl))
    peers = discover()
    print(f"Pares descobertos:")
    for p in peers:
        print(f"-> {p}")

    #print(unregister(dom))
    
