import os
import shutil
class Reverse:
    def __init__(self,apkfile,reversedir=""):
        self.apkfile = apkfile
        self.isdir = os.path.dirname(self.apkfile)
        self.apkname = os.path.basename(self.apkfile)
        if reversedir == "":
            _reverse = "none"
            if len(self.apkname) > 10:
                _reverse = self.apkname[:10]
            else:
                _reverse = self.apkname
            self.reversedir = os.path.join(self.isdir, _reverse+'_reverse')
        else:
            self.reversedir = reversedir
        if os.path.exists(self.reversedir):
            shutil.rmtree(self.reversedir)
        os.makedirs(self.reversedir)
        print("初始化{}完成".format(self.reversedir))

    def apktool(self):
        if self.apkfile.endswith('.apk'):
            apktool_dst = os.path.join(self.reversedir,'apktool')
            try:
                shell = 'apktool d "' + self.apkfile + '" -o "' + apktool_dst + '"'
                print(shell)
                os.system(shell)
            except:
                print("[ERROR] apk reverse failed! {}".format(self.apkfile))
            else:
                return True
        elif self.apkfile.endswith('.xapk'):
            unzip_dst = os.path.join(self.reversedir,'xapk_unzip')
            #unzip_dst = os.path.join('D:\\Lab\\MoneyMakingAPP\\Tool\\ProcessApk\\temp_reverse\\test')
            try:
                shell = '7z x "' + self.apkfile + '" -o"' + unzip_dst + '"'
                print(shell)
                os.system(shell)
                for file in os.listdir(unzip_dst):
                    if file.endswith('.apk'):
                        apkfile = os.path.join(unzip_dst, file)
                        apktool_dst = os.path.join(self.reversedir, 'apktool')
                        shell = 'apktool d "' + apkfile + '" -o "' + apktool_dst + '"'
                        print(shell)
                        os.system(shell)
                        # 如果里面有smali文件，则说明是主包,那其它的都不要了
                        if not os.path.exists(os.path.join(apktool_dst,'smali')):
                            shutil.rmtree(apktool_dst)
                        else:
                            return True
            except:
                print("[ERROR] xapk reverse failed!{}".format(self.apkfile))
            else:
                return True
        else:
            print('无效的文件名 {}'.format(self.apkfile))
        return False