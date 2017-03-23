import db
import sqlalchemy as sa

def subscribe(chat_id, node):
    node_exists = db.engine.execute(
        sa.select(
            (sa.exists(db.nodes.select().where(db.nodes.c.id==node)),)
        )
    ).fetchone()[0]
    print(node_exists)

    if not node_exists:
        db.nodes.insert().values((node, None, None, None)).execute()

    subscription_exists = db.engine.execute(
        sa.select(
            (sa.exists(db.subscriptions.select().where(
                sa.and_(
                    db.subscriptions.c.chat_id==chat_id,
                    db.subscriptions.c.node==node
                )
            )),)

        )
    ).fetchone()[0]

    print(subscription_exists)

    if not subscription_exists:
        db.subscriptions.insert().values((None, chat_id, node, True)).execute()


def unsubscribe(chat_id, node):
    db.subscriptions.delete().where(
        sa.and_(
            db.subscriptions.c.chat_id==chat_id,
            db.subscriptions.c.node==node
        )
    ).execute()

def unsubscribe_all(chat_id):
    db.subscriptions.delete().where(
        db.subscriptions.c.chat_id==chat_id,
    ).execute()

def get_subscriptions(chat_id):
    rows = db.subscriptions.select().where(db.subscriptions.c.chat_id==chat_id).execute()
    subs = [tuple(row) for row in rows]
    return subs

def get_subscribed_users(node_id):
    rows = db.subscriptions.select().where(db.subscriptions.c.node==node_id).execute()
    return [row.chat_id for row in rows]

