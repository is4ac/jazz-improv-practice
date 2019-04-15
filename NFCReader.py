#! /usr/bin/env python
import re, argparse
from smartcard.System import readers


#ACS ACR122U NFC Reader
#Suprisingly, to get data from the tag, it is a handshake protocol
#You send it a command to get data back
#This command below is based on the "API Driver Manual of ACR122U NFC Contactless Smart Card Reader"
COMMAND = [0xFF, 0xCA, 0x00, 0x00, 0x00] #handshake cmd needed to initiate data transfer
DATA_PAGE = 6 # the page that the custom data is written to
waiting_for_beacon = 1 # tells read to wait
did_read_before = False # keeps track of consecutive reads so you don't double read a card
reader = None # the card reader object
args = None # script command arguments

# get all the available readers
r = readers()
print("Available readers:", r)


def stringParser(dataCurr):
#--------------String Parser--------------#
    #([85, 203, 230, 191], 144, 0) -> [85, 203, 230, 191]
    if isinstance(dataCurr, tuple):
        temp = dataCurr[0]
        code = dataCurr[1]
    #[85, 203, 230, 191] -> [85, 203, 230, 191]
    else:
        temp = dataCurr
        code = 0

    dataCurr = ''

    #[85, 203, 230, 191] -> bfe6cb55 (int to hex reversed)
    for val in temp:
        # dataCurr += (hex(int(val))).lstrip('0x') # += bf
        dataCurr += format(val, '#04x')[2:] # += bf

    # bfe6cb55 -> BFE6CB55
    dataCurr = dataCurr.upper()

    # if return is successful
    if (code == 144):
        return dataCurr


def readTag(page=DATA_PAGE):
    global did_read_before # get global variable of consecutive read flag
    readingLoop = 1
    while(readingLoop):
        try:
            connection = reader.createConnection()
            status_connection = connection.connect()
            connection.transmit(COMMAND)
            #Read command [FF, B0, 00, page, #bytes]
            resp = connection.transmit([0xFF, 0xB0, 0x00, int(page), 0x04])
            dataCurr = stringParser(resp)

            #only allows new tags to be worked so no duplicates
            if dataCurr is not None and not did_read_before:
                did_read_before = True
                print(dataCurr)
                return dataCurr
            elif did_read_before:
                continue
            else:
                print("Something went wrong. Page " + str(page))
                break
        except Exception as e:
            if waiting_for_beacon == 1:
                did_read_before = False
                continue
            else:
                readingLoop=0
                print(str(e))
                break


def writeTag(page, value):
    if type(value) != str:
        print("Value input should be a string")
        exit()
    while(1):
        if len(value) == 8:
            try:
                connection = reader.createConnection()
                status_connection = connection.connect()
                connection.transmit(COMMAND)
                WRITE_COMMAND = [0xFF, 0xD6, 0x00, int(page), 0x04, int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), int(value[6:8], 16)]
                # Let's write a page Page 9 is usually 00000000
                resp = connection.transmit(WRITE_COMMAND)
                if resp[1] == 144:
                    print("Wrote " + value + " to page " + str(page))
                    break
            except Exception:
                continue
        else:
            print("Must have a full 4 byte write value")
            break


def setup():
    global reader
    global args

    parser = argparse.ArgumentParser(description='Read / write NFC tags')
    usingreader_group = parser.add_argument_group('usingreader')
    usingreader_group.add_argument('--usingreader', nargs=1, metavar='READER_ID',
                                   help='Reader to use [0-X], default is 0')
    wait_group = parser.add_argument_group('wait')
    wait_group.add_argument('--wait', nargs=1, metavar='0|1', help='Wait for beacon before returns [0|1], default is 1')
    read_group = parser.add_argument_group('read')
    read_group.add_argument('--read', nargs='+', help='Pages to read. Can be a x-x range, or list of pages')
    write_group = parser.add_argument_group('write')
    write_group.add_argument('--write', nargs=2, metavar=('PAGE', 'DATA'), help='Page number and hex value to write.')

    args = parser.parse_args()

    # Choosing which reader to use
    if args.usingreader:
        usingreader = args.usingreader[0]
        if (int(usingreader) >= 0 and int(usingreader) <= len(r) - 1):
            reader = r[int(usingreader)]
        else:
            reader = r[0]
    else:
        reader = r[0]

    print("Using:", reader)


def readAndWriteLoop():
    global waiting_for_beacon

    # Disabling wait for answer if wait == 0
    if args.wait:
        wait = args.wait[0]
        if (int(wait) == 0):
            waiting_for_beacon = 0
        else:
            waiting_for_beacon = 1
    else:
        waiting_for_beacon = 1

    print("Using:", reader)

    # loop for convenience until user types q or Q
    user_input = input("[R]ead from or [W]rite to card or [Q]uit: ")
    while user_input != "q" and user_input != "Q":
        # read from cards loop
        if user_input == "r" or user_input == "R":
            readTag(DATA_PAGE)

        # write to cards loop
        elif user_input == "w" or user_input == "W":
            user_input = "q" # set it to quit after this inner loop is done
            data_to_write = input("Data to write (4 byte hex - 8 char string) or [Q]uit: ")

            while data_to_write != "q" and data_to_write != "Q":
                if len(data_to_write) == 8:
                    writeTag(int(DATA_PAGE), data_to_write)
                else:
                    print("Error: Must have a full 4 byte write value")

                # read from card to confirm write was successful
                # Page numbers are sent as ints, not hex, to the reader
                #readTag(DATA_PAGE)

                data_to_write = input("Data to write (4 byte hex - 8 char string) or [Q]uit: ")


def improvPrototype():
    card1 = readTag(DATA_PAGE)
    card2 = readTag(DATA_PAGE)

    print(card1, card2)


def main():
    command = input("Choose an option:\n[1] Read or write to cards\n[2] Run music improv prototype\n[Q]uit\n")

    # run the read/write loop function if they choose 1
    if command == "1":
        readAndWriteLoop()
    elif command == "2":
        improvPrototype()

# call setup
setup()

if __name__ == "__main__":
    main()

