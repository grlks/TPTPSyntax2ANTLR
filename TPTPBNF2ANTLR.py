import sys
import re
from antlr4 import *
from TPTPBNFLexer import TPTPBNFLexer
from TPTPBNFParser import TPTPBNFParser
from TPTPBNFParserVisitor import TPTPBNFParserVisitor
from TPTPBNFParserListener import TPTPBNFParserListener

def main(argv):
    # get the grammar name
    regex = re.compile(r"[a-zA-Z0-9_]*")
    grammarName = regex.match(argv[1]).group()

    input = FileStream(argv[1])

    lexer = TPTPBNFLexer(input)
    stream = CommonTokenStream(lexer)
    
    parser = TPTPBNFParser(stream)
    tree = parser.tptpGrammar()
    # print(tree.toStringTree(recog=parser))

    # get the lexerIdentifiers and notFragmentIdentifiers
    idDistVisit = IdDistinguisher()
    idDistVisit.visit(tree)

    # generate antlr
    output = open(grammarName + ".g4", "w")

    toANTLRlistener = TPTP2ANTLRGenerator(
            idDistVisit.lexerIdentifiers,
            idDistVisit.notFragmentIdentifiers,
            grammarName,
            output)
    walker = ParseTreeWalker()
    walker.walk( toANTLRlistener, tree )

    output.close()


class IdDistinguisher(TPTPBNFParserVisitor):
    def __init__(self):
        self.lexerIdentifiers = []
        self.notFragmentIdentifiers = []

    def visitTptpGrammar(self, ctx):
        return self.visitChildren(ctx)

    # lexer identifier list
    def visitLexerRule(self, ctx):
        identifier = getIdentifier( ctx.head() )
        self.lexerIdentifiers.append(identifier)

    # not lexer fragment identifier list
    def visitGrammarRule(self, ctx):
        return self.visitChildren(ctx)

    def visitGrammmarExpr(self, ctx):
        return self.visitChildren(ctx)

    def visitGrammarIdentifier(self, ctx):
        # every identifier used in grammar mode is not (only) a lexer fragment
        identifier = getIdentifier(ctx)
        self.notFragmentIdentifiers.append(identifier)


def getIdentifier(ctx):
    # id_string has the form "<id_name>"
    id_string = ctx.IDENTIFIER().getText()
    # without < >
    return id_string[1:-1]

def id2lexer(identifier):
    return identifier.upper()

def id2parser(identifier):
    if identifier == "null":
        # null might be a reserved keyword causing antlr errors
        # nothing seems to be harmless
        return "nothing"
    else:
        return identifier.lower()

def id2lFrag(identifier):
    return identifier.upper() + "_frag"

def tptp2antlrCharset(tptpCharset):
    def replace(match):
        return '\\u{:04x}'.format(int(match.group(1), 8))
    regex = re.compile(r"\\(\d{1,3})")
    antlrCharset = regex.sub( replace, tptpCharset )
    return antlrCharset



class TPTP2ANTLRGenerator(ParseTreeListener):
    def __init__(self, lexerIdentifiers, notFragmentIdentifiers, grammarName, output):
        self.lexerIdentifiers = lexerIdentifiers
        self.notFragmentIdentifiers = notFragmentIdentifiers
        self.grammarName = grammarName
        self.output = output
        self.lexerMode = False

    # parse tree produced by TPTPBNFParser#tptpGrammar
    def enterTptpGrammar(self, ctx):
        self.output.write("/* generated using TPTP2ANTLR.py */\n")
        self.output.write("\ngrammar " + self.grammarName + ";\n")
        self.output.write("\n// matches the whole file, including EOF")
        self.output.write("\ntptp_eof_file : tptp_file EOF ;\n")
    def exitTptpGrammar(self, ctx):
        self.output.write("\nWS : [ \\t\\r\\n]+ -> skip ;\n")
        self.output.write("\nCOMMENT : COMMENT_frag -> skip ; \n")

    # parse tree produced by TPTPBNFParser#grammarRule
    def enterGrammarRule(self, ctx):
        self.lexerMode = False
    def exitGrammarRule(self, ctx):
        self.output.write("\n\t;\n")

    # parse tree produced by TPTPBNFParser#semanticRule
    # Semantic rules will be commented out by default.
    def enterSemanticRule(self, ctx):
        self.output.write("\n/*")
        self.enterGrammarRule(ctx)
    def exitSemanticRule(self, ctx):
        self.exitGrammarRule(ctx)
        self.output.write(" */")

    # parse tree produced by TPTPBNFParser#lexerRule
    def enterLexerRule(self, ctx):
        self.lexerMode = True
    def exitLexerRule(self, ctx):
        self.output.write("\n\t;\n")

    # parse tree produced by TPTPBNFParser#head
    def enterHead(self, ctx):
        identifier = getIdentifier( ctx )
        if self.lexerMode:
            if identifier in self.notFragmentIdentifiers:
                self.output.write(
                    "\n" + id2lexer(identifier) + " : " + id2lFrag(identifier) + " ;" )
            self.output.write(
                    "\nfragment " + id2lFrag(identifier)
                    + "\n\t:" )
        else:
            self.output.write(
                    "\n" + id2parser(identifier)
                    + "\n\t:"
            )
    def exitHead(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#grammarExpr
    def enterGrammarExpr(self, ctx):
        pass
    def exitGrammarExpr(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#grammarChoice
    def enterGrammarChoice(self, ctx):
        self.output.write( "\n\t" + ctx.getText() )
    def exitGrammarChoice(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#grammarIdentifier
    def enterGrammarIdentifier(self, ctx):
        identifier = getIdentifier( ctx )
        if identifier in self.lexerIdentifiers:
            self.output.write(" " + id2lexer(identifier) )
        else:
            self.output.write(" " + id2parser(identifier) )
    def exitGrammarIdentifier(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#grammarString
    def enterGrammarString(self, ctx):
        self.output.write( " '" + ctx.getText() + "'" )
    def exitGrammarString(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#grammarMult
    def enterGrammarMult(self, ctx):
        self.output.write( ctx.GRAMMAR_MULT().getText() )
    def exitGrammarMult(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#lexerIdentifier
    def enterLexerIdentifier(self, ctx):
        identifier = getIdentifier( ctx )
        self.output.write(" " + id2lFrag(identifier) )
    def exitLexerIdentifier(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#lexerPars
    def enterLexerPars(self, ctx):
        self.output.write( " (" )
    def exitLexerPars(self, ctx):
        self.output.write( " )" )

    # parse tree produced by TPTPBNFParser#lexerCharset
    def enterLexerCharset(self, ctx):
        antlrCharset = tptp2antlrCharset( ctx.getText() )
        self.output.write( " " + antlrCharset )
    def exitLexerCharset(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#lexerInvCharset
    def enterLexerInvCharset(self, ctx):
        # replace [+ by [
        tptpCharset = "[" + ctx.getText()[2:]
        antlrCharset = tptp2antlrCharset( tptpCharset )
        self.output.write( " ~" + antlrCharset )
    def exitLexerInvCharset(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#lexerDot
    def enterLexerDot(self, ctx):
        # excerpt from the tptp bnf syntax file:
        #   <printable_char>       ::: .
        #   %----<printable_char> is any printable ASCII character, codes 32 (space) to 126
        #   %----(tilde). <printable_char> does not include tabs, newlines, bells, etc. The
        #   %----use of . does not not exclude tab, so this is a bit loose.
        self.output.write( r" [\u0020-\u007E]" )
    def exitLexerDot(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#lexerMult
    def enterLexerMult(self, ctx):
        self.output.write( ctx.getText() )
    def exitLexerMult(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#lexerExpr
    def enterLexerExpr(self, ctx):
        pass
    def exitLexerExpr(self, ctx):
        pass

    # parse tree produced by TPTPBNFParser#lexerChoice
    def enterLexerChoice(self, ctx):
        self.output.write( "\n\t" + ctx.getText() )
    def exitLexerChoice(self, ctx):
        pass

 
if __name__ == '__main__':
    main(sys.argv)
