import os
import json
import sys
from Jtemplate import *
from CPPtemplate import *
from CSharptemplate import *
from ptcdef import Message

path_ = "../MorganShootingServer/protocols/"

protocols = []

whiteList = ["MessageBase.java", "MessageSender.java", "MsgHandler.java", "MsgHandler.cs"]

javaPath = "../MorganShootingServer/src/main/java/morgan/messages/"

cppPath = "../MorganShootingServer/msg/"

csharpPath = "../../MorganClient/Assets/Scripts/connection/messages/"

genCpp = True

if sys.argv.__len__() >= 2:
    path_ = sys.argv[1]
    
if sys.argv.__len__() >= 3:
    javaPath = sys.argv[2]

if sys.argv.__len__() >= 4:
    genCpp = sys.argv[3] == "-gencpp"
    
#delete all first
for f in os.listdir(javaPath):
    if f.endswith(".java") and f not in whiteList:
        os.remove(javaPath + f)
        
if genCpp:
    for f in os.listdir(cppPath):
        if f.startswith("ms_message"):
            os.remove(cppPath + f)
        
for f in os.listdir(csharpPath):
    if f not in whiteList:
        os.remove(csharpPath + f)

#load all Protocols
for f in os.listdir(path_):
    
    if f.endswith(".ptc"):
        # content = open(f).read()
        fHandle = open(path_ + f)
        content = ""
        for r in fHandle.readlines():
            r = r.strip();
            if r.startswith('//'):
                continue
            content += r.split('//')[0]
        js = json.loads(content)
        
        for k, v in js.items():
            m = Message(v["msgId"], k)
            
            for fk, fv in v.items():
                if fk == "msgId":
                    m.field = {}
                    continue
                
                t = fv.split("$")
                m.field[t[0]] = t[1]
                
            protocols.append(m)
            Message.PROTOCOLS_ALL.append(m.name)
            print("scaned ", m.name)

constJ_classToId = ""
constJ_caseBody = ""

cpp_h_ClassBody = ""
cpp_c_writeAndRead = ""
cpp_c_getIds = ""

csharp_getMsgId = ""
csharp_caseBody = ""

index = 0
for p in protocols:
    #gen javas
    jName = javaPath + p.name + ".java"
    f = open(jName, 'w')
    javaF = p.formatJava(JAVA_TEMPLATE)
    f.write(javaF)
    f.close()
    
    #append const java
    constJ_classToId += p.getConstJavaClassToId()
    constJ_caseBody += p.getConstJavaCaseBody()
    
    if genCpp:
        #append cpps
        cpp_h_ClassBody += p.getCPPClassBody(CLASS_BODY)
        cpp_c_writeAndRead += p.getCPPWriteOut()
        cpp_c_writeAndRead += p.getCPPReadIn()
        cpp_c_getIds += p.getCPPGetIds()
    
    #gen csharp
    csName = csharpPath + p.name + ".cs"
    csF = open(csName, 'w')
    csF.write(p.formatCSharp(CSHARP_CLASS_TEMPLATE))
    csF.close()
    
    #append csharp msgbase
    csharp_getMsgId += p.getCSharpGetMsgId(index)
    csharp_caseBody += p.getCSharpCaseBody()
    index += 1

#gen const java
constFName = javaPath + "ConstMessage.java"
cf = open(constFName, 'w')
cf.write(CONST_JAVA_TEMPLATE.replace("$classToId", constJ_classToId).replace("$caseBody", constJ_caseBody))
cf.close()
      
if genCpp:      
    #gen cpp .h file
    hFName = cppPath + "ms_message.h"
    hf = open(hFName, 'w')
    hf.write(CPP_H_TEMPLATE.replace("$classBody", cpp_h_ClassBody))
    hf.close()

    #gen cpp .cpp file
    hCName = cppPath + "ms_message.cpp"
    cppF = open(hCName, 'w')
    cppF.write(CPP_C_TEMPLATE.replace("$writeAndRead", cpp_c_writeAndRead).replace("$caseBody", cpp_c_getIds))
    cppF.close()

#gen csharp MessageBase
csBase = csharpPath + "MessageBase.cs"
csbF = open(csBase, 'w')
csbF.write(CSHARP_MSGBASE_TEMPLATE.replace("$getMsgId", csharp_getMsgId).replace("$caseBody", csharp_caseBody))
csbF.close()

print("done...")