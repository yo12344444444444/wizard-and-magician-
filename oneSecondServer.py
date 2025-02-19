import socket
import pickle  # לטיפול בנתונים בינאריים

IP = '127.0.0.1'
PORT = 8821
DEFAULT_BUFFER_SIZE = 30


def build_array_of_packets(arr_obj):
    """
    arr_obj[(rot,id,x,y,pos),...]
    get array with the objects and their coordinates
    build array with the small packets for the client

    protocol: # add the rotation of every object with rotation?
    bit 0: 1 for rotation, 0 for no rotation
    bits 1-6: type of the object(based on the json)
    bits 7-17: x coordinate
    bits 18-28: y coordinate
    bits 29-30: which rotation
    """
    array_for_client = []
    for i in range(0, len(arr_obj), 1):
        packet = ""

        # if true there is rotation for the object
        if arr_obj[i][0]:
            packet += b"1"
        else:
            packet += b"0"

        # the id
        packet += bin(ord(arr_obj[i][1])).zfill(6) #remove the 0b from the start?

        # the x coordination
        packet += bin(arr_obj[i][2]).zfill(11)

        # the y coordination
        packet += bin(arr_obj[i][3]).zfill(11)

        if packet[:1:]== b"1":
            packet += bin(arr_obj[i][4]).zfill(2)

        array_for_client[i] = packet
    return array_for_client



def handle_client(packed_data, server_socket):
    """
     Receives a packet from the main server (including client data + client address),
     sends the array with the small packets of the objects to the client
    """
    try:
        data, client_addr = pickle.loads(packed_data)
        print(f"Handling request from {client_addr}")
        arr_obj = [(False, "a", 234, 1799),(True, "b", 235,765)]
        response = build_array_of_packets(arr_obj)
        server_socket.sendto(response, client_addr)
        print(f"Response {response} sent to {client_addr}")

    except Exception as ex:
        print(f"Error handling client: {str(ex)}")



def udp_server():
    """
    listen to requests from the main server and calls the
    function that sends an answer to the client ^-^
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f"Secondary server listening on {IP}:{PORT}")

    while True:
        try:
            packed_data, _ = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            handle_client(packed_data, server_socket)
        except Exception as ex:
            print(f"Client exception: {str(ex)}")



def main():
    udp_server()

if __name__ == "__main__":
    main()
