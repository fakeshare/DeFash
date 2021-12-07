'''
流程如下：
[输入为apk目录]
循环 each apk
    1. 解包分析apk中包含的appid以及apk本身的packagename(暂时先用已有的)
    2. 自动安装apk到手机上
    循环 each appid-packagename：
        1）开启firda,hook我自己的ShareDemo
        2）脚本为将appid和packagename改成1.步检测到的
        3）看分享是否成功（进入到了朋友选择界面）
    3. 卸载apk
'''

import uiautomator2 as u2
import subprocess
import time
import os

def share_and_return():
    appName = ""
    try:
        d = u2.connect_usb("FA7760302843")
        d.press("home")
        #d(resourceId="com.google.android.apps.nexuslauncher:id/all_apps_handle").click()
        print("click home")
        time.sleep(1)
        d(text="ShareSecurity").click()
        #d(resourceId="com.google.android.apps.nexuslauncher:id/icon", text="ShareSecurity").click()
        print("click share app")
        time.sleep(1)
        d(resourceId="com.example.ShareSecurity:id/button3").click()
        print("click share")
        # 下面为微信界面的操作
        time.sleep(2) # 等待2秒
        print(d.app_current())
        if d.app_current()['activity'] == 'com.tencent.mm.ui.transmit.SelectConversationUI':
            d(resourceId="com.tencent.mm:id/gbv", text="文件传输助手").click()
            print("click file input")
            d(resourceId="com.tencent.mm:id/doz").click()
            print("click file share")
            appName = d(resourceId="com.tencent.mm:id/dom").get_text()
            appName = appName.replace("返回","")
            d(resourceId="com.tencent.mm:id/dom").click()
            print("click yes")
            time.sleep(2)
            d.press("home")
            print("click home")
        elif d.app_current()['activity'] == 'com.tencent.mm.plugin.base.stub.WXEntryActivity':
            appName = d(resourceId="com.tencent.mm:id/fgw").get_text()
            print(appName)
            d.press("back")
            print("click back")
            d.press("home")
            print("click home")
        else:
            time.sleep(1)
            d.press("home")
            print("click home")
            appName = "can't jump to wx"
            print("share error! [can't jump to wx]")
    except Exception as e:
        print("share_and_return_error!")
        appName = "share_and_return_error!"
    return appName

def run(filename):
    # 读取apk名称与packagename
    print("start frida!")
    info_format = ["can't jump to wx", "由于当前你分享的内容涉嫌违法违规，无法分享到微信",
                   "由于用户投诉，当前你分享的内容存在诱导分享行为，无法分享到微信", "由于不支持的分享类型，无法分享到微信",
                   "the content you sharing have security risk.", "share_and_return_error!"]
    resultfile = "testappid_result.txt"
    fp_w = open(resultfile, 'w+', encoding='utf-8')
    fp = open(filename,'r')
    lines = fp.readlines()
    fp.close()
    suspision_app = []
    for line in lines:
        print(line)
        apkpath = line.split(";")[0]
        print(apkpath)
        suspision = True
        if os.path.exists(apkpath):
            # 安装apk
            print("install apk {}".format(apkpath))
            shell1 = "adb install " + apkpath
            os.system(shell1)
            packagename = line.split(";")[1]
            appid_str = line.split(";")[2].strip()
            appids = appid_str.split(",")
            # 使用papckagename-appid对进行分享
            for appid in appids:
                # 写入temp_appid_packagename中
                shell2 = "python AppidMatch\\hook.py " + packagename + " " + appid
                child = subprocess.Popen(shell2)    # frida开始hook
                print("start hook !!!   {}".format(shell2))
                appName = share_and_return()
                if appName not in info_format:  # 表示包含有能够正常分享的appid,不认为可疑,则不再继续分析
                    suspision = False
                    break
                child.kill()    # 终止firda的hook
                # 记录结果
                fp_w.write("[{},{}]:{}\n".format(packagename, appid, appName))
                print("end hook !!!")
            # 卸载app
            shell3 = "adb uninstall " + packagename
            os.system(shell3)
        if suspision:
            suspision_app.append(apkpath)
    fp.close()
    return suspision_app
    
if __name__ == '__main__':
    run()