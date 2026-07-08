#############################################
###               GRUPO 15                ###
###   Pedro Dantas Freitas - 200026011    ###
###      Renato Correia - 242027390       ###
#############################################

import socket
import json
import threading
import queue
import uuid
import time
from datetime import datetime, timezone

import contatos
import mensagens


escutadas = set()           #lista especial confia

############################### ACEITA CONEXÕES ###############################
def procura_conexao(porta):
    global escutadas
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    #libera minha porta de volta caso feche
        s.bind(("0.0.0.0", int(porta)))
        s.listen(8)
        
        procura = True
        while procura:
            conexao, IPport = s.accept()
            
            mensagens.conexoes_ativas[IPport] = conexao
            escutadas.add(IPport)

            guardador = threading.Thread(target=guarda_conexao, args=(conexao, IPport))
            guardador.daemon = True
            guardador.start()


    except Exception as e:
        pass



############################### RECEBE MENSAGEM E GUARDA NA FILA ###############################
def guarda_conexao(conexao,IPport):

    try:
        conexao.settimeout(None)
        while True:
            msg_recived = conexao.recv(4096)
            if msg_recived:
                msg_recived = msg_recived.decode('utf-8').strip()
                msgs_recived = msg_recived.split('\n')

                for msg in msgs_recived:
                    if msg.strip():
                        msg = json.loads(msg)
                        if "type" in msg:
                            mensagens.fila_msg.put((msg, IPport, conexao))
                            
            else: break
                
    except Exception as e:
        pass
    finally:
        try: conexao.close()
        except: pass
        if IPport in mensagens.conexoes_ativas:
            del mensagens.conexoes_ativas[IPport]
        if IPport in escutadas:
            escutadas.remove(IPport)



############################### MANDA PINGs INDISCIRMINADAMENTE ###############################
def mantem_conexoes():
    parametros = contatos.carregar_parametros()
    tempo = int(parametros.get("PING"))
    
    while True:
        chaves_ativas = list(mensagens.conexoes_ativas.keys())
        for chave in chaves_ativas:
            mensagens.keep_alive[chave] = int(mensagens.keep_alive[chave]) + 1
            
            ip,port = chave
            #print(f" Mantem conexões {ip}:{port}")
            dst = contatos.resolver_ip(ip,port)
            if dst:
                funcionou = mensagens.ping(dst)
                if funcionou.get("type") == "ERRO":
                    print(f" Erro no PING para {dst}: {funcionou['payload']}")
            
                       
        time.sleep(tempo)
         
 
############################### TENTA ESCUTAR UM CONEXÃO ATIVA ###############################
def minhas_conexoes():
    global escutadas
    while True:
        chaves = list(mensagens.conexoes_ativas.keys())
        for chave in chaves:
            conexao = mensagens.conexoes_ativas[chave]

            escutador = threading.Thread(target=guarda_conexao, args=(conexao, chave))
            escutador.daemon = True
            escutador.start()
            if chave not in escutadas:
                escutadas.add(chave)
                
        time.sleep(1)

                
            
            
############################### ENCERRADOR ###############################
def encerra_conexao(chave):
    if chave in mensagens.conexoes_ativas:
        conexao = mensagens.conexoes_ativas[chave]
        try:
            conexao.close()
        except: pass

        try:
            del mensagens.conexoes_ativas[chave]
        except Exception as e: pass
            #ip,port = chave
            #dst = contatos.resolver_ip(ip,port)
            #print(f"Conexão com {dst} não foi encerrada... Tente novamente {e}") o del sempre da a chave como exeption
        
    if chave in escutadas:
        try:
            escutadas.remove(chave)
        except:
            ip,port = chave
            dst = contatos.resolver_ip(ip,port)
            print(f"Conexão com {dst} não foi encerrada... Tente novamente AAAA")



############################### AUTOREPLY ###############################
def responde():   
    parametros = contatos.carregar_parametros()
    meu_id = f"{parametros['Name']}@{parametros['@']}"
    
    while True:
        msg, IPport, conexao = mensagens.fila_msg.get()
        ip, port = IPport

        #print(msg)

        ######################## HELLO ########################
        if msg.get("type") == "HELLO":
            mensagens.conexoes_ativas[IPport] = conexao
            mensagens.keep_alive[IPport] = 0
            
            resposta = {
                "type": "HELLO_OK",
                "peer_id": meu_id,
                "version": "1.0",
                "features": ["ack", "metrics"],
                "ttl": 1
            }
            conexao.sendall((json.dumps(resposta) + "\n").encode('utf-8'))

            if __name__ == "__main__": print(f"-> HELLO_OK enviado\n")

            lista = contatos.carregar_json()
            for c in lista:
                if c['IP'] == ip and int(c['Port']) == int(port):
                    c['Active'] = "True"
                    #c['PONG'] = 0
                
            contatos.salvar_json(lista, 'CONTATOS.json')
            try:
                dst = resolver_ip(ip,port)
                mensagens.Outbound.append(dst)
            except: pass
            


        ######################## HELLO_OK ########################
        elif msg.get("type") == "HELLO_OK":
            mensagens.conexoes_ativas[IPport] = conexao
            mensagens.keep_alive[IPport] = 0
            
            resposta = {
                "type": "PING",
                "msg_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(), 
                "ttl": 1
            }
            conexao.sendall((json.dumps(resposta) + "\n").encode('utf-8'))

            if __name__ == "__main__": print(f"-> PING enviado\n")

            lista = contatos.carregar_json()
            for c in lista:
                if c['IP'] == ip and int(c['Port']) == int(port):
                    c['Active'] = "True"
                    #c['PONG'] = 0
                
            contatos.salvar_json(lista, 'CONTATOS.json')
            try:
                dst = resolver_ip(ip,port)
                mensagens.Inbound.append(dst)
            except: pass


        ######################## PING ########################
        elif msg.get("type") == "PING":
            mensagens.keep_alive[IPport] = 0
            
            agora = datetime.now(timezone.utc).isoformat()
            timedele = msg.get("timestamp")
            
            resposta = {
                "type": "PONG",
                "msg_id": msg.get("msg_id"),
                "timestamp": agora, 
                "ttl": 1
            }
            conexao.sendall((json.dumps(resposta) + "\n").encode('utf-8'))
            
            if __name__ == "__main__": print(f"-> PONG enviado\n")

            try:
                timedele = datetime.fromisoformat(timedele)
            except Exception as e:
                if "isoformat" in str(e):
                    #print(f"antes {timedele}")
                    timedele = timedele.replace("Z","+00:00")
                    #print(f"depois {timedele}")
                    timedele = datetime.fromisoformat(timedele)

                agora = datetime.fromisoformat(agora)
                delay = agora - timedele
                delay = delay.total_seconds()       # Half Trip Time
                if delay < 0:
                    print("\t delay negativo AKI no ping")
            
                lista = contatos.carregar_json()
                for c in lista:
                    if c['IP'] == ip and int(c['Port']) == int(port):
                        c['RTT'].append(delay*2)
                        #c['PONG'] = 0
                
                contatos.salvar_json(lista, 'CONTATOS.json')


        ######################## PONG ########################
        elif msg.get("type") == "PONG":
            mensagens.keep_alive[IPport] = 0
            agora = datetime.now(timezone.utc).isoformat()
            timedele = msg.get("timestamp")
            try:
                timedele = datetime.fromisoformat(timedele)
            except Exception as e:
                if "isoformat" in str(e):
                    #print(f"antes {timedele}")
                    timedele = timedele.replace("Z","+00:00")
                    #print(f"depois {timedele}")
                    timedele = datetime.fromisoformat(timedele)
            
            agora = datetime.fromisoformat(agora)
            delay = agora - timedele
            delay = delay.total_seconds()       # Half Trip Time
            if delay < 0:
                    print("\t delay negativo AKI no PONG")

            if __name__ == "__main__": print(f"-> PONG recebido\n")
                    
            lista = contatos.carregar_json()
            for c in lista:
                if c['IP'] == ip and int(c['Port']) == int(port):
                    c['RTT'].append(delay*2)
                    #c['PONG'] = 0
                    
            contatos.salvar_json(lista, 'CONTATOS.json')
            

        ######################## SEND ########################
        elif msg.get("type") == "SEND":
            timestamp = datetime.now(timezone.utc).isoformat()
            resposta = {
               "type": "ACK",
               "msg_id": msg.get("msg_id"),
               "timestamp": timestamp, 
               "ttl": 1
            }
            conexao.sendall((json.dumps(resposta) + "\n").encode('utf-8'))

            data, horario = timestamp.split("T")
            ano, mes, dia = data.split("-")
            horario, resto = horario.split("+")
            hora, minuto, seg = horario.split(":")
            hora = int(hora) - 3
            src = msg.get("src")
            payload = msg.get("payload")
            print(f"\n[{dia}/{mes}|{hora}h{minuto}|{src}]-> {payload} \n")

            if __name__ == "__main__": print(f"-> ACK enviado\n")


        ######################## PUB ########################
        elif msg.get("type") == "PUB":
            timestamp = datetime.now(timezone.utc).isoformat()
            data, horario = timestamp.split("T")
            ano, mes, dia = data.split("-")
            horario, resto = horario.split("+")
            hora, minuto, seg = horario.split(":")
            hora = int(hora) - 3
            src = msg.get("src")
            payload = msg.get("payload")
            print(f"\n[{dia}/{mes}|{hora}h{minuto}|{src}]-> {payload} \n")
            

        ######################## BYE ########################
        elif msg.get("type") == "BYE":
            resposta = {
                "type": "BYE_OK",
                "msg_id": msg.get("msg_id"),
                "src": meu_id,
                "dst": msg.get("src"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ttl": 1
            }
            conexao.sendall((json.dumps(resposta) + "\n").encode('utf-8'))

            if __name__ == "__main__": print(f"-> BYE_OK enviado\n")

            encerra_conexao(IPport)
            
            lista = contatos.carregar_json()
            for c in lista:
                if c['IP'] == ip and int(c['Port']) == int(port):
                    c['Active'] = "False"
                    c['RTT'] = []
                    #c['PONG'] = 0

            contatos.salvar_json(lista, 'CONTATOS.json')




if __name__ == "__main__":

    procurador = threading.Thread(target=procura_conexao, args=(4000,))
    procurador.daemon = True
    procurador.start()
    
    respondedor = threading.Thread(target=responde)
    respondedor.daemon = True
    respondedor.start()

    monitor_sainte = threading.Thread(target=minhas_conexoes)
    monitor_sainte.daemon = True
    monitor_sainte.start()

    mantedor = threading.Thread(target=mantem_conexoes)
    mantedor.daemon = True
    mantedor.start()

    mensagens.hello('vm_giga@CIC')
    mensagens.ping('vm_giga@CIC')
    mensagens.send('oi','vm_giga@CIC')
    while True:
        print("escutando...")
        time.sleep(5)














    
