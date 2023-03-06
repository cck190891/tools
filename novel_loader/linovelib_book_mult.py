'''
book class
|
|---book id
|   |---url
|
|---book info
|   |---title
|   |---author
|   |---book path:str (can be used to make save dir) 
|   |---catalog path : [ all chapter dir list:str] (can be used to catalog dir)
|   |---catalog/page table : dict { chapter:str : [all page title:str] }
                             Order by catalog (can be used to generate epub nox and catalog)
|---book chapter
|   |---all chapter : dict { chapter:str : { page title:str : page index:str }} 
                      Order by add time(now just for fix problem 1)

chapter class
|   |---chapter title
|   |---chapter info 
|       |---next chapter url : now just for fix problem 1      
|   |---page title
|   |---page index


problem 1:
    book chapter: (method:use_catalog_get_all_chapter_url)
        some chapter title in catalog page not work ( href show javascript:cid(0) )
        some chapter have inside page (/XX/XXXXXX_2,/XX/XXXXXX_3)
solve:
    do bfs in use_url_get_page
    check next page exist in view_list

'''

import urllib.request as req
import bs4
import re
import os
from multiprocessing.pool import ThreadPool

class linovelib_loader(object):
    def __init__(self,book_id) -> None:
        self.book_id=book_id
        self.dir=os.path.abspath(__file__)[:os.path.abspath(__file__).rfind('\\')]
        self.main_domain='https://tw.linovelib.com'
        self.main_url=self.main_domain+'/novel/'+str(book_id)+'.html'
        self.catalog_page_url=self.main_domain+'/novel/'+str(book_id)+'/catalog'
        self.chapter_len=0
        self.img_len=0
        self.img_src={}
        self.all_chapter={}
        self.view_list=[]
        
        self.get_book_info()
        self.use_catalog_get_all_chapter_url()

        
    def get_book_info(self):

        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
        }
        request=req.Request(self.main_url,headers=header)
        html = req.urlopen(request).read().decode("utf-8")

        root=bs4.BeautifulSoup(html,"html.parser")
        book_info=root.find('div',class_='book-detail-info')
        self.book_title=re.sub('[<>:"\\/|?*]', '_',book_info.find('h2',class_="book-title").text)
        self.book_author=book_info.find('div',class_="book-rand-a").find('span').text
        self.cover_url=book_info.find('img',class_="book-cover")['src']
        self.path=os.path.join(self.dir,self.book_title)

    def use_catalog_get_all_chapter_url(self):

        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
        }
        request=req.Request(self.catalog_page_url,headers=header)
        html = req.urlopen(request).read().decode("utf-8")

        root=bs4.BeautifulSoup(html,"html.parser")
        self.page_title_list=root.find_all('li',class_="chapter-li jsChapter")

        self.list_all_catalog_page=root.find('ol',id="volumes",class_="chapter-ol chapter-ol-catalog")
        self.catalog_page_table={}
        #self.page_url_table={}
        for one_line in self.list_all_catalog_page:
            if one_line.name == 'li':
                if "chapter-bar" in one_line['class']:
                    catalog_title=re.sub('[<>:"\\/|?*]', '_',one_line.text)
                    self.catalog_page_table[catalog_title]=[]
                else:
                    self.catalog_page_table[catalog_title].append(one_line.text)
                    self.chapter_len+=1
                    # if one_line.text not in self.page_url_table.keys():
                    #     self.page_url_table[catalog_title+'|'+one_line.text]=[self.main_domain+one_line.find('a')['href']]
                    # else:
                    #     self.page_url_table[catalog_title+'|'+one_line.text].append(self.main_domain+one_line.find('a')['href'])
                    

        self.catalog_path=[os.path.join(self.path,x) for x in self.catalog_page_table]
        self.page_url_list=[self.main_domain+x.find('a')['href'] for x in self.page_title_list if str(self.book_id) in x.find('a')['href']]
        
        #bfs for problem 1
        #while self.page_url_list:
        #    self.use_url_get_page(self.page_url_list)
        #bfs for problem 1
        while self.page_url_list:
            pool = ThreadPool(16)
            results1 = pool.map(self.use_url_get_page,[self.page_url_list])
            pool.close()
            pool.join()

    def use_url_get_page(self,page_url):
        self.page_url_list=[]
        for url in page_url:
            self.view_list.append(url)
            this_chapter=chapter(url)
            
            if this_chapter.chapter_info_dict['page'] == '1':
                if this_chapter.chapter_title not in self.all_chapter.keys():
                    self.all_chapter[this_chapter.chapter_title]={this_chapter.page_title:this_chapter.page_index}
                else:
                    self.all_chapter[this_chapter.chapter_title][this_chapter.page_title] = this_chapter.page_index
            else:
                origin_name=re.findall('(.*?)（[\s\d]*_[\s\d]*）',this_chapter.page_title)[0]
                self.all_chapter[this_chapter.chapter_title][origin_name]+=this_chapter.page_index
                
            if this_chapter.img_url:
                self.img_len+=len(this_chapter.img_url)
                if this_chapter.chapter_title not in  self.img_src.keys():
                    self.img_src[this_chapter.chapter_title]=this_chapter.img_url
                else:
                    self.img_src[this_chapter.chapter_title]+=this_chapter.img_url
            next_page=self.main_domain+this_chapter.chapter_info_dict['url_next']

            #bfs for problem 1
            if next_page not in self.view_list and next_page not in page_url and 'catalog' not in next_page:
                self.page_url_list.append(next_page)
            #bfs for problem 1





class chapter(object):

    def __init__(self,url) -> None:
        self.url=url
        self.get_all_info()

    def get_all_info(self):
        header = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
            }
        request=req.Request(self.url,headers=header)
        html = req.urlopen(request).read().decode("utf-8")

        root=bs4.BeautifulSoup(html,"html.parser")

        chapter_info_str=re.findall('var ReadParams=\{(.*)\}</script>',str(root))[0].split(',')
        self.chapter_info_dict={x[:x.rfind(':')]:x[x.find('\'')+1:x.rfind('\'')] for x in chapter_info_str}
        
        self.chapter_title=re.sub('[<>:"\\/|?*]', '_',root.find('div').find('h3').text)
        self.page_title=re.sub('[<>:"\\/|?*]', '_',root.find('div').find('h1').text)
        self.page_index=str(root.find('div',id="acontent",class_="acontent"))
        self.img_url=[img for img in re.findall('src=\"(.*?)\"',self.page_index) if 'img' in img]
        
        for img_src in self.img_url:
            print(img_src,'==>','../Images'+img_src[img_src.rfind('/'):])
            self.page_index=self.page_index.replace(img_src,'../Images'+img_src[img_src.rfind('/'):]) 

        print('')
        print('chapter title:',self.chapter_title,'page title:',self.page_title)
        print('Url:',self.url)
