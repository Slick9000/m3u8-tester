import asyncio
import datetime
from datetime import timedelta
import io
import os
import random
import re
import sys
import time

python = 'python3'

if 'win' in sys.platform:
    
    python = 'python'

print('(*) Checking for required dependencies...\n')

while True:
    
    try:
        
        import requests
        #NOTE: REQUIRES 64 BIT VLC TO BE INSTALLED
        import vlc
        
        break
    
    except ModuleNotFoundError as e:
        
        module = str(e)[17:-1]

        if module == "vlc":

            module = "python-vlc"
        
        print(f'(*) Installing {module} module for python')
        
        try:
            
            if os.system(f'{python} -m pip install {module}') != 0:
                
                raise error
            
        except Exception:
            print(f'(!) Error installing "{module}" module. Do you have pip installed?')
            
            input(f'(!) Failed to initialize m3u8 tester. Press Ctrl+C to exit...')
            
            sys.exit()


async def selection():

    option = input(
        "M3U8 Tester\n"
        "Select a method to input data:\n"
        "1 - Raw Webpage\n"
        "2 - M3U/M3U8 File\n"
        "3 - Raw Webpage with ONLY Links\n"
        "4 - Raw File with ONLY Links\n"
        "5 - Exit Program\n: "
        )

    while not any(x in option for x in ["1", "2", "3", "4", "5"]):

        print("Invalid option!\n")

        option = input(
            "M3U8 Tester\n"
            "Select a method to input data:\n"
            "1 - Raw Webpage\n"
            "2 - M3U/M3U8 File\n"
            "3 - Raw Webpage with ONLY Links\n"
            "4 - Raw File with ONLY Links\n"
            "5 - Exit Program\n: "
            )

    if option == "1":

        await webProcess()

    if option == "2":

        await fileProcess()

    if option == "3":

        await linkOnlyWebProcess()

    if option == "4":

        await linkOnlyFileProcess()

    if option == "5":

        try:
        
            input("Press enter to exit program!")
        
        except SyntaxError:
        
            pass

        exit()

async def webProcess():

    url = input("\nEnter '/RETURN' to return to option selection\nInput a link\n: ")

    if url == "/RETURN" or url == "/return":
        
        await selection()

    try:

        response = requests.get(url).content.decode('utf-8')

    except requests.exceptions.MissingSchema:

        print("\nURL invalid. Please enter a valid URL.")

        try:
        
            input("Press enter to continue.\n")
        
        except SyntaxError:
        
            pass

        await webProcess()

    print("Adding new data entries...")

    temp1_name = str(random.randint(111111, 999999))
    
    temp2_name = str(random.randint(111111, 999999))


    with io.open(f"{temp1_name}.txt", mode="a+", encoding="utf-8") as file1:

        file1.write(response)

        file1.close()

        print("New entries added to masterdata file.")

    with io.open(f"{temp2_name}.txt", mode="w", encoding="utf-8") as file2:

        file2.write(response)

        file2.close()

    with io.open(f"{temp2_name}.txt", mode="r", encoding="utf-8") as file2:

        contents = file2.read()

        file2.close()

        new_contents = contents.replace("\n", " ")
        
    with io.open(f"{temp2_name}.txt", mode="w", encoding="utf-8") as file2:
        
        file2.write(new_contents)
        
        file2.close()

    with io.open(f"{temp2_name}.txt", mode="r", encoding="utf-8") as file2:

        for line in file2:

            #removes quotes that get left over sometimes in the link searching
            #removes image links. image links don't stop it from working but increase
            #processing time
            #search for all other links
            remquote = re.sub(r'"', '', line)

            remimages = re.sub(r'[(http)(https)][^\s]+jpg|[(http)(https)][^\s]+jpeg|[(http)(https)][^\s]+png|[(http)(https)][^\s]+jpeg|[(http)(https)][^\s]+svg|[(http)(https)][^\s]+&s',
                               '', remquote)
        
            urls = re.findall(r'(https?://[^\s]+)', remimages)

    result_file_name = datetime.datetime.now().strftime("%dth %B, %Y (%X).m3u8")

    final_result_name = re.sub(r'(:\.?)', '-', result_file_name)

    with io.open(final_result_name, mode="w", encoding="utf-8") as result_file:

        failed = 0

        working = 0

        start_time = time.monotonic()

        result_file.write("#EXTM3U\n")

        print(f"Loading {len(urls)} URLS...\n\n")

        for i in urls:
    
            #create VLC instance
            instance = vlc.Instance('--no-video --rtsp-timeout=12')

            #define VLC player
            player=instance.media_player_new()

            #define VLC media
            media=instance.media_new(i)

            #set player media
            player.set_media(media)

            #play the media
            player.play()

            #sleep for 8 sec for VLC to complete retries
            print("Press 'Ctrl+C' to end process at any time.\n"
                  "All current progress will be saved.\n"
                  )

            await asyncio.sleep(8)

            #get current state.
            state = str(player.get_state())

            #find out if stream is working.
            if state == "vlc.State.Error" or state == "State.Error" or state == "vlc.State.Ended" or state == "State.Ended" or state == "vlc.State.Opening" or state == "State.Opening":

                failed = failed + 1

                print('Stream is dead. Current state = {}'.format(state))

                player.stop()

                print(f"Failed links: {failed}\n"
                      f"Working links: {working}\n"
                      f"Completed: {working + failed}/{len(urls)}"
                      )
                       
            else:

                working = working + 1

                with io.open(f"{temp1_name}.txt", mode="r", encoding="utf-8") as file1:

                    master_data = file1.read()
            
                    print('Stream is working. Current state = {}'.format(state))

                    player.stop()

                    print(f"Failed links: {failed}\n"
                          f"Working links: {working}\n"
                          f"Completed: {working + failed}/{len(urls)}"
                          )

                    #text formatting and regex
                    #escapes ? for regex, removes list formatting, and removes
                    #physical \n in text
                    escape_qm = i.replace("?", "\\?")

                    format_get = re.findall(r'#EXTINF.*\n{url}'
                        .format(url=escape_qm), master_data)

                    remove_start_bracket = str(format_get).replace("['", "")

                    remove_end_bracket = remove_start_bracket.replace("']", "")

                    remove_newline = remove_end_bracket.replace("\\n", "\n")

                    result_file.write(f"{remove_newline}\n\n")

    end_time = time.monotonic()
        
    result_file.close()

    file1.close()

    file2.close()
    
    os.remove(file1.name)
    
    os.remove(file2.name)

    if working == 0:

        print("No links available.\n"
              f"Removing {result_file.name} from folder..."
              )

        os.remove(result_file.name)

        print("File removed.")

    else:

        print("Link testing complete!"
              f"Working links can be located in {os.path.realpath(result_file.name)}."
              )

        print(f"Failed links: {failed}/{len(urls)}\n"
              f"Working links: {working}/{len(urls)}\n"
              f"Processing time: {timedelta(seconds=end_time - start_time)}\n"
              )

    try:
        
        input("Press enter to exit program!")
        
    except SyntaxError:
        
        pass

async def fileProcess():

    fileName = input("\nEnter '/RETURN' to return to option selection\n"
                     "Input file path\n"
                     "(If file name only is specified, it will read from the folder "
                     "the program is saved to)\n: "
                     )

    if fileName == "/RETURN" or fileName == "/return":

        await selection()

    length = len(re.findall(r'\\|/', fileName)) + 1

    if length == 1:

        fileName = f"{os.getcwd()}/{fileName}"

    if os.path.exists(fileName):

        with io.open(fileName, mode="r", encoding="utf-8") as master_content:

            file_content = master_content.read()

            print("Adding new data entries...")

            temp1_name = str(random.randint(111111, 999999))
            
            temp2_name = str(random.randint(111111, 999999))

        with io.open(f"{temp1_name}.txt", mode="a+", encoding="utf-8") as file1:

            file1.write(file_content)

            file1.close()

            print("New entries added to masterdata file.")

        with io.open(f"{temp2_name}.txt", mode="w", encoding="utf-8") as file2:

            file2.write(file_content)

            file2.close()

        with io.open(f"{temp2_name}.txt", mode="r", encoding="utf-8") as file2:

            contents = file2.read()

            file2.close()

            new_contents = contents.replace("\n", " ")
        
        with io.open(f"{temp2_name}.txt", mode="w", encoding="utf-8") as file2:
        
            file2.write(new_contents)
        
            file2.close()

        with io.open(f"{temp2_name}.txt", mode="r", encoding="utf-8") as file2:

            for line in file2:
                
                #removes quotes that get left over sometimes in the link searching
                #removes image links. image links don't stop it from working but increase
                #processing time
                #search for all other links
                remquote = re.sub(r'"', '', line)

                remimages = re.sub(r'[(http)(https)][^\s]+jpg|[(http)(https)][^\s]+jpeg|[(http)(https)][^\s]+png|[(http)(https)][^\s]+jpeg|[(http)(https)][^\s]+svg|[(http)(https)][^\s]+&s',
                                   '', remquote)
        
                urls = re.findall(r'(https?://[^\s]+)', remimages)

        result_file_name = datetime.datetime.now().strftime("%dth %B, %Y (%X).m3u8")

        final_result_name = re.sub(r'(:\.?)', '-', result_file_name)

        with io.open(final_result_name, mode="w", encoding="utf-8") as result_file:

            failed = 0

            working = 0

            start_time = time.monotonic()

            result_file.write("#EXTM3U\n")

            print(f"Loading {len(urls)} URLS...\n\n")

            for i in urls:
    
                #create VLC instance
                instance = vlc.Instance("--no-video --rtsp-timeout=12")

                #define VLC player
                player=instance.media_player_new()

                #define VLC media
                media=instance.media_new(i)

                #set player media
                player.set_media(media)

                #play the media
                player.play()

                #sleep for 8 sec for VLC to complete retries
                print("Press 'Ctrl+C' to end process at any time.\n"
                      "All current progress will be saved.\n"
                      )

                await asyncio.sleep(8)

                #get current state.
                state = str(player.get_state())

                #find out if stream is working.
                if state == "vlc.State.Error" or state == "State.Error" or state == "vlc.State.Ended" or state == "State.Ended" or state == "vlc.State.Opening" or state == "State.Opening":

                    failed = failed + 1

                    print('Stream is dead. Current state = {}'.format(state))

                    player.stop()

                    print(f"Failed links: {failed}\n"
                          f"Working links: {working}\n"
                          f"Completed: {working + failed}/{len(urls)}"
                          )
                       
                else:

                    working = working + 1

                    with io.open(f"{temp1_name}.txt", mode="r", encoding="utf-8") as file1:

                        master_data = file1.read()
            
                        print('Stream is working. Current state = {}'.format(state))

                        player.stop()

                        print(f"Failed links: {failed}\n"
                              f"Working links: {working}\n"
                              f"Completed: {working + failed}/{len(urls)}"
                              )

                        #text formatting and regex
                        #escapes ? for regex, removes list formatting, and removes
                        #physical \n in text
                        escape_qm = i.replace("?", "\\?")

                        format_get = re.findall(r'#EXTINF.*\n{url}'
                            .format(url=escape_qm), master_data)

                        remove_start_bracket = str(format_get).replace("['", "")

                        remove_end_bracket = remove_start_bracket.replace("']", "")

                        remove_newline = remove_end_bracket.replace("\\n", "\n")

                        result_file.write(f"{remove_newline}\n\n")

        end_time = time.monotonic()
        
        result_file.close()

        file1.close()

        file2.close()
    
        os.remove(file1.name)
    
        os.remove(file2.name)

        if working == 0:

            print("No links available.\n"
                  f"Removing {result_file.name} from folder..."
                  )

            os.remove(result_file.name)

            print("File removed.")

        else:

            print("Link testing complete! "
                  f"Working links can be located in {os.path.realpath(result_file.name)}."
                  )

            print(f"Failed links: {failed}/{len(urls)}\n"
                  f"Working links: {working}/{len(urls)}\n"
                  f"Processing time: {timedelta(seconds=end_time - start_time)}\n"
                  )

        try:
        
            input("Press enter to exit program!")
        
        except SyntaxError:
        
            pass

    else:
        
        print("\nInvalid file path input! Please re-enter file path.\n"
              "e.g 'C://(user)/Downloads/(file).m3u8'"
              )

        try:
        
            input("Press enter to continue.\n")
        
        except SyntaxError:
        
            pass

        await fileProcess()


async def linkOnlyWebProcess():

    url = input("\nEnter '/RETURN' to return to option selection\nInput a link\n: ")

    if url == "/RETURN" or url == "/return":
        
        await selection()

    try:

        response = requests.get(url).content.decode('utf-8')

    except requests.exceptions.MissingSchema:

        print("\nURL invalid. Please enter a valid URL.")

        try:
        
            input("Press enter to continue.\n")
        
        except SyntaxError:
        
            pass

        await linkOnlyWebProcess()

    print("Adding new data entries...")

    temp1_name = str(random.randint(111111, 999999))
    
    temp2_name = str(random.randint(111111, 999999))


    with io.open(f"{temp1_name}.txt", mode="a+", encoding="utf-8") as file1:

        file1.write(response)

        file1.close()

        print("New entries added to masterdata file.")

    with io.open(f"{temp2_name}.txt", mode="w", encoding="utf-8") as file2:

        file2.write(response)

        file2.close()

    with io.open(f"{temp2_name}.txt", mode="r", encoding="utf-8") as file2:

        contents = file2.read()

        file2.close()

        new_contents = contents.replace("\n", " ")
        
    with io.open(f"{temp2_name}.txt", mode="w", encoding="utf-8") as file2:
        
        file2.write(new_contents)
        
        file2.close()

    with io.open(f"{temp2_name}.txt", mode="r", encoding="utf-8") as file2:

        for line in file2:

            #removes quotes that get left over sometimes in the link searching
            #removes image links. image links don't stop it from working but increase
            #processing time
            #search for all other links
            remquote = re.sub(r'"', '', line)

            remimages = re.sub(r'[(http)(https)][^\s]+jpg|[(http)(https)][^\s]+jpeg|[(http)(https)][^\s]+png|[(http)(https)][^\s]+jpeg|[(http)(https)][^\s]+svg|[(http)(https)][^\s]+&s',
                               '', remquote)
        
            urls = re.findall(r'(https?://[^\s]+)', remimages)

    result_file_name = datetime.datetime.now().strftime("%dth %B, %Y (%X).m3u8")

    final_result_name = re.sub(r'(:\.?)', '-', result_file_name)

    with io.open(final_result_name, mode="w", encoding="utf-8") as result_file:

        failed = 0

        working = 0

        start_time = time.monotonic()

        print(f"Loading {len(urls)} URLS...\n\n")

        for i in urls:
    
            #create VLC instance
            instance = vlc.Instance('--no-video --rtsp-timeout=12')

            #define VLC player
            player=instance.media_player_new()

            #define VLC media
            media=instance.media_new(i)

            #set player media
            player.set_media(media)

            #play the media
            player.play()

            #sleep for 8 sec for VLC to complete retries
            print("Press 'Ctrl+C' to end process at any time.\n"
                  "All current progress will be saved.\n"
                  )

            await asyncio.sleep(8)

            #get current state.
            state = str(player.get_state())

            #find out if stream is working.
            if state == "vlc.State.Error" or state == "State.Error" or state == "vlc.State.Ended" or state == "State.Ended" or state == "vlc.State.Opening" or state == "State.Opening":

                failed = failed + 1

                print('Stream is dead. Current state = {}'.format(state))

                player.stop()

                print(f"Failed links: {failed}\n"
                      f"Working links: {working}\n"
                      f"Completed: {working + failed}/{len(urls)}"
                      )
                       
            else:

                working = working + 1
            
                print('Stream is working. Current state = {}'.format(state))

                player.stop()

                print(f"Failed links: {failed}\n"
                      f"Working links: {working}\n"
                      f"Completed: {working + failed}/{len(urls)}"
                      )

                result_file.write(f"{i}\n")

    end_time = time.monotonic()
        
    result_file.close()

    file1.close()

    file2.close()
    
    os.remove(file1.name)
    
    os.remove(file2.name)

    if working == 0:

        print("No links available.\n"
              f"Removing {result_file.name} from folder..."
              )

        os.remove(result_file.name)

        print("File removed.")

    else:

        print("Link testing complete!"
              f"Working links can be located in {os.path.realpath(result_file.name)}."
              )

        print(f"Failed links: {failed}/{len(urls)}\n"
              f"Working links: {working}/{len(urls)}\n"
              f"Processing time: {timedelta(seconds=end_time - start_time)}\n"
              )

    try:
        
        input("Press enter to exit program!")
        
    except SyntaxError:
        
        pass


async def linkOnlyFileProcess():

    fileName = input("\nEnter '/RETURN' to return to option selection\n"
                     "Input file path\n"
                     "(If file name only is specified, it will read from the folder "
                     "the program is saved to)\n: "
                     )

    if fileName == "/RETURN" or fileName == "/return":

        await selection()

    length = len(re.findall(r'\\|/', fileName)) + 1

    if length == 1:

        fileName = f"{os.getcwd()}/{fileName}"

    if os.path.exists(fileName):

        with io.open(fileName, mode="r", encoding="utf-8") as master_content:

            file_content = master_content.read()

            print("Adding new data entries...")

            temp1_name = str(random.randint(111111, 999999))
            
            temp2_name = str(random.randint(111111, 999999))

        with io.open(f"{temp1_name}.txt", mode="a+", encoding="utf-8") as file1:

            file1.write(file_content)

            file1.close()

            print("New entries added to masterdata file.")

        with io.open(f"{temp2_name}.txt", mode="w", encoding="utf-8") as file2:

            file2.write(file_content)

            file2.close()

        with io.open(f"{temp2_name}.txt", mode="r", encoding="utf-8") as file2:

            contents = file2.read()

            file2.close()

            new_contents = contents.replace("\n", " ")
        
        with io.open(f"{temp2_name}.txt", mode="w", encoding="utf-8") as file2:
        
            file2.write(new_contents)
        
            file2.close()

        with io.open(f"{temp2_name}.txt", mode="r", encoding="utf-8") as file2:

            for line in file2:
                
                #removes quotes that get left over sometimes in the link searching
                #removes image links. image links don't stop it from working but increase
                #processing time
                #search for all other links
                remquote = re.sub(r'"', '', line)

                remimages = re.sub(r'[(http)(https)][^\s]+jpg|[(http)(https)][^\s]+jpeg|[(http)(https)][^\s]+png|[(http)(https)][^\s]+jpeg|[(http)(https)][^\s]+svg|[(http)(https)][^\s]+&s',
                                   '', remquote)
        
                urls = re.findall(r'(https?://[^\s]+)', remimages)

        result_file_name = datetime.datetime.now().strftime("%dth %B, %Y (%X).m3u8")

        final_result_name = re.sub(r'(:\.?)', '-', result_file_name)

        with io.open(final_result_name, mode="w", encoding="utf-8") as result_file:

            failed = 0

            working = 0

            start_time = time.monotonic()

            print(f"Loading {len(urls)} URLS...\n\n")

            for i in urls:
    
                #create VLC instance
                instance = vlc.Instance('--no-video --rtsp-timeout=12')

                #define VLC player
                player=instance.media_player_new()

                #define VLC media
                media=instance.media_new(i)

                #set player media
                player.set_media(media)

                #play the media
                player.play()

                #sleep for 8 sec for VLC to complete retries
                print("Press 'Ctrl+C' to end process at any time.\n"
                      "All current progress will be saved.\n"
                      )

                await asyncio.sleep(8)

                #get current state.
                state = str(player.get_state())

                #find out if stream is working.
                if state == "vlc.State.Error" or state == "State.Error" or state == "vlc.State.Ended" or state == "State.Ended" or state == "vlc.State.Opening" or state == "State.Opening":

                    failed = failed + 1

                    print('Stream is dead. Current state = {}'.format(state))

                    player.stop()

                    print(f"Failed links: {failed}\n"
                          f"Working links: {working}\n"
                          f"Completed: {working + failed}/{len(urls)}"
                          )
                       
                else:

                    working = working + 1
            
                    print('Stream is working. Current state = {}'.format(state))

                    player.stop()

                    print(f"Failed links: {failed}\n"
                          f"Working links: {working}\n"
                          f"Completed: {working + failed}/{len(urls)}"
                          )
                        
                    result_file.write(f"{i}\n")

        end_time = time.monotonic()
        
        result_file.close()

        file1.close()

        file2.close()
    
        os.remove(file1.name)
    
        os.remove(file2.name)

        if working == 0:

            print("No links available.\n"
                  f"Removing {result_file.name} from folder..."
                  )

            os.remove(result_file.name)

            print("File removed.")

        else:

            print("Link testing complete! "
                  f"Working links can be located in {os.path.realpath(result_file.name)}."
                  )

            print(f"Failed links: {failed}/{len(urls)}\n"
                  f"Working links: {working}/{len(urls)}\n"
                  f"Processing time: {timedelta(seconds=end_time - start_time)}\n"
                  )

        try:
        
            input("Press enter to exit program!")
        
        except SyntaxError:
        
            pass

    else:
        
        print("\nInvalid file path input! Please re-enter file path.\n"
              "e.g 'C://(user)/Downloads/(file).m3u8'"
              )

        try:
        
            input("Press enter to continue.\n")
        
        except SyntaxError:
        
            pass

        await linkOnlyFileProcess()




async def main():

    await selection()


if __name__ == '__main__':

    asyncio.run(main())
