"""
这里包含了整个调用流程
"""
from ExtractionInfo import Extraction
import time
import AppidMatch.testappid as testappid
import os

def shuffle_suspision_apk(filedir):
    suspision_list = []
    for file in os.listdir(filedir):
        fp = open(os.path.join(filedir, file), 'r')
        lines = fp.readlines()
        fp.close()
        state = "continue"
        one_path = []
        for line in lines:
            if state == "continue":
                if line.strip() == 'path:':  # 扫描到了一条路径
                    state = "path"
            elif state == "path":
                if line.strip() == 'path:':
                    state = "path"
                    if ("android.content.Context" not in one_path[-1]) or ("(Native)" in one_path[-1]):  # 可疑的app
                        suspision_list.append(os.path.join(filedir, file.replace('.txt', '')))
                        break
                    one_path = []
                one_path.append(line)
    print(suspision_list)


def getapklist(apkdir):
    fp = open("apklist.txt", 'w+')
    for file in os.listdir(apkdir):
        fp.write("{}\n".format(os.path.join(apkdir, file)))
    print("build a apklist!")


if __name__ == '__main__':
    # 运行之前需要：连接测试手机、手机上登录微信、打开firda服务器、
    apkdir = "D:\\Lab\\MoneyMakingAPP\\apks\\ToProcess"
    # ExtractionInfo提取应用的appid
    print("[1-1] 开始appid分析")
    start_time = time.time()
    save_path = "D:\\Lab\\MoneyMakingAPP\\Tool\\ProcessApk\\toprocess.txt"
    process_num = 5
    myextract = Extraction(root_dir=apkdir, save_path=save_path, process_num=process_num)
    savefile = myextract.run()
    print("ExtractionInfo提取应用的appid耗时{}分钟".format((time.time() - start_time) / 60))
    print("结果保存在{}中".format(savefile))
    # 使用frida进行第一阶段自动化测试,得到一个可疑的apklist（里面每一行是一个apk地址）
    print("[1-2] 使用frida")
    suspision_apk_list1 = testappid.run(savefile)

    # eclipse静态分析
    print("[2] 开始soot静态分析")
    # 提取apk得到一个apklist
    getapklist(apkdir)
    os.system(
        "cd D:\Lab\MoneyMakingAPP\Tool\ProcessApk\StaticAnalysis_jar & java -version & java -jar LsyStaticAnalysis_13_win.jar")
    # 处理结果筛出异常的apk
    suspision_apk_list2 = shuffle_suspision_apk("D:\\Lab\\MoneyMakingAPP\\apks\\ToProcess_result")

    print("可疑的app分别如下：\n{}\n{}".format(suspision_apk_list1, suspision_apk_list2))
    set_1 = set(suspision_apk_list1)
    set_2 = set(suspision_apk_list2)
    all_suspision_app = set.union(set_1, set_2)
    print("所有的可疑app为：\n", all_suspision_app)

