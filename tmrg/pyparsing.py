# -*- coding: utf-8 -*-
# module pyparsing.py
#
# Copyright (c) 2003-2019  Paul T. McGuire
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__doc__ = \
"""
pyparsing module - Classes and methods to define and execute parsing grammars
=============================================================================

The pyparsing module is an alternative approach to creating and
executing simple grammars, vs. the traditional lex/yacc approach, or the
use of regular expressions.  With pyparsing, you don't need to learn
a new syntax for defining grammars or matching expressions - the parsing
module provides a library of classes that you use to construct the
grammar directly in Python.

Here is a program to parse "Hello, World!" (or any greeting of the form
``"<salutation>, <addressee>!"``), built up using :class:`Word`,
:class:`Literal`, and :class:`And` elements
(the :class:`'+'<ParserElement.__add__>` operators create :class:`And` expressions,
and the strings are auto-converted to :class:`Literal` expressions)::

    from pyparsing import Word, alphas

    # define grammar of a greeting
    greet = Word(alphas) + "," + Word(alphas) + "!"

    hello = "Hello, World!"
    print (hello, "->", greet.parseString(hello))

The program outputs the following::

    Hello, World! -> ['Hello', ',', 'World', '!']

The Python representation of the grammar is quite readable, owing to the
self-explanatory class names, and the use of '+', '|' and '^' operators.

The :class:`ParseResults` object returned from
:class:`ParserElement.parseString` can be
accessed as a nested list, a dictionary, or an object with named
attributes.

The pyparsing module handles some of the problems that are typically
vexing when writing text parsers:

  - extra or missing whitespace (the above program will also handle
    "Hello,World!", "Hello  ,  World  !", etc.)
  - quoted strings
  - embedded comments


Getting Started -
-----------------
Visit the classes :class:`ParserElement` and :class:`ParseResults` to
see the base classes that most other pyparsing
classes inherit from. Use the docstrings for examples of how to:

 - construct literal match expressions from :class:`Literal` and
   :class:`CaselessLiteral` classes
 - construct character word-group expressions using the :class:`Word`
   class
 - see how to create repetitive expressions using :class:`ZeroOrMore`
   and :class:`OneOrMore` classes
 - use :class:`'+'<And>`, :class:`'|'<MatchFirst>`, :class:`'^'<Or>`,
   and :class:`'&'<Each>` operators to combine simple expressions into
   more complex ones
 - associate names with your parsed results using
   :class:`ParserElement.setResultsName`
 - access the parsed data, which is returned as a :class:`ParseResults`
   object
 - find some helpful expression short-cuts like :class:`delimitedList`
   and :class:`oneOf`
 - find more useful common expressions in the :class:`pyparsing_common`
   namespace class
"""

__version__ = "2.4.1"
__versionTime__ = "16 Jul 2019 04:10 UTC"
__author__ = "Paul McGuire <ptmcg@users.sourceforge.net>"

import string
from weakref import ref as wkref
import copy
import sys
import warnings
import re
import sre_constants
import collections
import pprint
import traceback
import types
from datetime import datetime
from operator import itemgetter
import itertools
from functools import wraps

try:
    # Python 3
    from itertools import filterfalse
except ImportError:
    from itertools import ifilterfalse as filterfalse

try:
    from _thread import RLock
except ImportError:
    from threading import RLock

try:
    # Python 3
    from collections.abc import Iterable
    from collections.abc import MutableMapping, Mapping
except ImportError:
    # Python 2.7
    from collections import Iterable
    from collections import MutableMapping, Mapping

try:
    from collections import OrderedDict as _OrderedDict
except ImportError:
    try:
        from ordereddict import OrderedDict as _OrderedDict
    except ImportError:
        _OrderedDict = None

try:
    from types import SimpleNamespace
except ImportError:
    class SimpleNamespace: pass

# version compatibility configuration
__compat__ = SimpleNamespace()
__compat__.__doc__ = """
    A cross-version compatibility configuration for pyparsing features that will be
    released in a future version. By setting values in this configuration to True,
    those features can be enabled in prior versions for compatibility development
    and testing.

     - collect_all_And_tokens - flag to enable fix for Issue #63 that fixes erroneous grouping
       of results names when an And expression is nested within an Or or MatchFirst; set to
       True to enable bugfix released in pyparsing 2.3.0, or False to preserve
       pre-2.3.0 handling of named results
"""
__compat__.collect_all_And_tokens = True

__diag__ = SimpleNamespace()
__diag__.__doc__ = """
Diagnostic configuration
     - warn_multiple_tokens_in_named_alternation - flag to enable warnings when a results
       name is defined on a MatchFirst or Or expression with one or more And subexpressions
       (default=True) (only warns if __compat__.collect_all_And_tokens is False)
     - warn_ungrouped_named_tokens_in_collection - flag to enable warnings when a results
       name is defined on a containing expression with ungrouped subexpressions that also
       have results names (default=True)
     - warn_name_set_on_empty_Forward - flag to enable warnings whan a Forward is defined
       with a results name, but has no contents defined (default=False)
     - warn_on_multiple_string_args_to_oneof - flag to enable warnings whan oneOf is
       incorrectly called with multiple str arguments (default=True)
     - enable_debug_on_named_expressions - flag to auto-enable debug on all subsequent
       calls to ParserElement.setName() (default=False)
"""
__diag__.warn_multiple_tokens_in_named_alternation = True
__diag__.warn_ungrouped_named_tokens_in_collection = False
__diag__.warn_name_set_on_empty_Forward = False
__diag__.warn_on_multiple_string_args_to_oneof = True
__diag__.enable_debug_on_named_expressions = False

# ~ sys.stderr.write("testing pyparsing module, version %s, %s\n" % (__version__, __versionTime__))

__all__ = ['__version__', '__versionTime__', '__author__', '__compat__', '__diag__',
           'And', 'CaselessKeyword', 'CaselessLiteral', 'CharsNotIn', 'Combine', 'Dict', 'Each', 'Empty',
           'FollowedBy', 'Forward', 'GoToColumn', 'Group', 'Keyword', 'LineEnd', 'LineStart', 'Literal',
           'PrecededBy', 'MatchFirst', 'NoMatch', 'NotAny', 'OneOrMore', 'OnlyOnce', 'Optional', 'Or',
           'ParseBaseException', 'ParseElementEnhance', 'ParseException', 'ParseExpression', 'ParseFatalException',
           'ParseResults', 'ParseSyntaxException', 'ParserElement', 'QuotedString', 'RecursiveGrammarException',
           'Regex', 'SkipTo', 'StringEnd', 'StringStart', 'Suppress', 'Token', 'TokenConverter',
           'White', 'Word', 'WordEnd', 'WordStart', 'ZeroOrMore', 'Char',
           'alphanums', 'alphas', 'alphas8bit', 'anyCloseTag', 'anyOpenTag', 'cStyleComment', 'col',
           'commaSeparatedList', 'commonHTMLEntity', 'countedArray', 'cppStyleComment', 'dblQuotedString',
           'dblSlashComment', 'delimitedList', 'dictOf', 'downcaseTokens', 'empty', 'hexnums',
           'htmlComment', 'javaStyleComment', 'line', 'lineEnd', 'lineStart', 'lineno',
           'makeHTMLTags', 'makeXMLTags', 'matchOnlyAtCol', 'matchPreviousExpr', 'matchPreviousLiteral',
           'nestedExpr', 'nullDebugAction', 'nums', 'oneOf', 'opAssoc', 'operatorPrecedence', 'printables',
           'punc8bit', 'pythonStyleComment', 'quotedString', 'removeQuotes', 'replaceHTMLEntity',
           'replaceWith', 'restOfLine', 'sglQuotedString', 'srange', 'stringEnd',
           'stringStart', 'traceParseAction', 'unicodeString', 'upcaseTokens', 'withAttribute',
           'indentedBlock', 'originalTextFor', 'ungroup', 'infixNotation', 'locatedExpr', 'withClass',
           'CloseMatch', 'tokenMap', 'pyparsing_common', 'pyparsing_unicode', 'unicode_set',
           'conditionAsParseAction',
           ]

system_version = tuple(sys.version_info)[:3]
PY_3 = system_version[0] == 3
if PY_3:
    _MAX_INT = sys.maxsize
    basestring = str
    unichr = chr
    unicode = str
    _ustr = str

    # build list of single arg builtins, that can be used as parse actions
    singleArgBuiltins = [sum, len, sorted, reversed, list, tuple, set, any, all, min, max]

else:
    _MAX_INT = sys.maxint
    range = xrange

    def _ustr(obj):
        """Drop-in replacement for str(obj) that tries to be Unicode
        friendly. It first tries str(obj). If that fails with
        a UnicodeEncodeError, then it tries unicode(obj). It then
        < returns the unicode object | encodes it with the default
        encoding | ... >.
        """
        if isinstance(obj, unicode):
            return obj

        try:
            # If this works, then _ustr(obj) has the same behaviour as str(obj), so
            # it won't break any existing code.
            return str(obj)

        except UnicodeEncodeError:
            # Else encode it
            ret = unicode(obj).encode(sys.getdefaultencoding(), 'xmlcharrefreplace')
            xmlcharref = Regex(r'&#\d+;')
            xmlcharref.setParseAction(lambda t: '\\u' + hex(int(t[0][2:-1]))[2:])
            return xmlcharref.transformString(ret)

    # build list of single arg builtins, tolerant of Python version, that can be used as parse actions
    singleArgBuiltins = []
    import __builtin__

    for fname in "sum len sorted reversed list tuple set any all min max".split():
        try:
            singleArgBuiltins.append(getattr(__builtin__, fname))
        except AttributeError:
            continue

_generatorType = type((y for y in range(1)))

def _xml_escape(data):
    """Escape &, <, >, ", ', etc. in a string of data."""

    # ampersand must be replaced first
    from_symbols = '&><"\''
    to_symbols = ('&' + s + ';' for s in "amp gt lt quot apos".split())
    for from_, to_ in zip(from_symbols, to_symbols):
        data = data.replace(from_, to_)
    return data

alphas = string.ascii_uppercase + string.ascii_lowercase
nums = "0123456789"
hexnums = nums + "ABCDEFabcdef"
alphanums = alphas + nums
_bslash = chr(92)
printables = "".join(c for c in string.printable if c not in string.whitespace)


def conditionAsParseAction(fn, message=None, fatal=False):
    msg = message if message is not None else "failed user-defined condition"
    exc_type = ParseFatalException if fatal else ParseException
    fn = _trim_arity(fn)

    @wraps(fn)
    def pa(s, l, t):
        if not bool(fn(s, l, t)):
            raise exc_type(s, l, msg)

    return pa

class ParseBaseException(Exception):
    """base exception class for all parsing runtime exceptions"""
    # Performance tuning: we construct a *lot* of these, so keep this
    # constructor as small and fast as possible
    def __init__(self, pstr, loc=0, msg=None, elem=None):
        self.loc = loc
        if msg is None:
            self.msg = pstr
            self.pstr = ""
        else:
            self.msg = msg
            self.pstr = pstr
        self.parserElement = elem
        self.args = (pstr, loc, msg)

    @classmethod
    def _from_exception(cls, pe):
        """
        internal factory method to simplify creating one type of ParseException
        from another - avoids having __init__ signature conflicts among subclasses
        """
        return cls(pe.pstr, pe.loc, pe.msg, pe.parserElement)

    def __getattr__(self, aname):
        """supported attributes by name are:
           - lineno - returns the line number of the exception text
           - col - returns the column number of the exception text
           - line - returns the line containing the exception text
        """
        if aname == "lineno":
            return lineno(self.loc, self.pstr)
        elif aname in ("col", "column"):
            return col(self.loc, self.pstr)
        elif aname == "line":
            return line(self.loc, self.pstr)
        else:
            raise AttributeError(aname)

    def __str__(self):
        if self.pstr:
            if self.loc >= len(self.pstr):
                foundstr = ', found end of text'
            else:
                foundstr = (', found %r' % self.pstr[self.loc:self.loc + 1]).replace(r'\\', '\\')
        else:
            foundstr = ''
        return ("%s%s  (at char %d), (line:%d, col:%d)" %
                   (self.msg, foundstr, self.loc, self.lineno, self.column))
    def __repr__(self):
        return _ustr(self)
    def markInputline(self, markerString=">!<"):
        """Extracts the exception line from the input string, and marks
           the location of the exception with a special symbol.
        """
        line_str = self.line
        line_column = self.column - 1
        if markerString:
            line_str = "".join((line_str[:line_column],
                                markerString, line_str[line_column:]))
        return line_str.strip()
    def __dir__(self):
        return "lineno col line".split() + dir(type(self))

class ParseException(ParseBaseException):
    """
    Exception thrown when parse expressions don't match class;
    supported attributes by name are:
    - lineno - returns the line number of the exception text
    - col - returns the column number of the exception text
    - line - returns the line containing the exception text

    Example::

        try:
            Word(nums).setName("integer").parseString("ABC")
        except ParseException as pe:
            print(pe)
            print("column: {}".format(pe.col))

    prints::

       Expected integer (at char 0), (line:1, col:1)
        column: 1

    """

    @staticmethod
    def explain(exc, depth=16):
        """
        Method to take an exception and translate the Python internal traceback into a list
        of the pyparsing expressions that caused the exception to be raised.

        Parameters:

         - exc - exception raised during parsing (need not be a ParseException, in support
           of Python exceptions that might be raised in a parse action)
         - depth (default=16) - number of levels back in the stack trace to list expression
           and function names; if None, the full stack trace names will be listed; if 0, only
           the failing input line, marker, and exception string will be shown

        Returns a multi-line string listing the ParserElements and/or function names in the
        exception's stack trace.

        Note: the diagnostic output will include string representations of the expressions
        that failed to parse. These representations will be more helpful if you use `setName` to
        give identifiable names to your expressions. Otherwise they will use the default string
        forms, which may be cryptic to read.

        explain() is only supported under Python 3.
        """
        import inspect

        if depth is None:
            depth = sys.getrecursionlimit()
        ret = []
        if isinstance(exc, ParseBaseException):
            ret.append(exc.line)
            ret.append(' ' * (exc.col - 1) + '^')
        ret.append("{0}: {1}".format(type(exc).__name__, exc))

        if depth > 0:
            callers = inspect.getinnerframes(exc.__traceback__, context=depth)
            seen = set()
            for i, ff in enumerate(callers[-depth:]):
                frm = ff[0]

                f_self = frm.f_locals.get('self', None)
                if isinstance(f_self, ParserElement):
                    if frm.f_code.co_name not in ('parseImpl', '_parseNoCache'):
                        continue
                    if f_self in seen:
                        continue
                    seen.add(f_self)

                    self_type = type(f_self)
                    ret.append("{0}.{1} - {2}".format(self_type.__module__,
                                                      self_type.__name__,
                                                      f_self))
                elif f_self is not None:
                    self_type = type(f_self)
                    ret.append("{0}.{1}".format(self_type.__module__,
                                                self_type.__name__))
                else:
                    code = frm.f_code
                    if code.co_name in ('wrapper', '<module>'):
                        continue

                    ret.append("{0}".format(code.co_name))

                depth -= 1
                if not depth:
                    break

        return '\n'.join(ret)


class ParseFatalException(ParseBaseException):
    """user-throwable exception thrown when inconsistent parse content
       is found; stops all parsing immediately"""
    pass

class ParseSyntaxException(ParseFatalException):
    """just like :class:`ParseFatalException`, but thrown internally
    when an :class:`ErrorStop<And._ErrorStop>` ('-' operator) indicates
    that parsing is to stop immediately because an unbacktrackable
    syntax error has been found.
    """
    pass

#~ class ReparseException(ParseBaseException):
    #~ """Experimental class - parse actions can raise this exception to cause
       #~ pyparsing to reparse the input string:
        #~ - with a modified input string, and/or
        #~ - with a modified start location
       #~ Set the values of the ReparseException in the constructor, and raise the
       #~ exception in a parse action to cause pyparsing to use the new string/location.
       #~ Setting the values as None causes no change to be made.
       #~ """
    #~ def __init_( self, newstring, restartLoc ):
        #~ self.newParseText = newstring
        #~ self.reparseLoc = restartLoc

class RecursiveGrammarException(Exception):
    """exception thrown by :class:`ParserElement.validate` if the
    grammar could be improperly recursive
    """
    def __init__(self, parseElementList):
        self.parseElementTrace = parseElementList

    def __str__(self):
        return "RecursiveGrammarException: %s" % self.parseElementTrace

class _ParseResultsWithOffset(object):
    def __init__(self, p1, p2):
        self.tup = (p1, p2)
    def __getitem__(self, i):
        return self.tup[i]
    def __repr__(self):
        return repr(self.tup[0])
    def setOffset(self, i):
        self.tup = (self.tup[0], i)

class ParseResults(object):
    """Structured parse results, to provide multiple means of access to
    the parsed data:

       - as a list (``len(results)``)
       - by list index (``results[0], results[1]``, etc.)
       - by attribute (``results.<resultsName>`` - see :class:`ParserElement.setResultsName`)

    Example::

        integer = Word(nums)
        date_str = (integer.setResultsName("year") + '/'
                        + integer.setResultsName("month") + '/'
                        + integer.setResultsName("day"))
        # equivalent form:
        # date_str = integer("year") + '/' + integer("month") + '/' + integer("day")

        # parseString returns a ParseResults object
        result = date_str.parseString("1999/12/31")

        def test(s, fn=repr):
            print("%s -> %s" % (s, fn(eval(s))))
        test("list(result)")
        test("result[0]")
        test("result['month']")
        test("result.day")
        test("'month' in result")
        test("'minutes' in result")
        test("result.dump()", str)

    prints::

        list(result) -> ['1999', '/', '12', '/', '31']
        result[0] -> '1999'
        result['month'] -> '12'
        result.day -> '31'
        'month' in result -> True
        'minutes' in result -> False
        result.dump() -> ['1999', '/', '12', '/', '31']
        - day: 31
        - month: 12
        - year: 1999
    """
    def __new__(cls, toklist=None, name=None, asList=True, modal=True):
        if isinstance(toklist, cls):
            return toklist
        retobj = object.__new__(cls)
        retobj.__doinit = True
        return retobj

    # Performance tuning: we construct a *lot* of these, so keep this
    # constructor as small and fast as possible
    def __init__(self, toklist=None, name=None, asList=True, modal=True, isinstance=isinstance):
        if self.__doinit:
            self.__doinit = False
            self.__name = None
            self.__parent = None
            self.__accumNames = {}
            self.__asList = asList
            self.__modal = modal
            if toklist is None:
                toklist = []
            if isinstance(toklist, list):
                self.__toklist = toklist[:]
            elif isinstance(toklist, _generatorType):
                self.__toklist = list(toklist)
            else:
                self.__toklist = [toklist]
            self.__tokdict = dict()

        if name is not None and name:
            if not modal:
                self.__accumNames[name] = 0
            if isinstance(name, int):
                name = _ustr(name)  # will always return a str, but use _ustr for consistency
            self.__name = name
            if not (isinstance(toklist, (type(None), basestring, list)) and toklist in (None, '', [])):
                if isinstance(toklist, basestring):
                    toklist = [toklist]
                if asList:
                    if isinstance(toklist, ParseResults):
                        self[name] = _ParseResultsWithOffset(ParseResults(toklist.__toklist), 0)
                    else:
                        self[name] = _ParseResultsWithOffset(ParseResults(toklist[0]), 0)
                    self[name].__name = name
                else:
                    try:
                        self[name] = toklist[0]
                    except (KeyError, TypeError, IndexError):
                        self[name] = toklist

    def __getitem__(self, i):
        if isinstance(i, (int, slice)):
            return self.__toklist[i]
        else:
            if i not in self.__accumNames:
                return self.__tokdict[i][-1][0]
            else:
                return ParseResults([v[0] for v in self.__tokdict[i]])

    def __setitem__(self, k, v, isinstance=isinstance):
        if isinstance(v, _ParseResultsWithOffset):
            self.__tokdict[k] = self.__tokdict.get(k, list()) + [v]
            sub = v[0]
        elif isinstance(k, (int, slice)):
            self.__toklist[k] = v
            sub = v
        else:
            self.__tokdict[k] = self.__tokdict.get(k, list()) + [_ParseResultsWithOffset(v, 0)]
            sub = v
        if isinstance(sub, ParseResults):
            sub.__parent = wkref(self)

    def __delitem__(self, i):
        if isinstance(i, (int, slice)):
            mylen = len(self.__toklist)
            del self.__toklist[i]

            # convert int to slice
            if isinstance(i, int):
                if i < 0:
                    i += mylen
                i = slice(i, i + 1)
            # get removed indices
            removed = list(range(*i.indices(mylen)))
            removed.reverse()
            # fixup indices in token dictionary
            for name, occurrences in self.__tokdict.items():
                for j in removed:
                    for k, (value, position) in enumerate(occurrences):
                        occurrences[k] = _ParseResultsWithOffset(value, position - (position > j))
        else:
            del self.__tokdict[i]

    def __contains__(self, k):
        return k in self.__tokdict

    def __len__(self):
        return len(self.__toklist)

    def __bool__(self):
        return (not not self.__toklist)
    __nonzero__ = __bool__

    def __iter__(self):
        return iter(self.__toklist)

    def __reversed__(self):
        return iter(self.__toklist[::-1])

    def _iterkeys(self):
        if hasattr(self.__tokdict, "iterkeys"):
            return self.__tokdict.iterkeys()
        else:
            return iter(self.__tokdict)

    def _itervalues(self):
        return (self[k] for k in self._iterkeys())

    def _iteritems(self):
        return ((k, self[k]) for k in self._iterkeys())

    if PY_3:
        keys = _iterkeys
        """Returns an iterator of all named result keys."""

        values = _itervalues
        """Returns an iterator of all named result values."""

        items = _iteritems
        """Returns an iterator of all named result key-value tuples."""

    else:
        iterkeys = _iterkeys
        """Returns an iterator of all named result keys (Python 2.x only)."""

        itervalues = _itervalues
        """Returns an iterator of all named result values (Python 2.x only)."""

        iteritems = _iteritems
        """Returns an iterator of all named result key-value tuples (Python 2.x only)."""

        def keys(self):
            """Returns all named result keys (as a list in Python 2.x, as an iterator in Python 3.x)."""
            return list(self.iterkeys())

        def values(self):
            """Returns all named result values (as a list in Python 2.x, as an iterator in Python 3.x)."""
            return list(self.itervalues())

        def items(self):
            """Returns all named result key-values (as a list of tuples in Python 2.x, as an iterator in Python 3.x)."""
            return list(self.iteritems())

    def haskeys(self):
        """Since keys() returns an iterator, this method is helpful in bypassing
           code that looks for the existence of any defined results names."""
        return bool(self.__tokdict)

    def pop(self, *args, **kwargs):
        """
        Removes and returns item at specified index (default= ``last``).
        Supports both ``list`` and ``dict`` semantics for ``pop()``. If
        passed no argument or an integer argument, it will use ``list``
        semantics and pop tokens from the list of parsed tokens. If passed
        a non-integer argument (most likely a string), it will use ``dict``
        semantics and pop the corresponding value from any defined results
        names. A second default return value argument is supported, just as in
        ``dict.pop()``.

        Example::

            def remove_first(tokens):
                tokens.pop(0)
            print(OneOrMore(Word(nums)).parseString("0 123 321")) # -> ['0', '123', '321']
            print(OneOrMore(Word(nums)).addParseAction(remove_first).parseString("0 123 321")) # -> ['123', '321']

            label = Word(alphas)
            patt = label("LABEL") + OneOrMore(Word(nums))
            print(patt.parseString("AAB 123 321").dump())

            # Use pop() in a parse action to remove named result (note that corresponding value is not
            # removed from list form of results)
            def remove_LABEL(tokens):
                tokens.pop("LABEL")
                return tokens
            patt.addParseAction(remove_LABEL)
            print(patt.parseString("AAB 123 321").dump())

        prints::

            ['AAB', '123', '321']
            - LABEL: AAB

            ['AAB', '123', '321']
        """
        if not args:
            args = [-1]
        for k, v in kwargs.items():
            if k == 'default':
                args = (args[0], v)
            else:
                raise TypeError("pop() got an unexpected keyword argument '%s'" % k)
        if (isinstance(args[0], int)
                or len(args) == 1
                or args[0] in self):
            index = args[0]
            ret = self[index]
            del self[index]
            return ret
        else:
            defaultvalue = args[1]
            return defaultvalue

    def get(self, key, defaultValue=None):
        """
        Returns named result matching the given key, or if there is no
        such name, then returns the given ``defaultValue`` or ``None`` if no
        ``defaultValue`` is specified.

        Similar to ``dict.get()``.

        Example::

            integer = Word(nums)
            date_str = integer("year") + '/' + integer("month") + '/' + integer("day")

            result = date_str.parseString("1999/12/31")
            print(result.get("year")) # -> '1999'
            print(result.get("hour", "not specified")) # -> 'not specified'
            print(result.get("hour")) # -> None
        """
        if key in self:
            return self[key]
        else:
            return defaultValue

    def insert(self, index, insStr):
        """
        Inserts new element at location index in the list of parsed tokens.

        Similar to ``list.insert()``.

        Example::

            print(OneOrMore(Word(nums)).parseString("0 123 321")) # -> ['0', '123', '321']

            # use a parse action to insert the parse location in the front of the parsed results
            def insert_locn(locn, tokens):
                tokens.insert(0, locn)
            print(OneOrMore(Word(nums)).addParseAction(insert_locn).parseString("0 123 321")) # -> [0, '0', '123', '321']
        """
        self.__toklist.insert(index, insStr)
        # fixup indices in token dictionary
        for name, occurrences in self.__tokdict.items():
            for k, (value, position) in enumerate(occurrences):
                occurrences[k] = _ParseResultsWithOffset(value, position + (position > index))

    def append(self, item):
        """
        Add single element to end of ParseResults list of elements.

        Example::

            print(OneOrMore(Word(nums)).parseString("0 123 321")) # -> ['0', '123', '321']

            # use a parse action to compute the sum of the parsed integers, and add it to the end
            def append_sum(tokens):
                tokens.append(sum(map(int, tokens)))
            print(OneOrMore(Word(nums)).addParseAction(append_sum).parseString("0 123 321")) # -> ['0', '123', '321', 444]
        """
        self.__toklist.append(item)

    def extend(self, itemseq):
        """
        Add sequence of elements to end of ParseResults list of elements.

        Example::

            patt = OneOrMore(Word(alphas))

            # use a parse action to append the reverse of the matched strings, to make a palindrome
            def make_palindrome(tokens):
                tokens.extend(reversed([t[::-1] for t in tokens]))
                return ''.join(tokens)
            print(patt.addParseAction(make_palindrome).parseString("lskdj sdlkjf lksd")) # -> 'lskdjsdlkjflksddsklfjkldsjdksl'
        """
        if isinstance(itemseq, ParseResults):
            self.__iadd__(itemseq)
        else:
            self.__toklist.extend(itemseq)

    def clear(self):
        """
        Clear all elements and results names.
        """
        del self.__toklist[:]
        self.__tokdict.clear()

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return ""

    def __add__(self, other):
        ret = self.copy()
        ret += other
        return ret

    def __iadd__(self, other):
        if other.__tokdict:
            offset = len(self.__toklist)
            addoffset = lambda a: offset if a < 0 else a + offset
            otheritems = other.__tokdict.items()
            otherdictitems = [(k, _ParseResultsWithOffset(v[0], addoffset(v[1])))
                              for k, vlist in otheritems for v in vlist]
            for k, v in otherdictitems:
                self[k] = v
                if isinstance(v[0], ParseResults):
                    v[0].__parent = wkref(self)

        self.__toklist += other.__toklist
        self.__accumNames.update(other.__accumNames)
        return self

    def __radd__(self, other):
        if isinstance(other, int) and other == 0:
            # useful for merging many ParseResults using sum() builtin
            return