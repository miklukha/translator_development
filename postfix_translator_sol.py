from lex_sol import lex, tableOfSymb, tableOfLabel, tableOfId, tableOfConst, sourceCode, FSuccess

lex()
print('-'*30)
# print('tableOfSymb:{0}'.format(tableOfSymb))
# print('tableOfId:{0}'.format(tableOfId))

# print('-'*30)

# номер рядка таблиці розбору/лексем/символів ПРОГРАМИ tableOfSymb
numRow=1    
tableOfLet={}
lexName = ''
postfixCode = []
forVar = ''
forToValue = 0


# довжина таблиці символів програми 
# він же - номер останнього запису
len_tableOfSymb=len(tableOfSymb) #0

toView = False

def compileToPostfix():
  global len_tableOfSymb, FSuccess
  print('compileToPostfix: lexer Start Up\n') 
  print('compileToPostfix: lexer-FSuccess ={0}'.format(FSuccess))

  # чи був успiшним лексичний розбiр
  if (True,'Lexer') == FSuccess:
    print('-'*55)
    print('compileToPostfix: Start Up compiler = parser + codeGenerator\n')
    FSuccess = (False,'codeGeneration')
    FSuccess = parseProgram()

    if FSuccess == (True,'codeGeneration'):
      serv()
      savePostfixCode('sol')
  return FSuccess

def serv():
    print("\n Таблиця ідентифікаторів")
    s1 = '{0:<10s} {1:<15s} {2:<15s} {3:<10s} '
    print(s1.format("Index",  "Ident", "Type", "Value"))
    s2 = '{0:<10s} {2:<15s} {3:<15s} {1:<10s} '
    for id in tableOfLet:
        index, val, type = tableOfLet[id]
        print(s2.format(str(index), str(val), id, type))
    print('\t\t\t\t')
    print("\n Таблиця міток")
    s3 = '{0:<10s} {1:<10s} '
    print(s3.format("Label","Value"))
    for label in tableOfLabel: 
        value = tableOfLabel[label]
        print(s3.format(label, str(value)))
    print('\t\t\t\t')
    print('Код програми у постфiкснiй формi (ПОЛIЗ):')
    print('\t\t\t\t')

    s3 = '{0:<10s} {1:<15s}'
    print(s3.format("№","postfixCode"))

    for index, item in enumerate(postfixCode):
        print(f"{index:<10d} {item}")


def savePostfixCode(fileName):
    f = open('parser/' + fileName + '.postfix', 'w')

    print('.target: Postfix Machine', file=f)
    print('.version: 0.2', file=f)
    print('\n', file=f)
    # перемінні
    print(".vars(", file=f)
    for key, value in tableOfLet.items():
        type = value[2]
        print(f'    {key:<10} {type}', file=f)
    print(")", file=f)

    print('\n', file=f)
    # мітки
    print(".labels(", file=f)
    for key, value in tableOfLabel.items():
        print(f'    {key:<10} {value}', file=f)
    print(")", file=f)

    print('\n', file=f)
    # константи
    print(".constants(", file=f)
    for key, value in tableOfConst.items():
        print(f'    {key:<10} {value}', file=f)
    print(")", file=f)

    print('\n', file=f)
    # код
    print(".code(", file=f)
    for index, item in postfixCode:
        print(f'    {index:<10} {item}', file=f)
    print(")", file=f)
    # print(createPostfixData(), file=f)
    f.close()
    
  
# Функція для розбору за правилом
# Program = program StatementList end
# читає таблицю розбору tableOfSymb
def parseProgram():
    global numRow

    try:
        # перевірити наявність ключового слова 'program'
        parseToken('program','keyword','')

        parseProgName()
        parseDeclSection()
        parseDoSection()

        # перевірити наявність ключового слова 'end'
        
        parseToken('stop','keyword','')

        # повідомити про синтаксичну коректність програми
        print('Translator!: Переклад у ПОЛІЗ та синтаксичний аналіз завершились успішно')
        # serv()
        FSuccess = (True, 'codeGeneration')
        return FSuccess
    except SystemExit as e:
        # Повідомити про факт виявлення помилки
        print('Parser: Аварійне завершення програми з кодом {0}'.format(e))
        FSuccess = (False, 'codeGeneration')

			
# Функція перевіряє, чи у поточному рядку таблиці розбору
# зустрілась вказана лексема lexeme з токеном token
# параметр indent - відступ при виведенні у консоль
def parseToken(lexeme,token,indent = ''):
    # доступ до поточного рядка таблиці розбору
    global numRow
    
    # якщо всі записи таблиці розбору прочитані,
    # а парсер ще не знайшов якусь лексему
    if numRow > len_tableOfSymb :
        failParse('неочікуваний кінець програми',(lexeme,token,numRow))
        
    # прочитати з таблиці розбору 
    # номер рядка програми, лексему та її токен
    numLine, lex, tok = getSymb() 
        
    # тепер поточним буде наступний рядок таблиці розбору
    numRow += 1
        
    # чи збігаються лексема та токен таблиці розбору з заданими 
    if (lex, tok) == (lexeme,token):
        # вивести у консоль номер рядка програми та лексему і токен
        # print(indent+'parseToken: В рядку {0} токен {1}'.format(numLine,(lexeme,token)))
        return True
    else:
        # згенерувати помилку та інформацію про те, що 
        # лексема та токен таблиці розбору (lex,tok) відрізняються від
        # очікуваних (lexeme,token)
        failParse('невідповідність токенів',(numLine,lex,tok,lexeme,token))
        return False


# Прочитати з таблиці розбору поточний запис
# Повертає номер рядка програми, лексему та її токен
def getSymb():
    if numRow > len_tableOfSymb :
            failParse('getSymb(): неочікуваний кінець програми',numRow)
    # таблиця розбору реалізована у формі словника (dictionary)
    # tableOfSymb[numRow]={numRow: (numLine, lexeme, token, indexOfVarOrConst)
    numLine, lexeme, token, _ = tableOfSymb[numRow]	
    return numLine, lexeme, token        

# Обробити помилки
# вивести поточну інформацію та діагностичне повідомлення 
def failParse(str,tuple):
    if str == 'неочікуваний кінець програми':
        (lexeme,token,numRow)=tuple
        print('Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {1}. \n\t Очікувалось - {0}'.format((lexeme,token),numRow))
        exit(1001)
    if str == 'getSymb(): неочікуваний кінець програми':
        numRow=tuple
        print('Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {0}. \n\t Останній запис - {1}'.format(numRow,tableOfSymb[numRow-1]))
        exit(1002)
    elif str == 'невідповідність токенів':
        (numLine,lexeme,token,lex,tok)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - ({3},{4}).'.format(numLine,lexeme,token,lex,tok))
        exit(1)
    elif str == 'невідповідність інструкцій':
        (numLine,lex,tok,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,lex,tok,expected))
        exit(2)
    elif str == 'невідповідність у Expression.Factor':
        (numLine,lex,tok,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,lex,tok,expected))
        exit(3)
    elif str == 'невідомий тип':
        (numLine,lex,tok,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,lex,tok,expected))
        exit(4)
    elif str == 'очікувався ідентифікатор':
        (numLine,lex,tok,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,lex,tok,expected))
        exit(5)
    elif str == 'повторне оголошення змiнної':
        (numLine,lex)=tuple
        print('Parser ERROR: \n\t В рядку {0} повторне оголошення змінної {1}.'.format(numLine,lex))
        exit(6)
    elif str == 'пропуск знака декларації': 
        (numLine,lex,tok,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1}, {2}). \n\t Очікувався - знак декларації {3}.'.format(numLine,lex,tok,expected))
        exit(7)
    elif str == 'нерозпізнаний тип': 
        (numLine,lex,tok,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний тип ({1}, {2}). \n\t Очікувався - тип змінної {3}.'.format(numLine,lex,tok,expected))
        exit(8)
    elif str == 'неоголошена змiнна': 
        (numLine,lex)=tuple
        print('Parser ERROR: \n\t В рядку {0} неоголошена змінна {1}. '.format(numLine,lex))
        exit(9)
    elif str == 'невідповідність типів': 
        (numLine,received,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} невідповідність типів. \n\t Отриманий тип - {1}\n\t Очікуваний тип - {2}.'.format(numLine,received,expected))
        exit(10)
    elif str == 'помилка типів': 
        (numLine,lex,tok)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний тип ({1}, {2}).'.format(numLine,lex,tok))
        exit(11)
    elif str == 'ділення на 0': 
        (numLine)=tuple
        print('Parser ERROR: \n\t В рядку {0} ділення на 0. \n\t Ділення на 0 заборонено.'.format(numLine))
        exit(12)
    elif str == 'невідповідність у Boolean':
        (numLine,lex,tok,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,lex,tok,expected))
        exit(13)
    elif str == 'відсутність мітки':
        (numLine,lex)=tuple
        print('Parser ERROR: \n\t В рядку {0} перехід {1} на мітку, що не існує.'.format(numLine,lex))
        exit(14)
          


# Функція для розбору за правилом для StatementList 
# StatementList = Statement  { Statement }
# викликає функцію parseStatement() доти,
# доки parseStatement() повертає True
def parseStatementList():
        # print('\t' + 'parseStatementList:')
        while parseStatement():
                pass
        return True


def parseStatement(isFor = False):
    # print('\t\tparseStatement:')
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор

    if tok == 'ident':
        return defineOperation(isFor)
        
    # якщо лексема - ключове слово 'if'
    # обробити інструкцію розгалуження
    elif (lex, tok) == ('if','keyword'):
        parseIf()
        return True 

    elif (lex, tok) == ('prompt','keyword'):
        parsePrompt()
        return True 
  
    elif (lex, tok) == ('log','keyword'):
        parseLog()
        return True 
    
    elif (lex, tok) == ('for','keyword'):
        parseFor()
        return True 
    # тут - ознака того, що всі інструкції були коректно 
    # розібрані і була знайдена остання лексема програми.
    # тому parseStatement() має завершити роботу

    elif (lex, tok) == ('end','keyword'):
            return False
    
    elif (lex, tok) == ('finish','keyword'):
            return False

    else: 
        # жодна з інструкцій не відповідає 
        # поточній лексемі у таблиці розбору,
        failParse('невідповідність інструкцій',(numLine,lex,tok,'ident, prompt, for, finish, log, if'))
        return False

def defineOperation(isFor = False):
    global numRow, forVar
    numLine, lex, tok = getSymb()

    identTok = tok
    lexeme = lex
    if lex not in tableOfLabel:
        if lex not in tableOfLet:
            return failParse('неоголошена змiнна', (numLine, lex))

    # print('\t\t' + 'В рядку {0} - {1}'.format(numLine,(lex, tok)))
    if isFor:
        forVar = lex
        typeOfLet = tableOfLet[lex][2]
        if typeOfLet == 'real':
            print('Тип перемінної в циклі for має бути integer!')
            return failParse('невідповідність типів', (numLine, typeOfLet, 'integer'))
        

    numRow += 1

    numLine, lex, tok = getSymb()

    if (lex, tok) == ('=', 'assign_op'):
      parseAssign(lexeme, identTok)       
      return True
    if (lex, tok) == (':', 'punct'):
      parseLabelStatement()       
      return True

def parseAssign(lexeme, identTok):
    # номер запису таблиці розбору
    global numRow
    # print('\t\t'+'parseAssign:')

    # взяти поточну лексему
    numLine, lex, tok = getSymb()

    lType = getTypeLet(lexeme)
    postfixCodeGen('lval', (lexeme, identTok))

    if toView: configToPrint(lexeme, numRow)

    # встановити номер нової поточної лексеми
    numRow += 1
    # print('\t\t\t'+'В рядку {0} - {1}'.format(numLine,(lex, tok)))

    if (lex, tok) == ('=', 'assign_op'):
      numRow += 1
      numLine1, lex1, tok1 = getSymb()

      
    #   print('\t\t\t'+'В рядку {0} - {1}'.format(numLine1,(lex1, tok1)))
    #   print(tableOfLet)

      if lex1 not in '':
        current = tableOfLet[lexeme]
        new = (current[0], 'assigned', current[2])
        tableOfLet[lexeme] = new
    #   print(tableOfLet)
      numRow -= 1

      rType = parseExpression()

      if lType == rType:
          postfixCodeGen('=', ('=', 'assign_op'))
      else:
          failParse('невідповідність типів',(numLine,lType,rType))
          return 'type_error'
      if toView: configToPrint('=', numRow)
    return 'void'   

def getTypeOp(lType, op, rType):
    if lType == 'ident':
        lType = tableOfLet[lexName][2]

    if rType == 'ident':
        rType = tableOfLet[lexName][2]

    typesArithm = lType in ('integer','real') and \
    rType in ('integer','real')

    if not typesArithm:
        resType = 'type_error'

    if op in ('<','<=','>','>=','==','!='):
        resType = 'boolean'
    elif lType == 'integer' and rType == 'integer' \
        and op in '+-*':
        resType = 'integer'   
    elif lType == 'real' or rType == 'real' \
        and op in '+-*':
        resType = 'real'
    elif op in '/^':
        resType = 'real'
    else: resType = 'type_error'

    return resType

def parseExpression():
    global numRow, postfixCode
    # print('\t'*3+'parseExpression:')
    numLine, lex, tok = getSymb()


    lType = parseTerm()

    if (lex == '-'):
        numRow += 1
        postfixCodeGen(lex,(lex,'@')) # lex - унарний оператор '+' чи '-'
        if toView: configToPrint(lex,numRow)
        # print('\t'*4 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))

    resType = None
    F = True
    # продовжувати розбирати Доданки (Term)
    # розділені лексемами '+' або '-'
    while F:
        numLine, lex, tok = getSymb()
        if tok in ('add_op'):
            numRow += 1
            # print('\t'*4 + 'В рядку {0} - {1}'.format(numLine,(lex, tok)))
            rType = parseTerm()
            resType = getTypeOp(lType, lex, rType)

            if resType != 'type_error':
                postfixCodeGen(lex,(lex,tok)) # lex - бiнарний оператор '+' чи '-'
                # додається пiсля своїх операндiв
                if toView: configToPrint(lex,numRow)
            else:
                failParse('помилка типів',(numLine, lex, tok))
            # print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
        else:
            F = False
    res = resType or lType
    return res

def parseTerm():
    global numRow, postfixCode
    # print('\t'*4 + 'parseTerm():')

    lType = parseFactor()
    resType = lType

    F = True
    # продовжувати розбирати Множники (Factor)
    # розділені лексемами '*' або '/'

    while F:
        numLine, lex, tok = getSymb()
        if tok in ('mult_op'):
            numRow += 1       
            # print("tempPowOpHolder", tempPowOpHolder)
            numLine1, lex1, tok1 = getSymb()  
            if lex == '/' and lex1 == '0':
                failParse('ділення на 0',(numLine))

            # print('\t'*4 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            rType = parseFactor()
            resType = getTypeOp(lType, lex, rType)

            if resType != 'type_error':
                postfixCodeGen(lex,(lex,tok)) 
                if toView: configToPrint(lex,numRow)
            else:
                failParse('помилка типів',(numLine, lex, tok))
            # print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
        elif tok in ('ex_op'):
            numRow += 1
            # print('\t'*4 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            rType = parsePower()
            resType = getTypeOp(lType, lex, rType)
            # print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
            if resType != 'type_error':
                postfixCodeGen(lex,(lex,tok)) 
                if toView: configToPrint(lex,numRow)
            else:
                failParse('помилка типів',(numLine, lex, tok))
        else:
            F = False
    return resType
   
def parsePower():
    global numRow, postfixCode
    # print('\t' * 4 + 'parsePower():')
    lType = parseFactor()
    resType = lType
    F = True
    while F:
        numLine, lex, tok = getSymb()
        if lex == '^':
            numRow += 1
            # print('\t' * 4 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            rType = parsePower()
            resType = getTypeOp(lType, lex, rType)
            if resType != 'type_error':
                postfixCodeGen(lex,(lex,tok))
                if toView: configToPrint(lex,numRow)
            else:
                failParse('помилка типів',(numLine, lex, tok))
            # print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
        else:
            F = False
    return resType

def parseFactor(isFor = False):
    global numRow, lexName, postfixCode, forToValue

    numLine, lex, tok = getSymb()

    # перша і друга альтернативи для Factor
    # якщо лексема - це константа або ідентифікатор

    if tok in ('integer','real','ident', 'boolean'):    
        if tok == 'ident':
            lexName = lex
            # typeLet = getTypeLet(lex)
            # resType = typeLet

            postfixCodeGen('rval',(lex,tok))
            if toView: configToPrint(lex,numRow)

        if tok in ('integer', 'real'):
            if isFor:
                forToValue = lex
                if tok == 'real':
                    print("Значення константи після ключового слова 'to' має бути типу integer!")
                    return failParse('невідповідність типів', (numLine, tok, 'integer'))

            resType = tok
            postfixCodeGen('const',(lex,tok))
            if toView: configToPrint(lex,numRow)
        
        if tok == 'boolean':
            resType = tok
            postfixCodeGen('bool',(lex,tok))
            if toView: configToPrint(lex,numRow)
        numRow += 1
        # print('\t'*4+'в рядку {0} - {1}'.format(numLine,(lex, tok)))
        resType = tok
    
    # третя альтернатива для Factor
    # якщо лексема - це відкриваюча дужка
    elif lex=='(':
        numRow += 1
        resType = parseExpression()
        parseToken(')','brackets_op','\t'*4)
        # print('\t'*4+'В рядку {0} - {1}'.format(numLine,(lex, tok)))
    elif lex == '-':
        numRow += 1
        resType = parseFactor()
        numRow -= 1
    else:
        failParse('невідповідність у Expression.Factor',(numLine,lex,tok,'rel_op, integer, real, ident або \'(\' Expression \')\''))
    return resType

# розбір інструкції розгалуження за правилом
# IfStatement = if BoolExpr then Statement else Statement endif
# функція названа parseIf() замість parseIfStatement()
def parseIf():
    # print('\t'*3 + 'parseIf')
    global numRow
    _, lex, tok = getSymb()
    if lex=='if' and tok=='keyword':
        numRow += 1
        parseBoolExpr()
        parseToken('goto','keyword','\t'*4)
        parseLabelIdent('\t'*4)
        postfixCodeGen('JT', ('JT', 'jt'))
        return True
    else: return False


# розбір логічного виразу за правилом
# BoolExpr = Expression ('='|'<='|'>='|'<'|'>'|'<>') Expression
def parseBoolExpr():
    # print('\t'*4 + 'parseBoolExpr')
    global numRow
    lType = parseExpression()
    numLine, lex, tok = getSymb()

    if tok  == 'rel_op':
        numRow += 1
        # print('\t'*4+'В рядку {0} - {1}'.format(numLine,(lex, tok)))
    else:
        failParse('невідповідність у Boolean',(numLine,lex,tok,'relop'))
    rType = parseExpression()
    resType = getTypeOp(lType, lex, rType)

    if resType != 'boolean':
        failParse('помилка типів',(numLine,lex,tok))
    # else:
        # print('\t\t\t\tОчікуваний тип результату виразу: ', resType)

    if tok in ('rel_op'):
        postfixCodeGen(lex, (lex,tok)) 
    return True    

def parseProgName():
    # print('parseProgramName:')
    return parseIdent('\t')

def parseIdent(indent = '', rval = False):
    global numRow
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор
    if tok == 'ident':
        numRow += 1
        # print(indent+'В рядку {0} - {1}'.format(numLine, (lex, tok)))
        if rval:
            postfixCodeGen('rval', (lex, tok))
        return True
    else:
        failParse('очікувався ідентифікатор', (numLine, lex, tok, 'ident'))
        return False
    
def parseDeclIdent(indent = ''):
    global numRow
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор
    if tok == 'ident':
        ind=tableOfLet.get(lex)
        if ind is None:
            ind=len(tableOfLet)+1
            tableOfLet[lex]=(ind,'undefined')
        else: failParse('повторне оголошення змiнної', (numLine, lex))

        numRow += 1
        # print(indent+'В рядку {0} - {1}'.format(numLine, (lex, tok)))
        return True, lex
    else:
        failParse('очікувався ідентифікатор', (numLine, lex, tok, 'ident'))
        return False

def parseLabelIdent(indent = ''):
    global numRow
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор

    if lex not in tableOfLabel:
        failParse('відсутність мітки', (numLine, lex))
        return False

    if tok == 'ident':
        numRow += 1
        tableOfLabel[lex] = len(postfixCode)
        postfixCodeGen(lex, (lex, 'label'))
        # print(indent+'В рядку {0} - {1}'.format(numLine, (lex, tok)))
        return True
    else:
        failParse('очікувався ідентифікатор', (numLine, lex, tok, 'ident'))
        return False

def parseDeclSection():
    # print('parseDeclSection:')
    parseToken('let', 'keyword', '\t')
    parseDeclList()
    return True

def parseDeclList():
    while parseDeclaration():
        parseToken(';', 'punct', '\t')
    return True

def parseDeclaration():
    numLine, lex, tok = getSymb()
    if (lex, tok) == ('begin', 'keyword'):
        F = False
        return F
    
    F = parseDeclIdent('\t')

    if F:
        identifier = F[1]
        F = parseDeclSign()
        if F:
            return parseType(identifier)
    return F

def parseType(identifier):
    global numRow
    numLine, lex, tok = getSymb()
    if tok == 'keyword' and lex in ('real', 'integer', 'boolean'):
        tableOfLet[identifier] = tableOfLet[identifier] + (lex,)
        numRow += 1
        # print('\t' + 'В рядку {0} - {1}'.format(numLine, (lex, tok)))
        return True
    else:
        # tableOfLet[identifier] = tableOfLet[identifier] + ('undeclared_variable',)
        failParse('нерозпізнаний тип', (numLine, lex, tok, 'keyword'))
        return False

def parseDeclSign():
    global numRow
    numLine, lex, tok = getSymb()
    if tok == 'decl_op' and lex == '->':
        numRow += 1
        # print('\t' + 'В рядку {0} - {1}'.format(numLine, (lex, tok)))
    else:
        failParse('пропуск знака декларації', (numLine, lex, tok, '->'))
        return False
    return True

def parseDoSection(): 
    # print('parseDoSection:')
    parseToken('begin', 'keyword', '\t')
    parseStatementList()
    parseToken('finish', 'keyword', '\t')

def parseLabelStatement():
    global numRow
    numLine, lex, tok = getSymb()
    # print('\t'*2 + 'parseLabelStatement: В рядку: {0}\t (lex, tok):{1}'.format(numLine,(lex, tok)))

    if tok == 'punct' and lex == ':':
        numRow -= 1
        numLine1, lex1, tok1 = getSymb()
        tableOfLabel[lex1] = len(postfixCode)
        # print('tableOfLabel', tableOfLabel)
        postfixCodeGen(lex1, (lex1, 'label'))

        numRow += 1
        numLine2, lex2, tok2 = getSymb()
        postfixCodeGen(lex2, (lex2, 'colon'))

        numRow += 1
        parseStatement()
        return True
    else:
        failParse('невідповідність у LabelStatement',(numLine,lex,tok,':'))
        return False

def parsePromptIdent(indent = '', rval = False):
    global numRow
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор
    if tok == 'ident':
        numRow += 1
        # print(indent+'В рядку {0} - {1}'.format(numLine, (lex, tok)))

        current = tableOfLet[lex]
        new = (current[0], 'assigned', current[2])
        tableOfLet[lex] = new

        if rval:
            postfixCodeGen('rval', (lex, tok))
        return True
    else:
        failParse('очікувався ідентифікатор', (numLine, lex, tok, 'ident'))
        return False
    

def parsePrompt():
    # print('\t'*4 +'parsePrompt')
    F = parseToken('prompt', 'keyword', '\t'*4)
    if F:
        F = (parseToken('(', 'brackets_op', '\t'*4) and 
            parsePromptIdent('\t'*4, True) and 
            parseToken(')', 'brackets_op', '\t'*4))
        postfixCodeGen('in', ('IN', 'inp_op'))
    return F

def parseLog():
    # print('\t'*4 +'parseLog')
    F = parseToken('log', 'keyword', '\t'*4)
    if F:
        F = (parseToken('(', 'brackets_op', '\t'*4) and 
            parseIdent('\t'*4, True) and 
            parseToken(')', 'brackets_op', '\t'*4))
        postfixCodeGen('out', ('OUT', 'out_op'))
    return F

def parseFor():
    global numRow, forVar, forToValue
    # print('\t'*3 + 'parseFor:')
    _, lex, tok = getSymb()

    if lex == 'for' and tok == 'keyword':
        numRow += 1
        start = createLabel()
        action = createLabel()
        increment = createLabel()
        leave = createLabel()
        
        parseStatement(True)

        setValLabel(start)
        postfixCodeGen('label', start)
        postfixCodeGen('colon', (':', 'colon'))

        postfixCodeGen('rval', (forVar, 'r-val'))
        parseToken('to', 'keyword', '\t'*4)
        parseFactor(True)

        postfixCodeGen('to', ('TO', 'to'))

        postfixCodeGen('label', leave)
        postfixCodeGen('JF', ('JF', 'jf'))
        postfixCodeGen('label', action)
        postfixCodeGen('JUMP', ('JUMP', 'jump'))

        setValLabel(increment)
        postfixCodeGen('label', increment)
        postfixCodeGen('colon', (':', 'colon'))

        postfixCodeGen('lval', (forVar, 'l-val'))
        postfixCodeGen('rval', (forVar, 'r-val'))
        postfixCodeGen('integer', ('1', 'integer'))
        postfixCodeGen('operator', ('OP', 'operator'))
        postfixCodeGen('=', ('=', 'assign_op'))

        postfixCodeGen('label', start)
        postfixCodeGen('JUMP', ('JUMP', 'jump'))

        parseToken('do', 'keyword', '\t'*4)

        setValLabel(action)
        postfixCodeGen('label', action)
        postfixCodeGen('colon', (':', 'colon'))
        parseStatementList()

        postfixCodeGen('label', increment)
        postfixCodeGen('JUMP', ('JUMP', 'jump'))

        parseToken('end', 'keyword', '\t'*4)

        setValLabel(leave)
        postfixCodeGen('label', leave)
        postfixCodeGen('colon', (':', 'colon'))
        return True
    else: return False

def postfixCodeGen(case,toTran):
    if case == 'lval':
        lex,tok = toTran
        postfixCode.append((lex,'l-val'))
    elif case == 'rval':
        lex,tok = toTran
        postfixCode.append((lex,'r-val'))
    else:
        lex,tok = toTran
        postfixCode.append((lex,tok))

def getTypeLet(id):
    try:
        return tableOfLet[id][2]
    except KeyError:
        return 'undeclared_variable'

def configToPrint(lex,numRow):
    stage = '\nКрок трансляцiї\n'
    stage += 'лексема: \'{0}\'\n'
    stage += 'postfixCode = {3}\n'
    print('config')
    print(stage.format(lex,numRow,str(tableOfSymb[numRow]),str(postfixCode)))

def createLabel():
    global tableOfLabel
    nmb = len(tableOfLabel)+1
    lexeme = "m"+str(nmb)
    val = tableOfLabel.get(lexeme)
    if val is None:
        tableOfLabel[lexeme] = 'val_undef'
        tok = 'label' # # #
    else:
        tok = 'Конфлiкт мiток'
        print(tok)
        exit(1003)
    return lexeme, tok


def setValLabel(lbl):
    global tableOfLabel
    lex,_tok = lbl
    tableOfLabel[lex] = len(postfixCode)
    return True

# запуск парсера
# parseProgram()      
# createPostfixData()

# savePostfixCode('sol') 
compileToPostfix()
