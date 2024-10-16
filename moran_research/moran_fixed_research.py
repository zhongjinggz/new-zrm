import code
from datetime import datetime
import re

# 码表
FILENAME_DICT = 'moran_fixed_simp.dict.yaml'
         
class ByWord:
    def __init__(self, code_len = 0, word_len=0, count_duplicated_code = 2):
        """
        code_len: 编码长度，0表示不判断长度
        word_len: 词的长度，0表示不判断长度
        count_duplicated_code: 是否统计重复编码的词，0-不统计，1-统计，2-所有
        """

        self._code_len = code_len
        self._word_len = word_len
        self._count_duplicated_code = count_duplicated_code
        
        self._word_code_list = {}
        
        self._output = open(self._output_file_name(), 'w', encoding='utf-8')

        
    def _output_file_name(self):
        result = "by_word" 
        
      
        result += "_level" + str(self._code_len) if self._code_len > 0 else ""

        result +=("_" + str(self._word_len) +"char") if self._word_len > 0 else ""
            
        if self._count_duplicated_code == 1:
            result += "_duplicated" 
        elif self._count_duplicated_code == 0:
            result +=  "_unique"
        else:
            result += "_all"
            
        result += ".txt"
        
        return result
    
    def description(self):
        result = ""
        
        if self._count_duplicated_code == 1:
            result += "重复编码"
        elif self._count_duplicated_code == 0:
            result += "不重复编码"
        else:
            result += "重复及不重复编码"
        
        if self._code_len > 0:
            result += "的" + str(self._code_len) + "码"
            
        if self._word_len > 0:
            result +=  str(self._word_len) + "字词"
        else:
            result += "字词"
        
        return result
        
    def next(self, line_num, tokens, line):
        word = tokens[0]
        code_info_list = []
        for i in range(1, len(tokens)):
            code_info_list.append((line_num, tokens[i]))
        
        if word in self._word_code_list:
            self._word_code_list.get(word).extend(code_info_list)
        else:
            self._word_code_list[word] = code_info_list
        

    def post_process(self):
        if len(self._word_code_list) > 0:
            word_num = 0
            for word in self._word_code_list:
                code_info_list = self._word_code_list.get(word)
                
                if len(code_info_list) == 0:
                    continue
                
                if not self._meet_code_len_criteria(code_info_list):
                    continue

                if not self._meet_word_len_criteria(word):
                    continue
                
                if not self._meet_duplicated_code_criteria(code_info_list):
                    continue


                
                word_num +=1 
                self._output.write(f"{word_num}\t{word}")
                for code_info in code_info_list:
                    self._output.write(f"\t{code_info[0]}:{code_info[1]}")
                self._output.write("\n")
                
            self._output.write(f"#共计：{word_num}个{self.description()}\n")
            self._output.write(f"#{datetime.now()}")

    def _meet_duplicated_code_criteria(self, code_info_list):
        return (self._count_duplicated_code == 2) \
            or (self._count_duplicated_code == 1 and len(code_info_list) >= 2) \
            or (self._count_duplicated_code == 0 and len(code_info_list) == 1)
    
    def _meet_code_len_criteria(self, code_info_list):
        if self._code_len == 0:
            return True
        
        for code_info in code_info_list:
            if len(code_info[1]) == self._code_len:
                return True
        return False
    
    def _meet_word_len_criteria(self, word):
        return self._word_len == 0 or len(word) == self._word_len
    
        
    def close(self):
         if self._output:
             self._output.close()
            

         
class ByCode:
    def __init__(self, code_len = 0, word_len=0, count_duplicated_word = 2):
        """
        code_len: 编码长度，0表示不判断长度
        word_len: 词的长度，0表示不判断长度
        count_duplicated_word: 是否统计重码词，0-不统计，1-统计，2-所有
        """

        self._code_len = code_len
        self._word_len = word_len
        self._count_duplicated_word = count_duplicated_word
        
        self._code_word_list = {}
        
        self._output = open(self._output_name(), 'w', encoding='utf-8')

        
    def _output_name(self):
        result = "by_code" 
        
      
        result += "_level" + str(self._code_len) if self._code_len > 0 else ""

        result +=("_" + str(self._word_len) +"char") if self._word_len > 0 else ""
            
        if self._count_duplicated_word == 1:
            result += "_duplicated" 
        elif self._count_duplicated_word == 0:
            result +=  "_unique"
        else:
            result += "_all"
            
        result += ".txt"
        
        return result
    
    def description(self):
        result = ""
        
        if self._count_duplicated_word == 1:
            result += "重码"
        elif self._count_duplicated_word == 0:
            result += "不重码"
        else:
            result += "所有"
        
        if self._code_len > 0:
            result += str(self._code_len) + "码"
            
        if self._word_len > 0:
            result +=  str(self._word_len) + "字词编码"
        else:
            result += "字词编码"
        
        return result
        
    def next(self, line_num, tokens, line):
        word = tokens[0]
        word_info = (line_num, word)
        
        for i in range(1, len(tokens)):
            code = tokens[i]
            if code in self._code_word_list:
                self._code_word_list.get(code).append(word_info)
            else:
                self._code_word_list[code] = [word_info]

    def post_process(self):    
        if len(self._code_word_list) > 0:
            code_num = 0
            for code in self._code_word_list:
                word_info_list = self._code_word_list.get(code)
                
                if len(word_info_list) == 0:
                    continue
                
                if not self._meet_code_len_criteria(code):
                    continue

                if not self._meet_word_len_criteria(word_info_list):
                    continue
                
                if not self._meet_duplicated_word_criteria(word_info_list):
                    continue

                
                code_num +=1 
                self._output.write(f"{code_num}\t{code}")
                for word_info in word_info_list:
                    self._output.write(f"\t{word_info[0]}:{word_info[1]}")
                self._output.write("\n")
                
            self._output.write(f"#共计：{code_num}个{self.description()}\n")
            self._output.write(f"#{datetime.now()}")

    def _meet_duplicated_word_criteria(self, word_info_list):
        return (self._count_duplicated_word == 2) \
            or (self._count_duplicated_word == 1 and len(word_info_list) >= 2) \
            or (self._count_duplicated_word == 0 and len(word_info_list) == 1)
    
    def _meet_word_len_criteria(self, word_info_list):
        if self._word_len == 0:
            return True
        
        for word_info in word_info_list:
            if len(word_info[1]) == self._word_len:
                return True
            
        return False
    
    def _meet_code_len_criteria(self, code):
        return self._code_len == 0 or len(code) == self._code_len
    
        
    def close(self):
         if self._output:
             self._output.close()
  
class ByFilter:
    def __init__(self, code_len = 0, word_len=0):
        """
        code_len: 编码长度，0表示不判断长度
        word_len: 词的长度，0表示不判断长度
        """

        self._code_len = code_len
        self._word_len = word_len
        
        self._output = open(self._output_name(), 'w', encoding='utf-8')
        self._item_num = 0
    def _output_name(self):
        result = "filter" 
        result += "_level" + str(self._code_len) if self._code_len > 0 else ""
        result +=("_" + str(self._word_len) +"char") if self._word_len > 0 else ""
        result += ".txt"
        return result
    def description(self):
        result = "找出"
        
        if self._code_len > 0:
            result += str(self._code_len) + "码"
            
        if self._word_len > 0:
            result +=  str(self._word_len) + "字"

        result += "的编码"
        return result
    def next(self, line_num, tokens, line):
        word = tokens[0]
        code = tokens[1]

        if self._meet_code_len_criteria(code) and self._meet_word_len_criteria(word):
            self._item_num +=1
            self._output.write(f"{line_num}\t{line.strip()}\n")
    def post_process(self):    
            self._output.write(f"#共计：{self._item_num}个{self.description()}\n")
            self._output.write(f"#{datetime.now()}")
    def _meet_word_len_criteria(self, word):
        return self._word_len == 0 \
            or self._word_len == len(word)
    def _meet_code_len_criteria(self, code):
        return self._code_len == 0 \
            or len(code) == self._code_len
    def close(self):
         if self._output:
             self._output.close()
  

class Dict:
    def __init__(self, output_processor):
        self._file_dict = open(FILENAME_DICT, 'r', encoding='utf-8')
        self._output_processor = output_processor
        self._body_started_status = False
        self._line = None
        self._line_num = 0

    def _body_is_started(self):
        """判断是否已经到了正文"""
        if self._body_started_status == True:
            return True
        else:
            if '#----------词库----------#' in self._line:
                self._body_started_status = True
            return False
        
    def _not_space_line(self):
        return self._line.strip() != ''
    
    def _not_comment(self):
        striped = self._line.strip()
        return striped == '' or striped[0] != '#'
    
    
    def do(self):
        for line in self._file_dict:
            self._line = line
            self._line_num += 1
            if self._body_is_started() and self._not_space_line() and self._not_comment():
                    tokens = line.strip().split()
                    if len(tokens) >= 2:
                        self._output_processor.next(self._line_num, tokens, line)
        
        self._output_processor.post_process()
            
    def close(self):
        if self._file_dict:
            self._file_dict.close()
            self._output_processor.close()

def process(case):
    print(case.description())
    try:
        dict = Dict(case)
        dict.do()
    except FileNotFoundError:
        print(f"Sorry, the file {FileNotFoundError.filename} does not exist.")
    finally:
        dict.close()
        
    print("==== DONE ====\n")

if __name__ == '__main__':
    # process(ByFilter(word_len=1, code_len=2))
    process(ByCode(code_len=3, count_duplicated_word=1))
    # process(ByWord(word_len=3, count_duplicated_code=1))
    
 
                  
        
