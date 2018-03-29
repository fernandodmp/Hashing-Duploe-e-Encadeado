#Aluno: Fernando de Macedo Passos
#Versao do python utilizada: 3.5.3
#Trabalho de EDA2

#Modulo built-in do python pra transformar os dados em binario
import struct
#Modulo built-in do python pra calcular o piso na funcao h2 de hashing duplo
import math

TAMANHO_ARQUIVO = 11
#Posicao vazia na criacao do arquivo:
POS_VAZIA1 = b''
#Apos a insercao do primeiro registro, o python preenche os bytes restantes do arquivo com bytes 0(\x00) por isso o formato de posicao vazia se torna:
#Posicao vazia apos insercao do primeiro registro para hashing encadeado:
POS_VAZIA2 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
#Posicao vazia apos insercao do primeiro registro para hashing duplo:
POS_VAZIA3 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

#Funcoes de Hashing
def h1(chave):
    return(chave % TAMANHO_ARQUIVO)
def h2(chave):
    hashed = math.floor(chave/TAMANHO_ARQUIVO)
    hashed = h1(hashed)
    if hashed == 0:
        return 1
    return hashed

#Funcoes relativas ao Hashing Encadeado
#tamanho = struct.calcsize("i 21s i i") = quantidade de bytes que um registro ocupa
#unpacked indices: 0 = chave, 1 = nome, 2 = idade, 3 = prox posicao do encadeamento
#ponteiro pra lugar nenhum = TAMANHO_ARQUIVO
def procuraPosVazia(f):
    #Percorre o arquivo de tras pra frente procurando a ultima posicao vazia
    tamanho = struct.calcsize("i 21s i i")
    lastpos = TAMANHO_ARQUIVO - 1
    for i in range(lastpos, -1, -1):
        f.seek(i * tamanho)
        reg = f.read(tamanho)
        if reg == POS_VAZIA1 or reg == POS_VAZIA2:
            return i
    return(TAMANHO_ARQUIVO)
def procuraApontador(buscado, atual, arq):
    #Procura o apontador que aponta pra posicao buscada
    tamanho = struct.calcsize("i 21s i i")
    arq.seek(atual * tamanho)
    d = arq.read(tamanho)
    un = struct.unpack('i 21s i i', d)
    if (un[3] != buscado):
        return procuraApontador(buscado, un[3], arq)
    return atual
def verificaExistente(k, atual, arq):
    #Verifica se a chave ja se encontra no arquivo
    tamanho = struct.calcsize("i 21s i i")
    arq.seek(atual * tamanho)
    d = arq.read(tamanho)
    if (d == POS_VAZIA1 or d == POS_VAZIA2):
        return False
    un = struct.unpack('i 21s i i', d)
    if (un[0] != k):
        if (un[3] != TAMANHO_ARQUIVO):
            return verificaExistente(k, un[3], arq)
        return False
    return True
def iHashingEncadeado(arquivo):
    #faz a insercao em hashing encadeado
    chave = int(input())
    Nome = bytes(input(), 'utf-8')
    Idade = int(input())
    Prox = TAMANHO_ARQUIVO
    RegBin = struct.pack("i 21s i i", chave, Nome, Idade, Prox)
    tamanho = struct.calcsize("i 21s i i")
    pos = h1(chave)
    if verificaExistente(chave, pos, arquivo):
        print('chave ja existente: ' + str(chave))
        return
    arquivo.seek(pos * tamanho)
    Data = arquivo.read(tamanho)
    #Caso em que a posicao esta vazia
    if (Data == POS_VAZIA1 or Data == POS_VAZIA2):
        arquivo.seek(pos * tamanho)
        arquivo.write(RegBin)
        return
    else:
        unpacked = struct.unpack('i 21s i i', Data)
        #Caso em que o arquivo que esta na posicao indicada nao tem funcao de hashing pra a posicao
        if(h1(chave) != h1(unpacked[0])):
            aux = procuraPosVazia(arquivo)
            if aux == TAMANHO_ARQUIVO:
                return
            aux2 = procuraApontador(pos, h1(unpacked[0]), arquivo)
            arquivo.seek(aux2 * tamanho)
            LastReg = arquivo.read(tamanho)
            Ponteiro = struct.unpack('i 21s i i', LastReg)
            newPonteiro = struct.pack("i 21s i i", Ponteiro[0], Ponteiro[1], Ponteiro[2], aux)
            arquivo.seek(aux2 * tamanho)
            arquivo.write(newPonteiro)
            arquivo.seek(aux * tamanho)
            arquivo.write(Data)
            arquivo.seek(pos * tamanho)
            arquivo.write(RegBin)
            return
        #Caso em que a o hashing da posicao eh o mesmo porem ainda nao existe encadeamento
        if (unpacked[3] == TAMANHO_ARQUIVO):
            aux = procuraPosVazia(arquivo)
            if aux != TAMANHO_ARQUIVO:
                new = struct.pack("i 21s i i", unpacked[0], unpacked[1], unpacked[2], aux)
                arquivo.seek(pos * tamanho)
                arquivo.write(new)
                arquivo.seek(aux * tamanho)
                arquivo.write(RegBin)
                return
        #Caso em que a o hashing eh o mesmo mas ja existe encadeamento
        if (unpacked[3] != TAMANHO_ARQUIVO):
            aux = procuraPosVazia(arquivo)
            if aux == TAMANHO_ARQUIVO:
                return
            aux2 = procuraApontador(TAMANHO_ARQUIVO, h1(unpacked[0]), arquivo)
            arquivo.seek(aux2 * tamanho)
            LastReg = arquivo.read(tamanho)
            Ponteiro = struct.unpack('i 21s i i', LastReg)
            newPonteiro = struct.pack("i 21s i i", Ponteiro[0], Ponteiro[1], Ponteiro[2], aux)
            arquivo.seek(aux2 * tamanho)
            arquivo.write(newPonteiro)
            arquivo.seek(aux * tamanho)
            arquivo.write(RegBin)
            return
def insereHE():
    #Tenta abrir o arquivo pelo modo de rb+, caso o arquivo nao exista, cria-se ele com o modo wb+
    try:
        with open('HashingEncadeado.bin', mode='rb+') as file:
            iHashingEncadeado(file)
        file.close()

    except IOError:
        with open('HashingEncadeado.bin', mode='wb+') as file:
            iHashingEncadeado(file)
        file.close()
def buscaProxHE(k, atual, arq):
    #Busca na parte encadeada
    tamanho = struct.calcsize("i 21s i i")
    arq.seek(atual * tamanho)
    d = arq.read(tamanho)
    un = struct.unpack('i 21s i i', d)
    if (un[0] != k):
        if (un[3] != TAMANHO_ARQUIVO):
            buscaProxHE(k, un[3], arq)
            return
        print('chave nao encontrada: ' + str(k))
        return
    print('chave: ' + str(un[0]))
    print(un[1].decode('utf-8'))
    print(str(un[2]))
def buscaHE():
    try:
        #Inicia a busca da chave
        with open('HashingEncadeado.bin', mode='rb+') as file:
            tamanho = struct.calcsize("i 21s i i")
            chave = int(input())
            file.seek(h1(chave)*tamanho)
            Data = file.read(tamanho)
            #Se a posicao do hashing esta vazia quer dizer que nao houve chaves indicadas para aquela posicao
            if(Data == POS_VAZIA1 or Data == POS_VAZIA2):
                print('chave nao encontrada: ' + str(chave))
                return
            #Verifica se a cabeca do encadeamento nao contem a chave buscada e procura na cauda
            unpacked = struct.unpack('i 21s i i', Data)
            if(unpacked[0] != chave):
                if(unpacked[3] != TAMANHO_ARQUIVO):
                    buscaProxHE(chave, unpacked[3], file)
                    return
                print('chave nao encontrada: ' + str(chave))
                return
            #Chave na cabeca do encadeamento, imprime as informacoes pedidas
            print('chave: '+str(unpacked[0]))
            print(unpacked[1].decode('utf-8'))
            print(str(unpacked[2]))
    except IOError:
        print("arquivo inexistente")
def imprimeArquivoHE():
    try:
        #Percorre o arquivo e faz a impressao dos registros
        with open('HashingEncadeado.bin', mode='rb+') as file:
            tamanho = struct.calcsize("i 21s i i")
            for i in range(TAMANHO_ARQUIVO):
                file.seek(i * tamanho)
                reg = file.read(tamanho)
                if reg == POS_VAZIA1 or reg == POS_VAZIA2:
                    print(str(i)+': vazio')
                    continue
                regUnpacked = struct.unpack("i 21s i i", reg)
                if(regUnpacked[3] == TAMANHO_ARQUIVO):
                    print(str(i)+': '+str(regUnpacked[0])+' '+regUnpacked[1].decode('utf-8')+' '+str(regUnpacked[2])+' nulo')
                    continue
                print(str(i)+': '+str(regUnpacked[0])+' '+regUnpacked[1].decode('utf-8')+' '+str(regUnpacked[2])+' '+str(regUnpacked[3]))
    except IOError:
        print("arquivo inexistente")
def removeNextHE(chave, ant, atual, arq):
    #Procura o elemento a ser removido na cauda do encadeamento
    tamanho = struct.calcsize("i 21s i i")
    arq.seek(atual * tamanho)
    d = arq.read(tamanho)
    un = struct.unpack('i 21s i i', d)
    if(un[0] != chave):
        removeNextHE(chave, atual, un[3], arq)
        return
    arq.seek(ant * tamanho)
    anterior = arq.read(tamanho)
    anteriorUnpacked = struct.unpack("i 21s i i", anterior)
    anterior = struct.pack("i 21s i i", anteriorUnpacked[0], anteriorUnpacked[1], anteriorUnpacked[2], un[3])
    arq.seek(ant * tamanho)
    arq.write(anterior)
    arq.seek(atual * tamanho)
    arq.write(POS_VAZIA2)
def removeHE():
    try:
        with open('HashingEncadeado.bin', mode='rb+') as file:
            tamanho = struct.calcsize("i 21s i i")
            chave = int(input())
            pos = h1(chave)
            #Se a chave nao esta no arquivo nao tem porque remove-la
            if(not verificaExistente(chave, pos, file)):
                print('chave nao encontrada: ' + str(chave))
                return
            file.seek(h1(chave) * tamanho)
            Data = file.read(tamanho)
            unpacked = struct.unpack('i 21s i i', Data)
            #Verifica que se a posicao a ser removida esta na cabeca do encadeamento
            if(unpacked[0] == chave):
                #Remocao se a cabeca possui uma cauda
                if(unpacked[3] != TAMANHO_ARQUIVO):
                    file.seek(unpacked[3] * tamanho)
                    next = file.read(tamanho)
                    file.seek(pos * tamanho)
                    file.write(next)
                    file.seek(unpacked[3] * tamanho)
                    file.write(POS_VAZIA2)
                    return
                #Remocao caso contrario
                elif (unpacked[3] == TAMANHO_ARQUIVO):
                    file.seek(pos * tamanho)
                    file.write(POS_VAZIA2)
                    return
            #Busca chave na cauda
            removeNextHE(chave, pos, unpacked[3], file)
    except IOError:
        print("arquivo inexistente")
def contaProxAcessoHE(chave, atual, arq, contagem):
    #Verifica quantos acessos sao necessario para encontrar uma determinada chave na cauda do encadeamento
    tamanho = struct.calcsize("i 21s i i")
    arq.seek(atual * tamanho)
    d = arq.read(tamanho)
    un = struct.unpack('i 21s i i', d)
    if (un[0] != chave):
        if (un[3] != TAMANHO_ARQUIVO):
            contagem += 1
            contagem = contaProxAcessoHE(chave, un[3], arq, contagem)
            return contagem
    return contagem + 1
def contaAcessosHE(chave, arquivo, contagem):
    #Inicializa a contagem de acessos verificando a cabeca do encadeamento
    tamanho = struct.calcsize("i 21s i i")
    arquivo.seek(h1(chave) * tamanho)
    Data = arquivo.read(tamanho)
    unpacked = struct.unpack('i 21s i i', Data)
    if (unpacked[0] != chave):
        contagem += 1
        contagem = contaProxAcessoHE(chave, unpacked[3], arquivo, contagem)
        return contagem
    elif (unpacked[0] == chave):
        return contagem + 1
def mediaHE():
    try:
        with open('HashingEncadeado.bin', mode='rb+') as file:
            chaves = []
            acessos = []
            tamanho = struct.calcsize("i 21s i i")
            #Reune todas as chaves presentes no arquivo
            for i in range(TAMANHO_ARQUIVO):
                file.seek(i * tamanho)
                reg = file.read(tamanho)
                if reg == POS_VAZIA1 or reg == POS_VAZIA2:
                    continue
                regUnpacked = struct.unpack("i 21s i i", reg)
                chaves.append(regUnpacked[0])
            #Verica quantos acessos sao necessarios pra encontrar cada chave
            for i in chaves:
                acessos.append(contaAcessosHE(i, file, 0))
            media = 0
            #Calcula a media
            for i in acessos:
                media += i
            print("%.1f" % (media/len(acessos)))
    except IOError:
        print("arquivo inexistente")

#Funcoes relativas ao Hashing Duplo
#tamanho = struct.calcsize("i 21s i") = quantidade de bytes que um registro ocupa
#unpacked indices: 0 = chave, 1 = nome, 2 = idade
def verificaExistenteHD(chave, arquivo):
    pos = h1(chave)
    shift = h2(chave)
    tamanho = struct.calcsize("i 21s i")
    arquivo.seek(pos * tamanho)
    reg = arquivo.read(tamanho)
    # Verifica se a chave esta na posicao indicada por h1
    if (reg != POS_VAZIA1 and reg != POS_VAZIA3):
        regUnpacked = struct.unpack("i 21s i", reg)
        if (regUnpacked[0] == chave):
            return True
    # Procura a chave no arquivo seguindo o deslocamento dado por h2
    atual = pos + shift
    while (atual != pos):
        arquivo.seek(atual * tamanho)
        reg = arquivo.read(tamanho)
        if (reg != POS_VAZIA3 and reg != POS_VAZIA1):
            regUnpacked = struct.unpack("i 21s i", reg)
            if (regUnpacked[0] == chave):
                return True
        atual += shift
        if (atual >= TAMANHO_ARQUIVO):
            atual = atual - TAMANHO_ARQUIVO
    return False
def insereHashingDuplo(arquivo):
    chave = int(input())
    Nome = bytes(input(), 'utf-8')
    Idade = int(input())
    pos = h1(chave)
    shift = h2(chave)
    RegBin = struct.pack("i 21s i", chave, Nome, Idade)
    tamanho = struct.calcsize("i 21s i")
    #Verifica se a chave ja se encontra no arquivo
    if verificaExistenteHD(chave, arquivo):
        print('chave ja existente: ' + str(chave))
        return
    arquivo.seek(pos * tamanho)
    reg = arquivo.read(tamanho)
    #Verifica se a posicao dada por h1 esta vazia, se estiver a chave eh inserida
    if (reg == POS_VAZIA1 or reg == POS_VAZIA3):
        arquivo.seek(pos * tamanho)
        arquivo.write(RegBin)
        return
    #Percorre o arquivo, seguindo o deslocamento dado por h2 em busca de uma posicao vazia
    atual = pos + shift
    while (atual != pos):
        arquivo.seek(atual * tamanho)
        reg = arquivo.read(tamanho)
        if (reg == POS_VAZIA1 or reg == POS_VAZIA3):
            arquivo.seek(atual * tamanho)
            arquivo.write(RegBin)
            return
        atual += shift
        if(atual >= TAMANHO_ARQUIVO):
            atual = atual - TAMANHO_ARQUIVO
def insereHD():
    #Tenta abrir o arquivo, caso ele nao exista o arquivo eh criado
    try:
        with open('HashingDuplo.bin', mode='rb+') as file:
            insereHashingDuplo(file)
        file.close()
    except IOError:
        with open('HashingDuplo.bin', mode='wb+') as file:
            insereHashingDuplo(file)
        file.close()
def imprimeHD():
    try:
        #Percorre o arquivo e imprime seus registros
        with open('HashingDuplo.bin', mode='rb+') as file:
            tamanho = struct.calcsize("i 21s i")
            for i in range(TAMANHO_ARQUIVO):
                file.seek(i * tamanho)
                reg = file.read(tamanho)
                if reg == POS_VAZIA1 or reg == POS_VAZIA3:
                    print(str(i)+': vazio')
                    continue
                regUnpacked = struct.unpack("i 21s i", reg)
                print(str(i)+': '+str(regUnpacked[0])+' '+regUnpacked[1].decode('utf-8')+' '+str(regUnpacked[2]))
    except IOError:
        print("arquivo inexistente")
def buscaHD():
    try:
        #Busca uma chave no registro
        with open('HashingDuplo.bin', mode='rb+') as arquivo:
            chave = int(input())
            pos = h1(chave)
            shift = h2(chave)
            tamanho = struct.calcsize("i 21s i")
            arquivo.seek(pos * tamanho)
            reg = arquivo.read(tamanho)
            #Verifica se a chave esta na posicao indicada por h1
            if(reg != POS_VAZIA1 and reg != POS_VAZIA3):
                regUnpacked = struct.unpack("i 21s i", reg)
                if(regUnpacked[0] == chave):
                    print('chave: ' + str(regUnpacked[0]))
                    print(regUnpacked[1].decode('utf-8'))
                    print(str(regUnpacked[2]))
                    return
            #Procura a chave no arquivo seguindo o deslocamento dado por h2
            atual = pos + shift
            while(atual != pos):
                arquivo.seek(atual * tamanho)
                reg = arquivo.read(tamanho)
                if (reg != POS_VAZIA3 and reg != POS_VAZIA1):
                    regUnpacked = struct.unpack("i 21s i", reg)
                    if (regUnpacked[0] == chave):
                        print('chave: ' + str(regUnpacked[0]))
                        print(regUnpacked[1].decode('utf-8'))
                        print(str(regUnpacked[2]))
                        return
                atual += shift
                if (atual >= TAMANHO_ARQUIVO):
                    atual = atual - TAMANHO_ARQUIVO
            print("chave nao encontrada: " + str(chave))
    except:
        print("arquivo inexistente")
def mediaHD():
    try:
        #Verifica quantos acessos sao necessarios para encontrar cada chave e calcula a media
        with open('HashingDuplo.bin', mode='rb+') as file:
            tamanho = struct.calcsize("i 21s i")
            chaves = []
            acessosVetor = []
            media = 0
            #Reune todas as chaves que estao no arquivo
            for i in range(TAMANHO_ARQUIVO):
                file.seek(i * tamanho)
                reg = file.read(tamanho)
                if reg != POS_VAZIA1 and reg != POS_VAZIA3:
                    regUnpacked = struct.unpack("i 21s i", reg)
                    chaves.append(regUnpacked[0])
            #Busca-se as chaves uma a uma registrando cada acesso ao arquivo
            for i in chaves:
                pos = h1(i)
                shift = h2(i)
                acessos = 0
                tamanho = struct.calcsize("i 21s i")
                file.seek(pos * tamanho)
                reg = file.read(tamanho)
                if reg != POS_VAZIA1 and reg != POS_VAZIA3:
                    regUnpacked = struct.unpack("i 21s i", reg)
                    if (regUnpacked[0] == i):
                        acessos = 1
                        continue
                acessos = 1
                atual = pos + shift
                while(atual != pos):
                    file.seek(atual * tamanho)
                    reg = file.read(tamanho)
                    if reg != POS_VAZIA1 and reg != POS_VAZIA3:
                        regUnpacked = struct.unpack("i 21s i", reg)
                        if (regUnpacked[0] == i):
                            acessosVetor.append(acessos)
                    acessos += 1
                    atual += shift
                    if (atual >= TAMANHO_ARQUIVO):
                        atual = atual - TAMANHO_ARQUIVO
            #Calculo da media e saida
            for i in acessosVetor:
                media += i
            print("%.1f" % (media / len(acessosVetor)))
    except IOError:
        print("arquivo inexistente")
def removeHD():
    try:
        #Remocao
        with open('HashingDuplo.bin', mode='rb+') as arquivo:
            chave = int(input())
            pos = h1(chave)
            shift = h2(chave)
            tamanho = struct.calcsize("i 21s i")
            arquivo.seek(pos * tamanho)
            reg = arquivo.read(tamanho)
            #Verifica se a chave esta na posicao indicada por h1 e a remove
            if (reg != POS_VAZIA3 and reg != POS_VAZIA1):
                regUnpacked = struct.unpack("i 21s i", reg)
                if(regUnpacked[0] == chave):
                    arquivo.seek(pos * tamanho)
                    arquivo.write(POS_VAZIA3)
                    return
            #Caso nao esteja, busca-se a chave no arquivo seguindo o deslocamento dado por h2 para a remoçao
            atual = pos + shift
            while(atual != pos):
                arquivo.seek(atual * tamanho)
                reg = arquivo.read(tamanho)
                if (reg != POS_VAZIA3 and reg != POS_VAZIA1):
                    regUnpacked = struct.unpack("i 21s i", reg)
                    if (regUnpacked[0] == chave):
                        arquivo.seek(atual * tamanho)
                        arquivo.write(POS_VAZIA3)
                        return
                atual += shift
                if (atual >= TAMANHO_ARQUIVO):
                    atual = atual - TAMANHO_ARQUIVO
            print("chave nao encontrada: " + str(chave))
    except:
        print("arquivo inexistente")

#Entradas de modo de hashing e operacoes a serem realizadas no arquivo
modo = input()
if modo == 'l':
    operacao = input()
    while(operacao != 'e'):
        if operacao == 'i':
            insereHE()
        elif operacao == 'c':
            buscaHE()
        elif operacao == 'p':
            imprimeArquivoHE()
        elif operacao == 'r':
            removeHE()
        elif operacao == 'm':
            mediaHE()
        operacao = input()
elif modo == 'd':
    operacao = input()
    while(operacao != 'e'):
        if operacao == 'i':
            insereHD()
        elif operacao == 'p':
            imprimeHD()
        elif operacao == 'c':
            buscaHD()
        elif operacao == 'm':
            mediaHD()
        elif operacao == 'r':
            removeHD()
        operacao = input()