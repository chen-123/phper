#!/usr/bin python2.6
#link: blog.phpdba.com
#date: 2015-02-19
#author: chen-123
#-*-coding:utf-8-*-

import os, time, sys
import xdrlib
import xlrd
import xlwt
import xlsxwriter

reload(sys)
sys.setdefaultencoding('utf-8')

def parse_result_file(filename) :
        """分析phpdba_system_report.sh执行脚本结果"""
        debug = True
        #debug = False
        line = True
        split_txt = True
        #split_txt = False
        split_xls = True
        #split_xls = False
        start = False
        end = False
        start_end = False
        table = True
        hostname = False
        cpu_physical = False
        cpu_virtual = False
        cpu_core = False
        cpu_hyperthreading = False
        cpu_mode = False
        mem_total = False
        raid_info = False
        disk_total = False
        os_kernel = False
        os_release = False
        os_selinux = False
        service_tag = False
        system_info = False
        system_info_txt = False
        service_ip = False
        server_arch = False
        server_list = []
        serverlist_info = True
        #serverlist_info = False
        serverlist_info_xls_filename = 'phpdba_serverlist_info.xls'
        serverlist_info_xlsx_filename = 'phpdba_serverlist_info.xlsx'
        count = 0
        l = 0
        filedir,name = os.path.split(filename)
        name,ext = os.path.splitext(name)
        filedir = os.path.join(filedir,name)
        filedir_txt = filedir+"_split"
        file_xls_path =filedir+ "_xls"

        if not os.path.exists(filedir_txt) and split_txt :
                os.mkdir(filedir_txt)

        if not os.path.exists(file_xls_path) and split_xls :
                os.mkdir(file_xls_path)

        if not ext :
                ext=".txt"

        font_xls = xlwt.Font()
        font_xls.name = 'Times New Roman'
        font_xls.colour_index = 2
        font_xls.bold = True
        # 常规字体样式 ws.write(0, 0, 'Test', style_xls)
        style_font = xlwt.XFStyle()
        style_font.font = font_xls
        al_right = xlwt.Alignment()
        al_right.horz = xlwt.Alignment.HORZ_RIGHT
        al_right.vert = xlwt.Alignment.VERT_CENTER
        style_font_right = xlwt.XFStyle()
        style_font_right.font = font_xls
        style_font_right.alignment = al_right
        # 日期样式 ws.write(1, 0, datetime.now(), style_date)
        style_date = xlwt.XFStyle()
        style_date.num_format_str = 'D-MMM-YY'
        # 字体边框样式
        font_border = xlwt.Font()
        font_border.name = 'Arial'
        font_border.colour_index = 4
        font_border.bold = True
        font_border.height = 14*0x14
        borders = xlwt.Borders()
        borders.left = 6
        borders.right = 6
        borders.top = 6
        borders.bottom = 6
        al = xlwt.Alignment()
        al.horz = xlwt.Alignment.HORZ_CENTER
        al.vert = xlwt.Alignment.VERT_CENTER
        style_fb = xlwt.XFStyle()
        style_fb.font = font_border
        style_fb.borders = borders
        style_fb.alignment = al

        try:
                rfile = open(filename, 'r')
                while line:
                        line=rfile.readline()
                        if line.strip().startswith("# 服务器信息报表") :
                                if debug :
                                        print "start"
                                start=True
                                end=False
                                start_end=True
                                count=count+1
                                if split_txt :
                                        part_filename=os.path.join(filedir_txt,name + '_' + str(count) + ext)
                                        if debug :
                                                print 'write start %s' % part_filename
                                        part_stream = open(part_filename,'wb')

                                if split_xls :
                                        xls_file_path = file_xls_path+"/"+str(count)+".xls"
                                        if debug :
                                                print 'write %s start' % xls_file_path
                                        xls_file = xlwt.Workbook(encoding='utf-8')
                                        table = xls_file.add_sheet("sheet 1",cell_overwrite_ok=True)

                        if line.strip().startswith("Hostname |") :
                                line_l = line.strip().split("|")
                                hostname = line_l[1].strip().replace(".","_")
                                xls_file_path = file_xls_path+"/"+hostname+".xls"
                        if line.strip().startswith("Processors |") :
                                line_l = line.strip().split("|")
                                cpu_info = line_l[1].replace(" ","").split(",")
                                cpu_dict = {}
                                for line_c in cpu_info :
                                        line_tmp = line_c.split("=")
                                        cpu_dict[line_tmp[0]] = line_tmp[1]

                                cpu_physical = cpu_dict['physical']
                                cpu_core = cpu_dict['cores']
                                cpu_virtual = cpu_dict['virtual']
                                cpu_hyperthreading = cpu_dict['hyperthreading']
                        elif line.strip().startswith("Models |") :
                                line_l = line.strip().split("x")
                                cpu_mode = str(line_l[1])
                        elif line.strip().startswith("IP |") :
                                line_l = line.strip().split("|")
                                ip_info = line_l[1].replace(" ","").replace("_","").split(",")
                                ip_list = []
                                for ip in ip_info :
                                        ip_tmp = ip.split(":")
                                        ip_list.append(ip_tmp[1])
                                service_ip = str(ip_list[0])
                                elif line.strip().startswith("SELinux |") :
                                line_l = line.strip().split("|")
                                os_selinux = str(line_l[1])
                        elif line.strip().startswith("Total |") :
                                line_l = line.strip().split("|")
                                mem_total = str(int(float(line_l[1][:-1]))+1)+line_l[1][-1]
                        elif line.strip().startswith("System |") :
                                line_l = line.strip().split("|")
                                system_list = line_l[1].strip().split(";")
                                #system_info = str(system_list[1].strip())+";"+str(system_list[0].strip())
                                system_info = str(system_list[1].strip())
                        elif line.strip().startswith("Service Tag |") :
                                line_l = line.strip().split("|")
                                service_tag = str(line_l[1].strip())
                        elif line.strip().startswith("Release |") :
                                line_l = line.strip().split("|")
                                os_release = str(line_l[1].strip())
                        elif line.strip().startswith("Kernel |") :
                                line_l = line.strip().split("|")
                                os_kernel = str(line_l[1].strip())
                        elif line.strip().startswith("Controller |") and ( line.strip().find("SAS") > -1 or line.strip().find("Array") > -1 or line.strip().find("RAID") > -1):
                                line_l = line.strip().split("|")
                                raid_info = str(line_l[1].strip())
                        elif line.strip().startswith("Architecture |") :
                                line_l = line.strip().split("|")
                                server_arch = str(line_l[1].strip().replace(" ",""))
                        if line.strip().startswith("# The End") :
                                if debug :
                                        print "end"
                                start=False
                                end=True
                                start_end=False
                                server_info = [count,service_ip,system_info,service_tag,cpu_mode,cpu_physical,cpu_core,cpu_virtual,cpu_hyperthreading,mem_total,raid_info,os_release,os_kernel,hostname]
                                server_list.append(server_info)

                                if split_txt :
                                        part_stream.close()
                                        if debug :
                                                print 'write %s end' % part_filename
                                if split_xls :
                                        xls_file.save(xls_file_path)
                                        if debug :
                                                print 'write %s end' % xls_file_path
                                l = 0
                      if start and start_end and not end :
                                if split_txt :
                                        part_stream.write(line)

                                wline = line.strip()
                                if split_xls :
                                        if wline.startswith("#") :
                                                table.write_merge(l,l,0,12,wline,style_fb)
                                        else :
                                                if wline.find("：") > -1 :
                                                        wline_l = wline.split("：")
                                                        table.write_merge(l,l,0,1,wline_l[0],style_font_right)
                                                        table.write_merge(l,l,2,12,wline_l[1],style_font)
                                                elif wline.find("|") > -1 :
                                                        wline_l = wline.split("|")
                                                        table.write_merge(l,l,0,1,wline_l[0],style_font_right)
                                                        table.write_merge(l,l,2,12,wline_l[1],style_font)
                                                else :
                                                        table.write_merge(l,l,0,12,wline,style_font)
                                                        #table.write(l,0,wline,style_font)
                                l += 1
                                #print line.strip()


        except Exception as e :
                print e
                print "脚本异常，请检查脚本！"

        if debug :
                print str(count)+"文件写入成功"

        if serverlist_info :
                serverlist_info_xls_wirte(serverlist_info_xls_filename,'ci123',server_list)
                serverlist_info_xlsx_autofilter_wirte(serverlist_info_xlsx_filename,'ci123',server_list)
  
def open_excel(file='system_report.xls') :
        """读取xls文件内容"""
        try:
                data = xlrd.open_workbook(file)
                return data
        except Exception,e:
                print str(e)


def excel_table_byindex(file= 'file.xls',colnameindex=0,by_index=0):
        """
           根据索引获取Excel表格中的数据
           参数:
                  file：Excel文件路径
                  colnameindex：表头列名所在行的索引
                  by_index：表的索引
        """
        data = open_excel(file)
        table = data.sheets()[by_index]
        nrows = table.nrows #行数
        ncols = table.ncols #列数
        colnames =  table.row_values(colnameindex) #某一行数据
        list =[]

        for rownum in range(1,nrows):

                row = table.row_values(rownum)
                if row:
                        app = {}
                        for i in range(len(colnames)):
                                app[colnames[i]] = row[i]
                        list.append(app)
        return list

def excel_table_byname(file= 'file.xls',colnameindex=0,by_name=u'Sheet1'):
        """
           根据索引获取Excel表格中的数据
           参数:
                  file：Excel文件路径
                  colnameindex：表头列名所在行的索引
                  by_name：Sheet1名称
        """
        data = open_excel(file)
        table = data.sheet_by_name(by_name)
        nrows = table.nrows
        colnames =  table.row_values(colnameindex)
        list =[]
        for rownum in range(1,nrows):
                row = table.row_values(rownum)
                if row:
                        app = {}
                        for i in range(len(colnames)):
                                app[colnames[i]] = row[i]
                        list.append(app)
        return list

def write_data(data, name):
        """写入数据,data为符合条件的数据列表，name表示指定的哪三个列，以此命名"""
        file = xlwt.Workbook()
        table = file.add_sheet(name,cell_overwrite_ok=True)
        l = 0   # 表示行
        for line in data:
                c = 0   # 表示一行下的列数
                for col in line:
                        table.write(l,c,line[c])
                        c += 1
                l += 1
        defatul_f = r'/root/chen-123/python/server_xls'         # 默认路径
        f = raw_input(u'请选择保存文件的路径(按回车跳过)：')
        f_name = r'/%s.xls' % name
        filepath = [defatul_f+f_name, f+f_name][f != '']
        print filepath
        file.save(filepath)
        return True
  
  def excel_table_byindex(file= 'file.xls',colnameindex=0,by_index=0):
        """
           根据索引获取Excel表格中的数据
           参数:
                  file：Excel文件路径
                  colnameindex：表头列名所在行的索引
                  by_index：表的索引
        """
        data = open_excel(file)
        table = data.sheets()[by_index]
        nrows = table.nrows #行数
        ncols = table.ncols #列数
        colnames =  table.row_values(colnameindex) #某一行数据
        list =[]

        for rownum in range(1,nrows):

                row = table.row_values(rownum)
                if row:
                        app = {}
                        for i in range(len(colnames)):
                                app[colnames[i]] = row[i]
                        list.append(app)
        return list

def excel_table_byname(file= 'file.xls',colnameindex=0,by_name=u'Sheet1'):
        """
           根据索引获取Excel表格中的数据
           参数:
                  file：Excel文件路径
                  colnameindex：表头列名所在行的索引
                  by_name：Sheet1名称
        """
        data = open_excel(file)
        table = data.sheet_by_name(by_name)
        nrows = table.nrows
        colnames =  table.row_values(colnameindex)
        list =[]
        for rownum in range(1,nrows):
                row = table.row_values(rownum)
                if row:
                        app = {}
                        for i in range(len(colnames)):
                                app[colnames[i]] = row[i]
                        list.append(app)
        return list

def write_data(data, name):
        """写入数据,data为符合条件的数据列表，name表示指定的哪三个列，以此命名"""
        file = xlwt.Workbook()
        table = file.add_sheet(name,cell_overwrite_ok=True)
        l = 0   # 表示行
        for line in data:
                c = 0   # 表示一行下的列数
                for col in line:
                        table.write(l,c,line[c])
                        c += 1
                l += 1
        defatul_f = r'/root/chen-123/python/server_xls'         # 默认路径
        f = raw_input(u'请选择保存文件的路径(按回车跳过)：')
        f_name = r'/%s.xls' % name
        filepath = [defatul_f+f_name, f+f_name][f != '']
        print filepath
        file.save(filepath)
        return True

def write_xls(file_name, sheet_name, headings, data, heading_xf, data_xfs):
        """
        汇总各项统计xls写入样式
        参数：
                file_name : xls文件名
                sheet_name : sheet名称
                headings : 标题名称列表
                data ：表格数据列表
                heading_xf : 标题样式
                data_xfs : 数据样式
        """
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet(sheet_name)
        rowx = 0
        for colx, value in enumerate(headings):
                sheet.write(rowx, colx, value, heading_xf)
        sheet.set_panes_frozen(True) # frozen headings instead of split panes
        sheet.set_horz_split_pos(rowx+1) # in general, freeze after last heading row
        sheet.set_remove_splits(True) # if user does unfreeze, don't leave a split there
        for row in data:
                rowx += 1
                for colx, value in enumerate(row):
                        #print str(value)+"长度:"+str(len(str(value)))
                        if len(str(value)) > 10 :
                                sheet.col(colx).width = 256 * (len(str(value))+1)
                        sheet.write(rowx, colx, value, data_xfs[colx])
        book.save(file_name)

def serverlist_info_xls_wirte (file_name, sheet_name, data) :
        ezxf = xlwt.easyxf
        hdngs = ['序号', 'IP', '服务器型号', '服务器序列号', 'CPU信息','CPU个数','CPU内核数','CPU线程数','CPU超频','内存大小','Raid信息', 'OS版本','OS内核','Hostname',]
        kinds =  'int service_tag text service_tag text service_tag text text text service_tag text service_tag text text'.split()
        heading_xf = ezxf('font: bold on; align: wrap on, vert centre, horiz center')
        kind_to_xf_map = {
                'date': ezxf(num_format_str='yyyy-mm-dd'),
                'int': ezxf(num_format_str='#,##0'),
                'money': ezxf('font: italic on; pattern: pattern solid, fore-colour grey25',
                    num_format_str='$#,##0.00'),
                'price': ezxf(num_format_str='#0.000000'),
                'service_tag':ezxf('font: italic on; pattern: pattern solid, fore-colour grey25'),
                'text': ezxf(),
                }
        data_xfs = [kind_to_xf_map[k] for k in kinds]
        write_xls(file_name, sheet_name, hdngs, data, heading_xf, data_xfs)

def serverlist_info_xlsx_autofilter_wirte (file_name, sheet_name, data) :
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})
        hdngs = ['服务器型号', 'CPU信息','CPU个数','CPU内核数','CPU线程数','CPU超频','内存大小', 'OS版本','OS内核']
        worksheet.set_column('A:I', 24)
        worksheet.set_row(0, 20, bold)
        worksheet.write_row('A1', hdngs)
        worksheet.autofilter('A1:I55')
        row = 1
        for row_data in (data):
                row_data_new = []
                row_data_new.append(row_data[2])
                row_data_new.append(row_data[4])
                row_data_new.append(row_data[5])
                row_data_new.append(row_data[6])
                row_data_new.append(row_data[7])
                row_data_new.append(row_data[8])
                row_data_new.append(row_data[9])
                row_data_new.append(row_data[11])
                row_data_new.append(row_data[12])
                worksheet.write_row(row, 0, row_data_new)
                row += 1

if __name__ == '__main__':
        parse_result_file("ci123_system_report_20150318_v2.txt")
        
