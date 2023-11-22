SERVER_IP="129.254.202.135"
CLIENT_IP="129.254.175.71"
PORT = 5020

ITERATION = 2
TEST_DURATION = 1

# True / False
#TCP_ENABLED = True
TCP_ENABLED = False
TCP_INTERVAL = 30
UDP_INTERVAL = 5

MESSAGE_SIZES = [
    1024,
    8192,
    #16384,
    #65507,
    #65536,
    #1048575,    
]

TEST_TYPES = [    
    "under-load",
    "ping-pong",
    "throughput",
]


