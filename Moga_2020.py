import math
import random
import Modelo
import constantes
import historico
import interface

cont_analise_historico = [0]
cont_analise_nova = [0]
cont_analise_pre_check = [0]

def crossover(matriz_variaveis, p, q, x_min, x_max):
        pai1_ad = []
        pai2_ad = []
        ## admensionar
        for i in range(0, len(x_min)):
           pai1_ad.append((matriz_variaveis[p][i] - x_min[i])/(x_max[i] - x_min[i]))
           pai2_ad.append((matriz_variaveis[q][i] - x_min[i])/(x_max[i] - x_min[i]))

        #tirando decimal
        pai1_int = []
        pai2_int = []
        for i in range(0, len(x_min)):
           pai1_int.append(int(pai1_ad[i] * (10**(Modelo.x_res[i]))))
           pai2_int.append(int(pai2_ad[i] * (10**(Modelo.x_res[i]))))
           
        #transformando o NUMERO REAL em BINARIO
        pai1_bin = []
        pai2_bin = []
        
        for i in range(0, len(x_min)):
           pai1_bin.append(bin(pai1_int[i])[2:])
           pai2_bin.append(bin(pai2_int[i])[2:])
        
        for i in range(0, len(x_min)):
           for j in range(len(pai1_bin[i]), len(bin(10**(Modelo.x_res[i]))[2:])):
              pai1_bin[i] = '0' + pai1_bin[i]
           for j in range(len(pai2_bin[i]), len(bin(10**(Modelo.x_res[i]))[2:])):
              pai2_bin[i] = '0' + pai2_bin[i]
        
        #calculando a posição de corte
        pai1_str = ''
        pai2_str = ''
        for i in range(0, len(x_min)):
           pai1_str = pai1_str + str(pai1_bin[i])
           pai2_str = pai2_str + str(pai2_bin[i])
        
        tamanho_pai1 = len(pai1_str)
        tamanho_pai2 = len(pai2_str)
        
        posicao_corte = random.randint(0, tamanho_pai1) #qualquer número INTEIRO entre 0 e tamanho_pai1

        #cortando
        pai1_alfa1 = pai1_str[0:posicao_corte]
        pai1_alfa2 = pai1_str[(posicao_corte):(tamanho_pai1)] #resto
        
        pai2_alfa1 = pai2_str[0:posicao_corte]
        pai2_alfa2 = pai2_str[(posicao_corte):(tamanho_pai2)] #resto

        filho1 = pai1_alfa1 + pai2_alfa2 ## DNA
        filho2 = pai2_alfa1 + pai1_alfa2

        filho1 = mutation(filho1)
        filho2 = mutation(filho2)
        
        filho1_str = [ ]
        filho2_str = [ ]
        for i in range(0, len(x_min)):
           tamanho_x = len(bin(10**(Modelo.x_res[i]))[2:])
           filho1_str.append(filho1[i*tamanho_x: (i + 1)*tamanho_x])
           filho2_str.append(filho2[i*tamanho_x: (i + 1)*tamanho_x])

        filho1_final_int = [ ]
        filho2_final_int = [ ]       

        for i in range(0, len(x_min)):
           filho1_final_int.append(int(filho1_str[i], 2))
           filho2_final_int.append(int(filho2_str[i], 2))


        filho1_final = [ ]
        filho2_final = [ ]      

        for i in range(0, len(x_min)):
           filho1_final.append(filho1_final_int[i]/(10**(Modelo.x_res[i])) * (x_max[i] - x_min[i]) + x_min[i])
           filho2_final.append(filho2_final_int[i]/(10**(Modelo.x_res[i])) * (x_max[i] - x_min[i]) + x_min[i])
       

        return filho1_final, filho2_final

def mutation(solution):
    decisor = random.random()
    posicao = random.randint(0, len(solution))
    if decisor < Modelo.taxa_mutacao:
       parte1 = solution[0: posicao]
       parte2 = solution[posicao + 1: len(solution)]
       parte3 = solution[posicao:posicao + 1]
       if(parte3 == str(0)):
          solution = parte1 + '1' + parte2
       else:
          solution = parte1 + '0' + parte2
    return solution

def criar_individuo_random(x_min, x_max):
   individuo = [ ]
   for i in range(0, len(x_min)):
         individuo.append(x_min[i] +(x_max[i] - x_min[i])*random.random())      
   return individuo

def arredondarpop(matriz_pop, x_res):
   for i in range (0, len(matriz_pop)):
      for j in range(0, len(x_res)):
         matriz_pop[i][j] = round(matriz_pop[i][j], x_res[j])
   return matriz_pop

def evoluir(matriz_variaveis, x_min, x_max):
   filhos = [ ]
   while (len(filhos) < Modelo.pop_size):
           p = random.randint(0, Modelo.pop_size - 1)
           q = Buscar_Ind_Distante(matriz_variaveis, p)
           if (p != q):
                   filho1, filho2 = crossover(matriz_variaveis, p, q, x_min, x_max)
                   filhos.append(filho1)
                   filhos.append(filho2)
   return filhos

def Buscar_Ind_Distante(matriz_variaveis, p):
        dist_temp = 0
        i_temp = 0
        for i in range(0, len(matriz_variaveis)):
                if (i != p):
                        temp = Distancia_Escalar(matriz_variaveis, p, i)
                        if (temp > dist_temp):
                                i_temp = i
                                dist_temp = temp
        return i_temp
                
def Penalizacao(objetivo, restricao, g_sinal, g_limite, fatores_pen):
   objetivo_pen = objetivo[:]                  
   for i in range(0, len(objetivo)):
      for j in range(0, len(restricao)):
         if(g_sinal[j] * restricao[j] < g_sinal[j] * g_limite[j]):
            objetivo_pen[i] = objetivo_pen[i] + abs((restricao[j] - g_limite[j]) * fatores_pen[j])
   return objetivo_pen

def Checa_viavel(vetor_x, restricao, g_sinal, g_limite):
   if Viabilidade_Explicita(vetor_x) == constantes.solucao_inviavel:
      return constantes.solucao_inviavel

   if Modelo.pre_checagem(vetor_x) == constantes.solucao_inviavel :
      return constantes.solucao_inviavel

   for j in range(0, len(restricao)):
      if(g_sinal[j] * restricao[j] < g_sinal[j] * g_limite[j]):
         return constantes.solucao_inviavel # 1 significa Não Viável

   return constantes.solucao_viavel

def Viabilidade_Explicita(vetor_x):
   for i in range (0, len(vetor_x)):
           if(vetor_x[i] < Modelo.x_min[i] or vetor_x[i] > Modelo.x_max[i]):
                   return constantes.solucao_inviavel # não viável
   return constantes.solucao_viavel # viável
                 
def Distancia_Escalar(individuo, p, q):
        temp = 0
        for i in range(0, len(Modelo.x_min)):
                x1_ad = (individuo[p][i] - Modelo.x_min[i])/(Modelo.x_max[i] - Modelo.x_min[i])
                x2_ad = (individuo[q][i] - Modelo.x_min[i])/(Modelo.x_max[i] - Modelo.x_min[i])
                temp = temp + (x1_ad - x2_ad)**2
        return (temp**0.5)                 

def Elitismo(rank):
   # print (rank)
   new_solution = []           
   for i in range(0, len(rank)):
      for j in range(0, len(rank)):
         if(rank[j] == i) and (len(new_solution) < Modelo.pop_size):
            # print (rank[j])
            new_solution.append(j)
            # print (new_solution)
   return new_solution
      

def dominated(matriz_function, p, q):
   for i in range(0, len(matriz_function[p])):
      
      if(matriz_function[p][i] < matriz_function[q][i]):
         return 1
   return 0 

def Rank_pop(matriz_function):
        rank = [0 for i in range(0, len(matriz_function))] 
        for p in range(0, len(matriz_function)):
                for q in range(0, len(matriz_function)):
                        if(p != q):
                           dom = dominated(matriz_function, p, q)
                           if (dom == 0):
                              rank[p] = rank[p] + 1        
        return rank

def Criar_NovaGeracao(individuo, new_solution):
   individuo_new = [ ]
   for i in range(0, len(new_solution)):
      individuo_new.append(individuo[new_solution[i]])
   return individuo_new

def Adicionar_Filhos(individuo, filhos):
   for i in range(0, len(filhos)):
           individuo.append(filhos[i])
   return individuo

def Avalia_Individuo_NãoViavel():
   objective = [math.inf for i in range (0, Modelo.no_objetivo)]
   constraint = [0 for i in range (0, len(Modelo.g_limite))]
   parameters = [0 for i in range (0, Modelo.no_parameters)]

   return objective, constraint, parameters


def Avalia_Individuo_Geral(individuo, i, gen_no, geraca_inicial = False):
   vetor_x = individuo[i]
   n = historico.procurar_individuo(vetor_x)

   # Histórico
   if n > -1:
      vetor_x, objetivo, constraint, objective_penalizado, viavel, parameters = historico.retornar_individuo(n)
      cont_analise_historico[0] += 1

      return objetivo, constraint, objective_penalizado, viavel, parameters
      
   viavel_x = Viabilidade_Explicita(vetor_x)
   pre_check_viavel = Modelo.pre_checagem(vetor_x)
   
   # Inviável
   if ((viavel_x == constantes.solucao_inviavel) or (pre_check_viavel == constantes.solucao_inviavel)):
      objetivo, constraint, parameters = Avalia_Individuo_NãoViavel()
      objective_penalizado = objetivo
      viavel = constantes.solucao_inviavel 
      cont_analise_pre_check[0] +=1

      return objetivo, constraint, objective_penalizado, viavel, parameters

   # Indivíduo Novo
   objetivo, constraint, parameters = Modelo.Avalia_Individuo_Viavel(individuo, i, gen_no)    
   objective_penalizado = Penalizacao(objetivo, constraint, Modelo.g_sinal, Modelo.g_limite, Modelo.f_pen)
   viavel = Checa_viavel(vetor_x, constraint, Modelo.g_sinal, Modelo.g_limite)

   if not geraca_inicial:
      interface.Individuo_Avaliado(gen_no, i, vetor_x, objetivo, constraint, objective_penalizado, viavel, parameters)
   
   cont_analise_nova[0] += 1
   historico.adicionar_individuo(vetor_x, objetivo, constraint, objective_penalizado, viavel, parameters)
   
   return objetivo, constraint, objective_penalizado, viavel, parameters


def Avaliar_Pop(individuo, gen_no, geraca_inicial = False):
   pop_objective = []
   pop_constraint = []
   pop_viavel = []
   pop_objective_penalizado = []
   pop_parameters = []
   
   for i in range(0, len(individuo)):
      objetivo, constraint, objective_penalizado, viavel, parameters = Avalia_Individuo_Geral(individuo, i, gen_no, geraca_inicial) 
      pop_objective.append(objetivo)
      pop_constraint.append(constraint)
      pop_objective_penalizado.append(objective_penalizado)
      pop_viavel.append(viavel)
      pop_parameters.append(parameters)

   return pop_objective, pop_constraint, pop_objective_penalizado, pop_viavel, pop_parameters


def limpa_populacao_inviavel(populacao, function_viavel):
   for i in range(len(function_viavel)-1, -1, -1):
      if function_viavel[i] == 1:
         del populacao[i]
         del function_viavel[i]

         # print (f"Removido individuo {i}")

   return populacao


def Completa_PopInicial(pop_new):
   pop_fake = []

   while(len(pop_new) < Modelo.pop_size):
      pop_new.append(criar_individuo_random(Modelo.x_min, Modelo.x_max))

   pop_new = arredondarpop(pop_new, Modelo.x_res)
   function_objective, function_constraint, function_objective_penalizado, function_viavel, function_parameters = Avaliar_Pop(pop_new, -1, True)        
   continua = sum(function_viavel)/len(function_viavel) > (1 - Modelo.porcentagem_viavel_primeira_geracao)
   if not continua:
      return pop_new
      
   while continua:
      pop_new = limpa_populacao_inviavel(pop_new, function_viavel)
      pop_fake = pop_fake + pop_new
      pop_new = []

      while((len(pop_fake)+len(pop_new)) < Modelo.pop_size):
         pop_new.append(criar_individuo_random(Modelo.x_min, Modelo.x_max))
      pop_new = arredondarpop(pop_new, Modelo.x_res)
      function_objective, function_constraint, function_objective_penalizado, function_viavel, function_parameters = Avaliar_Pop(pop_new, -1, True)        

      continua = ((len(function_viavel) - sum(function_viavel) + len(pop_fake))/Modelo.pop_size) < Modelo.porcentagem_viavel_primeira_geracao

   return pop_fake + pop_new


def Evolucao(pop_new):
   pop_new = Completa_PopInicial(pop_new)
   for gen_no in range (0, Modelo.max_gen):
      interface.Geracao_Iniciada(gen_no, pop_new)
      individuo = pop_new[:]
      filhos = evoluir(individuo, Modelo.x_min, Modelo.x_max)
      individuo = Adicionar_Filhos(individuo, filhos)
      objetivos, constraints, objetivos_penalizados, viavel, parameters = Avaliar_Pop(individuo, gen_no)    
      
      interface.Geracao_Finalizada(gen_no, individuo, objetivos, constraints, objetivos_penalizados, viavel, parameters)
      
      rank = Rank_pop(objetivos_penalizados)

      new_solution = Elitismo(rank) # Retorna lista de indexes (os melhores)

      interface.Elitismo_Aplicado(rank, new_solution)

      pop_new = Criar_NovaGeracao(individuo, new_solution)

   interface.Evolucao_completada(pop_new)




         

