import logging
import os

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging for the game
logging.basicConfig(
    filename=os.path.join(log_dir, 'game.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure logging for the server
server_logger = logging.getLogger('server')
server_handler = logging.FileHandler(os.path.join(log_dir, 'server.log'))
server_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
server_handler.setFormatter(formatter)
server_logger.addHandler(server_handler)
