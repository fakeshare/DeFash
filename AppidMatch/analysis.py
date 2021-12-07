import xlwt

def Analysis():
	fp = open("result.txt",'r',encoding='utf-8')
	lines = fp.readlines()
	fp.close()
	dic = {}
	info_format = ["appName","can't jump to wx","由于当前你分享的内容涉嫌违法违规，无法分享到微信",
	"由于用户投诉，当前你分享的内容存在诱导分享行为，无法分享到微信","由于不支持的分享类型，无法分享到微信",
	"the content you sharing have security risk.","share_and_return_error!"]
	for line in lines:
		packagename = line.split(":")[0].split(",")[0].split("[")[1]
		appid = line.split(":")[0].split(",")[1].split("]")[0]
		info = line.split(":")[1].strip()
		if packagename not in dic.keys():
			dic[packagename] = {}
		dic[packagename][appid] = info
	print(dic)
	# 写入表格
	wb = xlwt.Workbook(encoding='utf-8')
	sheet1 = wb.add_sheet('share state')
	sheet1.write(0,0,"packagename")
	for i in range(len(info_format)):
		sheet1.write(0,i+1,info_format[i])
	row = 1
	for key,value in dic.items():
		sheet1.write(row,0,key)
		temp_write = [""]*len(info_format)
		for appid,info in value.items():
			if info in info_format:
				temp_write[info_format.index(info)] += (appid+",")
			else:
				temp_write[0] += (info+"("+appid+")")
		for index in range(len(temp_write)):
			print("write to {},{} ".format(row,index+1,temp_write[index]))
			sheet1.write(row,index+1,temp_write[index])
		row += 1
	wb.save("share_appid_packagename_paopaoche.xls")

if __name__ == '__main__':
	Analysis()	



