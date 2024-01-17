from lex_sol import lex
from lex_sol import tableOfSymb

lex()
print('-'*30)
# print('tableOfSymb:{0}'.format(tableOfSymb))
# print('-'*30)

# номер рядка таблиці розбору/лексем/символів ПРОГРАМИ tableOfSymb
numRow=1    
tableOfLet={}
# довжина таблиці символів програми 
# він же - номер останнього запису
len_tableOfSymb=len(tableOfSymb)
print(('len_tableOfSymb',len_tableOfSymb))

# Функція для розбору за правилом
# Program = program StatementList end
# читає таблицю розбору tableOfSymb
def parseProgram():
    try:
        # перевірити наявність ключового слова 'program'
        parseToken('program','keyword','')

        parseProgName()
        parseDeclSection()
        parseDoSection()

        # перевірити наявність ключового слова 'end'
        parseToken('stop','keyword','')

        # повідомити про синтаксичну коректність програми
        print('Parser: Семантичний аналіз завершився успішно')

        return True
    except SystemExit as e:
        # Повідомити про факт виявлення помилки
        print('Parser: Аварійне завершення програми з кодом {0}'.format(e))

			
# Функція перевіряє, чи у поточному рядку таблиці розбору
# зустрілась вказана лексема lexeme з токеном token
# параметр indent - відступ при виведенні у консоль
def parseToken(lexeme,token,indent):
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
        print(indent+'parseToken: В рядку {0} токен {1}'.format(numLine,(lexeme,token)))
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
        exit(11)
    elif str == 'невідповідність у Boolean':
        (numLine,lex,tok,expected)=tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(numLine,lex,tok,expected))
        exit(12)
          
# Функція для розбору за правилом для StatementList 
# StatementList = Statement  { Statement }
# викликає функцію parseStatement() доти,
# доки parseStatement() повертає True
def parseStatementList():
        print('\t' + 'parseStatementList:')
        while parseStatement():
                pass
        return True


def parseStatement():
    print('\t\tparseStatement:')
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор

    if tok == 'ident':
        return defineOperation()
        
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
    elif (lex, tok) == ('finish','keyword'):
            return False

    else: 
        # жодна з інструкцій не відповідає 
        # поточній лексемі у таблиці розбору,
        failParse('невідповідність інструкцій',(numLine,lex,tok,'ident, prompt, for, finish, log, if'))
        return False

def defineOperation():
    global numRow
    numLine, lex, tok = getSymb()

    lexeme = lex
    if lex not in tableOfLet:
        return failParse('неоголошена змiнна', (numLine, lex))

    print('\t\t' + 'В рядку {0} - {1}'.format(numLine,(lex, tok)))
    numRow += 1

    numLine, lex, tok = getSymb()

    if (lex, tok) == ('=', 'assign_op'):
      parseAssign(lexeme)       
      return True
    if (lex, tok) == (':', 'punct'):
      parseLabelStatement()       
      return True

def parseAssign(lexeme):
    # номер запису таблиці розбору
    global numRow
    print('\t\t'+'parseAssign:')

    # взяти поточну лексему
    numLine, lex, tok = getSymb()

    # встановити номер нової поточної лексеми
    numRow += 1

    print('\t\t\t'+'В рядку {0} - {1}'.format(numLine,(lex, tok)))

    if (lex, tok) == ('=', 'assign_op'):
      numRow += 1
      numLine1, lex1, tok1 = getSymb()

      if lex1 not in '':
        current = tableOfLet[lexeme]
        new = (current[0], 'assigned', current[2])
        tableOfLet[lexeme] = new
      numRow -= 1

      exprType = parseExpression()

      current = tableOfLet[lexeme]
      if exprType != current[2]:
          failParse('невідповідність типів',(numLine,exprType,current[2]))
      return True
    else: return False    

def getTypeOp(lType, op, rType):
    typesArithm = lType in ('integer','real') and \
    rType in ('integer','real')

    if not typesArithm:
        resType = 'type_error'

    if lType == 'integer' and rType == 'integer' \
        and op in '+-*':
        resType = 'integer'   
    elif lType == 'real' or rType == 'real' \
        and op in '+-*':
        resType = 'real'
    elif op in '/^':
        resType = 'real'
    elif op in ('<','<=','>','>=','==','!='):
        resType = 'boolean'
    else: resType = 'type_error'

    return resType

def parseExpression():
    global numRow
    print('\t'*3+'parseExpression:')
    numLine, lex, tok = getSymb()

    # символи '+' або '-'
    if (tok == 'add_op'):
        numRow += 1
        print('\t'*4 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))

    lType = parseTerm()
    resType = None
    F = True
    # продовжувати розбирати Доданки (Term)
    # розділені лексемами '+' або '-'
    while F:
        numLine, lex, tok = getSymb()
        if tok in ('add_op'):
            numRow += 1
            print('\t'*4 + 'В рядку {0} - {1}'.format(numLine,(lex, tok)))
            rType = parseTerm()
            resType = getTypeOp(lType, lex, rType)

            if resType == 'type_error':
                failParse('помилка типів',(numLine, (lex, tok)))
            print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
        else:
            F = False
    res = resType or lType
    return res

def parseTerm():
    global numRow
    print('\t'*4 + 'parseTerm():')
    lType = parseFactor()
    resType = lType

    F = True
    # продовжувати розбирати Множники (Factor)
    # розділені лексемами '*' або '/'
    while F:
        numLine, lex, tok = getSymb()
        if tok in ('mult_op'):
            numRow += 1       

            numLine1, lex1, tok1 = getSymb()  
            if lex == '/' and lex1 == '0':
                failParse('ділення на 0',(numLine))

            print('\t'*4 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            rType = parseFactor()
            resType = getTypeOp(lType, lex, rType)
            print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
        elif tok in ('ex_op'):
            numRow += 1
            print('\t'*4 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            rType = parsePower()
            resType = getTypeOp(lType, lex, rType)
            print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
        else:
            F = False
    return resType
   
def parsePower():
    global numRow
    print('\t' * 4 + 'parsePower():')
    lType = parseFactor()
    resType = lType
    F = True
    while F:
        numLine, lex, tok = getSymb()
        if tok == '^':
            numRow += 1
            print('\t' * 4 + 'в рядку {0} - {1}'.format(numLine, (lex, tok)))
            rType = parsePower()
            resType = getTypeOp(lType, lex, rType)
            print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
        else:
            F = False
    return resType


def parseFactor():
    global numRow
    numLine, lex, tok = getSymb()
    print('\t'*4+'parseFactor(): В рядку: {0}\t (lex, tok):{1}'.format(numLine,(lex, tok)))
    
    # перша і друга альтернативи для Factor
    # якщо лексема - це константа або ідентифікатор
    if tok in ('integer','real','ident', 'boolean'):
            numRow += 1
            print('\t'*4+'в рядку {0} - {1}'.format(numLine,(lex, tok)))
            resType = tok
    
    # третя альтернатива для Factor
    # якщо лексема - це відкриваюча дужка
    elif lex=='(':
        numRow += 1
        resType = parseExpression()
        parseToken(')','brackets_op','\t'*4)
        print('\t'*4+'В рядку {0} - {1}'.format(numLine,(lex, tok)))
    else:
        failParse('невідповідність у Expression.Factor',(numLine,lex,tok,'rel_op, integer, real, ident або \'(\' Expression \')\''))
    return resType

# розбір інструкції розгалуження за правилом
# IfStatement = if BoolExpr then Statement else Statement endif
# функція названа parseIf() замість parseIfStatement()
def parseIf():
    print('\t'*3 + 'parseIf')
    global numRow
    _, lex, tok = getSymb()
    if lex=='if' and tok=='keyword':
        numRow += 1
        parseBoolExpr()
        parseToken('goto','keyword','\t'*4)
        parseIdent('\t'*4)
        return True
    else: return False

# розбір логічного виразу за правилом
# BoolExpr = Expression ('='|'<='|'>='|'<'|'>'|'<>') Expression
def parseBoolExpr():
    print('\t'*4 + 'parseBoolExpr')
    global numRow
    lType = parseExpression()
    numLine, lex, tok = getSymb()
    if tok  == 'rel_op':
        numRow += 1
        print('\t'*4+'В рядку {0} - {1}'.format(numLine,(lex, tok)))
    else:
        failParse('невідповідність у Boolean',(numLine,lex,tok,'relop'))
    rType = parseExpression()
    resType = getTypeOp(lType, lex, rType)

    if resType != 'boolean':
        failParse('помилка типів',(numLine,lex,tok))
    else:
        print('\t\t\t\tОчікуваний тип результату виразу: ', resType)
    return True    

def parseProgName():
    print('parseProgramName:')
    return parseIdent('\t')

def parseIdent(indent):
    global numRow
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор
    if tok == 'ident':
        numRow += 1
        print(indent+'В рядку {0} - {1}'.format(numLine, (lex, tok)))
        return True
    else:
        failParse('очікувався ідентифікатор', (numLine, lex, tok, 'ident'))
        return False
    
def parseDeclIdent(indent):
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
        print(indent+'В рядку {0} - {1}'.format(numLine, (lex, tok)))
        return True, lex
    else:
        failParse('очікувався ідентифікатор', (numLine, lex, tok, 'ident'))
        return False
    
def parseDeclSection():
    print('parseDeclSection:')
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
        print('\t' + 'В рядку {0} - {1}'.format(numLine, (lex, tok)))
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
        print('\t' + 'В рядку {0} - {1}'.format(numLine, (lex, tok)))
    else:
        failParse('пропуск знака декларації', (numLine, lex, tok, '->'))
        return False
    return True

def parseDoSection(): 
    print('parseDoSection:')
    parseToken('begin', 'keyword', '\t')
    parseStatementList()
    parseToken('finish', 'keyword', '\t')

def parseLabelStatement():
    global numRow
    numLine, lex, tok = getSymb()
    print('\t'*2 + 'parseLabelStatement: В рядку: {0}\t (lex, tok):{1}'.format(numLine,(lex, tok)))

    if tok == 'punct' and lex == ':':
        numRow += 1
        parseStatement()
        return True
    else:
        failParse('невідповідність у LabelStatement',(numLine,lex,tok,':'))
        return False

def parsePromptIdent(indent):
    global numRow
    # прочитаємо поточну лексему в таблиці розбору
    numLine, lex, tok = getSymb()
    # якщо токен - ідентифікатор
    if tok == 'ident':
        numRow += 1
        print(indent+'В рядку {0} - {1}'.format(numLine, (lex, tok)))

        current = tableOfLet[lex]
        new = (current[0], 'assigned', current[2])
        tableOfLet[lex] = new

        return True
    else:
        failParse('очікувався ідентифікатор', (numLine, lex, tok, 'ident'))
        return False
    
    

def parsePrompt():
    print('\t'*4 +'parsePrompt')
    F = parseToken('prompt', 'keyword', '\t'*4)
    if F:
        F = (parseToken('(', 'brackets_op', '\t'*4) and 
            parsePromptIdent('\t'*4) and 
            parseToken(')', 'brackets_op', '\t'*4))
    return F

def parseLog():
    print('\t'*4 +'parseLog')
    F = parseToken('log', 'keyword', '\t'*4)
    if F:
        F = (parseToken('(', 'brackets_op', '\t'*4) and 
            parseIdent('\t'*4) and 
            parseToken(')', 'brackets_op', '\t'*4))
    return F

def parseFor():
    global numRow
    print('\t'*3 + 'parseFor:')
    _, lex, tok = getSymb()
    if lex == 'for' and tok == 'keyword':
        numRow += 1
        parseStatement()
        parseToken('to', 'keyword', '\t'*4)
        parseExpression()
        parseToken('do', 'keyword', '\t'*4)
        parseStatement()
        parseToken('end', 'keyword', '\t'*4)
        return True
    else: return False

# запуск парсера
parseProgram()      
