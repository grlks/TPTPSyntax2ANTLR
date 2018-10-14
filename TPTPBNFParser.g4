parser grammar TPTPBNFParser;
options { tokenVocab=TPTPBNFLexer; }

tptpGrammar
	: bnfrule* EOF
	;

bnfrule
	: head RULER1 /* ::= */ grammarExpr # grammarRule
	| head RULER2 /* :== */ grammarExpr # semanticRule
	| head RULER3 /* ::- */ lexerExpr # lexerRule
	| head RULER4 /* ::: */ lexerExpr # lexerRule
	;

head
	: IDENTIFIER 
	;

grammarExpr
	: grammarElem*
	| grammarExpr grammarChoice grammarExpr
	;

grammarChoice
	: GRAMMAR_CHOICE /* | */
	;

grammarElem
	: IDENTIFIER grammarMult?		# grammarIdentifier
	| GRAMMAR_STRING /* xyz */		# grammarString
	;

grammarMult
	: GRAMMAR_MULT /* * */
	;

lexerElem
	: IDENTIFIER				# lexerIdentifier
	| LEXER_LPAR lexerExpr LEXER_RPAR	# lexerPars /* ( ) */
	| LEXER_CHARSET    /* [  xyz ] */	# lexerCharset
	| LEXER_INVCHARSET /* [^ xyz ] */	# lexerInvCharset
	| LEXER_DOT /* . */			# lexerDot
	;

lexerMult
	: LEXER_PLUS /* + */ | LEXER_MULT /* * */
	;

lexerExpr
	: (lexerElem lexerMult?)+
	| lexerExpr lexerChoice lexerExpr
	;

lexerChoice
	: LEXER_CHOICE /* | */
	;

/*
identifier
//	: IDENTIFIER_OPEN  IDENTIFIER_NAME IDENTIFIER_CLOSE
	: IDENTIFIER
	; */
