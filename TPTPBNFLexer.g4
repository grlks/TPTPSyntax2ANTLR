lexer grammar TPTPBNFLexer;

fragment ID_STR : [a-zA-Z0-9_]*;

RULER1 : '::=' -> pushMode(GRAMMAR_EXPR_MODE); // grammar rule
RULER2 : ':==' -> pushMode(GRAMMAR_EXPR_MODE); // semantic rule (more specific grammar rule)
RULER3 : '::-' -> pushMode(LEXER_EXPR_MODE);   // lexer rule
RULER4 : ':::' -> pushMode(LEXER_EXPR_MODE);   // lexer fragment rule

IDENTIFIER : '<' ID_STR '>';

LINE_COMMENT
	: '%' ~[\r\n]* -> skip
	;
WS : [ \t\r\n]+ -> channel(HIDDEN);

mode LEXER_EXPR_MODE;
LEXER_INVCHARSET : '[^' .*? ']';
LEXER_CHARSET : '[' .*? ']';
LEXER_LPAR  : '(';
LEXER_RPAR  : ')';
LEXER_PLUS  : '+';
LEXER_MULT  : '*';
LEXER_DOT   : '.';
LEXER_CHOICE: '|';

// identical with the sea mode
LEXER_SWITCH_RULER1 : '::=' -> type(RULER1), popMode, pushMode(GRAMMAR_EXPR_MODE);
LEXER_SWITCH_RULER2 : ':==' -> type(RULER2), popMode, pushMode(GRAMMAR_EXPR_MODE);
LEXER_SWITCH_RULER3 : '::-' -> type(RULER3), popMode, pushMode(LEXER_EXPR_MODE);
LEXER_SWITCH_RULER4 : ':::' -> type(RULER4), popMode, pushMode(LEXER_EXPR_MODE);

LEXER_IDENTIFIER : '<' ID_STR '>' -> type(IDENTIFIER);

LEXER_LINE_COMMENT
	: '%' ~[\r\n]* -> skip
	;
LEXER_WS : [ \t\r\n]+ -> channel(HIDDEN);

mode GRAMMAR_EXPR_MODE;
GRAMMAR_CHOICE : '|';
GRAMMAR_MULT : '*';

// identical with the sea mode
GRAMMAR_SWITCH_RULER1 : '::=' -> type(RULER1), popMode, pushMode(GRAMMAR_EXPR_MODE);
GRAMMAR_SWITCH_RULER2 : ':==' -> type(RULER2), popMode, pushMode(GRAMMAR_EXPR_MODE);
GRAMMAR_SWITCH_RULER3 : '::-' -> type(RULER3), popMode, pushMode(LEXER_EXPR_MODE);
GRAMMAR_SWITCH_RULER4 : ':::' -> type(RULER4), popMode, pushMode(LEXER_EXPR_MODE);

GRAMMAR_IDENTIFIER : '<' ID_STR '>' -> type(IDENTIFIER);

GRAMMAR_LINE_COMMENT
	: '%' ~[\r\n]* -> skip
	;
GRAMMAR_WS : [ \t\r\n]+ -> channel(HIDDEN);

// match any string outside
// Could not contain <
// Does not start with *, but can contain it
// Does not match brackets { [ ( ) ] } as they are matched seperately
GRAMMAR_STRING : ~[<|* {[()\]}\t\r\n] ~[<| {[()\]}\t\r\n]*;

// match brackets symbol by symbol, as we do not want to match expressions like
// ',[' '])' ').' in a single string
GRAMMAR_STRING_BRACKETS : [{[()\]}] -> type(GRAMMAR_STRING);

// does not work!
//GRAMMAR_STR_WITH_LESS : ~[a-zA-Z|* \t\r\n]+ [ \t\r\n] -> type(GRAMMAR_STRING);

// FIXME: strings that are not recognised by the GRAMMAR_STRING rule above
GRAMMAR_STRING_MANUAL : ('<=>' | '<<' | '<=' | '<~>') -> type(GRAMMAR_STRING);
