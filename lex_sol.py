# Таблиця лексем мови
tableOfLanguageTokens = {'true': 'boolean',
                         'false': 'boolean',
												 'program':'keyword', 
												 'let':'keyword',
												 'begin':'keyword',
												 'end':'keyword',
												 'finish':'keyword',
												 'integer':'keyword', 
												 'real':'keyword', 
												 'boolean':'keyword',
												 'for':'keyword', 
												 'to':'keyword', 
												 'do':'keyword', 
												 'goto':'keyword', 
												 'if':'keyword', 
												 'prompt':'keyword',
												 'log':'keyword', 
												 'stop': 'keyword',
												 '=':'assign_op', 
												 '.':'dot', ' ':'ws',
												 '\t':'ws', '\n':'nl', 
												 '-':'add_op', '+':'add_op', 
												 '*':'mult_op', '/':'mult_op', 
												 '^':'ex_op', '<':'rel_op',
												 '<=':'rel_op', '>':'rel_op', 
												 '>=':'rel_op', '==':'rel_op',
												 '!=':'rel_op', '->':'decl_op',
												 '(':'brackets_op', ')':'brackets_op', 
												 '.':'punct', ',':'punct', ':':'punct',
												 ';':'punct', '_':'punct'}

# Решту токенів визначаємо не за лексемою, а за заключним станом
tableIdentFloatInt = {11:'ident', 23:'real', 24:'integer'}

# Діаграма станів

# δ - state-transition_function
stf={(0, 'ws'):0, 
		 (0, '^'):1, (0, '+'):1, (0,'*'):1, (0, '/'):1, 
		 (0, ')'):1, (0, '('):1, (0, ';'):1, (0, ','):1, (0, ':'):1, 
		 (0, 'nl'):2, 
		 (0,'Letter'):10,  (10,'Letter'):10, (10,'Digit'):10, 
		 (10,'UnderScore'):10, (10,'other'):11,
     (0,'Digit'):20, (20,'Digit'):20, (20,'dot'):21, (20,'other'):24, 
		 (21,'Digit'):22, (21,'other'):102, (22,'Digit'):22, (22,'other'):23,
     (0, '!'):30, (30,'='):31, (30,'other'):103,
		 (0, '='):40, (40,'='):41, (40,'other'):42,
		 (0, '<'):50, (50,'='):51, (50,'other'):52,
		 (0, '>'):60, (60,'='):61, (60,'other'):62,
		 (0, '-'):70, (70,'>'):71, (70,'other'):72,
     (0, 'other'):101
}

initState = 0   # q0 - стартовий стан
F={1,2,11,23,24,31,41,42,51,52,61,62,71,72,101,102,103}
Fstar={11,23,24,42,52,62,72}   # зірочка
Ferror={101,102,103}# обробка помилок


tableOfId={}   # Таблиця ідентифікаторів
tableOfConst={} # Таблиць констант
tableOfSymb={}  # Таблиця символів програми (таблиця розбору)


state=initState # поточний стан

f = open('parser/test.sol', 'r')
sourceCode=f.read()
f.close()

# FSuccess - ознака успішності розбору
FSuccess = (True,'Lexer')

lenCode=len(sourceCode)-1 # номер останнього символа у файлі з кодом програми
numLine=1 # лексичний аналіз починаємо з першого рядка
numChar=-1 # з першого символа (в Python'і нумерація - з 0)
char='' # ще не брали жодного символа
lexeme='' # ще не починали розпізнавати лексеми


def lex():
	global state,numLine,char,lexeme,numChar,FSuccess
	try:
		while numChar<lenCode:
			char=nextChar()					# прочитати наступний символ
			classCh=classOfChar(char)		# до якого класу належить 
			state=nextState(state,classCh)	# обчислити наступний стан
			if (is_final(state)): 			# якщо стан заключний
				processing()				# виконати семантичні процедури
				# if state in Ferror:	    # якщо це стан обробки помилки  
					# break					#      то припинити подальшу обробку 
			elif state==initState:lexeme=''	# якщо стан НЕ заключний, а стартовий - нова лексема
			else: lexeme+=char		# якщо стан НЕ закл. і не стартовий - додати символ до лексеми
		print('Lexer: Лексичний аналіз завершено успішно')
	except SystemExit as e:
		# Встановити ознаку неуспішності
		FSuccess = (False,'Lexer')
		# Повідомити про факт виявлення помилки
		print('Lexer: Аварійне завершення програми з кодом {0}'.format(e))

def processing():
	global state,lexeme,char,numLine,numChar, tableOfSymb
	if state==2:		# \n
		numLine+=1
		state=initState
	if state in (11,23,24):	# keyword, ident, real, int
		token=getToken(state,lexeme) 
		if token!='keyword': # не keyword
			index=indexIdConst(state,lexeme)
			print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(numLine,lexeme,token,index))
			tableOfSymb[len(tableOfSymb)+1] = (numLine,lexeme,token,index)
		else: # якщо keyword
			print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine,lexeme,token)) #print(numLine,lexeme,token)
			tableOfSymb[len(tableOfSymb)+1] = (numLine,lexeme,token,'')
		lexeme=''
		numChar=putCharBack(numChar) # зірочка
		state=initState
	if state in (1, 31, 41, 51, 61, 71): # char != == <= >= ->
		lexeme += char
		token = getToken(state, lexeme)
		print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
		tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
		lexeme = ''
		state = initState
	if state in (42, 52, 62, 72): # = < > -
		token = getToken(state, lexeme)
		print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
		tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
		lexeme = ''
		numChar = putCharBack(numChar)  # зірочка
		state = initState
	if state in Ferror:  # ERROR
		fail()

def fail():
	global state,numLine,char
	print(numLine)
	if state == 101:
		print('Lexer: у рядку ',numLine,' неочікуваний символ '+char)
		exit(101)
	if state == 102:
		print('Lexer: у рядку ',numLine,' очікувалася цифра, а не '+char)
		exit(102)
	if state == 103:
		print('Lexer: у рядку ',numLine,' очікувався символ =, а не '+char)
		exit(103)
	
		
def is_final(state):
	if (state in F):
		return True
	else:
		return False

def nextState(state,classCh):
	try:
		return stf[(state,classCh)]
	except KeyError:
		return stf[(state,'other')]

def nextChar():
	global numChar
	numChar+=1
	return sourceCode[numChar]

def putCharBack(numChar):
	return numChar-1

def classOfChar(char):
	if char in '.' :
		res="dot"
	elif char in 'abcdefghijklmnopqrstuvwxyz' :
		res="Letter"
	elif char in "0123456789" :
		res="Digit"
	elif char in '_' :
		res="UnderScore"
	elif char in " \t" :
		res="ws"
	elif char in "\n" :
		res="nl"
	elif char in "+-=*/()^:;,!<>" :
		res=char
	else: res='символ не належить алфавіту'
	return res

def getToken(state,lexeme):
	try:
		return tableOfLanguageTokens[lexeme]
	except KeyError:
		return tableIdentFloatInt[state]

def indexIdConst(state,lexeme):
	indx=0
	if state==11:
		indx=tableOfId.get(lexeme)
#		token=getToken(state,lexeme)
		if indx is None:
			indx=len(tableOfId)+1
			tableOfId[lexeme]=indx
	if state==23:
		indx=tableOfConst.get(lexeme)
		if indx is None:
			indx=len(tableOfConst)+1
			tableOfConst[lexeme]=indx
	if state==24:
		indx=tableOfConst.get(lexeme)
		if indx is None:
			indx=len(tableOfConst)+1
			tableOfConst[lexeme]=indx
	return indx


# запуск лексичного аналізатора	
lex()

# Таблиці: розбору, ідентифікаторів та констант
print('-'*30)
# print('tableOfSymb:{0}'.format(tableOfSymb))
print('tableOfId:{0}'.format(tableOfId))
print('tableOfConst:{0}'.format(tableOfConst))

