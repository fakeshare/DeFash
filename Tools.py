"""
这里面保存的是一些临时小工具
"""
import pandas as pd
import os
import shutil
def readexcel(filename):
    """
    读取excel的函数
    :param filename:
    :return:
    """
    df = pd.read_excel(filename,sheet_name="new",converters={0:str})
    height,_ = df.shape
    dirname = "F:\\Apk\\ContentShare_2_nofake"
    packagenames = []
    for i in range(height):
        packagenames.append(df.iloc[i,0]+'.apk')
    if os.path.exists(dirname+"_toprocess"):
        shutil.rmtree(dirname+"_toprocess")
    os.makedirs(dirname+"_toprocess")
    count = 0
    for file in os.listdir(dirname):
        if file in packagenames:
            # 移动文件
            dstfile = os.path.join(dirname+"_toprocess",file)
            shutil.move(os.path.join(dirname,file),dstfile)
            count += 1
            print("{} not to process, need to analysis!".format(file))

    print("scan end!",count)

def getapklist(apkdir):
    # 生成一个apkdir
    fp = open("apklist.txt",'w+')
    for file in os.listdir(apkdir):
        fp.write("{}\n".format(os.path.join(apkdir,file)))
    fp.close()

if __name__ == '__main__':
    #readexcel("D:\\Lab\MoneyMakingAPP\\Information\\AppResult\\all_app.xlsx")
    getapklist("D:\\Lab\\MoneyMakingAPP\\apks\\ToProcess")