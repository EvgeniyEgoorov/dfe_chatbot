import sys
from configparser import ConfigParser
import logging
import random
import time
from colorama import Fore

from df_db_connector import connector_factory
from df_engine.core import Context, Actor
from scenario import script


logger = logging.getLogger(__name__)

parser = ConfigParser()
parser.read("config.ini")

DB_NAME = parser.get("db", "db_name")
DB_HOST = parser.get("db", "db_host")
DB_PORT = parser.get("db", "db_port")
DB_LOGIN = parser.get("db", "db_login")
DB_PASSWORD = parser.get("db", "db_password")

db = connector_factory(  # try except?
    f"postgresql://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


ACTOR = Actor(
    script,
    start_label=("root", "start_node"),
    fallback_label=("root", "fallback_node"),
)


def turn_handler(
    in_request: str,
    user_id: str,
    actor: Actor,
):
    ctx = db.get(user_id, Context(id=user_id))
    ctx.add_request(in_request)
    ctx = actor(ctx)
    out_response = ctx.last_response
    db[user_id] = ctx

    logging.info(
        f"{Fore.WHITE}Bot: {Fore.GREEN}{out_response} \n{Fore.WHITE}<<hint>> I'm here: {ctx.last_label}"
    )
    return out_response, ctx


def run_interactive_mode(actor, user_id):
    while True:
        time.sleep(0.1)  # added to avoid output overlapping
        in_request = input("Me: ")
        turn_handler(in_request, user_id, actor)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )
    if len(sys.argv) > 1:
        USER_ID = sys.argv[1]
    else:
        USER_ID = str(random.randint(0, 100))
    logging.info(USER_ID)
    run_interactive_mode(ACTOR, USER_ID)
