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
porta = 4000
ttl = 7200

print("Abrindo o chat...\n")

print("Registrar no Rendevouz: ")
name = input("--> Nome: ")
namespace = input("--> Dominio: ")
print()

meu_id = name + "@" + namespace
eu = contatos.carregar_eu()
eu = eu[0]
eu['Name'] = name
eu['@'] = namespace


resposta = rendevouz.register(namespace, name, porta, ttl)
if resposta.get("status") == "OK": 
    print(f"{name}@{namespace} registrado com sucesso.\n")
    eu['IP'] = resposta.get("ip")
    eu['Port'] = resposta.get("port") 

eu = [eu]
contatos.salvar_json(eu, "EU.json")

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








                





















        
