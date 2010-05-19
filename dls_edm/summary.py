#!/bin/env python
usage = """usage: ./%prog [options] <xls_file> <output_file>

This script generates an edm summary screen for temperatures, waterflows or motors
given a table_dict """

import sys, os
from optparse import OptionParser
from edmTable import *
from edmObject import *
from titlebar import Titlebar
from common import label, rd, embed, tooltip, rd_visible, can_optimise, \
                   shell_visible

def Summary(row_dicts,domain="$(dom)",vtype="temp",aspectratio=0.65):
    """Take a list of dicts, and make a summary screen out of them. each dict in
    row_dict should represent the line on a spreadsheet, ie have NAME,
    DESCRIPTION, NTEMP, NFLOW, NMOTOR, EDM_MACROS, FILE defined.
    e.g dict["NAME"] = S1, dict["NFLOW"]=1. domain should be the domain that
    will appear in the titlebar. vtype is "temp", "flow" or "motor". aspectratio is
    the aspectratio of the resulting screen"""
    screen = EdmObject("Screen")
    if vtype == "motor":
        table = EdmTable(yborder=0)
    else:
        table = EdmTable()
    screen.addObject(table)
    if vtype == "temp":
        headerText = "Temperature Summary"
    elif vtype =="flow":
        headerText = "Water Flow Summary"
    else:
        headerText = "Motion Summary"
    done_devices = []
    nvtype = "N"+vtype.upper()
    totalv = 0
    maxv = 0
    nvtypev = 0
    height = 0
    init_flag = True
    
    # find the table height in number of blocks
    for dict in row_dicts:
        totalv = totalv + int(dict[nvtype])
        maxv = max(maxv,int(dict[nvtype]))
    height = max(int(totalv**aspectratio)+2,maxv+2)

    for dict in row_dicts:
        # set the number of cells to be filled in
        nvtypev = int(dict[nvtype])
        if nvtypev > 0:
            p = dict["P"]
            skip_list = []
            # a flow can be used for more than one device. Only show it for
            # the first device it appears in
            for i in range(int(dict["NFLOW"])):
                wn = dict["W"]+dict["W"+str(i+1)]
                if wn in done_devices:
                    skip_list.append(wn)
                else:
                    done_devices.append(wn)
            # only add device text if there are more cells to write
            if vtype !="flow" or not len(skip_list) == int(dict["NFLOW"]):
                i = 1    
                if init_flag:
                    # don't make an extra cell at the start
                    init_flag = False
                else:
                    # if there is no room in current column, force a new one
                    table.nextCell(max_y=height-nvtypev-1)
                # write the device header
                dfilename = dict["FILE"]  
                if can_optimise(dfilename):
                    dfilename=dict["P"]+"-device-screen-0.edl"
                if vtype=="motor":
                    xs = 110
                    ob = shell_visible(0,0,xs,20,"Home "+dict["NAME"],
                            'gnome-terminal --disable-factory --hide-menubar -t "Home %s" -e "$(dom)-motorhome.py %s"'
                            %(dict["NAME"],dict["NAME"]) )
                    table.addObject(ob,xoff=xs)
                    xoff = -xs                    
                else:
                    xoff = 0
                    xs = 90
                table.addObject(rd(0,0,xs,20,dfilename,dict["EDM_MACROS"]),xoff=xoff)
                table.addObject(tooltip(0,0,xs,20,dict["DESCRIPTION"]),xoff=xoff)
                lab = label(0,0,xs,20,dict["NAME"],"center")
                lab["font"]=quoteString("arial-bold-r-14.0")
                table.addObject(lab,xoff=xoff)                    
                table.nextCell()
                # write the cells
                while not i > nvtypev:
                    if vtype=="temp":
                        ob = embed(0,0,90,20,"BLGui-temp-embed","label=T"+\
                                   str(i)+",temp="+p+dict["T"+str(i)]+",P="+\
                                   dict["P"])
                    elif vtype=="flow":
                        ob = embed(0,0,90,20,"BLGui-flow-embed","flow="+\
                                   dict["W"]+dict["W"+str(i)]+",label=Flow "+\
                                   str(i)+",P="+dict["P"])
                    else:
                        # Strip off the colon from the motor name
                        motorLabel = dict["M"+str(i)]
                        motorLabel = motorLabel[1:]
                        ob = embed(0,0,223,22,"BLGui-motorSummary-embed","motor="+\
                                   dict["P"]+dict["M"+str(i)]+",label="+\
                                   motorLabel)
                    table.addObject(ob)
                    table.nextCell()
                    i += 1

    # create screen
    if vtype=="motor":
        ob = embed(0,0,223,22,"BLGui-motor-key","a=b")
        table.addObject(ob)
    else:
        interlock = rd_visible(0,0,90,20,"Interlocks",domain+"-interlocks")
        interlock["fgColor"] = interlock.Colour["Related display"]
        table.addObject(interlock)
    screen.autofitDimensions()
    table.ungroup()
    Titlebar(screen,button="text",button_text=domain,header="text",\
             header_text=headerText,tooltip="generic-tooltip",title=headerText)
    return screen

# commented out as it requires BLgen
##def cl_summary():
##    from excel_parser import ExcelHandler
##    from table_dict import gen_gui_table
##    parser = OptionParser(usage)
##    (options, args) = parser.parse_args()
##    assert len(args)==2, "Incorrect number of arguments"
##    data = ExcelHandler(args[0])
##    for name, table in data.tables:
##        if name.replace("!","_").replace("-","_")=="_GUI_MO":
##            if "TEMP" in args[1].upper():
##                vtype = "temp"
##           else:
##               vtype = "flow"
##           # generate table_dict
##           table_dict = gen_gui_table(table,name)
##           # generate a screen for each subst file
##           screen = Summary([ table_dict.device_dict[d] \
##                              for d in table_dict.devices ],"$(dom)",vtype)
##           open(args[1],"w").write(screen.read())
##           print "Vacuum screen written to: "+args[1]

if __name__=="__main__":
    cl_summary()