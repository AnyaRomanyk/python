import socket, threading, json

HOST = '0.0.0.0'
PORT = 5000

clients_lock = threading.Lock()
clients = {}      
positions = {}    

def send_json(sock, obj):
    try:
        data = (json.dumps(obj) + '\n').encode('utf-8')
        sock.sendall(data)
    except Exception:
        raise

def broadcast(obj, exclude_name=None):
    """Розсилає JSON всім підключеним клієнтам, опціонально виключаючи одного."""
    dead = []
    with clients_lock:
        for name, sock in list(clients.items()):
            if name == exclude_name:
                continue
            try:
                send_json(sock, obj)
            except Exception:
                dead.append(name)
        for name in dead:
            sock = clients.pop(name, None)
            positions.pop(name, None)
            print(f"[server] видалено {name} через помилку при відправці")

def handle_client(conn, addr):
    print(f"[server] нове підключення {addr}")
    f = conn.makefile('r', encoding='utf-8')
    name = None
    try:
        line = f.readline()
        if not line:
            return
        msg = json.loads(line)
        if msg.get('type') != 'register' or not msg.get('user'):
            conn.close()
            return
        name = msg['user']
        with clients_lock:
            clients[name] = conn
        print(f"[server] {name} зареєстрований")
        broadcast({"type":"message","user":"server","text":f"{name} увійшов у чат"}, exclude_name=None)
        send_json(conn, {"type":"positions","positions":positions})

        while True:
            line = f.readline()
            if not line: 
                break
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            mtype = msg.get('type')
            if mtype == 'position':
                x = float(msg.get('x', 0))
                y = float(msg.get('y', 0))
                with clients_lock:
                    positions[msg.get('user')] = [x, y]
                broadcast({"type":"positions","positions":positions})
            elif mtype == 'message':
                broadcast({"type":"message","user":msg.get('user'), "text":msg.get('text')})
            else:
                pass
    except Exception as e:
        print(f"[server] помилка для {addr}: {e}")
    finally:
        with clients_lock:
            if name and name in clients:
                clients.pop(name, None)
            if name and name in positions:
                positions.pop(name, None)
        print(f"[server] {name or addr} відключився")
        broadcast({"type":"message","user":"server","text":f"{name or addr} вийшов"}, exclude_name=None)
        broadcast({"type":"positions","positions":positions})
        try:
            conn.close()
        except:
            pass

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"[server] слухаю на {HOST}:{PORT}")
    try:
        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[server] зупинка сервера")
    finally:
        sock.close()

if __name__ == '__main__':
    main()
