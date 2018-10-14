# translate the TPTP Syntax BNF into ANTLR4

## Prerequisites
* antlr4
* python3
* python3-antlr4

## Installation
```
antlr4 -Dlanguage=Python3 TPTPBNFLexer.g4
antlr4 -Dlanguage=Python3 TPTPBNFParser.g4 -visitor
```

## Usage
1. open http://tptp.cs.miami.edu/TPTP/SyntaxBNF.html
2. copy plain text (without html tags) into `example.txt`
3. translate
```
python3 TPTPBNF2ANTLR.py example.txt
```
4. compile generated antlr (optional)
```
antlr4 example.g4
javac example*.java
```
5. test generated antlr on `problem.p` (optional)
```
grun example tptp_file -gui problem.p
```
