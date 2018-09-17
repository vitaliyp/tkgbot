from tkgbot.tkgbot import ShowCommand
from tkgbot.models import NodeType
from tkgbot.testutils import objectview

def test__get_node_description():
    c = ShowCommand()
    
    assert c._get_node_description('') == '', 'Empty description for empty node_id'
    assert c._get_node_description(1) == '', 'Empty description for positive values'
    assert c._get_node_description(100) == '', 'Empty description for positive values'

    assert c._get_node_description(NodeType.SECTION) == '', 'Empty description for valid but not added values'
    assert c._get_node_description(NodeType.OTHER) == '', 'Empty description for valid but not added values'

    assert len(c._get_node_description(NodeType.ALL)) > 0, 'Non empty description for valid values'
    assert len(c._get_node_description(NodeType.EVENT)) > 0, 'Non empty description for valid values'
    assert len(c._get_node_description(NodeType.MATERIAL)) > 0, 'Non empty description for valid values'
    assert len(c._get_node_description(NodeType.NEWS)) > 0, 'Non empty description for valid values'
    assert len(c._get_node_description(NodeType.TOPIC)) > 0, 'Non empty description for valid values'

def test__get_node_str():
    c = ShowCommand()
    
    assert c._get_node_str('') == '', 'Empty value for empty node_id'
    assert c._get_node_str(1) == '', 'Empty value for positive values'
    assert c._get_node_str(100) == '', 'Empty value for positive values'
    
    assert c._get_node_str(NodeType.SECTION) == '', 'Empty value for valid but not added values'
    assert c._get_node_str(NodeType.OTHER) == '', 'Empty value for valid but not added values'

    assert len(c._get_node_str(NodeType.ALL)) > 0, 'Non empty value for valid values'
    assert len(c._get_node_str(NodeType.EVENT)) > 0, 'Non empty value for valid values'
    assert len(c._get_node_str(NodeType.MATERIAL)) > 0, 'Non empty value for valid values'
    assert len(c._get_node_str(NodeType.NEWS)) > 0, 'Non empty value for valid values'
    assert len(c._get_node_str(NodeType.TOPIC)) > 0, 'Non empty value for valid values'

def test__build_subscription_info():
    c = ShowCommand()

    def empty_sub():
        return objectview({
            'node_id' : '',
            'node' : objectview({
                'name' : ''
            }),
            'exception' : False,
            'no_comments' : False,
            'no_replies' : False,

        })

    sub = empty_sub()
    sub.node_id = 12
    assert c._build_subscription_info(sub) == r'  - \[`12`]', 'Display node_id if numerical value provided'

    sub = empty_sub()
    sub.node_id = 'all'
    assert c._build_subscription_info(sub) == r'  - \[`all`]', 'Display node_id if text value provided'

    sub = empty_sub()
    sub.node_id = 100
    sub.node.name = "Epic"
    assert c._build_subscription_info(sub) == r'  - "Epic" \[`100`]', 'Display name when provided'

    sub = empty_sub()
    sub.node_id = 100
    sub.node.name = "Epic"
    sub.no_comments = True
    assert len(c._build_subscription_info(sub)) > len(r'  - "Epic" \[`100`]'), 'Display additional info for not excluded subs'

    sub = empty_sub()
    sub.node_id = 100
    sub.node.name = "Epic"
    sub.no_replies = True
    assert len(c._build_subscription_info(sub)) > len(r'  - "Epic" \[`100`]'), 'Display additional info for not excluded subs'