from linovelib_book import linovelib_loader 
from generate_epub_info import generate_toc,generate_opf,generate_xhtml,generate_css,generate_container
from tqdm import tqdm
from datetime import datetime

import urllib.request as req
import os
import shutil

import time
import zipfile

def make_save_path(save_path):
    '''    Make main folder   '''

    if not os.path.exists(save_path):
        os.mkdir(save_path)
    else:
        shutil.rmtree(save_path)
        os.mkdir(save_path)

def make_epub_structure(catalog_path):
    '''    Make folder for epub    '''
    for p in catalog_path:
        os.mkdir(p)
        os.mkdir(os.path.join(p,'Text'))
        os.mkdir(os.path.join(p,'Styles'))
        os.mkdir(os.path.join(p,'Images'))


def make_html(book_path,title,total_len,all_chapter):
    """    Make html and save it to corresponding folder    """
    bar=tqdm(range(1,total_len),desc=title)
    for c_t in all_chapter:
        for p_t in all_chapter[c_t]:
            with open(os.path.join(book_path,c_t,'Text',p_t)+'.xhtml','w',encoding='UTF-8') as f:
                f.write(generate_xhtml(
                            title=p_t,
                            body=all_chapter[c_t][p_t]
                        )
                )
            bar.update(1)

def make_ncx(nxcpath,title,catalog_page_table):
    for p,c_p_table in zip(nxcpath,catalog_page_table):
        toc=generate_toc(
                title=title,
                identifier='make_by_autocreate',
                catalog_page_table=catalog_page_table[c_p_table]
            )

        with open(os.path.join(p,'toc.ncx'),'w',encoding="utf-8") as f :
            f.write(toc)
        f.close()

def get_img(path,pic_len,all_img_url,cover_url):
    
    bar=tqdm(range(pic_len+1),desc='Picture:')
    for chapter in all_img_url:
        for url in all_img_url[chapter]:
            header = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
            }
            request=req.Request(url,headers=header)
            html = req.urlopen(request).read()
            pic_name=url[url.rfind('/')+1:]
            with open(os.path.join(path,chapter,'Images',pic_name),'wb') as f :
                f.write(html)
            f.close()
            bar.update(1)
    
        #cover
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
        }
        request=req.Request(cover_url,headers=header)
        html = req.urlopen(request).read()
        pic_name=url[url.rfind('/')+1:]
        with open(os.path.join(path,chapter,'Images','cover.jpg'),'wb') as f :
            f.write(html)
        f.close()
        bar.update(1)

def make_opf(title,author,all_chapter,book_path):
    for chapter in all_chapter:
        opf=generate_opf(
            title=title+' '+chapter,
            language='zh-TW',
            date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            author=author,
            identifier='make_by_autocreate',
            item_path=[os.path.join(book_path,chapter,'Text'),os.path.join(book_path,chapter,'Images')],
            chapter=all_chapter[chapter],
        )

        with open(os.path.join(book_path,chapter,'content.opf'),'w',encoding="utf-8") as f :
            f.write(opf)
        f.close()

def make_css(catalog_path):
    for p in catalog_path:
        with open(os.path.join(p,'Styles','main.css'),'w') as f:
            f.write(generate_css())

def move_to_OEBPS(path):
    dir_list=os.listdir(path)
    for dir in dir_list:
        file_list=os.listdir(os.path.join(path,dir))
        os.mkdir(os.path.join(path,dir,'OEBPS'))
        os.mkdir(os.path.join(path,dir,'META-INF'))
        for file in file_list:
            os.rename(os.path.join(path,dir,file), os.path.join(path,dir,'OEBPS',file))

        with open(os.path.join(path,dir,'mimetype'),'w') as f:
            f.write('application/epub+zip')

        with open(os.path.join(path,dir,'META-INF','container.xml'),'w') as f:
            f.write(generate_container())
    
def make_epub(path,book_title):
    
    for dir in os.listdir(path):
        os.chdir(os.path.join(path,dir))
        with zipfile.ZipFile(book_title+dir+'.epub', mode='w') as zf:
            zf.write(os.path.join('mimetype'))
        with zipfile.ZipFile(book_title+dir+'.epub', mode='a') as zf:
            for file in os.listdir(os.path.join('OEBPS')):
                zf.write(os.path.join('OEBPS',file))
            for file in os.listdir(os.path.join('META-INF')):
                zf.write(os.path.join('META-INF',file))

if __name__ == "__main__":
    book_id=input('book id:')
    start = time.time()

    print('-----------------------------')
    print('--------Get book info--------')
    book=linovelib_loader(book_id)
    print('----------Save Path:---------')
    print(book.path)
    make_save_path(book.path)

    print('--Create epub structure dir--')
    make_epub_structure(book.catalog_path)

    print('-----------Get Image---------')
    get_img(book.path,book.img_len,book.img_src,book.cover_url)

    print('-----------Make css----------')
    make_css(book.catalog_path)
    
    print('----Make all chapter html----')
    make_html(book.path,book.book_title,book.chapter_len,book.all_chapter)
    
    print('---------Make toc.ncx--------')
    make_ncx(book.catalog_path,book.book_title,book.catalog_page_table)
    
    print('-----------Make opf----------')
    make_opf(book.book_title,book.book_author,book.all_chapter,book.path)

    print('------Mimetype/OEBPS FIX-----')
    move_to_OEBPS(book.path)

    print('-----------Make epub---------')
    make_epub(book.path,book.book_title)
    print('-----------Finish------------')
    
  
    end = time.time()
    print(f'花費時間：{end - start}')