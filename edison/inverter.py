import mraa


analog_input = mraa.Aio(1)
analog_input.read()
