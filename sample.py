from TelloDrone_Lib import TelloDrone

drone = TelloDrone("192.168.10.1",
                    8889,
                    send_reg_j=True,
                    capture_setting=False,
                    take_movie=False)

while True:
    msg = input()
    answer = drone.send_command(msg)
    if not answer:
        break
