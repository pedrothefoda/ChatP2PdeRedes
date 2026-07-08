#############################################
###               GRUPO 15                ###
###   Pedro Dantas Freitas - 200026011    ###
###      Renato Correia - 242027390       ###
#############################################

import socket
import os
import json
import queue
import uuid
import threading
from datetime import datetime, timezone

from contatos import carregar_json
from contatos import resolver_ip
from contatos import procura_contato
from contatos import carregar_parametros
from contatos import salvar_json


fila_msg = queue.Queue()    
conexoes_ativas = {}
keep_alive = {}
Inbound = []
Outbound = []

def enviar_mensagem(mensagem, ip, port):
    global conexoes_ativas
    global fila_msg
    global Inbound
    global Outbound
    global keep_alive

    parametros = carregar_parametros()
    meu_id = f"{parametros['Name']}@{parametros['@']}"

    helloo = {
        "type": "HELLO",
        "peer_id": meu_id,
        "version": "1.0",
        "features": ["ack", "metrics"],
        "ttl": 1
    }
    
    chave = (ip, int(port))

    if chave not in conexoes_ativas:        #se nao tem: tenta mandar um HELLO e cria
        try:                    
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(7.0)
            s.connect(chave)
            s.sendall((json.dumps(helloo) + "\n").encode('utf-8'))
            
            resposta = s.recv(4096)
            
            if resposta:
                resposta_texto = resposta.decode('utf-8').strip().split('\n')[0]
                resposta_json = json.loads(resposta_texto)
                if resposta_json.get("type") == "HELLO_OK":
                    s.settimeout(None)
                    conexoes_ativas[chave] = s
                    
                    keep_alive[chave] = 0

                    lista = carregar_json()
                    for c in lista:
                        if c['IP'] == ip and int(c['Port']) == int(port):
                            c['Active'] = "True"
                    salvar_json(lista,"CONTATOS.json")
                    
                    try:
                        dst = resolver_ip(ip,port)
                        Outbound.append(dst)
                    except: pass
                    
                else:
                    erro = {"type": "ERRO", "payload": "Não recebi HELLO_OK"}
                    return erro
            
        except Exception as e:
            erro = {"type": "ERRO", "payload": e, "IPport": chave}
            return erro
        
    conexao = conexoes_ativas[chave]
    
    try:
        mensagem_json = json.dumps(mensagem) + "\n"
        conexao.sendall(mensagem_json.encode('utf-8'))

        acerto = {"type": "OK", "payload": mensagem}
        return acerto
    
    except Exception as e:
        try:
            conexao.close()
        except:
            pass
        
        del conexoes_ativas[chave]    
        erro = {"type": "ERRO", "payload": e, "IPport": chave}
        return erro


##################### HELLO #####################
def hello(dst):
    parametros = carregar_parametros()
    meu_id = f"{parametros['Name']}@{parametros['@']}"
    mensagem = {}
    uid = str(uuid.uuid4())
    time = datetime.now(timezone.utc).isoformat()
    
    mensagem["type"] = "HELLO"
    mensagem["peer_id"] = meu_id
    mensagem["version"] = "1.0"
    mensagem["features"] = ["ack", "metrics"]
    mensagem["ttl"] = 1

    ip,port = procura_contato(dst)   
    funcionou = enviar_mensagem(mensagem, ip, port)

    return funcionou


##################### PING #####################
def ping(dst):
    mensagem = {}
    uid = str(uuid.uuid4())
    time = datetime.now(timezone.utc).isoformat()
    
    mensagem["type"] = "PING"
    mensagem["msg_id"] = uid
    mensagem["timestamp"] = time
    mensagem["ttl"] = 1

    ip,port = procura_contato(dst)   
    funcionou = enviar_mensagem(mensagem, ip, port)

    return funcionou


##################### SEND #####################
def send(payload, dst):
    parametros = carregar_parametros()
    meu_id = f"{parametros['Name']}@{parametros['@']}"
    mensagem = {}
    uid = str(uuid.uuid4())
    #time = datetime.now(timezone.utc).isoformat()
    
    mensagem["type"] = "SEND"
    mensagem["msg_id"] = uid
    mensagem["src"] = meu_id
    mensagem["dst"] = dst
    mensagem["payload"] = payload
    mensagem["require_ack"] = True
    mensagem["ttl"] = 1

    ip,port = procura_contato(dst)   
    funcionou = enviar_mensagem(mensagem, ip, port)

    return funcionou



##################### PUB #####################
def pub(payload, dst):
    parametros = carregar_parametros()
    meu_id = f"{parametros['Name']}@{parametros['@']}"
    mensagem = {}
    uid = str(uuid.uuid4())
    #time = datetime.now(timezone.utc).isoformat()
    
    mensagem["type"] = "PUB"
    mensagem["msg_id"] = uid
    mensagem["src"] = meu_id
    mensagem["dst"] = dst
    mensagem["payload"] = payload
    mensagem["require_ack"] = False
    mensagem["ttl"] = 1

    ip,port = procura_contato(dst)   
    funcionou = enviar_mensagem(mensagem, ip, port)

    return funcionou



##################### BYE #####################
def bye(dst):
    parametros = carregar_parametros()
    meu_id = f"{parametros['Name']}@{parametros['@']}"
    mensagem = {}
    uid = str(uuid.uuid4())
    
    mensagem["type"] = "BYE"
    mensagem["msg_id"] = uid
    mensagem["src"] = meu_id
    mensagem["dst"] = dst
    mensagem["reason"] = "Encerrando sessão"
    mensagem["ttl"] = 1

    ip,port = procura_contato(dst)   
    funcionou = enviar_mensagem(mensagem, ip, port)

    chave = (ip,port)
    if chave in conexoes_ativas:
        conexao = conexoes_ativas[chave]
        try:
            conexao.close()
        except: pass
        
        del conexoes_ativas[IPport]

    return funcionou
    
    
    
##################### TESTES #####################
if __name__ == "__main__":
    import time
    print(hello('vm_giga@CIC'))
    print(ping('vm_giga@CIC'))
    print(send('Olá?', 'vm_giga@CIC'))
    time.sleep(5)
    print(hello('pedro@note'))
    print(ping('pedro@note'))
    print(send('Teste123', 'pedro@note'))




  
