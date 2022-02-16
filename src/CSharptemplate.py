CSHARP_CLASS_TEMPLATE = """using System.Collections.Generic;
public class $name : MSMessageBase
{
$fields
    public $name()
    {
        id = $id;
    }

    public override void write(OutputStream output)
    {
$writeOut
    }

    public override void read(InputStream input)
    {
$readIn
    }
}"""

CSHARP_MSGBASE_TEMPLATE = """public abstract class MSMessageBase
{
    protected int id;

    public abstract void write(OutputStream output);
    public abstract void read(InputStream input);

    public static int GetMessageId(MSMessageBase msg)
    {
$getMsgId
        return 0;
    }

    public static MSMessageBase GetEmptyMessageById(int id)
    {
        MSMessageBase msg = null;
        switch (id)
        {
$caseBody
            default:
                break;
        }
        return msg;
    }
}"""