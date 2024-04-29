import socket

from typing import List

TCP_ADDRESS = '169.254.168.150'


def ncdt6500_get_data() -> List[bytes]:
    """Get the raw data as list with one byte string per channel."""

    tcp_port = 10001

    timeout = 0.4

    bytes_per_channel = 4

    channels_max = 8

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    s.settimeout(timeout)

    s.connect((TCP_ADDRESS, tcp_port))

    data = s.recv(channels_max * bytes_per_channel)

    s.close()

    if (len(data) % 4) != 0:
        raise ValueError(f"data length is {len(data)} which is not the expected multiple of 4")

    return [data[k:k + 4] for k in range(len(data) // 4)]


def ncdt6500_decode(s: bytes) -> float:
    """Convert the raw data of a channel to the according voltage.





    Data format:

    the MSB of the first byte is one, all other MSBs are zero

    bits 4 to 6 of the first byte encode the channel

    bit 3 of the first byte is high for negative numbers (not supported by this module!)

    bits 0 to 2 of the first byte and bits 0 to 6 of the others encode the value

    """

    if len(s) != 4 or not isinstance(s, bytes):
        raise ValueError('a byte string of length 4 is expected')

    start_flag = (s[0] & 0x80) > 0

    channel_id = (s[0] & 0x70) >> 4

    if channel_id == 0:

        if not start_flag:
            raise ValueError('start flag is not set although channel number is 0')

    negative_flag = (s[0] & 0x08) > 0

    if negative_flag:
        raise ValueError('negative values are not supported')

    if (s[1] & 0x80) > 0:
        raise ValueError('unexpected set MSB in 2nd byte')

    if (s[2] & 0x80) > 0:
        raise ValueError('unexpected set MSB in 3rd byte')

    if (s[3] & 0x80) > 0:
        raise ValueError('unexpected set MSB in 4th byte')

    value_int = (s[0] & 0x07) << 21

    value_int += (s[1] & 0x7F) << 14

    value_int += (s[2] & 0x7F) << 7

    value_int += (s[3] & 0x7F)

    return value_int / pow(2, 24) * 10


#if __name__ == "__main__":

#    for channel, raw_data in enumerate(ncdt6500_get_data()):
#        print(f"channel #{channel}: {ncdt6500_decode(raw_data):.6g} V")

if __name__ == "__main__":
    while True:
        for channel, raw_data in enumerate(ncdt6500_get_data()):
            s = raw_data
            value_int = 0
            value_int = (s[0] & 0xFF) << 21

            # value_int += (s[1] & 0x7F) << 14
            #
            # value_int += (s[2] & 0x7F) << 7
            #
            # value_int += (s[3] & 0x7F)

 #           print(f"{channel}, {ncdt6500_decode(raw_data):06.3g}, {hex(value_int)}, {raw_data}")
            print(f" {ncdt6500_decode(raw_data):06.3g}")
            import time
            time.sleep(1)