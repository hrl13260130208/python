from collector import excel_rw
from collector import name_manager
from collector import threads
from collector import htmls
import os
import logging
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger("logger")

UPDATE="update"

#文件路径配置
# REPORT_PATH="F:/pdfs/report.txt"
# back_file="F:/pdfs/backup"
# first_dir = "F:/pdfs/"

REPORT_PATH="C:/pdfs/report.txt"
first_dir = "C:/pdfs/"
back_file="C:/pdfs/backup"

test_file="C:/File/sdf.pdf"
#test_file="C:/File/sdf.pdf"

#重试次数
DOWNLOAD_URL_RETRY=5
DOWNLOAD_RETRY=5
CHECK_PDF_RETRY=3

executor=ThreadPoolExecutor(4)

def init_download_url_thread(um,tm,thread_list,dir):
    url_set_names=um.get_sourcenames()
    for url_set_name in url_set_names:
        if url_set_name == "Elsevier":
            th=threads.Elsevier_download(url_set_name,um,tm,dir)
        else:
            th=threads.download_url(url_set_name, um, tm)
        thread_list.append(th)
        th.start()
    return thread_list

def init_download_and_check_thread(um,thread_list,dir):
    sns=um.get_sourcenames()
    for sn in sns:
        if sn =="Elsevier":
            continue
        th=threads.download(sn, um, dir)
        thread_list.append(th)
        th.start()
    return thread_list

def create_dir(dir_name):
    # first_dir = "F:/pdfs/"

    dir = first_dir +dir_name + "/"
    if not os.path.exists(dir):
        if not os.path.exists(first_dir):
            os.mkdir(first_dir)
        os.mkdir(dir)
    return dir

def start(name,file_path):
    thread_list = []

    um = name_manager.url_manager(name)
    tm = name_manager.template_manager()
    execl = excel_rw.excels(file_path, um)
    execl.write()
    um.clear()
    execl.read()
    dir = create_dir(name)

    thread_list = init_download_url_thread(um, tm, thread_list,dir)
    thread_list = init_download_and_check_thread(um, thread_list, dir)

    for th in thread_list:
        th.join()

    execl.write()
    execl.report()
    um.clear()

def run_thread(name,file_path):
    # name="test"
    # file_path="C:/temp/gruyter2018-2019待采全文的文章清单.xls"
    list = []

    um = name_manager.url_manager(name)
    tm = name_manager.template_manager()
    execl = excel_rw.excels(file_path, um)
    execl.write()
    um.clear()
    execl.read()
    dir = create_dir(name)

    url_set_names = um.get_sourcenames()
    for url_set_name in url_set_names:
        if url_set_name == "Elsevier":
            th = threads.Elsevier_download(url_set_name, um, tm, dir)
        else:
            th = threads.download_url(url_set_name, um, tm)
        fu=executor.submit(th.run)
        list.append(fu)

    sns = um.get_sourcenames()
    for sn in sns:
        if sn == "Elsevier":
            continue
        th = threads.download(sn, um, dir)
        list.append(executor.submit(th.run))

    while (list.__len__() > 0):
        time.sleep(3600)
        print("++++++++++++++++")
        for li in list:
            print('==============')
            if li.done():
                print(li.result())
                if li.exception() != None:
                    exit(0)
                    break
                else:
                    list.remove(li)

    execl.write()
    execl.report()
    um.clear()




def check_task(name):
    um = name_manager.url_manager(name)
    um.query()

def check_finsh_task(name):
    um = name_manager.url_manager(name)
    um.query_finsh_url()

def check_conf():
    tm=name_manager.template_manager()
    tm.check_confs()

def test_download():
    url_="http://dx.doi.org/10.1515/math-2018-0003"

    section="Gruyter_2391-5455"
    cp=htmls.config_parser()
    cp.get_section(section)
    d_url=htmls.HTML(None,None,None).do_run(cp.get_section(section),url_)
    print(d_url)
    htmls.download(d_url.strip(),test_file)
    print(htmls.checkpdf(test_file))




class test(threading.Thread):
    def run(self):

        print(self.name+"  ",time.time())
        time.sleep(10)
        return "dsf"



class test2(threading.Thread):
    def run(self):

        print(self.name+"  ",time.time())
        time.sleep(5)
        a=1/0
        return "ddff"

if __name__ == '__main__':

    name = "test"
    #name = "yj0122"
    # name = "jx0122"

    #file_path = "F:/hrl/mc/0121/冶金所待补全文清单_20190121..xls"
    # file_path = "F:/hrl/mc/0121/机械所待补全文清单_20190121..xls"
    file_path = "C:/temp/gruyter2018-2019待采全文的文章清单.xls"

    #check_task(name)
    cp=htmls.config_parser()
    cp.paser()
    run_thread(name,file_path)
    cp.backup()
    #
    # test_download()






