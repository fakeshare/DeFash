import frida  #导入frida模块
import sys
pacakge_name = sys.argv[1]
filename = "D:\\Lab\\DroidBotMine\\test_result\\" + pacakge_name + ".txt"
fp = open(filename,"a+")
fp.write("start hook\n")
fp.close()
def on_message(message,data): #js中执行send函数后要回调的函数
	fp = open(filename,"a+")
	fp.write(pacakge_name + ":\n" + message['payload'] + "\n")
	print(pacakge_name + ":\n" + message['payload'] + "\n")
	fp.close()

#得到设备并劫持进程com.example.testfrida（开始用get_usb_device函数用来获取设备，但是一直报错找不到设备，改用get_remote_device函数即可解决这个问题）
process = frida.get_usb_device().attach(pacakge_name)

jscode = """Java.perform(function(){ 
    var ShareActivity = Java.use('android.app.Activity'); //获得类
    ShareActivity.startActivity.overload("android.content.Intent").implementation = function(args){ 
        send("android.app.Activity:["+ args + "]" + "PackageName:" + args.getExtra("_mmessage_appPackage") + "  AppidContent:" + args.getExtra("_mmessage_content"))
        args = this.startActivity(args)
    }
    //case 2
    var ShareContext = Java.use('android.app.ContextImpl');
    ShareContext.startActivity.overload("android.content.Intent").implementation = function(args){
        send("android.app.Activity:["+ args + "]" + "PackageName:" + args.getExtra("_mmessage_appPackage") + "  AppidContent:" + args.getExtra("_mmessage_content"))
        args = this.startActivity(args)
    }
});
"""
#创建js脚本
script = process.create_script(jscode)
#加载回调函数，也就是js中执行send函数规定要执行的python函数
script.on('message',on_message)
#加载脚本
script.load()
sys.stdin.read()