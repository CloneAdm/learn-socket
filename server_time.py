import time
import socket

port = 6633


def send_answer(conn, status="200 OK", typ="text/plain; charset=utf-8", data=""):
    data = data.encode("utf-8")
    conn.send(b"HTTP/1.1 " + status.encode("utf-8") + b"\r\n")
    conn.send(b"Server: simplehttp\r\n")
    conn.send(b"Connection: close\r\n")
    conn.send(b"Content-Type: " + typ.encode("utf-8") + b"\r\n")
    conn.send(b"Content-Length: " + str(len(data)).encode() + b"\r\n")
    conn.send(b"\r\n")  # после пустой строки в HTTP начинаются данные
    conn.send(data)


def parse(conn, addr):  # обработка соединения в отдельной функции
    data = b""

    while not b"\r\n" in data:  # ждём первую строку
        tmp = conn.recv(1024)
        if not tmp:  # сокет закрыли, пустой объект
            break
        else:
            data += tmp

    if not data:  # данные не пришли
        return  # не обрабатываем

    udata = data.decode("utf-8")
    udata = udata.split("\r\n", 1)[0]  # берём только первую строку - там главное. Далее заголовки, сейчас не нужны
    method, address, protocol = udata.split(" ", 2)  # разбиваем по пробелам нашу строку

    if method != "GET" or address != "/time.html":
        send_answer(conn, status="404 Not Found", data="Не найдено")
        return

    answer = f"""\
    <!DOCTYPE html>
    <html><head><title>Время</title></head><body><h1>
    {time.strftime("%H:%M:%S %d.%m.%Y")}
    </h1></body></html>"""

    send_answer(conn, typ="text/html; charset=utf-8", data=answer)


sock = socket.socket()
sock.bind(("", port))
sock.listen(5)

try:
    while True:  # работаем постоянно
        conn, addr = sock.accept()
        print("New connection from " + addr[0])
        try:
            parse(conn, addr)
        except:
            send_answer(conn, "500 Internal Server Error", data="Ошибка")
        finally:
            # так при любой ошибке
            # сокет закроем корректно
            conn.close()
finally:
    sock.close()
    # так при возникновении любой ошибки сокет
    # всегда закроется корректно и будет всё хорошо
