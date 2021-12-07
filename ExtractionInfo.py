'''2021-01-18
从apk中提取appid的代码（多进程），使用apktool进行反编译
'''
import re
import os
import sys
from multiprocessing import Pool, Lock
import multiprocessing
import time
import shutil
from xml.dom.minidom import parse
import xml.dom.minidom
from ReverseApk import Reverse

lock = Lock()

class Extraction(object):
    """docstring for Extraction"""

    def __init__(self, root_dir="", save_path="", process_num=5):
        self.root_dir = root_dir
        self.process_num = process_num
        _now_path = os.path.split(os.path.realpath(__file__))[0]
        self.save_dir_2 = os.path.join(_now_path, 'Manifest')
        self.save_dir = os.path.join(_now_path,'temp_reverse')
        self.save_path = os.path.join(_now_path, save_path)
        self.find_in_code = True
        self.find_in_xml = True
        self.rename = True

        self.APPID_PACKAGE = {}  # appid:[package1,package2,...]
        self.PACKAGE_APPID = {}  # package:[appid1,appid2,...]
        self.PACKAGE_APK = {}  # package:appid
        self.packagename = ""

    '''
    travel all apk in root_dir and process them
    '''

    def run(self):
        pool = Pool(processes=self.process_num)
        self.APPID_PACKAGE = multiprocessing.Manager().dict()
        self.PACKAGE_APPID = multiprocessing.Manager().dict()
        self.PACKAGE_APK = multiprocessing.Manager().dict()
        count = 0
        for root, dirs, files in os.walk(self.root_dir, topdown=True):
            for name in files:
                if name.endswith('.apk') or name.endswith('.xapk'):
                    apkfile = os.path.join(root, name)
                    count += 1
                    pool.apply_async(self.ProcessAPK, args=(apkfile, count))
        pool.close()
        pool.join()
        return self.SaveResultToTXT(self.save_path)

    '''
    process each apk
    '''

    def ProcessAPK(self, apkfile, count):
        print(">>>>Process:[{}]{}".format(count, apkfile))
        reverse_dir = os.path.join(self.save_dir, apkfile.strip(self.root_dir).replace('\\', '-').strip('.apk'))
        my_reverse = Reverse(apkfile, reverse_dir)
        if not my_reverse.apktool():  # 反编译失败，直接删除文件并返回
            try:
                shutil.rmtree(reverse_dir)
            except:
                print("[ERROR]remove dir {} failed!".format(reverse_dir))
            return

        # 把manifest另外保存起来
        self.SaveManifest(reverse_dir)

        self.packagename = self.GetPackageName(reverse_dir)
        print("packagename:",self.packagename)
        if (self.packagename in self.PACKAGE_APK) or self.packagename == '':
            try:
                shutil.rmtree(reverse_dir)
                print("[{}]remove:{}".format(count,reverse_dir))
            except:
                print("[ERROR]remove dir {} failed!".format(reverse_dir))
        else:
            travel_all = True
            if travel_all:
                self.PACKAGE_APK[self.packagename] = apkfile
                print("[{}]Travel in :{}".format(count,os.path.join(reverse_dir,'apktool')))
                self.TravelApk(os.path.join(reverse_dir,'apktool'))
                print("[{}]Travel end :{}".format(count,os.path.join(reverse_dir,'apktool')))
            else:
                for file in os.listdir(os.path.join(reverse_dir,'apktool')):
                    if ("smali" in file) and self.find_in_code:
                        print("[{}]Travel in :{}".format(count,os.path.join(reverse_dir,'apktool',file)))
                        self.TravelApk(os.path.join(reverse_dir,'apktool',file))
                        print("[{}]Travel end :{}".format(count,os.path.join(reverse_dir,'apktool',file)))
                    if file=="res" and self.find_in_xml:
                        print("[{}]Travel in :{}".format(count,os.path.join(reverse_dir,'apktool','res')))
                        self.TravelApk(os.path.join(reverse_dir,'apktool','res'))
                        print("[{}]Travel end :{}".format(count,os.path.join(reverse_dir,'apktool','res')))
            try:
                shutil.rmtree(reverse_dir)
                print("[{}]remove:{}".format(count, reverse_dir))
            except:
                print("[ERROR] remove {} failed!".format(reverse_dir))

        # rename the apk by it's packagename
        self.rename =  True
        if self.rename:
            _basename = os.path.basename(apkfile)
            dstfile = apkfile.replace(_basename, self.packagename + ".apk")
            _num = 1
            while os.path.exists(dstfile):
                dstfile = apkfile.replace(_basename, self.packagename + "-" + str(_num) + ".apk")
                _num += 1
            os.rename(apkfile, dstfile)

    '''
    reverse apk
    '''

    def Reverse(self, apkfile, dstdir):
        if os.path.exists(dstdir):  # 删除原来的
            shutil.rmtree(dstdir)
        os.makedirs(dstdir)  # 创建新的
        # apktool,解包得到xml布局文件于./apktool
        apktool_dst = os.path.join(dstdir, "apktool")
        shell = 'apktool -q d ' + "\"" + apkfile + "\"" + ' -o ' + "\"" + apktool_dst + "\""
        print(shell)
        os.system(shell)

    '''
    get packagename
    '''

    def GetPackageName(self, reverse_dir):
        packagename = ''
        xmlfile = os.path.join(reverse_dir, 'apktool', 'AndroidManifest.xml')
        try:
            DOMTree = xml.dom.minidom.parse(xmlfile)
            collection = DOMTree.documentElement
            # 得到packagename
            packagename = collection.getAttribute('package')
            print(">>>>>>>>>>>>[in GetPackageName]", packagename)
        except Exception as e:
            print('[ERROR] can\'t parse mainifest {}!!!!'.format(xmlfile))
            print(e)
        return packagename

    '''
    get manifest
    '''

    def SaveManifest(self, reverse_dir):
        packagename = 'None'
        xmlfile = os.path.join(reverse_dir, 'apktool', 'AndroidManifest.xml')
        try:
            DOMTree = xml.dom.minidom.parse(xmlfile)
            collection = DOMTree.documentElement
            # 得到packagename(xapk里面所有manifest的package都是一样的)
            packagename = collection.getAttribute('package')
            new_xmlfile = os.path.join(self.save_dir_2, packagename + '.xml')
            print(">>>>>>>>>>>>[new xmlfile]", new_xmlfile)
            shutil.copyfile(xmlfile, new_xmlfile)
            print(">>>>>>>>>>>>[in GetPackageName]", packagename)
        except Exception as e:
            print('[ERROR] can\'t parse mainifest {}!!!!'.format(xmlfile))
            print(e)
        return packagename

    '''
    travel the apk reversed dir
    '''

    def TravelApk(self, reverse_dir):
        if not os.path.exists(reverse_dir):
            print('[ERROR]reverse_dir not exists :{}'.format(reverse_dir))
            return
        for root, dirs, files in os.walk(reverse_dir, topdown=False):
            for name in files:
                filename = os.path.join(root, name)
                if self.find_in_code == True and name.endswith('.smali'):
                    self.GetAppID(filename)
                if self.find_in_xml == True and name.endswith('.xml'):
                    self.GetAppID(filename)

    '''
    extract appid
    '''

    def GetAppID(self, filename):
        filestr = ''
        try:
            fp = open(filename, 'r', encoding='utf-8')
            filestr = fp.read()
            fp.close()
        except Exception as e:
            pass
        pattern = re.compile(r'wx(?=.*[a-z])(?=.*\d)[a-z0-9]{16}')
        result = pattern.findall(filestr)
        if len(result) != 0:
            lock.acquire()
            for appid in result:
                print('*************find appid *************:{}/{}'.format(appid, self.packagename))
                if (appid in self.APPID_PACKAGE):
                    if self.packagename not in self.APPID_PACKAGE[appid]:
                        self.APPID_PACKAGE[appid] += [os.path.basename(self.packagename)]
                        # print('add in APPID_PACKAGE!!!now:{}'.format(self.APPID_PACKAGE[appid]))
                else:
                    self.APPID_PACKAGE[appid] = []
                    self.APPID_PACKAGE[appid] += [os.path.basename(self.packagename)]
                    # print('new in APPID_PACKAGE!!!now:{},{}'.format(self.APPID_PACKAGE[appid],self.now_package))

                if self.packagename in self.PACKAGE_APPID:
                    if appid not in self.PACKAGE_APPID[self.packagename]:
                        self.PACKAGE_APPID[self.packagename] += [appid]
                        # print('add in PACKAGE_APPID!!!now:{}'.format(self.PACKAGE_APPID[self.now_package]))
                else:
                    self.PACKAGE_APPID[self.packagename] = []
                    self.PACKAGE_APPID[self.packagename] += [appid]
                    # print('new in PACKAGE_APPID!!!now:{},{}'.format(self.PACKAGE_APPID[self.now_package],appid))
            lock.release()

    '''
    save the dic to txt
    '''
    def SaveResultToTXT(self, txtpath):
        if txtpath == "":
            print("[ERROR]save txtpath is None")
            return
        all_save = False
        if all_save:
            # appid_package
            fp = open(txtpath.replace('.txt', '-APPID_PACKAGE.txt'), 'w')
            for key, value in self.APPID_PACKAGE.items():
                fp.write(key + ":" + ",".join(value) + '\n')
            fp.close()

            # apk_appid
            fp = open(txtpath.replace('.txt', '-PACKAGE_APPID.txt'), 'w')
            for key, value in self.PACKAGE_APPID.items():
                fp.write(key + ":" + ",".join(value) + '\n')
            fp.close()

            fp = open(txtpath.replace('.txt', '-PACKAGE_APK.txt'), 'w')
            for key, value in self.PACKAGE_APK.items():
                fp.write('{}:{}\n'.format(key, value))
            fp.close()
            return None
        else:
            fp = open(txtpath.replace('.txt','-path_package_appid.txt'),'w')
            for key, value in self.PACKAGE_APPID.items():
                path = self.PACKAGE_APK[key]
                fp.write('{};{};{}\n'.format(path,key,",".join(value)))
            fp.close()
            return txtpath.replace('.txt','-path_package_appid.txt')



if __name__ == '__main__':
    start_time = time.time()
    root_dir = sys.argv[1]
    save_path = sys.argv[2]  # 一个txt文件
    process_num = int(sys.argv[3])
    myextract = Extraction(root_dir=root_dir, save_path=save_path, process_num=process_num)
    myextract.run()
    print("耗时{}分钟".format((time.time() - start_time) / 60))
