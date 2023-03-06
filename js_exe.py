import execjs
from pprint import pprint

class js_runner(object):
    def __init__(self) -> None:
        self.js={}
        self.js_no_func='''
        function {function_name}() {{
            return {js_code}
        }}
        '''
        self.result={}

    def create_js(self,function_name:str,js_code:str)-> None:
        #For have function title
        self.js[function_name]=js_code

    def create_js_no_func(self,function_name:str,js_code:str)-> None:
        #For no function title
        self.js[function_name]=self.js_no_func.format(function_name=function_name,
                                                        js_code=js_code)

    def __str__(self) -> str:
        pprint(self.js)

    def run_js(self,function_name:str,paras=None)-> str:
        #Execute js 
        #paras max:6
        self.jsContext = execjs.compile(self.js[function_name])   

        if paras:
            if len(paras)==1:
                self.result[function_name] = self.jsContext.call(function_name,paras[0])
            elif len(paras)==2:
                self.result[function_name] = self.jsContext.call(function_name,paras[0],paras[1])
            elif len(paras)==3:
                self.result[function_name] = self.jsContext.call(function_name,paras[0],paras[1],paras[2])
            elif len(paras)==4:
                self.result[function_name] = self.jsContext.call(function_name,paras[0],paras[1],paras[2],paras[3])
            elif len(paras)==5:
                self.result[function_name]= self.jsContext.call(function_name,paras[0],paras[1],paras[2],paras[3],paras[4])
            elif len(paras)==6:
                self.result[function_name] = self.jsContext.call(function_name,paras[0],paras[1],paras[2],paras[3],paras[4],paras[5])
        else:
            self.result[function_name] = self.jsContext.call(function_name)
        return self.result[function_name]