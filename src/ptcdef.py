class Message:
    
    msgId = 0
    name = ""
    field = None
    PROTOCOLS_ALL = []
    
    def __init__(self, msgId, name):
        self.msgId = msgId
        self.name = name
        
    def getJavaType(self, ptcType):
        if ptcType == "string":
            return "String"
        if ptcType == "bool":
            return "boolean"
        return ptcType
    
    def getConstJavaClassToId(self):
        return "        classToId.put({}.class, {});\n".format(self.name, self.msgId)
    
    def getConstJavaCaseBody(self):
        return "            case {}:\n                return new {}();\n".format(self.msgId, self.name)
    
    def formatJava(self, template):
        template = template.replace("$name", self.name)
        template = template.replace("$msgId", str(self.msgId))
        
        importList = ""
        fields = ""
        writeOut = ""
        readIn = ""
        
        i = 0
        for k, v in self.field.items():
            #fields
            if v.startswith("[") and v.endswith("]"):
                importList = "import java.util.ArrayList;\nimport java.util.List;"
                f = ("" if i == 0 else "    ") + "public List<" + self.getJavaType(v).replace("[", "").replace("]", "") + "> " + k + " = new ArrayList<>();\n"
                fields += f
            else:
                f = ("" if i == 0 else "    ") + "public " + self.getJavaType(v) + " " + k + ";\n"
                fields += f

            #output and input
            writeOut += ("" if i == 0 else "        ") + "out.write({});\n".format(k)
            readIn += ("" if i == 0 else "        ") + "{} = in.read();\n".format(k)
            i += 1
        
        template = template.replace("$importList", importList)
        template = template.replace("$fields", fields)
        template = template.replace("$writeOut", writeOut)
        template = template.replace("$readIn", readIn)
        
        return template
    
    def getCPPType(self, ptcType):
        if ptcType == "int":
            return "int32"
        if ptcType == "long":
            return "int64"
        if ptcType == "string":
            return "std::string"
        return ptcType
        
    def getCPPClassBody(self, template):
        fields = ""
        for k, v in self.field.items():
            if v.startswith("[") and v.endswith("]"):
                fields += "        std::vector<" + self.getCPPType(v.replace("[", "").replace("]", "")) + "> " + k + ";\n"
            else:
                fields += "        " + self.getCPPType(v) + " " + k + ";\n"
        return template.replace("$fields", fields).replace("$name", self.name).replace("$id", str(self.msgId))
        
    def getCPPReadIn(self):
        ret = """    void $name::read(STREAM::InputStream* in)
    {
$body
    }\n\n"""
        body = ""
        for field, fType in self.field.items():
            if fType.startswith("[") and fType.endswith("]"):
                realT = fType.replace("[", "").replace("]", "")
                res = """        auto fb = in->readV(1)[0];
        int32 length = in->ResolveNumber((fb & 0xF0) >> 4);
        for (int32 i = 0; i < length; i++)
        {
            $field.push_back(*reinterpret_cast<$realT*>(in->ReadMsg()));
        }\n""".replace("$field", field).replace("$realT", realT)
                body +=  res
            elif fType != "string":
                if fType not in Message.PROTOCOLS_ALL:
                    body += "        " + field + " = in->Read" + self.getCPPType(fType).capitalize() + "();\n"
                else:
                    body += "        " + field + " = *reinterpret_cast<$Type*>(in->ReadMsg());\n".replace("$Type", fType)
            else:
                body +=  "        " + field + " = in->ReadString();\n"
        
        return ret.replace("$body", body).replace("$name", self.name)
    
    def getCPPWriteOut(self):
        ret = """    void $name::write(STREAM::OutputStream* out)
    {
$body
    }\n\n"""
        body = ""
        for field, fType in self.field.items():
            if fType.startswith("[") and fType.endswith("]"):
                res = """        auto b = out->ResolveNumber($field.size());
        out->WriteTandVL(STREAM::TYPE_LIST, b[0], b + 1);
        for (auto t : $field)
        {
            out->write($ifAndt);
        }""".replace("$field", field).replace("$ifAnd", "" if fType.replace("[", "").replace("]", "") not in Message.PROTOCOLS_ALL else "&")
                body += res
            elif fType in Message.PROTOCOLS_ALL:
                body += "        out->write(&" + field + ");\n"
            else:
                body += "        out->write(" + field + ");\n"

        return ret.replace("$body", body).replace("$name", self.name)
    
    def getCPPGetIds(self):
        return """            case $id:
            {
                msmessage::$name *$lowerCase = new msmessage::$name;
                return $lowerCase;
            }\n\n""".replace("$id", str(self.msgId)).replace("$name", self.name).replace("$lowerCase", self.name.lower())

    def formatCSharp(self, template):
        fields = ""
        writeOut = ""
        readIn = ""
        
        for k, v in self.field.items():
            if v.startswith("[") and v.endswith("]"):
                realT = v.replace("[", "").replace("]", "")
                if realT in Message.PROTOCOLS_ALL:
                    fields += "    public List<MSMessageBase> " + k + " = new List<MSMessageBase>();  //" + realT + "\n"
                    writeOut += "        output.write<MSMessageBase>({});\n".format(k)
                    readIn += "        {} = input.read<List<MSMessageBase>>();\n".format(k)
                else:
                    fields += "    public List<{}>".format(realT) + k + " = new List<{}>();\n".format(realT)
                    writeOut += "        output.write<{}>({});\n".format(v, k)
                    readIn += "        {} = input.read<List<{}>>();\n".format(k, v)
            else:
                fields += "    public {} {};\n".format(v, k)
                writeOut += "        output.write<{}>({});\n".format(v, k)
                readIn += "        {} = input.read<{}>();\n".format(k, v)
                
        return template.replace("$name", self.name).replace("$id", str(self.msgId)).replace("$fields", fields).replace("$writeOut", writeOut).replace("$readIn", readIn)

    def getCSharpGetMsgId(self, index):
        ret = "        "
        if index == 0:
            ret += "if "
        else:
            ret += "else if"
        
        ret += """ (msg is $name)
        {
            return $id;
        }\n""".replace("$name", self.name).replace("$id", str(self.msgId))
        return ret

    def getCSharpCaseBody(self):
        return """            case $id:
                msg = new $name();
                break;\n\n""".replace("$id", str(self.msgId)).replace("$name", self.name)
                