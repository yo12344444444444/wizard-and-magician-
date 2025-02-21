import socket
import pickle  # לטיפול בנתונים בינאריים

IP = '127.0.0.1'
PORT = 8821
DEFAULT_BUFFER_SIZE = 1024



def build_array_of_packets(arr_obj):
    """
    arr_obj[(rot,id,x,y,pos),...]
    get array with the objects and their coordinates
    build array with the small packets for the client

    protocol:
    (length of every packet-32 bits)
    bit 0: 1 for rotation, 0 for no rotation
    bits 1-7: type of the object(based on the json)
    bits 8-18: x coordinate
    bits 19-29: y coordinate
    bits 30-31: which rotation, 00 for no rotation
    """
    array_for_client = []
    for i in range(0, len(arr_obj), 1):

        # if true there is rotation for the object
        if arr_obj[i][0]:
            packet = f'{1:01b}'
        else:
            packet = f'{0:01b}'

        # the id
        packet += f'{ord(arr_obj[i][1]):07b}'.zfill(7)

        # the x coordination
        packet += f'{arr_obj[i][2]:011b}'.zfill(11)

        # the y coordination
        packet += f'{arr_obj[i][3]:011b}'.zfill(11)


        if packet[0:1]== '1':
            packet += f'{arr_obj[i][4]:02b}'.zfill(2)
        else:
            packet += '00'

        array_for_client.insert(i, packet)
    print(array_for_client)
    return array_for_client


def response_to_bytes(array_for_client):
    """
    gets the array of the small packets(of the protocol)
    and convert it to bytes(every small packet with 32 bits --> 4 bytes)
    """
    combined_bit_string = ''.join(array_for_client)
    number = int(combined_bit_string, 2)
    byte_value = number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')
    print(byte_value)
    return byte_value


def create_array_from_map():
    pass



def handle_client(packed_data, server_socket, client_addr):
    """
     Receives a packet from the main server (including client data + client address),
     sends the array with the small packets of the objects to the client
    """
    try:
        print(f"Handling {packed_data}  request from {client_addr}")
        arr_obj = [(False, "a", 234, 1799),(True, "b", 235,765,2)] # for test

        response = build_array_of_packets(arr_obj)
        response_in_bytes = response_to_bytes(response)
        print(client_addr)
        server_socket.sendto(response_in_bytes, client_addr)
        print(f"Response {response_in_bytes} sent to {client_addr}")

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
            packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            handle_client(packed_data, server_socket, client_addr)
        except Exception as ex:
            print(f"Client exception: {str(ex)}")



def main():
    udp_server()

if __name__ == "__main__":
    main()
