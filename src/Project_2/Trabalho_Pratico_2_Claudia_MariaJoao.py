# Author: Marco Simoes, Cláudia Torres, Maria João Rosa
# Adapted from Java's implementation of Rui Pedro Paiva
# Teoria da Informacao, LEI, 2022

import sys
from huffmantree import HuffmanTree
from typing import Counter

class GZIPHeader:
    ''' class for reading and storing GZIP header fields '''

    ID1 = ID2 = CM = FLG = XFL = OS = 0
    MTIME = []
    lenMTIME = 4
    mTime = 0

    # bits 0, 1, 2, 3 and 4, respectively (remaining 3 bits: reserved)
    FLG_FTEXT = FLG_FHCRC = FLG_FEXTRA = FLG_FNAME = FLG_FCOMMENT = 0   
    
    # FLG_FTEXT --> ignored (usually 0)
    # if FLG_FEXTRA == 1
    XLEN, extraField = [], []
    lenXLEN = 2
    
    # if FLG_FNAME == 1
    fName = ''  # ends when a byte with value 0 is read
    
    # if FLG_FCOMMENT == 1
    fComment = ''   # ends when a byte with value 0 is read
        
    # if FLG_HCRC == 1
    HCRC = []
    
    def read(self, f):
        ''' reads and processes the Huffman header from file. Returns 0 if no error, -1 otherwise '''

        # ID 1 and 2: fixed values
        self.ID1 = f.read(1)[0]  
        if self.ID1 != 0x1f: return -1 # error in the header
            
        self.ID2 = f.read(1)[0]
        if self.ID2 != 0x8b: return -1 # error in the header
        
        # CM - Compression Method: must be the value 8 for deflate
        self.CM = f.read(1)[0]
        if self.CM != 0x08: return -1 # error in the header
                    
        # Flags
        self.FLG = f.read(1)[0]
        
        # MTIME
        self.MTIME = [0]*self.lenMTIME
        self.mTime = 0
        for i in range(self.lenMTIME):
            self.MTIME[i] = f.read(1)[0]
            self.mTime += self.MTIME[i] << (8 * i)                 
                        
        # XFL (not processed...)
        self.XFL = f.read(1)[0]
        
        # OS (not processed...)
        self.OS = f.read(1)[0]
        
        # --- Check Flags
        self.FLG_FTEXT = self.FLG & 0x01
        self.FLG_FHCRC = (self.FLG & 0x02) >> 1
        self.FLG_FEXTRA = (self.FLG & 0x04) >> 2
        self.FLG_FNAME = (self.FLG & 0x08) >> 3
        self.FLG_FCOMMENT = (self.FLG & 0x10) >> 4
                    
        # FLG_EXTRA
        if self.FLG_FEXTRA == 1:
            # read 2 bytes XLEN + XLEN bytes de extra field
            # 1st byte: LSB, 2nd: MSB
            self.XLEN = [0]*self.lenXLEN
            self.XLEN[0] = f.read(1)[0]
            self.XLEN[1] = f.read(1)[0]
            self.xlen = self.XLEN[1] << 8 + self.XLEN[0]
            
            # read extraField and ignore its values
            self.extraField = f.read(self.xlen)
        
        def read_str_until_0(f):
            s = ''
            while True:
                c = f.read(1)[0]
                if c == 0: 
                    return s
                s += chr(c)
    
        # FLG_FNAME
        if self.FLG_FNAME == 1:
            self.fName = read_str_until_0(f)
        
        # FLG_FCOMMENT
        if self.FLG_FCOMMENT == 1:
            self.fComment = read_str_until_0(f)
        
        # FLG_FHCRC (not processed...)
        if self.FLG_FHCRC == 1:
            self.HCRC = f.read(2)
            
        return 0
            
class GZIP:
    ''' class for GZIP decompressing file (if compressed with deflate) '''

    gzh = None
    gzFile = ''
    fileSize = origFileSize = -1
    numBlocks = 0
    f = None

    bits_buffer = 0
    available_bits = 0        

    def __init__(self, filename):
        self.gzFile = filename                                                 #Nome do ficheiro
        self.f = open(filename, 'rb')                                          #Ler o ficheiro em binário (rb: "read in binary")
        self.f.seek(0,2)                                                       #Função seek(x,y): x= nº posições a mover para a frente (da ESQ para a DT) | y= ponto de referência (neste caso: "2" significa que é no fim do file) | Mais informação: https://www.geeksforgeeks.org/python-seek-function/
        self.fileSize = self.f.tell()                                          #Função tell(): diz nos a posição atual (neste caso é o tamanho do file)
        self.f.seek(0)                                                         #Função seek(x,y): se não específicado, y é 0 por default, ou seja o ponto de referência é no inicio do ficheiro (como x é 0 ele mantém se no inicio do ficheiro)

    def decompress(self):
        ''' main function for decompressing the gzip file with deflate algorithm '''
        
        numBlocks = 0

        # get original file size: size of file before compression
        origFileSize = self.getOrigFileSize()
        print("Tamanho do ficheiro original: " + str(origFileSize))
        
        # read GZIP header
        error = self.getHeader()
        if error != 0:
            print('Formato invalido!')
            return
        
        # show filename read from GZIP header
        print("Nome do ficheiro: " + self.gzh.fName)
        
        # MAIN LOOP - decode block by block -----------------------------------
        
        BFINAL = 0    
        while not BFINAL == 1:                                                 #Enquanto houverem blocos
            
            BFINAL = self.readBits(1)                                          #Ler 1º bit do bloco (1 - último bloco /0 - há mais blocos)
                            
            BTYPE = self.readBits(2)                                           #Ler os 2 bits segintes do bloco (00 - sem compressão /01 - Huffman Fixo /10 - Huffman Dinâmico /11 - Reservado)        
            
            if BTYPE != 2:                                                     #Se BTYPE for diferente de 2 (decimal), ou seja 10 (binario), ou seja, se não for Huffman Dinâmico, não queremos descomprimir
                
                print('Error: Block %d not coded with Huffman Dynamic coding' % (numBlocks+1))
                return
                                
            #--- STUDENTS --- ADD CODE HERE - descompressao bloco a bloco -----
            
            #EXERCICIO 1 ------------------------------------------------------
            print("\nEXERCICIO 1-------------------------------------------\n")
            
            def formato():
                lit = self.readBits(5)                                         #ler os 1ºs 5 bits
                dist = self.readBits(5)                                        #ler os 5 bits seguintes
                clen = self.readBits(4)                                        #ler os 4 bits seguintes    
                
                #Para ficar com o tamanho certo
                lit += 257                                                     #(257–286)
                dist += 1                                                      #(1-32)
                clen += 4                                                      #(4-19)
                
                return lit, dist, clen
            
            #Tamanhos dos blocos
            HLIT, HDIST, HCLEN= formato()
            
            print("HLIT= " + str(HLIT))
            print("HDIST= " + str(HDIST))
            print("HCLEN= " + str(HCLEN))
            
            #EXERCICIO 2 ------------------------------------------------------
            print("\nEXERCICIO 2-------------------------------------------")
            
            def comprimentosCLEN():
                CLEN = [0 for i in range(19)]                                  #inicializar o array CLEN a zeros 
                ordem = [16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]       #ordem dos indices
                
                for i in range(HCLEN):                                         #ler HCLEN (tamanho correspondente)
                    elemento = self.readBits(3)                                #ler de 3 em 3 bits 
                    CLEN[ordem[i]] = elemento                                  #pôr o elemento CLEN na posição correspondente
                
                return CLEN
            
            #Lista de comprimentos de HCLEN
            HCLEN_lens= comprimentosCLEN()
            
            print("\nHCLEN_lens:")
            print(HCLEN_lens)
    
            #EXERCICIO 3 ------------------------------------------------------
            print("\nEXERCICIO 3-------------------------------------------")
            
            def huffman(comp):
                ''' gets an array with sizes of the codes and converts them into an array of Huffman codes (in binary) '''

                #A nossa versão do algoritmo do slide 34:
                
                #bl_count: lista com as ocorrencias de 1bit, 2bits, 3bits,...
                #(até ao nº max de bits q temos em comp)
                bl_count= [0 for i in range(max(comp)+1)]                      #inicializar a 0 (max+1 pois comeca em 0)
                
                #next_code: lista com os códigos
                next_code= [0 for i in range(max(comp)+1)]                     #inicializar a 0 (max+1 pois comeca em 0)
                
                #tree: lista final que vai ter os códigos em binário
                tree= [0 for i in range(len(comp))]                            #inicializar a 0 (tree tem o tamanho de comp)
                
                #inicializar bl_count
                dicio= Counter(comp)                                           #dicionario: chaves= nº bits /valores= ocorrencias em comp
                
                for chave,item in dicio.items():                               #percorrer o dicionario
                    bl_count[int(chave)]= item                                 #pôr as ocorrencias dos bits em bl_count
                
                #algoritmo
                code = 0
                bl_count[0] = 0                                                #repôr bl_count de 0 a 0
               
                for bits in range(1, max(comp)+1):
                    code = (code + bl_count[bits-1]) << 1                      #codigo dos bits atuais tendo em conta os anteriores
                    next_code[bits] = code                                     #guardar o código no array "next_code"
                
                for n in range(len(comp)):                                     #pôr itens na lista tree
                    length = comp[n]                                           #length= nº bits (ou seja os comprimentos) em comp
                    if(length != 0):                                           #Se o comprimento for != 0
                        tree[n] = next_code[comp[n]]                           #juntar á tree o código correspondente
                        next_code[comp[n]] += 1                                #incrementar o item em "next_code"   
                
                for i in range(len(comp)):
                    if(comp[i]==0):                                            #se comp for 0, deixá-lo o em tree
                        continue
                    else:                                                      #se não for: converter para binário
                        binario= bin(tree[i])[2:]                              #função "bin": exemplo= 2 fica 0b10 (logo [2:] - tira o 0b) | Mais informação: https://www.geeksforgeeks.org/bin-in-python/
                        string = str(binario)                                  #converter para string
                        stringWithZeros= string.zfill(comp[i])                 #pôr os zeros que faltam nos numeros binários
                        tree[i]= stringWithZeros                               #adicionar o código binário à tree

                return tree
            
            #Códigos de Huffman de HCLEN
            HCLEN_codes= huffman(HCLEN_lens)
            
            print("\nCodigos de Huffman (HCLEN):")
            print(HCLEN_codes)
            
            #HCLEN TREE
            print("\nInsert Tree (HCLEN):")
            
            def criarTree(nomeTree, array_codes, verbose):
                
                for i in range(len(array_codes)):
                    if(array_codes[i] != 0):
                        code= array_codes[i]
                        insert = nomeTree.addNode(code, i, verbose)
            
            hft = HuffmanTree()
            criarTree(hft, HCLEN_codes, True)
            
            #EXERCICIO 4 ------------------------------------------------------
            print("\nEXERCICIO 4-------------------------------------------")
            
            def comprimentos(tam):
                ''' gets the size of HLIT/HDIST and returns an array with the sizes of their codes '''
                lens=[]
                block= tam
                
                #Ler arvore HCLEN
                while(block != 0):                                             #ler bits até a lista "lens" ter o tamanho certo
                    bit= self.readBits(1)                                      #continuar a ler os bits do ficheiro
                    pos = hft.nextNode(str(bit))                               #percorrer bits pela árvore HCLEN
                    
                    if pos == -2:                                              #(-2): ha caminhos
                        continue                                               #continuar a ler bits e a percorrer a árvore
                    
                    elif pos == -1:                                            #(-1): erro no ficheiro
                        print("Erro no ficheiro!")
                        break
                    
                    elif (pos >= 0) and (pos <= 15):                           #(0-15): literal (guardar valor)
                        ant=pos
                        lens.append(pos)
                        block -= 1                                             #decrescer 1 no tamanho
                        hft.resetCurNode()                                     #voltar ao topo da árvore
                       
                    #Casos especiais
                    elif pos == 16:
                        bits= self.readBits(2)                                 #ler 2 bits extra
                        bits += 3                                              #adicionar á posição inicial (3)
                        
                        for i in range(bits):                                  #juntar o código anterior n vezes (3-6)
                            lens.append(ant)
                            block -= 1
                        hft.resetCurNode()                                     
                        
                    elif pos == 17:
                        bits= self.readBits(3)                                 #ler 3 bits extra
                        bits += 3                                              #adicionar á posição inicial (3)
                        
                        for i in range(bits):                                  #juntar "0" n vezes (3-10)
                            lens.append(0)
                            block -= 1
                        hft.resetCurNode()
                        
                    elif pos == 18:
                        bits= self.readBits(7)                                 #ler 7 bits extra
                        bits += 11                                             #adicionar á posição inicial (11)
                        
                        for i in range(bits):                                  #juntar "0" n vezes (11-138)
                            lens.append(0)
                            block -= 1
                        hft.resetCurNode()
                        
                    else:
                        print("Erro no ficheiro!")
                
                return lens
            
            #Lista de comprimentos de HLIT
            HLIT_lens= comprimentos(HLIT)
            
            print("\nHLIT_lens:")
            print(HLIT_lens)
            
            #EXERCICIO 5 ------------------------------------------------------
            print("\nEXERCICIO 5-------------------------------------------")
            
            #Lista de comprimentos de HDIST
            HDIST_lens= comprimentos(HDIST)
            
            print("\nHDIST_lens:")
            print(HDIST_lens)
            
            #EXERCICIO 6 ------------------------------------------------------
            print("\nEXERCICIO 6-------------------------------------------")
            
            #Códigos de Huffman de HLIT
            HLIT_codes= huffman(HLIT_lens)
            
            print("\nCodigos de Huffmann (HLIT):")
            print(HLIT_codes)
            
            #HLIT TREE
            print("\nInsert Tree (HLIT):")
            
            hft_lit = HuffmanTree()
            criarTree(hft_lit, HLIT_codes, True)
            
            #------------------------------
            
            #Códigos de Huffman de HDIST
            HDIST_codes= huffman(HDIST_lens)
            
            print("\nCodigos de Huffmann (HDIST):")
            print(HDIST_codes)
            
            #HDIST TREE
            print("\nInsert Tree (HDIST):")
            
            hft_dist = HuffmanTree()
            criarTree(hft_dist, HDIST_codes, True)
            
            #EXERCICIO 7 ------------------------------------------------------
            print("\nEXERCICIO 7-------------------------------------------")
            
            def descompactar(output_buffer):
                
                #HLIT
                pos= 0
                while(pos != 256):
                    bit= self.readBits(1)                                      #continuar a ler os bits do ficheiro agora em HLIT
                    pos = hft_lit.nextNode(str(bit))                           #(<256): literal ,(256): final, (>256): length
                    
                    if pos == -2:
                        continue
                    
                    elif pos == -1:
                        print("Erro no ficheiro!")
                        break
                    
                    elif pos < 256:
                       output_buffer.append(pos)
                       hft_lit.resetCurNode()
                    
                    elif pos > 256:
                        
                        if (pos >= 257) and (pos <= 264):
                            length= pos-254
                        
                        elif (pos >= 265) and (pos <= 268):
                            bit_extra= self.readBits(1)                        #0 ou 1
                            valor_somar= pos-265
                            length= pos - (254-valor_somar) + bit_extra
                        
                        elif (pos >= 269) and (pos <= 272):
                            bit_extra= self.readBits(2)                        #0, 1, 2, 3
                            valor_somar= pos-269
                            length= pos - (250-(valor_somar*3)) + bit_extra
                            
                        elif (pos >= 273) and (pos <= 276):
                            bit_extra= self.readBits(3)
                            valor_somar= pos-273
                            length= pos - (238-(valor_somar*7)) + bit_extra
                            
                        elif (pos >= 277) and (pos <= 280):
                            bit_extra= self.readBits(4)
                            valor_somar= pos-277
                            length= pos - (210-(valor_somar*15)) + bit_extra
                            
                        elif (pos >= 281) and (pos <= 284):
                            bit_extra= self.readBits(5)
                            valor_somar= pos-281
                            length= pos - (150-(valor_somar*31)) + bit_extra
                            
                        elif pos == 285:
                            length= 285
                        
                        else:
                            print("Erro no ficheiro!")
                            break
                        
                        #HDIST
                        p=30
                        while((p >29 ) or (p < 0)):                            #temos a length, agora precisamos da dist
                            bit= self.readBits(1)                              #continuar a ler os bits do ficheiro agora em HDIST
                            p = hft_dist.nextNode(str(bit))                    #(dist: p tem valores entre 0 e 29)
                            
                            if p == -2:
                                continue
                            
                            elif p == -1:
                                print("Erro no ficheiro!")
                                break
                            
                            elif (p >= 0) and (p <= 3):
                                dist= p+1
                            
                            elif (p == 4) or (p == 5):
                                bit_extra= self.readBits(1)
                                dist= p + (p-3) + bit_extra
                                
                            elif (p == 6) or (p == 7):
                                 bit_extra= self.readBits(2)
                                 dist= p + ((p-5)*3) + bit_extra
                                 
                            elif (p == 8) or (p == 9):
                                 bit_extra= self.readBits(3)
                                 aux= p-7
                                 dist= 9+aux + (aux*7) + bit_extra 
                            
                            elif (p == 10) or (p == 11):
                                 bit_extra= self.readBits(4)
                                 aux= p-9
                                 dist= 17+aux + (aux*15) + bit_extra
                                 
                            elif (p == 12) or (p == 13):
                                 bit_extra= self.readBits(5)
                                 aux= p-11
                                 dist= 33+aux + (aux*31) + bit_extra
                            
                            elif (p == 14) or (p == 15):
                                 bit_extra= self.readBits(6)
                                 aux= p-13
                                 dist= 65+aux + (aux*63) + bit_extra
                                 
                            elif (p == 16) or (p == 17):
                                 bit_extra= self.readBits(7)
                                 aux= p-15
                                 dist= 129+aux + (aux*127) + bit_extra
                                 
                            elif (p == 18) or (p == 19):
                                 bit_extra= self.readBits(8)
                                 aux= p-17
                                 dist= 257+aux + (aux*255) + bit_extra
                                 
                            elif (p == 20) or (p == 21):
                                 bit_extra= self.readBits(9)
                                 aux= p-19
                                 dist= 513+aux + (aux*511) + bit_extra
                                 
                            elif (p == 22) or (p == 23):
                                 bit_extra= self.readBits(10)
                                 aux= p-21
                                 dist= 1025+aux + (aux*1023) + bit_extra
                                 
                            elif (p == 24) or (p == 25):
                                 bit_extra= self.readBits(11)
                                 aux= p-23
                                 dist= 2049+aux + (aux*2047) + bit_extra
                                 
                            elif (p == 26) or (p == 27):
                                 bit_extra= self.readBits(12)
                                 aux= p-25
                                 dist= 4097+aux + (aux*4095) + bit_extra
                                 
                            elif (p == 28) or (p == 29):
                                 bit_extra= self.readBits(13)
                                 aux= p-27
                                 dist= 8193+aux + (aux*8191) + bit_extra
                            
                            else:
                                print("Erro no ficheiro!")
                                break
                            
                        #LZ77                                                  #tendo length e dist, agora aplicamos o algoritmo LZ77
                        inicio= len(output_buffer)-dist                        #posicao inicial
                        
                        for i in range(length):                                #copiar "length" vezes
                            output_buffer.append(output_buffer[inicio])        #adicionar o item da posição inicio
                            inicio += 1                                        #incrementar a variável inicio (índice)
                        
                        hft_lit.resetCurNode()                                 #voltar ao topo da árvore HLIT
                        hft_dist.resetCurNode()                                #voltar ao topo da árvore HDIST
                        
            #Criar o output buffer
            output_buffer= []  
            descompactar(output_buffer)
            
            print("\nOutput Buffer:")
            print(output_buffer)
            
            #EXERCICIO 8 ------------------------------------------------------
            print("\nEXERCICIO 8-------------------------------------------")
            
            binaryFile = open(self.gzh.fName, "wb")                            #abrir ficheiro binário para escrita (wb: "write in binary")
            binaryFile.write(bytes(output_buffer))                             #escrever no ficheiro binário | Função bytes(): converte a lista para bytes (ex: bytes([1, 2, 3])= '\x01\x02\x03')
            
            print("\nGuardado no ficheiro.")
    
            #--- STUDENTS CODE ENDED ------------------------------------------
                                                                                                                                                              
            # update number of blocks read
            numBlocks += 1
        
        # close file            
        self.f.close()    
        print("\nEnd: %d block(s) analyzed." % numBlocks)
            
    
    def getOrigFileSize(self):
        ''' reads file size of original file (before compression) - ISIZE '''
        
        # saves current position of file pointer
        fp = self.f.tell()
        
        # jumps to end-4 position
        self.f.seek(self.fileSize-4)
        
        # reads the last 4 bytes (LITTLE ENDIAN)
        sz = 0
        for i in range(4): 
            sz += self.f.read(1)[0] << (8*i)
        
        # restores file pointer to its original position
        self.f.seek(fp)
        
        return sz        

    
    def getHeader(self):  
        ''' reads GZIP header'''

        self.gzh = GZIPHeader()
        header_error = self.gzh.read(self.f)
        return header_error
        

    def readBits(self, n, keep=False):
        ''' reads n bits from bits_buffer. if keep = True, leaves bits in the buffer for future accesses '''

        while n > self.available_bits:
            self.bits_buffer = self.f.read(1)[0] << self.available_bits | self.bits_buffer
            self.available_bits += 8
        
        mask = (2**n)-1
        value = self.bits_buffer & mask

        if not keep:
            self.bits_buffer >>= n
            self.available_bits -= n

        return value


if __name__ == '__main__':

    # gets filename from command line if provided
    filename = "FAQ.txt.gz"
    if len(sys.argv) > 1:
        fileName = sys.argv[1]            

    # decompress file
    gz = GZIP(filename)
    gz.decompress()