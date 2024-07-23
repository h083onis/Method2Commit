from enum import Enum

class State(Enum):
    CODE = 1
    C_COMMENT = 2
    CPP_COMMENT = 3
    STRING_SINGLE_LITERAL = 4
    STRING_DUBLE_LITERAL = 5
    
def remove_c_com_and_doc(text):
        result = []
        prev = ''
        state = State.CODE
        escape_cnt = 0

        for ch in text:
            # Skip to the end of C-style comment
            if state == State.C_COMMENT:
                if escape_cnt % 2 == 0 and prev == '*' and ch == '/':
                    state = State.CODE
                    escape_cnt = 0
                    prev = ''
                    continue
                if ch == '\\':
                    escape_cnt += 1
                else:
                    escape_cnt = 0
                if ch == '\n':
                    prev = ''
                else:
                    prev = ch
                continue

            # Skip to the end of the line (C++ style comment)
            if state == State.CPP_COMMENT:
                if ch == '\n':  # End comment
                    state = State.CODE
                    result.append('\n')
                    prev = ''
                continue

            # Skip to the end of the string literal
            #\\エスケープ文字の数を数えて奇数，偶数で対応を返る必要性がある
            if state == State.STRING_DUBLE_LITERAL:
                if escape_cnt % 2 == 0 and ch == '"':
                    state = State.CODE
                    escape_cnt = 0
                if ch == '\\':
                    escape_cnt += 1
                else:
                    escape_cnt = 0
                # print(prev)
                result.append(prev)
                prev = ch
                continue
            
             # Skip to the end of the string literal
            if state == State.STRING_SINGLE_LITERAL:
                if escape_cnt % 2 == 0 and ch == '\'':
                    state = State.CODE
                    escape_cnt = 0
                if ch == '\\':
                    escape_cnt += 1
                else:
                    escape_cnt = 0
                # print(prev)
                result.append(prev)
                prev = ch
                continue
            
            if ch == '\\':
                escape_cnt += 1
            else:
                escape_cnt = 0
            # Starts C-style comment?
            if escape_cnt % 2 == 0 and prev == '/' and ch == '*':
                state = State.C_COMMENT
                prev = ''
                escape_cnt = 0
                continue

            # Starts C++ style comment?
            if escape_cnt % 2 == 0 and prev == '/' and ch == '/':
                state = State.CPP_COMMENT
                prev = ''
                escape_cnt = 0
                continue

            # Comment has not started yet
            if prev: result.append(prev)

            # Starts string literal?
            if escape_cnt % 2 == 0 and ch == '\'':
                state = State.STRING_SINGLE_LITERAL
                escape_cnt = 0
            
            # Starts string literal?
            if escape_cnt % 2 == 0 and ch == '"':
                state = State.STRING_DUBLE_LITERAL
                escape_cnt = 0
            prev = ch

        # Returns filtered text
        if prev: result.append(prev)
        line_list = [line for line in ''.join(result).split('\n') if line.strip() != '']
        # line_list = [line for line in ''.join(result).split('\n')]
        result = '\n'.join(line_list)
        return result