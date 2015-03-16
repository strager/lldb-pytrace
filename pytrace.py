import lldb

def read_c_string(value):
    # TODO(strager): Find a better way.
    string = value.GetSummary()
    # Trim surrounding double quotes.
    if string[0] != '"' or string[-1] != '"':
        raise TypeError('Not a string: {}'.format(string))
    return string[1:-1]

def read_python_string(value):
    # FIXME(strager): This is fragile.
    return read_c_string(lldb.frame.EvaluateExpression(
        '(const char *) PyString_AsString({})'.format(
            value.GetValue(),
        ),
    ))

class Frame(object):
    __token = object()

    def __init__(self, frame_py, token):
        if token is not Frame.__token:
            raise Exception(
                'Use static methods to construct Frame objects',
            )
        self.__frame_py = frame_py

    @classmethod
    def current(cls):
        return cls.from_frame_object(lldb.frame.EvaluateExpression(
            '(PyFrameObject *) PyEval_GetFrame()',
        ))

    @classmethod
    def from_frame_object(cls, frame_object):
        # HACK(strager): Assumes NULL is 0.
        null = 0
        if frame_object.GetValueAsUnsigned(null) == null:
            return None
        return cls(frame_object, Frame.__token)

    @property
    def file_name(self):
        return read_python_string(
            self.__frame_py
                .GetChildMemberWithName('f_code')
                .GetChildMemberWithName('co_filename'),
        )

    @property
    def function_name(self):
        return read_python_string(
            self.__frame_py
                .GetChildMemberWithName('f_code')
                .GetChildMemberWithName('co_name'),
        )

    @property
    def line_number(self):
        x = lldb.frame.EvaluateExpression(
            '(int) PyFrame_GetLineNumber({})'.format(
                self.__frame_py.GetValue(),
            ),
        ).GetValueAsSigned(-1)
        if x == -1:
            return None
        return x

    @property
    def next(self):
        return self.from_frame_object(
            self.__frame_py.GetChildMemberWithName('f_back'),
        )

    def __str__(self):
        return '{}:{} ({})'.format(
            self.file_name,
            self.line_number,
            self.function_name,
        )

def print_python_traceback():
    frame = Frame.current()
    while frame is not None:
        print frame
        frame = frame.next
