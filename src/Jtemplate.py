JAVA_TEMPLATE = """package morgan.messages;

import morgan.structure.serialize.InputStream;
import morgan.structure.serialize.OutputStream;

$importList

public class $name extends MessageBase {
    $fields

    public $name() {
        msgId = $msgId;
    }

    @Override
    public void writeOut(OutputStream out) {
        $writeOut
    }

    @Override
    public void readIn(InputStream in) {
        $readIn
    }
}"""

CONST_JAVA_TEMPLATE = """package morgan.messages;

import java.util.HashMap;
import java.util.Map;

public class ConstMessage implements IConstMessage {

    private static final Map<Class<? extends MessageBase>, Integer> classToId = new HashMap<>();

    static {
        initIdToClass();
    }

    private static void initIdToClass() {
$classToId
    }

    public MessageBase getEmptyMessageById(int id) {
        switch (id){
$caseBody
        }
        return null;
    }

    public int getMessageId(MessageBase m) {
        return classToId.get(m.getClass());
    }
}"""