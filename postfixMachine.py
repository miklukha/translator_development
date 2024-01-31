# завантаження ПОЛІЗ-програми у форматі .postfix 
import re
from stack import Stack
# from parsePostfixProgram import getValue, f2i #loadPostfixFile

class PSM():             # Postfix Stack Machine
  def __init__(self):
    self.tableOfId    = {}
    self.tableOfLabel = {}
    self.tableOfConst = {}
    self.postfixCode   = []
    self.mapDebug     = {}
    self.numLine = 0
    self.fileName = ""
    self.file = ""
    self.slt      = ""
    self.headSection = {"VarDecl":".vars(", "LblDecl":".labels(", "ConstDecl":".constants(", "Code":".code("}
    self.errMsg = {1:"неочікуваний заголовок", 2:"тут очікувався хоч один порожній рядок", 3:"тут очікувався заголовок секції", 4:"очікувалось два елемента в рядку", 8:"неініційована змінна", 9: "тип введеного значення не відповідає очікуваному" }
    self.stack = Stack()
    self.numInstr = 0
    self.maxNumbInstr = 0
    self.forSign = ''
    self.step = ''

    
    
# завантаження ПОЛІЗ-програми у форматі .postfix    

# завантаження ПОЛІЗ-програми у форматі .postfix 

  def loadPostfixFile(self,fileName):
    try:
      self.fileName = 'parser/' + fileName + '.postfix'
      self.file = open(self.fileName, 'r')
      self.parsePostfixProgram()
      self.file.close()
    except PSMExcept as e:
      print(f"PSM.loadPostfixFile ERROR: у рядку {self.numLine}, код винятку - {e.msg}, msg = {self.errMsg[e.msg]}")
      

  def parsePostfixProgram(self):
    # print("--------- header ")
    self.parseHeader(".target: Postfix Machine")
    # print(f"have header1 {self.numLine}")    
    self.parseHeader(".version: 0.2")   
    # print(f"have header2 {self.numLine}")
    
    self.parseSection("VarDecl")
    # print(f"have var {self.numLine}")
    
    self.parseSection("LblDecl")
    # print("have lbl ")
    
    self.parseSection("ConstDecl")
    # print("have const ")
    
    self.parseSection("Code") # mapDebug:: numInstr -> numLine
    # print("have code ")


  def parseHeader(self, header):  
    if self.file.readline().rstrip() != header: 
      raise PSMExcept(1)
    self.numLine += 1
    


  def parseSection(self,section):
    # print("============Section: "+section)
    headerSect = self.headSection[section]
    s = self.file.readline().partition("#")[0].strip()
    self.numLine += 1
    # один порожній рядок обов'язковий 
    if s != "": 
      raise PSMExcept(2)
    # інші (можливі) порожні рядки та заголовок секції
    F = True
    while F:
      s = self.file.readline().partition("#")[0].strip()
      # print("s=",s)
      self.numLine += 1
      if s == "": 
        pass #self.numLine += 1
      elif s == headerSect: 
        # self.numLine += 1
        F = False
      else: raise PSMExcept(3)
    # формування відповідної таблиці (можливі і порожні рядки)
    F = True
    while F:
      s = self.file.readline().partition("#")[0].strip()
      self.numLine += 1
      if s == "": 
        pass
      elif s == ")": # кінець секції
        F = False
      else: 
        self.slt = s
        self.procSection(section) 
  
  def procSection(self,section):
    list =self.slt.split() 
    if len(list) !=2:
      raise PSMExcept(4)
    else:
      item1 = list[0]
      item2 = list[1]
      if section == "VarDecl":
        table = self.tableOfId
        indx=len(table)+1
        table[item1]=(indx,item2,'val_undef')
       
      if section == "LblDecl":
        table = self.tableOfLabel
        indx=len(table)+1
        table[item1]=item2
      
      if section == "ConstDecl":
        table = self.tableOfConst
        indx=len(table)+1
        if item2 == "integer":
          val = int(item1)
        elif item2 == "real":
          val = float(item1)
        elif item2 == "boolean":
          val = item1  
        table[item1]=(indx,item2,val)
      
      if section == "Code":
        indx=len(self.postfixCode)
        self.postfixCode.append((item1,item2))
        instrNum = len(self.postfixCode)-1
        self.mapDebug[instrNum] = self.numLine
      
  

  def postfixExec(self):
    "Виконує postfixCode"
    print('postfixExec:')
    self.maxNumbInstr = len(self.postfixCode)
    try:
      while self.numInstr < self.maxNumbInstr:
        self.stack.print()
        lex,tok = self.postfixCode[self.numInstr]
        if tok in ('integer','real','l-val','r-val','label','boolean'):
          self.stack.push((lex,tok))
          self.numInstr = self.numInstr +1
        elif tok in ('jump','jf', 'jt', 'colon'):
          self.doJumps(lex,tok)
        elif tok == 'to':
          # self.stack.push((lex,tok))
          lexR,tokR = self.stack.pop() 
          lexL,tokL = self.stack.pop() 
          valueOfVar = self.tableOfId[lexL][2]

          if self.forSign == '':
            isLessFirst = valueOfVar <= int(lexR)

            if isLessFirst:
              self.forSign = '<='
              self.step = '+'
            else:
              self.forSign = '>'
              self.step = '-'

          self.applyOperator((lexL,tokL,valueOfVar),self.forSign,(lexR,tokR,int(lexR)))
            
          self.numInstr = self.numInstr +1
        elif tok == 'operator':
          self.doIt(self.step, 'add_op')        
          self.numInstr = self.numInstr + 1
        elif tok == '@':
          value, tok = self.stack.pop()
          if tok == 'integer':
            value = -int(value)
          elif tok == 'real':
            value = -float(value)
          self.stack.push((value,tok))
          self.numInstr = self.numInstr +1
        elif tok == 'out_op':
          id, _ = self.stack.pop()
          self.numInstr = self.numInstr +1
          print(f'-------------- OUT: {id}={self.tableOfId[id][2]}')
        elif tok == 'inp_op':
          self.inputOperation()
        else: 
          print(f'-=-=-=========({lex},{tok})  numInstr={self.numInstr}')
          self.doIt(lex,tok)
          self.numInstr = self.numInstr +1
      self.stack.print()
    except PSMExcept as e:
      # Повідомити про факт виявлення помилки
      print('RunTime: Аварійне завершення програми з кодом {0}'.format(e))
      

  def doJumps(self,lex,tok):
    ni = self.numInstr
    if tok =='jump':
      lexLbl, _ = self.stack.pop()                 # зняти з вершини стека мітку
      self.numInstr = int(self.tableOfLabel[lexLbl])    # номер наступної інструкції = значення мітки
    elif tok =='colon':
      _, _  = self.stack.pop()                       # зняти з вершини стека 
      self.numInstr = self.numInstr +1          # непотрібну нам мітку
    elif tok =='jf':
      lexLbl, _ = self.stack.pop()                   # зняти з вершини стека мітку
      valBoolExpr, _ = self.stack.pop()              # зняти з вершини стека значення BoolExpr
      if valBoolExpr=='false':
        self.numInstr = int(self.tableOfLabel[lexLbl])
      else:
        self.numInstr = self.numInstr + 1
    elif tok =='jt':
      lexLbl, _ = self.stack.pop()                   # зняти з вершини стека мітку
      valBoolExpr, _ = self.stack.pop()              # зняти з вершини стека значення BoolExpr
      if valBoolExpr=='true':
        self.numInstr = int(self.tableOfLabel[lexLbl])
      else:
        self.numInstr = self.numInstr + 1
    print(f'+=+=+=========({lex},{tok})  numInstr={ni} nextNumInstr={self.numInstr}')
  
  def inputOperation(self):
    id, _ = self.stack.pop()
    self.numInstr = self.numInstr + 1
    constType = self.tableOfId[id][1]

    newValue = input("Введіть {0} значення: ".format(constType))

    try:
      if constType == 'real':
        newValue = float(newValue)
      elif constType == 'integer':
        newValue = int(newValue)
      print('Введене значення: ', newValue)
    except ValueError:
      print("Тип введеного значення не відповідає очікуваному")
      raise PSMExcept(9)  

    self.tableOfId[id] = (self.tableOfId[id][0], self.tableOfId[id][1], newValue)

  def doIt(self,lex,tok):
    # зняти з вершини стека ідентифікатор (правий операнд)
    # self.stack.print()
    (lexR,tokR) = self.stack.pop()
    # зняти з вершини стека запис (лівий операнд)
    (lexL,tokL) = self.stack.pop()


    if tokL == 'real' or tokR == 'real':
      tokL = 'real'
      tokR = 'real'
   
    if (lex,tok) == ('=', 'assign_op'):
      tokL = self.tableOfId[lexL][1]
      if tokL != tokR: 
        print(f'(lexR,tokR)={(lexR,tokR)}\n(lexL,tokL)={(lexL,tokL)}')
        raise PSMExcept(7)    # типи змінної відрізняється від типу значення
      else:
        # виконати операцію:
        # оновлюємо запис у таблиці ідентифікаторів
        # ідентифікатор/змінна  =  
        #              (index - не змінився, 
        #               тип - як у правого операнда (вони однакові),  
        #               значення - як у правого операнда)
        self.tableOfId[lexL] = (self.tableOfId[lexL][0],tokR,getValue(lexR,tokR))
    else:
      self.processingArthBoolOp((lexL,tokL),lex,(lexR,tokR))

  def processingArthBoolOp(self,lexTokL,arthBoolOp,lexTokR): 
    (lexL,tokL) = lexTokL
    (lexR,tokR) = lexTokR
    typeL,valL = self.getValTypeOperand(lexL,tokL)
    typeR,valR = self.getValTypeOperand(lexR,tokR)
    self.applyOperator((lexL,typeL,valL),arthBoolOp,(lexR,typeR,valR))
    
  def getValTypeOperand(self,lex,tok):
    if tok == "r-val":
      if self.tableOfId[lex][2] == 'val_undef':
        raise PSMExcept(8)  #'неініційована змінна', (lexL,tableOfId[lexL], (lexL,tokL
      else:
        type,val = (self.tableOfId[lex][1],self.tableOfId[lex][2])
    elif tok == 'integer':
      val = int(lex)
      type = tok
    elif tok == 'real':
      val = float(lex)
      type = tok
    elif tok == 'boolean':
      val = lex
      type = tok
    return (type,val)
  
    
  def applyOperator(self,lexTypeValL,arthBoolOp,lexTypeValR):
    (lexL,typeL,valL) = lexTypeValL
    (lexR,typeR,valR) = lexTypeValR

    # if typeL != typeR:
    #   raise PSMExcept(9)  # типи операндів відрізняються
    if arthBoolOp == '+':
      value = valL + valR
    elif arthBoolOp == '-':
      value = valL - valR
    elif arthBoolOp == '*':
      value = valL * valR
    elif arthBoolOp == '/' and valR ==0:
      raise PSMExcept(10)  # ділення на нуль
    elif arthBoolOp == '/' and typeL=='real':
      value = valL / valR
    elif arthBoolOp == '/' and typeL=='integer':
      value = int(valL / valR)
    elif arthBoolOp == '^':
      value = valL ** valR
    elif arthBoolOp == '<':
      value = str(valL < valR).lower()
    elif arthBoolOp == '<=':
      value = str(valL <= valR).lower()
    elif arthBoolOp == '>':
      value = str(valL > valR).lower()
    elif arthBoolOp == '>=':
      value = str(valL >= valR).lower()
    elif arthBoolOp == '==':
      value = str(valL == valR).lower()
    elif arthBoolOp == '!=':
      value = str(valL != valR).lower()
    else:
        pass
    # покласти результат на стек
    if arthBoolOp in ('<','<=','>','>=','==','!='):
      self.stack.push((str(value),'boolean'))

      if str(value) == 'false':
        self.forSign = ''
    elif arthBoolOp in ('^', '/'):
      self.stack.push((str(value),'real'))
    else: 
      self.stack.push((str(value),typeL))

class PSMExcept(Exception): 
  def __init__(self,msg):
    self.msg = msg

def getValue(lex,tok):
  if tok=='real':
    return float(lex)
  elif tok=='integer':
    return int(lex)
  elif tok=='boolean':
    return lex


    
pm1=PSM() 
pm1.loadPostfixFile('sol')  #  завантаження .postfix - файла

pm1.postfixExec()

print(f"pm1.tableOfId:\n  {pm1.tableOfId}\n")
# print(f"pm1.tableOfLabel:\n  {pm1.tableOfLabel}\n")
# print(f"pm1.tableOfConst:\n  {pm1.tableOfConst}\n")
# print(f"pm1.postfixCode:\n  {pm1.postfixCode}\n")

# for i in range(0,len(pm1.postfixCode)):
  # s= "{0:4}  {1:4}   {2}".format(i, pm1.mapDebug[i], pm1.postfixCode[i])
  # print(s) 
  
# print(f"pm1.mapDebug:\n  {pm1.mapDebug}\n")