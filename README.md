# lldb-pytrace

lldb-pytrace is a module installable into LLDB (the native
code debugger) which provides basic backtracing from the
CPython virtual machine.

Basic usage:

    (lldb) script import pytrace
    (lldb) script pytrace.print_python_traceback()
