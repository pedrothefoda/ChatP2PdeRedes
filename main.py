#############################################
###               GRUPO 15                ###
###   Pedro Dantas Freitas - 200026011    ###
###      Renato Correia - 242027390       ###
#############################################

import socket
import os
import json
import uuid
import queue
import time
import threading
from datetime import datetime, timezone

import contatos
import rendevouz
import mensagens
import conexoes
import comandos

comandos.encerrar_tudo()

# --- Configurações Iniciais ---
parametros = contatos.carregar_parametros()
porta = parametros.get("Port")
ttl = parametros.get("TTL")

print("Abrindo o chat...\n")

conectado = False
while not conectado:
    print("Registrar no Rendevouz: ")
    name = input("--> Nome: ")
    namespace = input("--> Dominio: ")
    print()

    meu_id = name + "@" + namespace
    parametros['Name'] = name
    parametros['@'] = namespace


    resposta = rendevouz.register(namespace, name, porta, ttl)
    if resposta.get("status") == "OK":
        conectado = True
        print(f"{name}@{namespace} registrado com sucesso.\n")
        parametros['IP'] = resposta.get("ip")
        parametros['Port'] = resposta.get("port")
    else:
        print(f"Conexão com servidor Rendevoux FALHOU... Tente novamente")
 

contatos.salvar_json(parametros, "PARAMETROS.json")


procurador = threading.Thread(target=conexoes.procura_conexao, args=(4000,))
procurador.daemon = True
procurador.start()
    
respondedor = threading.Thread(target=conexoes.responde)
respondedor.daemon = True
respondedor.start()

monitor = threading.Thread(target=conexoes.minhas_conexoes)
monitor.daemon = True
monitor.start()

pegador = threading.Thread(target=comandos.pega_comando)
pegador.daemon = True
pegador.start()

mantedor = threading.Thread(target=conexoes.mantem_conexoes)
mantedor.daemon = True
mantedor.start()








                





















        
