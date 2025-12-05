import socket, threading, json, sys

SERVER_HOST = '127.0.0.1'   
SERVER_PORT = 5000

def send_json(sock, obj):
    data = (json.dumps(obj) + '\n').encode('utf-8')
    sock.sendall(data)

def listen_thread(sock):
    f = sock.makefile('r', encoding='utf-8')
    try:
        while True:
            line = f.readline()
            if not line:
                print("[client] з'єднання закрито сервером")
                break
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            mtype = msg.get('type')
            if mtype == 'positions':
                pos = msg.get('positions', {})
                print("[positions]")
                if not pos:
                    print("  (нічого)")
                for user, coords in pos.items():
                    print(f"  {user}: {coords}")
            elif mtype == 'message':
                user = msg.get('user')
                text = msg.get('text')
                print(f"[{user}] {text}")
            else:
                print(f"[debug] отримано: {msg}")
    except Exception as e:
        print(f"[client] помилка прослуховування: {e}")
    finally:
        try:
            sock.close()
        except:
            pass
        sys.exit(0)

def main():
    name = input("Введіть своє ім'я: ").strip()
    if not name:
        print("Ім'я не може бути пустим.")
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        print(f"Не зміг підключитись: {e}")
        return

    send_json(sock, {"type":"register","user":name})

    t = threading.Thread(target=listen_thread, args=(sock,), daemon=True)
    t.start()

    try:
        while True:
            line = input()
            if not line:
                continue
            if line.startswith('/move'):
                parts = line.split()
                if len(parts) != 3:
                    print("Формат: /move x y")
                    continue
                try:
                    x = float(parts[1])
                    y = float(parts[2])
                except ValueError:
                    print("x і y мають бути числами.")
                    continue
                send_json(sock, {"type":"position","user":name,"x":x,"y":y})
            else:
                send_json(sock, {"type":"message","user":name,"text":line})
    except (KeyboardInterrupt, EOFError):
        print("\n[client] вихід...")
    finally:
        try:
            sock.close()
        except:
            pass

if __name__ == '__main__':
    main()
