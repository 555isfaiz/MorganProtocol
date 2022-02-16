CPP_H_TEMPLATE = """#ifndef _ms_messages_
#define _ms_messages_

#include <vector>
#include <string>
#include "ms_types.h"

namespace msutils
{
    namespace msstream
    {
        class OutputStream;
        class InputStream;
    }
}

namespace msmessage
{
    class MessageBase
    {
    public:
        int64 id;
        virtual void write(msutils::msstream::OutputStream* out){}
        virtual void read(msutils::msstream::InputStream* in){}
        MessageBase(){}
        virtual ~MessageBase(){}
    };

$classBody

    MessageBase* GetMsgById(int64 id);
}

#endif"""

CPP_C_TEMPLATE = """#include "ms_message.h"
#include "ms_logger.h"
#include "input_stream.h"
#include "output_stream.h"

namespace msmessage
{
$writeAndRead
    //InputStream.ReadMsg need a instance of the message
    //dont want to override operator '=' for all messages
    //so return a pointer here
    //should delete message manually afterward
    MessageBase *GetMsgById(int64 id)
    {
        switch (id)
        {
$caseBody
        }

        mLogError("can't find message by Id:" << id);
        return nullptr;
    }
}"""

CLASS_BODY = """    class $name : public MessageBase 
    {
    public:
$fields
        void write(msutils::msstream::OutputStream* out) override ;
        void read(msutils::msstream::InputStream* in) override ;
        $name(){ id = $id; }
        virtual ~$name(){}
    };\n\n"""