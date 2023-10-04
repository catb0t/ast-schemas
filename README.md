ast-schemas
===

Experimental JSON Schemas that describe the ASTs of various pre-existing or invented-here cool programming languages

very good tool to learn/teach about the semantics of JSON Schema: https://json-schema.org/learn

specifically, to teach the most important thing to remember when writing JSON Schema:

extremely influenced by JSOL: https://github.com/clarkduvall/JSOL

primarily written in draft-07 because 2019-09 (or JSON Schema latest) are so different and have almost no validator implementations

- Factor: https://factorcode.org https://github.com/factor/factor
- Brat: https://brat-lang.org https://github.com/presidentbeef/brat


- Pyrat is a Brat-like Lisp thing that started off as a schema for the simplistic JSOL/PSOL, but now taking PSOL, Brat, and Lisp to their silly, but cool, logical conclusions
  Its interpreter doesn't do much right now because it's a complicated language.

- Lambda Calculus' AST is extremely simple (although the current JSON declaration might be wrong), but I find it hard to implement reductions (and haven't yet) with this AST representation, even though it's the most obvious representation

- YACL, "Yet Another Concatenative Language", placeholder name for messing around with FORTH- and Factor-like syntax
