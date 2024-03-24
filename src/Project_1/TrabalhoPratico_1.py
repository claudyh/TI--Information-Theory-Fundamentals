#TI TRABALHO PRÁTICO 1 - CLÁUDIA E MARIA JOÃO

#Imports_______________________________________________________________________
    
from typing import Counter
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
import huffmancodec
#import math

#Funções_______________________________________________________________________

#Contagem do número de ocorrencias:
    
def ocorrencias(alfabeto, fonte):
    
    dicionario={chave:0 for chave in alfabeto}                                 #Dicionario 'dicionario' -> Chaves: alfabeto / Valores: 0
    fonte= Counter(fonte)                                                      #Dicionario 'fonte' -> Chaves: nºs fonte / Valores: nº ocorrencias
    for chave in alfabeto:                                                     #Percorre chaves de 'dicionario'
        if chave in fonte.keys():                                              #Verifica a lista de valores de 'fonte'
            dicionario[chave]= fonte[chave]                                    #Update: 'dicionario' -> Chaves: alfabeto / Valores: nº ocorrencias
    ocorrencias= np.array(list(dicionario.values()))                           #Ocorrencias -> lista dos valores de 'dicionario'
    
    return ocorrencias


#Exercicio 1 - Histograma ocorrência simbolos:

def histograma(alfabeto, ocorrencias, titulo, cor):
    
    plt.title(titulo)
    plt.xlabel("Alfabeto")
    plt.ylabel("Ocorrências")
    plt.bar(alfabeto, ocorrencias, color=cor)
    plt.show()  


#Exercicio 2 - Entropia:

def entropia(ocorrencias):
    
    total= np.sum(ocorrencias)
    if (total != 0):                                                           #Verificar tamanho da fonte (x/0 impossivel)
        ocorrencias_sem_zeros= ocorrencias[np.nonzero(ocorrencias)]            #Eliminar os zeros pois log2(0) é impossível
        probabilidades = np.divide(ocorrencias_sem_zeros, total)               #p(x)= ocorrencias(x)/total
        H = - np.sum(probabilidades * np.log2(probabilidades))                 #Fórmula entropia= - Sum(p(x)*log2(p(x)))
    
    return H, probabilidades


#Exercicio 3 - Imagens, audios e textos:

def BmpWavTxt(ficheiro):
    
    if(ficheiro.endswith("bmp") == 1):                                         #Se ficheiro for de imagem (bmp)
        Alfabeto= np.arange(256)                                               #Imagem: range valor pixeis é de 0-255 
        Ficheiro= plt.imread(ficheiro)                                         #Ler ficheiro: Ficheiro = matriz
        Ficheiro= np.ravel(Ficheiro)                                           #Dar 'flatten' à matriz: Ficheiro = lista
        
    elif(ficheiro.endswith("wav") == 1):                                       #Se ficheiro for de som (wav)
        Alfabeto= np.arange(256)                                               #Função para ficheiros de 1 só canal!
        [rate, Ficheiro]= wavfile.read(ficheiro)                               #Ler ficheiro: Ficheiro = lista
        
    elif(ficheiro.endswith("txt") == 1):                                       #Se ficheiro for de texto (txt)
        Alfabeto= ["a","b","c","d","e","f","g","h","i","j","k","l","m",        #Em ascii:   ([chr(i) for i in range(65,91)]
                   "n","o","p","q","r","s","t","u","v","w","x","y","z",        #          + [chr(i) for i in range(97,123)])
                   "A","B","C","D","E","F","G","H","I","J","K","L","M",
                   "N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        with open (ficheiro) as text:
            Ficheiro= text.read()
            text.close()
    
    return Ficheiro, Alfabeto


#Exercicio 4 - HuffmanCode:

def huffmancode(probabilidades, lengths):
    
    mult= np.multiply(probabilidades, lengths)                                 #Esperança ou valor medio (E[X])
    n_medio= np.sum(mult)                                                      #E[X]= sum(x * p(x))
    
    formula= np.power(np.subtract(lengths, n_medio), 2)                        #Variancia (Var(X))
    mult= np.multiply(probabilidades, formula)                                 #V(x)= E[(X - E[X])^2]
    variancia= np.sum(mult)
    
    return n_medio, variancia


#Exercicio 5 - Agrupamento de Simbolos:

def paresSimbolos(ficheiro):
    
    Ficheiro=np.ravel(ficheiro)                                                #ravel: melhor implementação do flatten (necessário para audios/texto)
    comprimento= len(Ficheiro)
    
    pPares = Ficheiro[0:comprimento:2]                                         #Lista dos valores nas posições pares
    pImpares = Ficheiro[1:comprimento:2]                                       #Lista dos valores nas posições ímpares
    
    paresSimbolos=[]                                                           #Lista com os pares de simbolos
    contador= 0
    
    for i in range(comprimento):

        if (type(Ficheiro[i]) == np.uint8):                                    #Se for do tipo: unsigned int 8 bits
            contador += 1                                                      #Numeros de 0 a 254 possiveis!
            
            if (contador == comprimento):                                      #Se todos valores forem desse tipo (bmp/wav)
                for i in range (comprimento//2):                               #Percorrer comp de "posicoesPares/Impares" 
                    par = pPares[i]*256 + pImpares[i]
                    paresSimbolos.append(par)

        elif (type(Ficheiro[i]) == np.str_):                                   #Se for do tipo: string
            contador += 1                                                      #Contador++: para verificar que todos os elementos do ficheiro sao do mesmo tipo
            
            if (contador == comprimento):                                      #Se todos valores forem desse tipo (txt)
                for i in range (comprimento//2):
                    par = pPares[i] + pImpares[i]
                    paresSimbolos.append(par)
          
                
    unique, Counts = np.unique(paresSimbolos, return_counts=True)              #Obter ocorrencias (Counts) usando np.unique        
    
    return unique, Counts
          

#Exercicio 6 - Ondas sonoras:

#Alinea a):

def IM(X, Y):
    
    uniquex, CountsX = np.unique(X, return_counts=True, axis=0)
    EntropiaX, prob= entropia(CountsX)                                         
    
    uniquey, CountsY = np.unique(Y, return_counts=True, axis=0)
    EntropiaY, prob= entropia(CountsY)
    
    XY = np.c_[X,Y]                                                            #Concatenar elementos das mesmas pocições da lista X e Y
    uniquexy, CountsXY = np.unique(XY, return_counts=True, axis=0)             #Obter ocorrencias (Counts) usando np.unique
    EntropiaXY, prob= entropia(CountsXY)                                       #EntropiaXY -> EntropiaCondicionada(X,Y)
    
    return EntropiaX + EntropiaY - EntropiaXY                                  #IM(X,Y)= E(X) + E(Y) - E(X,Y)
    
def informacaoMutua(query,target,alfabeto,passo):
    
    inicio=0
    final= query.size
    n_janelas= int(((target.size-query.size)/passo)+1)
    
    infoMutua=[]

    while (n_janelas>0):                                                       #Enquanto não tiver o nº janelas esperado..
        janela=target[inicio:final]                                            #Dar slicing ao target (comprimento da query)
        
        info= IM(query,janela)                                                 #Informação Mutua entre query e a janela
        infoMutua.append(info)                                                 #Juntar essa info á lista final
                                                                               #Repete-se para todas as janelas
        inicio += passo
        final += passo
        n_janelas -= 1
        
    return infoMutua

#Alínea b):

def variacaoIM(query, target1, target2, alfabeto):
    
    [rate, Query]= wavfile.read(query)                                         #Ler o query
    Query= Query[:,0]                                                          #Ficheiros tipo Stereo (2 col) mas neste exercicio devemos ignorar a 2ª col
                                                                               #[:,0] -> Copia todos numero da 1ª col (os de indice 0)
    [rate, Target1]= wavfile.read(target1)
    Target1= Target1[:,0]
    
    [rate, Target2]= wavfile.read(target2)
    Target2= Target2[:,0]
    
    #passo=(Query.size)/4
    #passo=math.ceil(passo)   
    
    passo=int((Query.size)/4)
    
    IM1= informacaoMutua(Query, Target1, alfabeto, passo)
    IM2= informacaoMutua(Query, Target2, alfabeto, passo)
    
    print("_____________________________________________________________")
    print("InfoMutua (saxriff e target01) =\n")
    print(IM1)
    print("_____________________________________________________________")
    print("InfoMutua (saxriff e target02) =\n")
    print(IM2)
    
    plt.plot(IM1)
    plt.plot(IM2)
    plt.show()
      
#Alínea c):

def IMmax(query, target):
    [rate, query] =wavfile.read(query)
    query= query[:,0]
    
    [rate, song] =wavfile.read(target)

    if(song.ndim>1):                                                           #Se for stereo (2 canais)
        canal1= song[:,0]                                                      #Info do canal 1 (indice 0)
        canal2= song[:,1]                                                      #Info do canal 2 (indice 1)
        song= np.concatenate((canal1,canal2))                                  #Song= canal 1 + canal 2 (seguidos)

    #passo=(query.size)/4
    #passo=math.ceil(passo)   
    
    passo=int((query.size)/4) 
    
    infoMutua= informacaoMutua(query,song,alfabeto,passo)                      #Obter lista de informações mutuas
    IM_max= max(infoMutua)                                                     #Obter a informação mutua máxima
    
    return IM_max


#Implementação_________________________________________________________________

print("Trabalho Prático TI _____________________")
print("_________________________________________")

#Exercicio 1 e 2

def ex1_2(alfabeto, fonte):
    
    Ocorrencias= ocorrencias(alfabeto, fonte)
    histograma(alfabeto, Ocorrencias, "Exercicio 1", "#d67ff0")
    H, Probabilidades= entropia(Ocorrencias)                                        
    print("Exercicio 1\n\nEntropia (bits/símbolo): %.5f"%H)

Alfabeto= [13,8,6,10]
Fonte= [5,13,7,6,4,5,8,13,8,8,6]
ex1_2(Alfabeto, Fonte)


#Exercicio 3, 4 e 5

def ex3_4_5(ficheiro, cor):
    
    Titulo= ficheiro
    Ficheiro, Alfabeto= BmpWavTxt(ficheiro)
    
    #3
    Ocorrencias= ocorrencias(Alfabeto, Ficheiro)
    histograma(Alfabeto, Ocorrencias, Titulo, cor)
    H, Probabilidades= entropia(Ocorrencias)                                         
    print("_________________________________________")
    print(Titulo + "\n\nEntropia (bits/símbolo): %.5f"%H)
    
    #4
    if Titulo.endswith('.txt'):                                                #Se o Ficheiro for txt
        Ficheiro = [i for i in Ficheiro if i.isalpha()]                        #Retirar todos chr que não sejam letras
        
    codec = huffmancodec.HuffmanCodec.from_data(Ficheiro)                      #Ler Ficheiro com o HuffmanCodec
    symbols,lengths = codec.get_code_len()                                     #symbols = Alfabeto / lengths = lista nº bits
    N_medio, Variancia = huffmancode(Probabilidades, lengths)
    
    print("Media: %.5f"%N_medio)
    print("Variancia: %.5f"%Variancia)
    
    #5
    Alfabeto, Counts= paresSimbolos(Ficheiro)
    histograma(Alfabeto, Counts, Titulo, cor)
    EntropiaPares, prob= entropia(Counts)
    EntropiaPares /= 2                                                         #Divide-se a entropia por 2 (pares de simbolos)!
    print('Entropia agrupada (bits/simbolo): %.5f'%(EntropiaPares))
    
ex3_4_5('landscape.bmp', "#947ff0")
ex3_4_5('MRI.bmp', "#7fc5f0")
ex3_4_5('MRIbin.bmp', "#7ff090")
ex3_4_5('soundMono.wav', "#f0e37f")
ex3_4_5('lyrics.txt', "#f0a87f")    


#Exercicio 6
#Alinea a)

query = np.array([2, 6, 4, 10, 5, 9, 5, 8, 0, 8])
target = np.array([6, 8, 9, 7, 2, 4, 9, 9, 4, 9, 1, 4, 8, 0, 1, 2, 2, 6, 3, 2, 0, 7, 4, 9, 5, 4, 8, 5, 2, 7, 8, 0, 7, 4, 8, 5, 7, 4, 3, 2, 2, 7, 3, 5, 2, 7, 4, 9, 9, 6]) 
alfabeto = np.array([3,4,5,8,10,2,10])
passo = 1

print("______________________________________________________________"
      + "\ninfoMutua =\n")
print(informacaoMutua(query,target,alfabeto,passo))

#Alinea b)

variacaoIM("saxriff.wav", "target01 - repeat.wav", "target02 - repeatNoise.wav", alfabeto)

#Alinea c)

def simulador():
    dicio={}
    
    dicio["Song01-IM-max"]= IMmax("saxriff.wav", "Song01.wav")
    dicio["Song02-IM-max"]= IMmax("saxriff.wav", "Song02.wav")
    dicio["Song03-IM-max"]= IMmax("saxriff.wav", "Song03.wav")
    dicio["Song04-IM-max"]= IMmax("saxriff.wav", "Song04.wav")
    dicio["Song05-IM-max"]= IMmax("saxriff.wav", "Song05.wav")
    dicio["Song06-IM-max"]= IMmax("saxriff.wav", "Song06.wav")
    dicio["Song07-IM-max"]= IMmax("saxriff.wav", "Song07.wav")
    
    sorted_dicio = sorted(dicio.items(), key=lambda x:x[1], reverse=True)      #Ordenar dicionario: ordem decrescente de valores
    converted_dicio = dict(sorted_dicio)                                       #Converted_dicio: dicionario sorted
    
    print("______________________________________________________________")
    print("Info Mutua Máx:\n")
    for c,v in converted_dicio.items():
        print(c, ":", v)

simulador()