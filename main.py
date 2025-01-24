import nodriver as uc
import socket
import eel
import time
import threading
import random
import logging
from colorama import init, Fore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cloudflare_bypass.log', mode='w')
    ]
)

init(autoreset=True)

async def run(browserId, browsersAmount, proxyList):
    try:
        link = 'https://tickets.rolandgarros.com/en/'
        
        config = uc.Config(user_data_dir=None, headless=False, browser_executable_path=None,\
        browser_args=None, sandbox=True, lang='en-US')
        config.add_extension(extension_path="./BPProxySwitcher")
        driver = await uc.Browser.create(config=config)
        await driver.get(link)
        tab = driver.main_tab


        if proxyList:
            await tab.get('chrome://extensions/')
            script = """
                    (async () => {let data = await chrome.management.getAll(); return data;})();
            """

            extensions = await tab.evaluate(expression=script, await_promise=True)
            # print("extensions", extensions)
            if extensions is None: 
               print('Проксі розширення не встановлене!')
               return None
            filtered_extensions = [extension for extension in extensions if "BP Proxy Switcher" in extension['name']]

            vpn_id = [extension['id'] for extension in filtered_extensions if 'id' in extension][0]
            vpn_url = f'chrome-extension://{vpn_id}/popup.html'
            await tab.get(vpn_url)
            # await tab.get(vpn_url)
            delete_tab = await tab.select('#deleteOptions')
            # driver.evaluate("arguments[0].scrollIntoView();", delete_tab)
            await delete_tab.mouse_click()
            time.sleep(1)
            temp = await tab.select('#privacy > div:first-of-type > input')
            await temp.mouse_click()
            time.sleep(1)
            temp1 = await tab.select('#privacy > div:nth-of-type(2) > input')
            await temp1.mouse_click()
            time.sleep(1)
            temp2 = await tab.select('#privacy > div:nth-of-type(4) > input')
            await temp2.mouse_click()
            time.sleep(1)
            temp3 = await tab.select('#privacy > div:nth-of-type(7) > input')
            await temp3.mouse_click()


            optionsOK = await tab.select('#optionsOK')

            # driver.execute_script("arguments[0].scrollIntoView();", optionsOK)
            await optionsOK.mouse_click()
            time.sleep(1)
            edit = await tab.select('#editProxyList > small > b')
            # driver.execute_script("arguments[0].scrollIntoView();", edit)
            await edit.mouse_click()
            time.sleep(1)
            text_area = await tab.select('#proxiesTextArea')
            await text_area.send_keys(proxyList)
            time.sleep(1)
            ok_button = await tab.select('#addProxyOK')
            await ok_button.mouse_click()
            time.sleep(3)
            
            proxy_switch_list = await tab.find_all('#proxySelectDiv > div > div > ul > li')
            if len(proxy_switch_list) == 3: await proxy_switch_list[2].mouse_click()
            else: proxy_switch_list[random.randint(2, await len(proxy_switch_list))-1].mouse_click()
            time.sleep(5)
            
            proxy_auto_reload_checkbox = await tab.select('#autoReload')
            # driver.execute_script("arguments[0].scrollIntoView();", proxy_auto_reload_checkbox)
            await proxy_auto_reload_checkbox.mouse_click()
            time.sleep(2)
            # print('success')
        await tab.get(link)
        print(Fore.GREEN + f"Thread {browserId}: Successfully started!\n")
        input('exit?')
        return False

    except Exception as e: print(e)


def is_port_open(host, port):
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.connect((host, port))
    return True
  except (socket.timeout, ConnectionRefusedError):
    return False
  finally:
    sock.close()


def intermidiate(browserId, browsersAmount, proxyList):
   uc.loop().run_until_complete(run(browserId, browsersAmount, proxyList))


@eel.expose
def main(browsersAmount, proxyList):
    # print(browsersAmount, proxyList)

    threads = []
    for i in range(1, int(browsersAmount)+1):
        if i!= 1: time.sleep(i*30)
        thread = threading.Thread(target=intermidiate, args=(i, browsersAmount, proxyList))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    eel.init('web')

    port = 8000
    while True:
        try:
            if not is_port_open('localhost', port):
                eel.start('main.html', size=(600, 800), port=port)
                break
            else:
                port += 1
        except OSError as e:
            print(e)
