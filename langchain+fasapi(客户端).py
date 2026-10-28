import requests

url = "http://127.0.0.1:9256/users"
id = input("请输入你的名字:")
password = input("请输入你的密码:")

def use_chat():
    data = [{"role": "system", "content": "你是一个英语老师"}]
    while True:
        user_input = input("请输入你的问题(输入end退出):")
        if user_input.strip() == "end":
            print("结束对话")
            break
        data.append({"role": "user", "content": user_input})
        try:
            response = requests.post(url, json={"id": id, "password": password, "data": data}, stream=True, timeout=30)
            # 状态码判断
            if response.status_code == 200:
                full_text = ""
                print("AI:", end="", flush=True)
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    chunk_txt = line
                    full_text += chunk_txt
                    print(chunk_txt, end="", flush=True)
                print()
                data.append({"role": "assistant", "content": full_text})
            elif response.status_code == 400:
                print(f"\n【400】参数错误：{response.text}")
            elif response.status_code == 404:
                print("\n【404】接口不存在")
            elif response.status_code == 405:
                print("\n【405】请求方法错误，请使用POST")
            elif response.status_code == 500:
                print("\n【500】服务端内部报错")
            elif response.status_code == 502:
                print("\n【502】网关异常，上游无响应")
            else:
                print(f"\n【{response.status_code}】未知错误")
        except requests.exceptions.ConnectionError:
            print("\n【连接失败 10061】服务没有启动或者端口不对")
        except Exception as e:
            print(f"\n【异常】{e}")

if __name__ == "__main__":
    use_chat()
